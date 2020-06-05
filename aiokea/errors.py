class DuplicateResourceError(Exception):
    error_msg = "duplicate_resource"


class ResourceNotFoundError(Exception):
    error_msg = "resource_not_found"
