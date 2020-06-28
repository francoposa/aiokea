import json
import os

import pytest
from aiohttp import web
from aiopg.sa import create_engine, Engine

from aiokea.http.handlers import AIOHTTPServiceHandler
from tests.stubs.user.http_adapter import UserHTTPAdapter
from tests.stubs.user.repo import AIOPGUserRepo, USER, setup_user_repo
from tests.stubs.user.repo_adapter import UserRepoAdapter


@pytest.fixture
def user_repo_adapter():
    return UserRepoAdapter()


@pytest.fixture
async def aiopg_engine() -> Engine:
    conf = {
        "host": os.getenv("POSTGRES_HOST", default="127.0.0.1"),
        "port": os.getenv("POSTGRES_PORT", default=5432),
        "user": os.getenv("POSTGRES_USER", default="postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", default="postgres"),
        "database": "aiokea_test",
    }
    return await create_engine(**conf)


@pytest.fixture
async def aiopg_user_repo(aiopg_engine):
    pg = AIOPGUserRepo(aiopg_engine)
    yield pg
    pg.engine.close()
    await pg.engine.wait_closed()


@pytest.fixture
async def aiopg_db(loop, aiopg_engine, aiopg_user_repo):

    tables = [USER]

    for table in tables:
        async with aiopg_engine.acquire() as conn:
            await conn.execute("TRUNCATE TABLE {0} CASCADE".format(table.name))

    await setup_user_repo(aiopg_user_repo)
    yield

    for table in tables:
        async with aiopg_engine.acquire() as conn:
            await conn.execute("TRUNCATE TABLE {0} CASCADE".format(table.name))

    aiopg_engine.close()
    await aiopg_engine.wait_closed()


@pytest.fixture
def user_http_adapter():
    return UserHTTPAdapter()


@pytest.fixture
def user_post():
    return json.load(open("./tests/stubs/user/json/POST.json"))


@pytest.fixture
def http_app(
    aiopg_db, aiopg_user_repo, user_http_adapter,
):
    async def startup_handler(app):
        """Run all initialization tasks.

       These are tasks that should be run after the event loop has been started
       but before the HTTP server has been started.
       """

        # Users endpoint
        user_handler = AIOHTTPServiceHandler(
            service=aiopg_user_repo, adapter=user_http_adapter
        )
        app.router.add_get("/api/v1/users", user_handler.get_handler)
        app.router.add_post("/api/v1/users", user_handler.post_handler)

    app = web.Application()
    app.on_startup.append(startup_handler)
    return app


@pytest.fixture
async def http_client(aiohttp_client, http_app):
    client = await aiohttp_client(http_app)
    return client
