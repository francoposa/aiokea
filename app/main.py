import argparse
import json
import os
from typing import Mapping

from aiohttp import web
from aiopg.sa import create_engine

from app import usecases
from app.infrastructure.datastore.postgres import UserPostgresClient
from app.infrastructure.server import setup_routes, app_constants
from app.infrastructure.server.adapters.user import UserHTTPAdapter
from app.infrastructure.server.setup import register_dependency


def on_startup(conf: Mapping):
    """Return a startup handler that will perform background tasks"""

    async def startup_handler(app: web.Application) -> None:
        """Run all initialization tasks.

        These are tasks that should be run after the event loop has been started but before the HTTP
        server has been started.
        """
        setup_routes(app)
        pg_engine = await create_engine(**conf["postgres"])
        user_pg_client = UserPostgresClient(pg_engine)

        # Register dependencies with the aiohttp app
        register_dependency(
            app, app_constants.DATABASE_CLIENT, user_pg_client, usecases.User
        )
        register_dependency(
            app, app_constants.HTTP_ADAPTER, UserHTTPAdapter(), usecases.User
        )

    return startup_handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Config file")
    args = parser.parse_args()

    # Load config.
    with open(args.config, "r") as conf_file:
        conf = json.load(conf_file)

    app = web.Application()
    app.on_startup.append(on_startup(conf))
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
