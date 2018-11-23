"""
Setup functions for HTTP server.
"""

import aiohttp_cors

from app.infrastructure.server.http.handlers import health
from app.infrastructure.server.http.errors import ERROR_HANDLERS


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


def configure_app(app):
    """Configure the web.Application."""

    _setup_routes(app)


def register_dependency(app, constant_key, dependency, usecase=None):
    """Add dependencies used by the HTTP handlers."""

    if usecase is None:
        app[constant_key] = dependency
    else:
        if constant_key not in app:
            app[constant_key] = {}
        app[constant_key][usecase] = dependency
