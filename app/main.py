import argparse
import json
import logging
import os
import sys
from typing import Mapping

from aiohttp import web
from aiopg.sa import create_engine


from app.infrastructure.datastore.postgres.user_repo import PostgresUserRepo
from app.infrastructure.server.http.adapters.user import UserHTTPAdapter
from app.infrastructure.server.http.handlers import health
from app.infrastructure.server.http.handlers.base import HTTPHandler
from app.infrastructure.server.http.routes import (
    HEALTH_PATH,
    HEALTH_NAME,
    USER_PATH,
    USER_ID_PATH,
)


def on_startup(conf: Mapping):
    """Return a startup handler that will perform background tasks"""

    async def startup_handler(app: web.Application) -> None:
        """Run all initialization tasks.

        These are tasks that should be run after the event loop has been started
        but before the HTTP server has been started.
        """
        pg_engine = await create_engine(**conf["postgres"])
        user_pg_client = PostgresUserRepo(pg_engine)

        # Health check
        app.router.add_get(HEALTH_PATH, health.health_check, name=HEALTH_NAME)

        # Users endpoint
        user_handler = HTTPHandler(db_client=user_pg_client, adapter=UserHTTPAdapter())
        app.router.add_get(USER_PATH, user_handler.get_handler)
        app.router.add_post(USER_PATH, user_handler.post_handler)
        app.router.add_patch(USER_ID_PATH, user_handler.patch_handler)

    return startup_handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Config file")
    parser.add_argument(
        "--level", default=os.environ.get("LOG_LEVEL", "INFO"), help="Logging level."
    )
    args = parser.parse_args()

    # Load config.
    with open(args.config, "r") as conf_file:
        conf = json.load(conf_file)

    # Initialize logger
    logging.basicConfig(stream=sys.stdout, level=args.level)

    app = web.Application()
    app.on_startup.append(on_startup(conf))
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
