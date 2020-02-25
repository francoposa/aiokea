import datetime
from typing import Any, Dict, Iterable, List, Type, Optional

import attr

import aiopg.sa
import psycopg2
import sqlalchemy as sa
from aiopg.sa.result import ResultProxy, RowProxy
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql import and_, Select, Update
from sqlalchemy.sql.schema import Column


from aiokea.abc import IService, Struct
from aiokea.errors import DuplicateResourceError
from aiokea.filters import Filter, FilterOperators


class PostgresService(IService):
    def __init__(
        self,
        struct_class: Type,
        engine: aiopg.sa.Engine,
        table: sa.Table,
        id_field: str = None,
        db_generated_fields: Iterable[str] = None,
    ):
        self.struct_class = struct_class
        self.engine = engine
        self.table = table
        self.id_field = id_field or "id"
        self.db_generated_fields = db_generated_fields or ["created_at", "updated_at"]

    async def get(self, id: Any) -> Struct:
        return await self.get_first_where(
            filters=[Filter(self.id_field, FilterOperators.EQ, id)]
        )

    async def get_where(self, filters: Optional[List[Filter]] = None) -> List[Struct]:
        where_clause: BinaryExpression = self._where_clause_from_filters(
            filters
        ) if filters else None
        select: Select = self.table.select(whereclause=where_clause)
        async with self.engine.acquire() as conn:
            results: ResultProxy = await conn.execute(select)
            return [await self._load_to_struct(result) async for result in results]

    async def get_first_where(self, filters: List[Filter] = None) -> Optional[Struct]:
        where_clause: BinaryExpression = self._where_clause_from_filters(
            filters
        ) if filters else None
        select: Select = self.table.select(whereclause=where_clause).limit(1)
        async with self.engine.acquire() as conn:
            results: ResultProxy = await conn.execute(select)
            if results:
                return await self._load_to_struct(await results.first())
            return None

    async def create(self, struct: Struct) -> Struct:
        serialized_struct: Dict = self._dump_from_struct(struct)
        insert: Insert = (
            self.table.insert()
            .values(**serialized_struct)
            .returning(*[column for column in self.table.columns])
        )
        async with self.engine.acquire() as conn:
            try:
                results: ResultProxy = await conn.execute(insert)
                result = await results.fetchone()
            except psycopg2.errors.UniqueViolation as e:
                raise DuplicateResourceError(e)
        return await self._load_to_struct(result)

    async def update(self, struct: Struct) -> Struct:
        serialized_struct: Dict = self._dump_from_struct(struct)
        id = serialized_struct.get(self.id_field)
        id_filter = Filter(self.id_field, FilterOperators.EQ, id)
        where_clause: BinaryExpression = self._where_clause_from_filters([id_filter])
        update: Update = (
            self.table.update(whereclause=where_clause)
            .values(**serialized_struct)
            .returning(*[column for column in self.table.columns])
        )
        async with self.engine.acquire() as conn:
            try:
                results: ResultProxy = await conn.execute(update)
                result = await results.fetchone()
            except psycopg2.errors.UniqueViolation as e:
                # TODO possibly raise a more descriptive error
                raise DuplicateResourceError(e)
        return await self._load_to_struct(result)

    async def partial_update(self, id: Any, **kwargs) -> Struct:
        id_filter = Filter(self.id_field, FilterOperators.EQ, id)
        current_struct: Struct = await self.get_first_where(filters=[id_filter])

        # Use attr.evolve to ensure validation & field generation/calculation
        # is re-run, and to handle case of frozen classes
        unsaved_updated_struct: Struct = attr.evolve(current_struct, **kwargs)
        serialized_unsaved_updated_struct: Dict = self._dump_from_struct(
            unsaved_updated_struct
        )

        where_clause: BinaryExpression = self._where_clause_from_filters([id_filter])
        update: Update = (
            self.table.update(whereclause=where_clause)
            .values(**serialized_unsaved_updated_struct)
            .returning(*[column for column in self.table.columns])
        )
        async with self.engine.acquire() as conn:
            try:
                results: ResultProxy = await conn.execute(update)
                result = await results.fetchone()
            except psycopg2.errors.UniqueViolation as e:
                # TODO possibly raise a more descriptive error
                raise DuplicateResourceError(e)
        return await self._load_to_struct(result)

    async def update_where(
        self, filters: Optional[List[Filter]] = None, **kwargs
    ) -> List[Struct]:
        where_clause: BinaryExpression = self._where_clause_from_filters(
            filters
        ) if filters else None
        update: Update = self.table.update(whereclause=where_clause).values(
            **kwargs
        ).returning(*[column for column in self.table.columns])
        async with self.engine.acquire() as conn:
            results: ResultProxy = await conn.execute(update)
            return [await self._load_to_struct(result) async for result in results]

    def _where_clause_from_filters(self, filters: List[Filter]):
        eq_ands = []
        ne_ands = []
        for filter in filters:
            table_col: Column = getattr(self.table.c, filter.field)
            if filter.operator == FilterOperators.EQ:
                eq_ands.append(table_col == filter.value)
            elif filter.operator == FilterOperators.NE:
                ne_ands.append(table_col != filter.value)
        return and_(*eq_ands, *ne_ands)

    async def _load_to_struct(self, record: RowProxy) -> Struct:
        # returns attrs object if successful
        row_dict = dict(record)
        return self.struct_class(**row_dict)

    def _dump_from_struct(self, struct: Struct) -> Dict:
        struct_data: Dict = attr.asdict(struct)
        for db_generated_field in self.db_generated_fields:
            if struct_data.get(db_generated_field) is None:
                # inserting a non-nullable field with value None will result in a
                # `psycopg2.IntegrityError: null value in column violates not-null constraint`
                # we delete the value from the dict instead
                del struct_data[db_generated_field]
        for k, v in struct_data.items():
            if isinstance(v, datetime.datetime):
                struct_data[k]: str = v.isoformat()
        return struct_data
