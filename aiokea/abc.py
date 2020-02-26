from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence

import attr

from aiokea.filters import Filter


@attr.s
class Struct(ABC):
    pass


class IService(ABC):
    """
    Defines abstract behavior of Create-Read-Update-Delete
    resource access via direct unique id lookup and filtering methods

    Implement this interface to provide CRUD access to resources where
    the provided methods are appropriate, such as a REST API,
    relational DB, document DB, file system, in-memory map/tree, etc.

    While you could provide an IService interface for many types of
    infrastructure components, it is meant to most closely resemble
    operations and behavior available from a REST API.
    As such, each call to an IService method is assumed to be an atomic
    operation. IService is not intended to provide the ability to batch up
    multiple method calls as a single atomic operation.
    """

    @abstractmethod
    async def get(self, id: Any) -> Optional[Struct]:
        pass

    @abstractmethod
    async def get_where(
        self, filters: Optional[Sequence[Filter]] = None
    ) -> Sequence[Struct]:
        pass

    @abstractmethod
    async def get_first_where(
        self, filters: Optional[Sequence[Filter]] = None
    ) -> Optional[Struct]:
        pass

    @abstractmethod
    async def create(self, struct: Struct) -> Struct:
        pass

    @abstractmethod
    async def partial_update(self, id: Any, **kwargs) -> Struct:
        pass

    @abstractmethod
    async def update(self, struct: Struct) -> Struct:
        pass

    @abstractmethod
    async def delete(self, id: Any) -> Struct:
        pass


class IRepo(IService):
    """
    IRepo extends IService to offer behaviors generally expected from
    database systems, such as the ability to execute multiple operations
    within an atomic transaction, or the ability to perform batch updates
    or deletes based on filter criteria.

    Implementations of IRepo do not necessarily have to be backed by a database,
    as long as the implementation fulfills the expected atomic-transactional behavior
    """
