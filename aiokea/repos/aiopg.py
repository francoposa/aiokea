from typing import (
    Any,
    Iterable,
    Optional,
    Mapping,
)

import aiopg.sa
import psycopg2
import sqlalchemy as sa
from aiopg.sa.result import ResultProxy
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql import and_, Select, Update, Delete
from sqlalchemy.sql.schema import Column


from aiokea.abc import IRepo, Struct
from aiokea.errors import DuplicateResourceError, ResourceNotFoundError
from aiokea.filters import Filter, FilterOperators
from aiokea.repos.adapters import BaseMarshmallowAIOPGSQLAlchemyRepoAdapter


class AIOPGSQLAlchemyTableRepo(IRepo):
    def __init__(
        self,
        adapter: BaseMarshmallowAIOPGSQLAlchemyRepoAdapter,
        engine: aiopg.sa.Engine,
        table: sa.Table,
    ):
        self.adapter = adapter
        self.engine = engine
        self.table = table

    async def get(self, id: Any) -> Struct:
        where_clause: BinaryExpression = self._where_clause_from_id(id)
        select: Select = self.table.select(whereclause=where_clause).limit(1)
        async with self.engine.acquire() as conn:
            results: ResultProxy = await conn.execute(select)
            if results.rowcount:
                return await self.adapter.to_struct(await results.first())
            raise ResourceNotFoundError(
                f"No {self.adapter.struct_class.__name__} found with {self.adapter.schema.Meta.id_field} {id}"
            )

    async def get_where(
        self, filters: Optional[Iterable[Filter]] = None
    ) -> Iterable[Struct]:
        where_clause: BinaryExpression = self._where_clause_from_filters(
            filters
        ) if filters else None
        select: Select = self.table.select(whereclause=where_clause)
        async with self.engine.acquire() as conn:
            results: ResultProxy = await conn.execute(select)
            return [await self.adapter.to_struct(result) async for result in results]

    async def get_first_where(
        self, filters: Optional[Iterable[Filter]] = None
    ) -> Optional[Struct]:
        where_clause: BinaryExpression = self._where_clause_from_filters(
            filters
        ) if filters else None
        select: Select = self.table.select(whereclause=where_clause).limit(1)
        async with self.engine.acquire() as conn:
            results: ResultProxy = await conn.execute(select)
            if results.rowcount:
                return await self.adapter.to_struct(await results.first())
            return None

    async def create(self, struct: Struct) -> Struct:
        serialized_struct: Mapping = self.adapter.from_struct(struct)
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
        return await self.adapter.to_struct(result)

    async def update(self, struct: Struct) -> Struct:
        id = getattr(struct, self.adapter.schema.Meta.id_field)
        # Call get to make sure the resource exists; will throw error if not
        # TODO ^ this is lazy, let's do it in one database call
        _ = await self.get(id=id)

        serialized_struct: Mapping = self.adapter.from_struct(struct)
        where_clause: BinaryExpression = self._where_clause_from_id(id)
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
        return await self.adapter.to_struct(result)

    async def delete(self, id: Any) -> Struct:
        # Call get to make sure the resource exists; will throw error if not
        # TODO ^ this is lazy, let's do it in one database call
        _ = await self.get(id=id)

        where_clause: BinaryExpression = self._where_clause_from_id(id)
        delete: Delete = (
            self.table.delete(whereclause=where_clause).returning(
                *[column for column in self.table.columns]
            )
        )
        async with self.engine.acquire() as conn:
            try:
                results: ResultProxy = await conn.execute(delete)
                result = await results.fetchone()
            except psycopg2.errors.UniqueViolation as e:
                # TODO possibly raise a more descriptive error
                raise DuplicateResourceError(e)
        return await self.adapter.to_struct(result)

    def _where_clause_from_id(self, id: Any) -> BinaryExpression:
        id_filter = Filter(self.adapter.schema.Meta.id_field, FilterOperators.EQ, id)
        return self._where_clause_from_filters([id_filter])

    def _where_clause_from_filters(self, filters: Iterable[Filter]) -> BinaryExpression:
        eq_ands = []
        ne_ands = []
        for filter in filters:
            table_col: Column = getattr(self.table.c, filter.field)
            if filter.operator == FilterOperators.EQ:
                eq_ands.append(table_col == filter.value)
            elif filter.operator == FilterOperators.NE:
                ne_ands.append(table_col != filter.value)
        return and_(*eq_ands, *ne_ands)
