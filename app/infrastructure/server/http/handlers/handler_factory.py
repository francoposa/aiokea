import json
import re
from typing import Type, List, Set

import attr
import marshmallow
from aiohttp import web
from multidict import MultiMapping

from app.infrastructure.common.filters.filters import PaginationParams, Filter
from app.infrastructure.common.filters.operators import EQ, FilterOperators
from app.infrastructure.datastore.postgres.clients.base import BasePostgresClient
from app.infrastructure.server.http.app_constants import DATABASE_CLIENT, HTTP_ADAPTER
from app.infrastructure.server.http.adapters.base import BaseHTTPAdapter

"""
Our adapters provide methods for marshalling data between the mapping types returned
by HTTP requests and the attrs usecase types we have defined.

Our database clients provide the same generality for database CRUD operations.

The handler is only skeleton functionality that dictates when and how we use 
the those adapters and clients, and is the only place where web requests and
database operations are explicitly tied together.

This is what makes the app CRUD out of the box.
"""

FILTER_KEY_REGEX = re.compile(r"\[(.*?)\]")


def post_handler_factory(usecase_class: Type):
    """Create post handler coroutine to be called by aiohttp upon receipt of a POST request"""

    async def post_handler(request: web.Request) -> web.Response:
        """POST handler for a usecase."""

        db_client: BasePostgresClient = request.app[DATABASE_CLIENT][usecase_class]
        adapter: BaseHTTPAdapter = request.app[HTTP_ADAPTER][usecase_class]

        try:
            post_data = await request.json()
        except Exception:
            raise web.HTTPBadRequest(text=json.dumps({"errors": ["The supplied JSON is invalid."]}))

        try:
            request_usecase = adapter.mapping_to_usecase(post_data)
        except marshmallow.exceptions.ValidationError as e:
            error_list = [{k: v} for k, v in e.messages.items()]
            raise web.HTTPUnprocessableEntity(
                text=json.dumps({"errors": error_list}), content_type="application/json"
            )
        try:
            db_usecase = await db_client.insert(request_usecase)
        except BasePostgresClient.DuplicateError as e:
            raise web.HTTPConflict(
                text=json.dumps({"errors": [e.api_error]}), content_type="application/json",
            )
        response_usecase = adapter.usecase_to_mapping(db_usecase)
        return web.json_response({"data": response_usecase})

    return post_handler


def get_handler_factory(usecase_class: Type):
    """Create get handler coroutine to be called by aiohttp upon receipt of a GET request"""

    async def get_handler(request: web.Request) -> web.Response:
        """GET handler for a usecase."""
        db_client: BasePostgresClient = request.app[DATABASE_CLIENT][usecase_class]
        adapter: BaseHTTPAdapter = request.app[HTTP_ADAPTER][usecase_class]
        filters: List[Filter] = _query_to_filters(request.query, adapter)
        db_usecases = await db_client.select_where(filters=filters)
        response_usecases = [adapter.usecase_to_mapping(u) for u in db_usecases]
        return web.json_response({"data": response_usecases})

    return get_handler


def _query_to_filters(raw_query_map: MultiMapping, adapter: BaseHTTPAdapter) -> List[Filter]:
    valid_filter_fields: Set[str] = _valid_query_params(adapter.usecase_class)
    valid_filter_operators: Set[str] = {item.value for item in FilterOperators}
    query_filters: List[Filter] = []
    for full_query_param in raw_query_map.keys():
        # Regex split allows for standard query: `name=test`
        # as well as filter-style query: `created_at[lte]=2019-06-01`
        query_param_parts: List[str] = FILTER_KEY_REGEX.split(full_query_param)
        if query_param_parts[0] in valid_filter_fields:
            query_field: str = query_param_parts[0]
            if len(query_param_parts) == 1:
                # Normal query like `name=test`
                # We assume requester wants a standard equality check
                query_filters.extend(
                    Filter(query_field, EQ, query_value)
                    for query_value in raw_query_map.getall(full_query_param)
                )
            elif query_param_parts[1] in valid_filter_operators:
                # Filter-style query like `created_at[lte]=2019-06-01`
                query_operator: str = query_param_parts[1]
                query_filters.extend(
                    Filter(query_field, query_operator, query_value)
                    for query_value in raw_query_map.getall(full_query_param)
                )
    return query_filters


def _valid_query_params(usecase_class: Type) -> Set[str]:
    valid_query_params = set()
    for field in attr.fields(usecase_class):
        valid_query_params.add(field.name)
    for item in PaginationParams:
        valid_query_params.add(item.value)
    return valid_query_params
