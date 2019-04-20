from app import usecases

stub_users = [
    usecases.User(username="domtoretto", email="americanmuscle@fastnfurious.com"),
    usecases.User(username="brian", email="importtuners@fastnfurious.com"),
    usecases.User(username="roman", email="ejectoseat@fastnfurious.com"),
]


async def setup_db(user_pg_client):

    for user in stub_users:
        await user_pg_client.insert(user)
