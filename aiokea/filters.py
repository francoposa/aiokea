from typing import Any


class Filter:
    def __init__(self, field: Any, operator: str, value: Any):
        self.field = field
        self.operator = operator
        self.value = value


class FilterOperators:
    EQ = "eq"  # equal to
    NE = "ne"  # not equal to
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal to
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal to
    IN = "in"  # inclusion operator


class PaginationParams:
    PAGE = "page"
    PAGE_SIZE = "page_size"
