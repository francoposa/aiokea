import os

import pytest
from aiopg.sa import create_engine, Engine

from app.infrastructure.datastore import postgres
import tests.db_setup as db_setup


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
    pg = postgres.UserPostgresClient(engine)
    yield pg
    pg.engine.close()
    await pg.engine.wait_closed()


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
