from typing import Dict, List, Mapping, Type

import marshmallow
from marshmallow import Schema
from aiokea.abc import Entity, IHTTPAdapter, IHTTPSchema
from aiokea.errors import ValidationError


MarshmallowSchema = Schema
# MarshmallowSchema = TypeVar("MarshmallowSchema", Schema)


# class BaseMarshmallowHTTPSchema(Schema, IHTTPSchema, metaclass=SchemaMeta):
#     class Meta:
#         ordered = True
#         strict = True

#         id_field = "id"
#         patchable_fields: List[str] = []


class BaseMarshmallowHTTPAdapter(IHTTPAdapter):
    def __init__(self, schema: MarshmallowSchema, entity_class: Type):
        self._schema: MarshmallowSchema = schema
        self.entity_class: Type = entity_class

    @property
    def schema(self) -> MarshmallowSchema:
        return self._schema

    def to_entity(self, data: Mapping) -> Entity:
        try:
            entity_data: Dict = self.schema.load(data)
        except marshmallow.exceptions.ValidationError as e:
            error_list = [{k: v} for k, v in e.messages.items()]
            raise ValidationError(errors=error_list)
        return self.entity_class(**entity_data)

    def from_entity(self, entity: Entity) -> Mapping:
        """Override if you need to decouple entity fields from api schema"""
        return self.schema.dump(entity)
