from typing import Mapping, Type

import attr
from marshmallow import Schema, post_dump


class BaseSchema(Schema):
    pass


class BaseHTTPUsecaseAdapter:
    def __init__(self, schema: BaseSchema, usecase_class: Type):
        self.schema = schema
        self.UsecaseClass: Type = usecase_class

    def mapping_to_usecase(self, mapping: Mapping):
        usecase_dict = self.schema.load(mapping)
        return self.UsecaseClass(**usecase_dict)

    def usecase_to_mapping(self, usecase):
        return self.schema.dump(usecase)
