import re
from typing import List, Set

from aiohttp import web
from multidict import MultiMapping

from aiokea.abc import IService, Struct
from aiokea.filters import Filter, EQ, PageNumberPaginationParams, FilterOperators
from aiokea.http.adapters import BaseMarshmallowAdapter


FILTER_KEY_REGEX = re.compile(r"\[(.*?)\]")


class AIOHTTPServiceHandler:
    def __init__(
        self, service: IService, adapter: BaseMarshmallowAdapter, id_field: str = None,
    ):
        super().__init__()
        self.service = service
        self.adapter = adapter
        self.id_field = id_field or "id"

    async def get_handler(self, request: web.Request) -> web.Response:
        """GET handler to retrieve usecases."""
        filters: List[Filter] = _query_to_filters(request.query, self.adapter)
        structs: List[Struct] = await self.service.get_where(filters=filters)
        response_data = [self.adapter.dump_from_struct(s) for s in structs]
        return web.json_response({"data": response_data})


def _query_to_filters(
    raw_query_map: MultiMapping, adapter: BaseMarshmallowAdapter
) -> List[Filter]:
    valid_filter_fields: Set[str] = _valid_query_params(adapter)
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
            elif query_param_parts[1] in FilterOperators.values:
                # Filter-style query like `created_at[lte]=2019-06-01`
                query_operator: str = query_param_parts[1]
                query_filters.extend(
                    Filter(query_field, query_operator, query_value)
                    for query_value in raw_query_map.getall(full_query_param)
                )
    return query_filters


def _valid_query_params(adapter: BaseMarshmallowAdapter) -> Set[str]:
    valid_query_params = set()
    for field in adapter.schema.fields:
        valid_query_params.add(field)
    valid_query_params.update(PageNumberPaginationParams.values)
    return valid_query_params
