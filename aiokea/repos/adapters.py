import datetime
from abc import ABC
from typing import Mapping, MutableMapping, Type


from marshmallow import Schema

from aiokea.abc import Entity


class BaseMarshmallowRepoSchema(Schema):
    class Meta:
        ordered = True
        strict = True

        id_field = "id"
        repo_generated_fields = ["created_at", "updated_at"]


class BaseMarshmallowSQLAlchemyRepoAdapter(ABC):
    """
    Adapter utilizing Marshmallow Schemas to marshall Entity instances
    to and from queries created with the SQLAlchemy Table API.
    """

    def __init__(self, schema: BaseMarshmallowRepoSchema, entity_class: Type):
        self.schema = schema
        self.entity_class: Type = entity_class

    async def to_entity(self, data: Mapping) -> Entity:
        """
        Load repo query result data into Entity

        Override if you need to decouple entity fields from db schema

        Not actually async, but needs to be marked async for use in
        async iterators and other async repo patterns
        """
        return self.entity_class(**data)

    def from_entity(self, entity: Entity) -> Mapping:
        """
        Dump Entity into Mapping which can be unpacked into the `values` clause
        on the `create` or `update` statements created with the SQLAlchemy Table API

        Override if you need to decouple entity fields from db schema

        You will likely want to keep the call to _from_entity in order to
        take advantage of the generalized marshalling functionality it provides.
        """
        entity_data = vars(entity)
        return self._from_entity(entity_data)

    def _from_entity(self, entity_data: Mapping) -> Mapping:
        entity_data = self._strip_repo_generated_fields(entity_data)
        entity_data = self._dump_datetime_fields(entity_data)
        return entity_data

    def _strip_repo_generated_fields(self, entity_data: Mapping) -> Mapping:
        for db_generated_field in self.schema.Meta.repo_generated_fields:
            if (
                db_generated_field in entity_data
                and entity_data.get(db_generated_field) is None
            ):
                # Inserting value None into a non-nullable field will result in error
                # Even it is nullable, we want to let the database generate the fields
                # Delete these values from the dict instead
                del entity_data[db_generated_field]
        return entity_data

    def _dump_datetime_fields(self, entity_data: Mapping) -> Mapping:
        for k, v in entity_data.items():
            if isinstance(v, datetime.datetime):
                entity_data[k]: str = v.isoformat()
        return entity_data
