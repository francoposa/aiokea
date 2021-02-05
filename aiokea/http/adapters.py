from typing import Dict, Mapping, Type

import marshmallow
from marshmallow import Schema

from aiokea.abc import Struct, IHTTPAdapter
from aiokea.errors import ValidationError


class BaseMarshmallowHTTPSchema(Schema):
    class Meta:
        ordered = True
        strict = True

        id_field = "id"
        patchable_fields = []


class BaseMarshmallowHTTPAdapter(IHTTPAdapter):
    def __init__(self, schema: BaseMarshmallowHTTPSchema, struct_class: Type):
        self._schema = schema
        self.struct_class: Type = struct_class

    @property
    def schema(self) -> BaseMarshmallowHTTPSchema:
        return self._schema

    def to_struct(self, data: Mapping) -> Struct:
        try:
            struct_data: Dict = self.schema.load(data)
        except marshmallow.exceptions.ValidationError as e:
            error_list = [{k: v} for k, v in e.messages.items()]
            raise ValidationError(errors=error_list)
        return self.struct_class(**struct_data)

    def from_struct(self, struct: Struct) -> Mapping:
        """Override if you need to decouple struct fields from api schema"""
        return self.schema.dump(struct)

