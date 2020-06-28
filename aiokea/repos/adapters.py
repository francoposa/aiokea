import datetime
from abc import ABC
from typing import Mapping, MutableMapping, Type


from marshmallow import Schema

from aiokea.abc import Struct


class BaseMarshmallowRepoSchema(Schema):
    class Meta:
        ordered = True
        strict = True

        id_field = "id"
        repo_generated_fields = ["created_at", "updated_at"]


class BaseMarshmallowRepoAdapter(ABC):
    """
    Adapter utilizing Marshmallow Schemas to marshall Struct instances to and from
    statements created with the SQLAlchemy Table API.
    """

    def __init__(self, schema: BaseMarshmallowRepoSchema, struct_class: Type):
        self.schema = schema
        self.struct_class: Type = struct_class

    async def to_struct(self, data: Mapping) -> Struct:
        """
        Load repo query result data into Struct

        Override if you need to decouple struct fields from db schema

        Not actually async, but needs to be marked async for use in
        async iterators and other async repo patterns
        """
        return self.struct_class(**data)

    def from_struct(self, struct: Struct) -> Mapping:
        """
        Dump Struct into Mapping which can be unpacked into the `values` clause
        on the `create` or `update` statements created with the SQLAlchemy Table API

        Override if you need to decouple struct fields from db schema

        You will likely want to keep the call to _from_struct in order to
        take advantage of the generalized marshalling functionality it provides.
        """
        struct_data = vars(struct)
        return self._from_struct(struct_data)

    def _from_struct(self, struct_data: Mapping) -> Mapping:
        struct_data = self._strip_repo_generated_fields(struct_data)
        struct_data = self._dump_datetime_fields(struct_data)
        return struct_data

    def _strip_repo_generated_fields(self, struct_data: Mapping) -> Mapping:
        for db_generated_field in self.schema.Meta.repo_generated_fields:
            if (
                db_generated_field in struct_data
                and struct_data.get(db_generated_field) is None
            ):
                # Inserting value None into a non-nullable Postgres field will result
                # in a `psycopg2.IntegrityError: null value in column violates not-null
                # constraint`. Delete the value from the dict instead
                del struct_data[db_generated_field]
        return struct_data

    def _dump_datetime_fields(self, struct_data: Mapping) -> Mapping:
        for k, v in struct_data.items():
            if isinstance(v, datetime.datetime):
                struct_data[k]: str = v.isoformat()
        return struct_data
