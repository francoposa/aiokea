import sqlalchemy as sa

from aiokea.repos.aiopg import AIOPGRepo
from tests.stubs.user.repo_adapter import UserRepoAdapter
from tests.stubs.user.entity import User, stub_users

METADATA = sa.MetaData()

USER = sa.Table(
    "users",
    METADATA,
    sa.Column("id", sa.String, primary_key=True),
    sa.Column("username", sa.String, unique=True, nullable=False),
    sa.Column("email", sa.String, unique=True, nullable=False),
    sa.Column("is_enabled", sa.Boolean, nullable=False, server_default="true"),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)


class AIOPGUserRepo(AIOPGRepo):
    def __init__(self, engine):
        super().__init__(UserRepoAdapter(), engine, USER)


async def setup_user_repo(user_repo: AIOPGUserRepo):
    for user in stub_users:
        await user_repo.create(user)
