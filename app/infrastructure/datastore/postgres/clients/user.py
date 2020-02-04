from app.infrastructure.datastore.postgres.clients.base_postgres import PostgresClient
from app.infrastructure.datastore.postgres.tables import USER
from app.usecases.resources.user import User


class UserPostgresClient(PostgresClient):
    def __init__(self, engine):
        super().__init__(User, engine, USER)
