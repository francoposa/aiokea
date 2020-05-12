import json
import os

import pytest
from aiopg.sa import create_engine, Engine

from tests import pg_setup
from tests.stubs.users.adapter import UserHTTPAdapter
from tests.stubs.users.repo import AiopgUserRepo, USER


@pytest.fixture
def user_http_adapter():
    return UserHTTPAdapter()


@pytest.fixture
def user_post():
    return json.load(open("./tests/stubs/users/json/POST.json"))


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
    pg = AiopgUserRepo(aiopg_engine)
    yield pg
    pg.engine.close()
    await pg.engine.wait_closed()


@pytest.fixture
async def aiopg_db(loop, aiopg_engine, aiopg_user_repo):

    tables = [USER]

    for table in tables:
        async with aiopg_engine.acquire() as conn:
            await conn.execute("TRUNCATE TABLE {0} CASCADE".format(table.name))

    await pg_setup.setup_db(aiopg_user_repo)
    yield

    for table in tables:
        async with aiopg_engine.acquire() as conn:
            await conn.execute("TRUNCATE TABLE {0} CASCADE".format(table.name))

    aiopg_engine.close()
    await aiopg_engine.wait_closed()
