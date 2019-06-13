from app.usecases import User
from tests import db_setup


async def test_where(db, user_pg_client):
    stub_count = len(db_setup.stub_users)
    # No filters
    results = await user_pg_client.select_where()
    assert len(results) == stub_count

    # Filters
    result_include = await user_pg_client.select_where(
        include={"username": ["brian", "roman"]}
    )
    result_exclude = await user_pg_client.select_where(
        exclude={"username": ["brian", "roman"]}
    )
    assert len(result_include) + len(result_exclude) == stub_count


async def test_where_paginated(db, user_pg_client):
    db_count = len(await user_pg_client.select_where())
    retrieved_records = 0
    page = 0
    page_size = 1
    while retrieved_records < db_count:
        results = await user_pg_client.select_where(page=page, page_size=page_size)
        retrieved_records += len(results)
        assert retrieved_records == (page * page_size) + len(results)
        page += 1


async def test_insert(db, user_pg_client):
    old_user_count = len(await user_pg_client.select_where())
    new_user = User(username="test", email="test")
    inserted_user = await user_pg_client.insert(new_user)
    assert inserted_user.id == new_user.id
    new_user_count = len(await user_pg_client.select_where())
    assert new_user_count == old_user_count + 1
