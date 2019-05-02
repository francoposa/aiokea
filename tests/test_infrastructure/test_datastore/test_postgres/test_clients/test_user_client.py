from tests import db_setup


async def test_where(db, user_pg_client):
    stub_count = len(db_setup.stub_users)
    # No filters
    results = await user_pg_client.select_where()
    assert len(results) == stub_count

    # Filters
    result_include = await user_pg_client.select_where(
        inclusion_map={"username": ["brian", "roman"]}
    )
    result_exclude = await user_pg_client.select_where(
        exclusion_map={"username": ["brian", "roman"]}
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
