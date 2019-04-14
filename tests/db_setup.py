from app import usecases


async def setup_db(user_pg_client):

    users = [
        usecases.User(username="domtoretto", email="americanmuscle@fastnfurious.com"),
        usecases.User(username="brian", email="importtuners@fastnfurious.com"),
        usecases.User(username="roman", email="ejectoseat@fastnfurious.com"),
    ]

    for user in users:
        await user_pg_client.insert(user)
