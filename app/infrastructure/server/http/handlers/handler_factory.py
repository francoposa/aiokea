import asyncio
from aiohttp import web

"""
Our adapters provide generalized methods for marshaling and un-marshaling objects
and our database clients provide the same generality for database CRUD operations.
The handler is the only skeleton functionality that dictates when and how we use 
the those adapters and clients, and is the only place where web requests and
database operations are explicitly tied together
This is what makes the skeleton just *work* out of the box.
"""


def post_handler_factory(usecase_class) -> asyncio.coroutine:
    """Create post handler coroutine to be called by aiohtttp upon receipt of a POST request"""

    async def post_handler(request: web.Request) -> web.Response:
        pass

    return post_handler
