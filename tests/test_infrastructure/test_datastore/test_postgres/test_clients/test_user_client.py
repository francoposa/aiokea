async def test_generate_where_clause(db, user_pg_client):
    results = await user_pg_client.where(
        inclusion_map={"username": "domtoretto"},
        exclusion_map={"email": ["ejectoseat@fastnfurious.com"]},
    )
    print(results)
    assert False
