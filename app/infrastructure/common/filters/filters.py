from enum import Enum
from typing import Any


class PaginationParams(Enum):
    LIMIT = "limit"
    OFFSET = "offset"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class Filter:
    def __init__(self, field: str, operator: str, value: Any):
        self.field = field
        self.operator = operator
        self.value = value
