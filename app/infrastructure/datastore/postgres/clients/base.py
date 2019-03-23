import aiopg.sa
import sqlalchemy as sa


class BasePostgresClient:
    def __init__(self, usecase_class, engine: aiopg.sa.Engine, table: sa.Table):
        self.usecase_class = usecase_class
        self.engine = engine
        self.table = table
