from aiokea.psql import PostgresRepo

from app.infrastructure.datastore.postgres.tables import USER
from app.usecases.resources.user import User


class PostgresUserRepo(PostgresRepo):
    def __init__(self, engine):
        super().__init__(User, engine, USER)
