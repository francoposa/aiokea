import json
import os

import pytest
from aiohttp import web
from aiopg.sa import create_engine, Engine

import tests.db_setup as db_setup
from app.infrastructure.datastore.postgres.clients.user import UserPostgresClient
from app.infrastructure.server.http.adapters.user import UserHTTPAdapter
from app.infrastructure.server.http.handlers.base import HTTPHandler
from app.infrastructure.server.http.routes import USER_PATH


@pytest.fixture
async def engine() -> Engine:
    conf = {
        "host": os.getenv("POSTGRES_HOST", default="127.0.0.1"),
        "port": os.getenv("POSTGRES_PORT", default=5432),
        "user": os.getenv("POSTGRES_USER", default="postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", default="postgres"),
        "database": "aiohttp_crud_test",
    }
    return await create_engine(**conf)


@pytest.fixture
async def user_pg_client(engine):
    pg = UserPostgresClient(engine)
    yield pg
    pg.engine.close()
    await pg.engine.wait_closed()


@pytest.fixture
def user_http_adapter():
    return UserHTTPAdapter()


@pytest.fixture
def user_post():
    return json.load(open("./tests/stubs/users/POST.json"))


@pytest.fixture
async def db(loop, engine, user_pg_client):

    tables = ["users"]

    for table in tables:
        async with engine.acquire() as conn:
            await conn.execute("TRUNCATE TABLE {0} CASCADE".format(table))

    await db_setup.setup_db(user_pg_client)
    yield

    for table in tables:
        async with engine.acquire() as conn:
            await conn.execute("TRUNCATE TABLE {0} CASCADE".format(table))

    engine.close()
    await engine.wait_closed()


@pytest.fixture
def http_app(
    loop, user_pg_client, user_http_adapter,
):
    async def startup_handler(app):
        """Run all initialization tasks.

       These are tasks that should be run after the event loop has been started
       but before the HTTP server has been started.
       """

        # Users endpoint
        user_handler = HTTPHandler(db_client=user_pg_client, adapter=UserHTTPAdapter())
        app.router.add_get(USER_PATH, user_handler.get_handler)
        app.router.add_post(USER_PATH, user_handler.post_handler)

    app = web.Application()
    app.on_startup.append(startup_handler)
    return app


@pytest.fixture
async def http_client(aiohttp_client, http_app):
    client = await aiohttp_client(http_app)
    return client
