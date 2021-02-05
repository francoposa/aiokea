from abc import ABC, abstractmethod
from typing import Any, Optional, Iterable, List, Mapping

from aiokea.filters import Filter


class Struct(ABC):
    pass


class IService(ABC):
    """
    Abstract Base Class for implementations of the Service Pattern

    The IService interface defines abstract behavior of Create-Read-Update-Delete
    resource access via direct unique id lookup and filtering methods

    IService implementation code ONLY contains business logic!
    IService implementations are a usecase-layer construct.
    IService implementations wrap around IRepo implementations and should call the public
    methods of an IRepo implementation in order to persist any changes to application state.
    Services may *not* perform the Repo's role of interacting with an infrastructure layer.

    In contrast, IRepo implementation code does not contain any business logic.
    IRepo implementations provide an interface consumable by the usecase layer, but Repo code
    lives in the infrastructure layer. Repo implementation code's purpose to marshall your
    nice usecase-layer objects into and out of whatever infrastructure persistence layer
    the Repo is wrapped around, while providing an convenient interface to the usecase
    layer that hides all of those hairy details.

    Any implementation of the IRepo interface also implements the IService interface.
    This is intentional.
    If you simply need to Create-Read-Update-Delete usecase objects with zero business
    logic applied, you can just directly use an IRepo, while still satisfying the outward
    behavior expected from an IService implementation.

    Each call to an IService method is assumed to be an atomic operation.
    IService is not intended to provide the ability to batch up
    multiple method calls as a single atomic operation.
    """

    @abstractmethod
    async def get(self, id: Any) -> Optional[Struct]:
        pass

    @abstractmethod
    async def get_where(
        self, filters: Optional[Iterable[Filter]] = None
    ) -> List[Struct]:
        pass

    @abstractmethod
    async def get_first_where(
        self, filters: Optional[Iterable[Filter]] = None
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


class IRepo(IService):
    """
    Abstract Base Class for implementations of the Repository Pattern

    The IRepo interface defines abstract behavior of Create-Read-Update-Delete
    resource access via direct unique id lookup and filtering methods

    Implement this interface to provide CRUD access to resources where
    the provided methods are appropriate, such as a REST API,
    relational/document DB, file system, in-memory map/tree, etc.

    IRepo implementation code does NOT contain business logic!
    IRepo implementations are an infrastructure-layer construct.
    IRepo implementation code's purpose is to marshall your nice usecase-layer objects
    in & out of whatever infrastructure layer the Repo is wrapped around: Database,
    external API, file system etc., while providing an convenient interface to the usecase
    layer that hides all of those hairy details.

    The IRepo interface, in the form of the public methods of an IRepo implementation,
    may be called in the usecase/business logic layer. Therefore, the public methods of a
    Repo implementation must not expose details about the infrastructure/persistence layer.

    This differs from a Service - IService implementation code ONLY contains business logic.
    IService implementations wrap around IRepo implementations and should call the public
    methods of an IRepo implementation in order to persist any changes to application state.

    Any implementation of the IService interface also implements the IRepo interface (for now).
    This is NOT intended to be taken advantage of and should NOT be relied upon.
    Services may *not* perform the Repo's role of interacting with an infrastructure layer.
    Therefore it does not make sense to use an IService where an IRepo is expected.

    Each call to an IRepo method is assumed to be an atomic operation.
    IRepo is not intended to provide the ability to batch up
    multiple method calls as a single atomic operation.
    """

    @abstractmethod
    async def get(self, id: Any) -> Optional[Struct]:
        pass

    @abstractmethod
    async def get_where(
        self, filters: Optional[Iterable[Filter]] = None
    ) -> List[Struct]:
        pass

    @abstractmethod
    async def get_first_where(
        self, filters: Optional[Iterable[Filter]] = None
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


class IHTTPSchema(ABC):

    @property
    @abstractmethod
    def fields(self) -> List:
        pass

class IHTTPAdapter(ABC):

    @property
    @abstractmethod
    def schema(self) -> IHTTPSchema:
        pass

    @abstractmethod
    def to_struct(self, data: Mapping) -> Struct:
        """

        :param data:
        :return:
        :raises ValidationError:
        """
        pass

    @abstractmethod
    def from_struct(self, struct: Struct) -> Mapping:
        """

        :param struct:
        :return:
        :raises V
        """
        pass
