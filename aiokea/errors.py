from typing import Any, List


class DuplicateResourceError(Exception):
    msg = "duplicate_resource"


class ResourceNotFoundError(Exception):
    msg = "resource_not_found"


class ValidationError(Exception):
    msg = "validation_error"

    def __init__(self, errors: List[Any]):
        self.errors = errors
