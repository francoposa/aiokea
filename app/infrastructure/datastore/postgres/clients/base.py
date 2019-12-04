import datetime
from typing import Dict, Iterable, Mapping, List

import attr

import aiopg.sa
from aiopg.sa.result import ResultProxy, RowProxy
import psycopg2
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql import and_, not_
from sqlalchemy.sql.schema import Column

from app.infrastructure.common.filters.filters import Filter
from app.infrastructure.common.filters.operators import FilterOperators

DEFAULT_PAGE_SIZE = 25


class BasePostgresClient:
    class DuplicateError(Exception):
        api_error = "duplicate resource"

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
            try:
                results: ResultProxy = await conn.execute(statement)
            except psycopg2.errors.UniqueViolation as e:
                raise self.DuplicateError()
            result = await results.fetchone()
            return await self._deserialize_from_db(result)

    async def select_first_where(self, filters: List[Filter] = None):
        results = await self.select_where(filters=filters, page_size=1)
        if results:
            return results[0]
        return None

    async def select_where(self, filters: List[Filter] = None, page=0, page_size=None):
        where_clause = self._generate_where_clause_from_filters(filters) if filters else None
        select: Select = self.table.select(whereclause=where_clause)
        page_size = page_size if page_size else DEFAULT_PAGE_SIZE
        paginated_select = self._paginate_query(select, page, page_size)
        async with self.engine.acquire() as conn:
            results: ResultProxy = await conn.execute(paginated_select)
            return [await self._deserialize_from_db(result) async for result in results]

    async def update_where(
        self, set_values: Mapping, include: Mapping = None, exclude: Mapping = None
    ):
        where_clause = self._generate_where_clause(include, exclude)
        async with self.engine.acquire() as conn:
            statement = self.table.update.where(where_clause)

    def _generate_where_clause(self, include: Mapping = None, exclude: Mapping = None):
        """Turn inclusion/exclusion maps into SQLAlchemy `where` clause"""
        inclusion_ands = []
        exclusion_ands = []
        if include:
            for field, includes in include.items():
                table_col: Column = getattr(self.table.c, field)
                if _isiterable(includes):
                    # Use SQL [column] IN [(values)]
                    inclusion_ands.append(table_col.in_(includes))
                else:
                    # Use SQL [column] = [value]
                    inclusion_ands.append(table_col == includes)
        if exclude:
            for field, excludes in exclude.items():
                table_col: Column = getattr(self.table.c, field)
                if _isiterable(excludes):
                    # Use SQL [column] NOT IN [(values)]
                    exclusion_ands.append(not_(table_col.in_(excludes)))
                else:
                    # Use SQL [column] != [value]
                    exclusion_ands.append(table_col != excludes)
        return and_(*inclusion_ands, *exclusion_ands)

    def _generate_where_clause_from_filters(self, filters: List[Filter]):
        eq_ands = []
        ne_ands = []
        for filter in filters:
            table_col: Column = getattr(self.table.c, filter.field)
            if filter.operator == FilterOperators.EQ.value:
                eq_ands.append(table_col == filter.value)
            elif filter.operator == FilterOperators.NE.value:
                ne_ands.append(table_col != filter.value)
        return and_(*eq_ands, *ne_ands)

    def _generate_values_clause(self, set_values: Mapping):
        pass

    def _paginate_query(self, statement, page=0, page_size=None):
        if page_size:
            statement = statement.limit(page_size)
        if page:
            statement = statement.offset(page * page_size)
        return statement

    async def _deserialize_from_db(self, row: RowProxy):
        # returns attrs object if successful
        row_dict = dict(row)
        return self.usecase_class(**row_dict)

    def _serialize_for_db(self, usecase) -> Dict:
        # at this point we're assuming attrs objects for usecases
        usecase_dict: Dict = attr.asdict(usecase)
        for db_generated_field in self.db_generated_fields:
            if usecase_dict.get(db_generated_field) is None:
                # inserting a non-nullable field with value None will result in a
                # `psycopg2.IntegrityError: null value in column violates not-null constraint`
                # we delete the value from the dict instead
                del usecase_dict[db_generated_field]
        for k, v in usecase_dict.items():
            if isinstance(v, datetime.datetime):
                usecase_dict[k]: str = v.isoformat()
        return usecase_dict


def _isiterable(var) -> bool:
    return isinstance(var, Iterable) and not isinstance(var, str)
