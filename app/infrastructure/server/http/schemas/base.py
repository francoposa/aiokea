# """Base Serializer"""
#
#
# from marshmallow import Schema, post_dump
#
#
# class BaseSchema(Schema):
#     """Base Serializer"""
#
#     class Meta:  # pylint: disable=too-few-public-methods
#         """Meta data for BaseSchema."""
#
#         type_ = None
#
#     @post_dump
#     def process_post_dump(self, data):
#         """Adds record type field post-dump."""
#         data["record_type"] = self.Meta.type_
