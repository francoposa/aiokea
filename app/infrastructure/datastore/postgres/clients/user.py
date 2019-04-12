from app.usecases import User
from app.infrastructure.datastore.postgres.clients.base import BasePostgresClient
from app.infrastructure.datastore.postgres.tables import USER


class UserPostgresClient(BasePostgresClient):
    def __init__(self, engine):
        super().__init__(User, engine, USER)
