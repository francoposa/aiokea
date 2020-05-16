import re
from typing import List

from aiohttp import web
from multidict import MultiMapping

from aiokea.abc import IService, Struct
from aiokea.filters import Filter, EQ
from aiokea.http.adapters import BaseHTTPAdapter


FILTER_KEY_REGEX = re.compile(r"\[(.*?)\]")


class HTTPServiceView:
    def __init__(
        self, service: IService, adapter: BaseHTTPAdapter, id_field: str = None,
    ):
        self.service = service
        self.adapter = adapter
        self.id_field = id_field or "id"

    async def get_handler(self, request: web.Request) -> web.Response:
        """GET handler to retrieve usecases."""
        filters: List[Filter] = _query_to_filters(request.query)
        structs: List[Struct] = await self.service.get_where(filters=filters)
        response_data = [self.adapter.dump_from_struct(s) for s in structs]
        return web.json_response({"data": response_data})


def _query_to_filters(raw_query_map: MultiMapping,) -> List[Filter]:
    query_filters: List[Filter] = []
    for full_query_param in raw_query_map.keys():
        # Regex split allows for standard query: `name=test`
        # as well as filter-style query: `created_at[lte]=2019-06-01`
        query_param_parts: List[str] = FILTER_KEY_REGEX.split(full_query_param)
        query_field: str = query_param_parts[0]
        if len(query_param_parts) == 1:
            # Normal query like `name=test`
            # We assume requester wants a standard equality check
            query_filters.extend(
                Filter(query_field, EQ, query_value)
                for query_value in raw_query_map.getall(full_query_param)
            )
        else:
            # Filter-style query like `created_at[lte]=2019-06-01`
            query_operator: str = query_param_parts[1]
            query_filters.extend(
                Filter(query_field, query_operator, query_value)
                for query_value in raw_query_map.getall(full_query_param)
            )
    return query_filters
