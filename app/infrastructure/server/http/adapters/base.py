# import attr
# from marshmallow import Schema, ValidationError
#
#
# class BaseJSONUsecaseAdapter:
#     """Class to marshal JSON into attrs classes using marshmallow"""
#
#     def __init__(self, usecase_cls, post_schema: Schema):
#         self.UsecaseClass = usecase_cls  # attrs class
#         self.post_schema: Schema = post_schema
#
#     def to_usecase(self, mapping):
#         """Return a UsecaseClass() from an HTTP Request."""
#
#         try:
#             usecase_dict = self.post_schema.load(mapping).data
#         except ValidationError as e:
#             errors = self._handle_invalid_parameters(e.messages)
#             raise self.InvalidMapping(errors)
#
#         return self.UsecaseClass(**usecase_dict)
