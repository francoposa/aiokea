from enum import Enum
from typing import Any


class FilterOperators(Enum):
    EQ = "eq"  # equal to
    NE = "ne"  # not equal to
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal to
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal to
    IN = "in"  # inclusion operator

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


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
