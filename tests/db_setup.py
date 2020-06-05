from app.usecases.resources.user import User

stub_users = [
    User(username="domtoretto", email="americanmuscle@fastnfurious.com"),
    User(username="brian", email="importtuners@fastnfurious.com"),
    User(username="roman", email="ejectoseat@fastnfurious.com"),
    User(username="han", email="han@fastnfurious.com", is_enabled=False),
]


async def setup_db(user_pg_client):

    for user in stub_users:
        await user_pg_client.create(user)
