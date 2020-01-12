from typing import Dict, Mapping, Type

from marshmallow import Schema, post_dump


class BaseSchema(Schema):
    """Base Serializer"""

    class Meta:
        """Meta data for BaseSchema."""

        ordered = True
        strict = True
        record_type = None

        patchable_fields = []

    @post_dump
    def tag_record_type(self, data, **kwargs):
        """Adds record type metadata post-dump."""
        data["record_type"] = self.Meta.record_type
        return data


class BaseHTTPAdapter:
    def __init__(self, schema: BaseSchema, entity_class: Type):
        self.schema = schema
        self.entity_class: Type = entity_class

    def mapping_to_entity(self, mapping: Mapping):
        entity_data: Dict = self.schema.load(mapping)
        return self.entity_class(**entity_data)

    def entity_to_mapping(self, entity) -> Mapping:
        return self.schema.dump(entity)
