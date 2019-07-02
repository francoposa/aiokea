import json
import re
from collections import defaultdict
from enum import Enum
from typing import Type, List, Mapping

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

FILTER_KEY_REGEX = re.compile(r"\[(.*?)\]")


class HTTPFilterParams(Enum):
    LIMIT = "limit"
    OFFSET = "offset"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class HTTPFilterOperators(Enum):
    EQ = "eq"  # equal to
    NE = "ne"  # not equal to
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal to
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal to
    IN = "in"  # inclusion operator

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


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


def _parse_query_params(request: web.Request) -> Mapping[str, Mapping[str, list]]:
    raw_query_dict: MultiDictProxy = request.query
    merged_query_dict = defaultdict(lambda: defaultdict(list))
    for full_key in raw_query_dict.keys():
        key_parts: List[str] = FILTER_KEY_REGEX.split(full_key)
        if key_parts:
            key_field: str = key_parts[0]
            if len(key_parts) == 1:
                # Normal query param key like "created_at"
                merged_query_dict[key_field][HTTPFilterOperators.EQ.value].extend(
                    raw_query_dict.getall(full_key)
                )
            else:
                # Filter-style query param key like "created_at[eq]"
                key_filter = key_parts[1]
                merged_query_dict[key_field][key_filter].extend(
                    raw_query_dict.getall(full_key)
                )
    return merged_query_dict
