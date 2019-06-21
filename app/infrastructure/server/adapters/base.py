from typing import Mapping, Type

from marshmallow import Schema, post_dump


class BaseSchema(Schema):
    """Base Serializer"""

    class Meta:
        """Meta data for BaseSchema."""

        type_ = None

    @post_dump
    def tag_record_type(self, data):
        """Adds record type field post-dump."""
        data["record_type"] = self.Meta.type_


class BaseHTTPUsecaseAdapter:
    def __init__(self, schema: BaseSchema, usecase_class: Type):
        self.schema = schema
        self.UsecaseClass = usecase_class

    def mapping_to_usecase(self, mapping: Mapping):
        usecase_dict = self.schema.load(mapping)
        return self.UsecaseClass(**usecase_dict)
