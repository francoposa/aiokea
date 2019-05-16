import datetime
from collections.abc import Iterable
from typing import Dict, Iterable, Mapping

import attr

import aiopg.sa
from aiopg.sa.result import ResultProxy, RowProxy
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql import select, and_, not_
from sqlalchemy.sql.schema import Column

DEFAULT_PAGE_SIZE = 100


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
            results: ResultProxy = await conn.execute(statement)
            return await results.fetchone()

    async def select_where(
        self,
        inclusion_map: Mapping = None,
        exclusion_map: Mapping = None,
        page=0,
        page_size=None,
    ):
        where_clause = self._generate_where_clause(inclusion_map, exclusion_map)
        page_size = page_size if page_size else DEFAULT_PAGE_SIZE
        async with self.engine.acquire() as conn:
            statement: Select = self.table.select().where(where_clause)
            paginated_statement = self._paginate_query(statement, page, page_size)
            results: ResultProxy = await conn.execute(paginated_statement)
            return [await self._deserialize_from_db(result) async for result in results]

    async def update_where(
        self,
        values_map: Mapping,
        inclusion_map: Mapping = None,
        exclusion_map: Mapping = None,
    ):
        where_clause = self._generate_where_clause(inclusion_map, exclusion_map)
        async with self.engine.acquire() as conn:
            statement = self.table.update.where(where_clause)

    def _generate_where_clause(
        self, inclusion_map: Mapping = None, exclusion_map: Mapping = None
    ):
        """Turn inclusion/exclusion maps into SQLAlchemy `where` clause"""
        inclusion_ands = []
        exclusion_ands = []
        if inclusion_map:
            for field, includes in inclusion_map.items():
                table_col: Column = getattr(self.table.c, field)
                if _isiterable(includes):
                    # Use SQL [column] IN [(values)]
                    inclusion_ands.append(table_col.in_(includes))
                else:
                    # Use SQL [column] = [value]
                    inclusion_ands.append(table_col == includes)
        if exclusion_map:
            for field, excludes in exclusion_map.items():
                table_col: Column = getattr(self.table.c, field)
                if _isiterable(excludes):
                    # Use SQL [column] NOT IN [(values)]
                    exclusion_ands.append(not_(table_col.in_(excludes)))
                else:
                    # Use SQL [column] != [value]
                    exclusion_ands.append(table_col != excludes)
        return and_(*inclusion_ands, *exclusion_ands)

    def _generate_values_clause(self, values_map: Mapping):
        pass

    def _paginate_query(self, where_clause, page=0, page_size=None):
        if page_size:
            where_clause = where_clause.limit(page_size)
        if page:
            where_clause = where_clause.offset(page * page_size)
        return where_clause

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
