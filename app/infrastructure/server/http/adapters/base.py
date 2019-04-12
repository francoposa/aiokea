from typing import Mapping

import attr
from marshmallow import Schema, ValidationError


class BaseJSONUsecaseAdapter:
    """Class to marshal JSON into attrs classes using marshmallow"""

    def __init__(self, usecase_cls, post_schema: Schema):
        self.UsecaseClass = usecase_cls  # attrs class
        self.post_schema: Schema = post_schema

    def to_usecase(self, mapping):
        """Return a UsecaseClass() from an HTTP Request."""

        try:
            usecase_data: Mapping = self.post_schema.load(mapping).data
            return self.UsecaseClass(**usecase_data)
        except ValidationError as e:
            # TODO see what this error looks like, get useful info out, and re-raise as as a different error
            pass
