
from typing import Type

from aiohttp import web

from app.infrastructure.server import app_constants

"""
Our adapters provide generalized methods for marshaling and un-marshaling objects
and our database clients provide the same generality for database CRUD operations.
The handler is the only skeleton functionality that dictates when and how we use 
the those adapters and clients, and is the only place where web requests and
database operations are explicitly tied together
This is what makes the app CRUD out of the box.
"""


def post_handler_factory(usecase_class: Type):
    """Create post handler coroutine to be called by aiohttp upon receipt of a POST request"""

    async def post_handler(request: web.Request) -> web.Response:
        """POST handler for a usecase."""

        datastore_client = request.app[app_constants.DATASTORE_CLIENT][usecase_class]
        adapter = request.app[app_constants.HTTP_ADAPTER][usecase_class]


    return post_handler
