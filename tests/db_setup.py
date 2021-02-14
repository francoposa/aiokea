from tests.stubs.user.entity import User

stub_users = [
    User(username="domtoretto", email="americanmuscle@fastnfurious.com"),
    User(username="brian", email="importtuners@fastnfurious.com"),
    User(username="roman", email="ejectoseat@fastnfurious.com"),
    User(username="han", email="han@fastnfurious.com", is_enabled=False),
]


async def setup_db(aiopg_user_repo):

    for user in stub_users:
        await aiopg_user_repo.create(user)
