import sqlalchemy as sa

from aiokea.psql import PostgresRepo
from tests.stubs.users.struct import User

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


class PostgresUserRepo(PostgresRepo):
    def __init__(self, engine):
        super().__init__(User, engine, USER)
