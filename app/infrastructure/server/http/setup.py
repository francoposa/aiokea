"""
Setup functions for HTTP server.
"""
from typing import Awaitable

import aiohttp_cors
from aiohttp import web

from app.infrastructure.server.http.handlers import health

RUNNING_TASKS = "running_tasks"

HEALTH = "/health"
INFO = "/info"


def _setup_routes(app):
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


def configure_app(app: web.Application, startup_handler):
    """Configure the web.Application."""

    _setup_routes(app)
    # Schedule custom startup routine.
    app.on_startup.append(startup_handler)


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

    task = app.loop.create_task(coro)
    app[RUNNING_TASKS].append(task)
