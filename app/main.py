import os
from typing import Mapping

from aiohttp import web

from app.infrastructure.server import http


def on_startup(conf: Mapping):
    """Return a startup handler that will perform background tasks"""

    async def startup_handler(app: web.Application) -> None:
        """Run all initialization tasks.

        These are tasks that should be run after the event loop has been started but before the HTTP
        server has been started.
        """
        pass

    return startup_handler


def main():
    app = web.Application()
    http.configure_app(app)
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
