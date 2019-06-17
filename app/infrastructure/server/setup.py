"""
Setup functions for HTTP server.
"""
import asyncio
from typing import Awaitable

import aiohttp_cors
from aiohttp import web

from app.infrastructure.server.handlers import health

RUNNING_TASKS = "running_tasks"

HEALTH = "/health"
INFO = "/info"


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

    # Health check.
    app.router.add_get(HEALTH, health.health_check)

    # Metadata.
    app.router.add_get(INFO, health.info)


def register_dependency(app, constant_key, dependency, usecase=None):
    """Add dependencies used by the HTTP handlers."""

    if usecase is None:
        app[constant_key] = dependency
    else:
        if constant_key not in app:
            app[constant_key] = {}
        app[constant_key][usecase] = dependency


def register_task(app: web.Application, coro: Awaitable):
    """Register a background task with the aiohttp app.
    """

    if RUNNING_TASKS not in app:
        app[RUNNING_TASKS] = []

    task = asyncio.create_task(coro)
    app[RUNNING_TASKS].append(task)
