import datetime
from typing import Iterable, Dict

import attr
import aiopg.sa
import sqlalchemy as sa
from aiopg.sa.result import ResultProxy
from sqlalchemy.dialects.postgresql import Insert


class BasePostgresClient:
    def __init__(
        self,
        usecase_class,
        engine: aiopg.sa.Engine,
        table: sa.Table,
        db_generated_fields: Iterable[str] = None,
    ):
        self.usecase_class = usecase_class
        self.engine = engine
        self.table = table
        self.db_generated_fields = db_generated_fields or ["created_at", "updated_at"]

    async def insert(self, usecase):
        serialized_usecase: Dict = self._serialize_for_db(usecase)
        async with self.engine.acquire() as conn:
            statement: Insert = (
                self.table.insert()
                .values(**serialized_usecase)
                .returning(*[column for column in self.table.columns])
            )
            result: ResultProxy = await conn.execute(statement)
            return await result.fetchone()

    def _serialize_for_db(self, usecase) -> Dict:
        usecase_dict: Dict = attr.asdict(usecase)
        for db_generated_field in self.db_generated_fields:
            if usecase_dict.get(db_generated_field) is None:
                del usecase_dict[db_generated_field]
        for k, v in usecase_dict.items():
            if isinstance(v, datetime.datetime):
                usecase_dict[k]: str = v.isoformat()
        return usecase_dict
