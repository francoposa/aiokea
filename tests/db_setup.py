from app import usecases


async def setup_db(user_repo):

    users = [
        usecases.User(username="domtoretto", email="americanmuscle@fastnfurious.com"),
        usecases.User(username="brian", email="importtuners@fastnfurious.com"),
        usecases.User(username="roman", email="ejectoseat@fastnfurious.com"),
    ]

    for user in users:
        await user_repo.insert(user)
