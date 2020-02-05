from abc import ABC, abstractmethod


class IRepo(ABC):
    """Defines abstract behavior of a Create-Read-Update-Delete datastore
    that supports access via direct lookup and filtering methods

    Implement this interface to provide CRUD access to datastores where
    the provided methods are appropriate, such as a relational DB,
    document DB, file system, in-memory map/tree, etc.
    """
    pass