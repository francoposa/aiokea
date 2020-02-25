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

    Implementation details are yours to hide!
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
