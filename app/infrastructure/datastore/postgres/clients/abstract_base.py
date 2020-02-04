from abc import ABC, abstractmethod
from typing import List, Optional, Mapping

import attr

from app.infrastructure.common.filters.filters import Filter


@attr.s
class Struct(ABC):
    """
    Abstract class for type hinting attrs classes
    """


class IDBClient(ABC):
    """"""

    @abstractmethod
    async def select_first_where(self, filters: List[Filter] = None) -> Optional[Struct]:
        pass

    @abstractmethod
    async def select_where(
        self,
        filters: Optional[List[Filter]] = None,
        page: Optional[int] = 0,
        page_size: Optional[int] = None,
    ) -> List[Struct]:
        pass

    @abstractmethod
    async def insert(self, struct: Struct) -> Struct:
        pass

    @abstractmethod
    async def update(self, struct: Struct) -> Struct:
        pass

    @abstractmethod
    async def update_where(
        self, set_values: Mapping, filters: Optional[List[Filter]] = None
    ) -> List[Struct]:
        pass

    class DuplicateError(Exception):
        api_error = "duplicate_resource"
