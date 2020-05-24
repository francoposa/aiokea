from abc import ABC
from typing import Dict, Mapping, Type

from marshmallow import Schema

from aiokea.abc import Struct


class BaseMarshmallowSchema(Schema):
    class Meta:
        ordered = True
        strict = True

        patchable_fields = []


class BaseMarshmallowAdapter(ABC):
    def __init__(self, schema: BaseMarshmallowSchema, struct_class: Type):
        self.schema = schema
        self.struct_class: Type = struct_class

    def load_to_struct(self, data: Mapping) -> Struct:
        """Override if you need to decouple struct fields from api schema"""
        struct_data: Dict = self.schema.load(data)
        return self.struct_class(**struct_data)

    def dump_from_struct(self, struct: Struct) -> Mapping:
        """Override if you need to decouple struct fields from api schema"""
        return self.schema.dump(struct)
