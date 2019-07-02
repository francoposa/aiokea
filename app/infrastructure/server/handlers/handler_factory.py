import json
from enum import Enum
from typing import Type, Dict

import marshmallow
from aiohttp import web
from multidict import MultiDictProxy

from app.infrastructure.datastore.postgres.clients.base import BasePostgresClient
from app.infrastructure.server.app_constants import DATABASE_CLIENT, HTTP_ADAPTER
from app.infrastructure.server.adapters.base import BaseHTTPAdapter

"""
Our adapters provide methods for marshalling data between the mapping types returned
by HTTP requests and the attrs usecase types we have defined.

Our database clients provide the same generality for database CRUD operations.

The handler is the only skeleton functionality that dictates when and how we use 
the those adapters and clients, and is the only place where web requests and
database operations are explicitly tied together.

This is what makes the app CRUD out of the box.
"""


class HTTPFilterParams(Enum):
    LIMIT = "limit"
    OFFSET = "offset"


class HTTPFilterOperators(Enum):
    EQ = "eq"  # equal to
    NE = "ne"  # not equal to
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal to
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal to
    IN = "in"  # inclusion operator


def post_handler_factory(usecase_class: Type):
    """Create post handler coroutine to be called by aiohttp upon receipt of a POST request"""

    async def post_handler(request: web.Request) -> web.Response:
        """POST handler for a usecase."""

        db_client: BasePostgresClient = request.app[DATABASE_CLIENT][usecase_class]
        adapter: BaseHTTPAdapter = request.app[HTTP_ADAPTER][usecase_class]

        try:
            post_data = await request.json()
        except Exception:
            raise web.HTTPBadRequest(text="The supplied JSON is invalid.")

        try:
            request_usecase = adapter.mapping_to_usecase(post_data)
        except marshmallow.exceptions.ValidationError as e:
            raise web.HTTPUnprocessableEntity(
                text=json.dumps({"errors": e.messages}), content_type="application/json"
            )
        try:
            db_usecase = await db_client.insert(request_usecase)
        except BasePostgresClient.DuplicateError as e:
            raise web.HTTPConflict(
                text=json.dumps({"errors": e.api_error}),
                content_type="application/json",
            )
        response_usecase = adapter.usecase_to_mapping(db_usecase)
        return web.json_response(response_usecase)

    return post_handler


def get_handler_factory(usecase_class: Type):
    """Create get handler coroutine to be called by aiohttp upon receipt of a POST request"""

    async def get_handler(request: web.Request) -> web.Response:
        """GET handler for a usecase."""
        db_client: BasePostgresClient = request.app[DATABASE_CLIENT][usecase_class]
        adapter: BaseHTTPAdapter = request.app[HTTP_ADAPTER][usecase_class]
        query_dict = _parse_query_params(request)
        return web.json_response(query_dict)

    return get_handler


def _parse_query_params(request: web.Request):
    raw_query_dict: MultiDictProxy = request.query
    for key in raw_query_dict.keys():
        print(key)
        print(raw_query_dict.getall(key))
