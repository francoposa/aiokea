from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence

import attr

from aiokea.filters import Filter


class Struct(ABC):
    pass


class IRepo(ABC):
    """
    Abstract Base Class for implementations of the Repository Pattern

    Defines abstract behavior of Create-Read-Update-Delete
    resource access via direct unique id lookup and filtering methods

    Implement this interface to provide CRUD access to resources where
    the provided methods are appropriate, such as a REST API,
    relational/document DB, file system, in-memory map/tree, etc.

    Each call to an IRepo method is assumed to be an atomic operation.
    IRepo is not intended to provide the ability to batch up
    multiple method calls as a single atomic operation.

    IRepo methods return usecase-layer objects we call "structs". Structs
    are business-logic objects which should be completely divorced from and
    unaware of any infrastructure-layer implementation details.
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
    async def update(self, struct: Struct) -> Struct:
        pass

    @abstractmethod
    async def delete(self, id: Any) -> Struct:
        pass


class ITransactionalRepo(IRepo):
    """
    ITransactionalRepo extends IRepo to offer behaviors generally expected from
    transactional database systems, such as the ability to execute multiple operations
    within an atomic transaction, or the ability to perform batch updates
    or deletes based on filter criteria.

    Implementations of ITransactionalRepo do not necessarily have to be backed by a database,
    as long as the implementation fulfills the expected atomic-transactional behavior
    """
