from app.infrastructure.datastore.postgres.clients.base import BasePostgresClient
from app.infrastructure.datastore.postgres.tables import USER
from app.usecases.resources.user import User


class UserPostgresClient(BasePostgresClient):
    def __init__(self, engine):
        super().__init__(User, engine, USER)
