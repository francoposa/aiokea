from typing import Any


EQ = "eq"  # equal to
NE = "ne"  # not equal to
GT = "gt"  # greater than
GTE = "gte"  # greater than or equal to
LT = "lt"  # less than
LTE = "lte"  # less than or equal to
IN = "in"  # inclusion operator


class FilterOperators:
    EQ = EQ  # equal to
    NE = NE  # not equal to
    GT = GT  # greater than
    GTE = GTE  # greater than or equal to
    LT = LT  # less than
    LTE = LTE  # less than or equal to
    IN = IN  # inclusion operator

    values = {EQ, NE, GT, GTE, LT, LTE, IN}


class Filter:
    def __init__(self, field: Any, operator: str, value: Any):

        if operator not in FilterOperators.values:
            raise ValueError(
                f"Invalid operator {operator}. Must be one of {FilterOperators.values}"
            )

        self.field = field
        self.operator = operator
        self.value = value


class PaginationParams:
    PAGE = "page"
    PAGE_SIZE = "page_size"

    values = {PAGE, PAGE_SIZE}
