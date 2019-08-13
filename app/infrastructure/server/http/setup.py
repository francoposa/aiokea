"""
Setup functions for HTTP server.
"""
import asyncio
from typing import Coroutine

import aiohttp_cors
from aiohttp import web

from app.infrastructure.server.http.app_constants import RUNNING_TASKS
from app.infrastructure.server.http.handlers import health
from app.infrastructure.server.http.handlers.handler_factory import (
    post_handler_factory,
    get_handler_factory,
)
from app.infrastructure.server.http.routes import (
    HEALTH_PATH,
    HEALTH_NAME,
    USER_PATH,
    USER_NAME,
)
from app.usecases import User


def setup_routes(app):
    """Add routes to the given aiohttp app."""

    # Default cors settings.
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*"
            )
        },
    )

    # Health check
    app.router.add_get(HEALTH_PATH, health.health_check, name=HEALTH_NAME)

    # Users endpoint
    app.router.add_get(
        USER_PATH, get_handler_factory(usecase_class=User), name=USER_NAME
    )
    app.router.add_post(
        USER_PATH, post_handler_factory(usecase_class=User), name=USER_NAME
    )


def register_dependency(app, constant_key, dependency, usecase_cls=None):
    """Add dependencies used by the HTTP handlers."""

    if usecase_cls is None:
        app[constant_key] = dependency
    else:
        if constant_key not in app:
            app[constant_key] = {}
        app[constant_key][usecase_cls] = dependency


def register_task(app: web.Application, coroutine: Coroutine):
    """Register a background task with the aiohttp app."""

    if RUNNING_TASKS not in app:
        app[RUNNING_TASKS] = []

    task = asyncio.create_task(coroutine)
    app[RUNNING_TASKS].append(task)
