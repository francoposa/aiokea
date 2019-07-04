from enum import Enum

EQ = "eq"  # equal to
NE = "ne"  # not equal to
GT = "gt"  # greater than
GTE = "gte"  # greater than or equal to
LT = "lt"  # less than
LTE = "lte"  # less than or equal to
IN = "in"  # inclusion operator


class FilterOperators(Enum):
    EQ = EQ  # equal to
    NE = NE  # not equal to
    GT = GT  # greater than
    GTE = GTE  # greater than or equal to
    LT = LT  # less than
    LTE = LTE  # less than or equal to
    IN = IN  # inclusion operator

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)
