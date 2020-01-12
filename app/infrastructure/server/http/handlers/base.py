import json
import re
from typing import Type, List, Set, Mapping

import attr
import marshmallow
from aiohttp import web
from multidict import MultiMapping

from app.infrastructure.common.filters.filters import PaginationParams, Filter
from app.infrastructure.common.filters.operators import EQ, FilterOperators
from app.infrastructure.datastore.postgres.clients.base import PostgresClient
from app.infrastructure.server.http.adapters.base import BaseHTTPAdapter

"""
Our adapters provide methods for marshalling data between the mapping types returned
by HTTP requests and the attrs usecase types we have defined.

Our database clients provide the same generality for database CRUD operations.

The handler is only framework functionality that dictates when and how we use 
the those adapters and clients, and is the only place where web requests and
database operations are explicitly tied together.

This is what makes the app CRUD out of the box.
"""

FILTER_KEY_REGEX = re.compile(r"\[(.*?)\]")


class HTTPHandler:
    def __init__(
        self, db_client, adapter: BaseHTTPAdapter, id_field: str = None,
    ):
        self.db_client = db_client
        self.adapter = adapter
        self.id_field = id_field or "id"

    async def get_handler(self, request: web.Request) -> web.Response:
        """GET handler to retrieve usecases."""
        filters: List[Filter] = _query_to_filters(request.query, self.adapter)
        usecases = await self.db_client.select_where(filters=filters)
        response_data = [self.adapter.usecase_to_mapping(u) for u in usecases]
        return web.json_response({"data": response_data})

    async def post_handler(self, request: web.Request) -> web.Response:
        """POST handler to create a usecase."""
        try:
            request_data = await request.json()
        except Exception:
            raise web.HTTPBadRequest(text=json.dumps({"errors": ["The supplied JSON is invalid."]}))

        try:
            request_usecase = self.adapter.mapping_to_usecase(request_data)
        except marshmallow.exceptions.ValidationError as e:
            error_list = [{k: v} for k, v in e.messages.items()]
            raise web.HTTPUnprocessableEntity(
                text=json.dumps({"errors": error_list}), content_type="application/json"
            )
        try:
            usecase = await self.db_client.insert(request_usecase)
        except PostgresClient.DuplicateError as e:
            raise web.HTTPConflict(
                text=json.dumps({"errors": [e.api_error]}), content_type="application/json"
            )
        response_data = self.adapter.usecase_to_mapping(usecase)
        return web.json_response({"data": response_data})

    async def patch_handler(self, request: web.Request) -> web.Response:
        """PATCH handler to partially update a usecase."""
        id = request.match_info["id"]
        id_filter = Filter(self.id_field, FilterOperators.EQ.value, id)
        db_usecase = await self.db_client.select_first_where([id_filter])
        if not db_usecase:
            self._raise_usecase_not_found_for_id(id)
        try:
            request_data = await request.json()
        except Exception:
            raise web.HTTPBadRequest(text=json.dumps({"errors": ["The supplied JSON is invalid."]}))

        try:
            serialized_request_data: Mapping = self.adapter.schema.load(request_data, partial=True)
        except marshmallow.exceptions.ValidationError as e:
            error_list = [{k: v} for k, v in e.messages.items()]
            raise web.HTTPUnprocessableEntity(
                text=json.dumps({"errors": error_list}), content_type="application/json"
            )

        patchable_fields = self.adapter.schema.Meta.patchable_fields
        for request_field, request_value in serialized_request_data.items():
            if request_data.get(request_field) is not None:
                # data serialized from request may have default or calculated
                # fields set that were not actually sent in the patch request
                if request_field not in patchable_fields:
                    raise web.HTTPConflict(
                        text=json.dumps(
                            {
                                "errors": [
                                    f"Field {request_field} is not a patchable field of {self.adapter.schema.Meta.record_type}. Patchable fields are {patchable_fields}"
                                ]
                            }
                        ),
                        content_type="application/json",
                    )
                # Using evolve here ensures that validators & field generators are re-run
                # on the new instance. Setattr or similar does not re-trigger attrs validation
                db_usecase = attr.evolve(db_usecase, **{request_field: request_value})

        try:
            usecase = await self.db_client.update(db_usecase)
        except PostgresClient.DuplicateError as e:
            raise web.HTTPConflict(
                text=json.dumps({"errors": [e.api_error]}), content_type="application/json"
            )
        response_data = self.adapter.usecase_to_mapping(usecase)
        return web.json_response({"data": response_data})

    def _raise_usecase_not_found_for_id(self, id):
        raise web.HTTPNotFound(
            text=json.dumps(
                {
                    "errors": [
                        f"No {self.adapter.schema.Meta.record_type} found with {self.id_field} {id}"
                    ]
                }
            )
        )


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
