from abc import ABC, abstractmethod

from pydantic import BaseModel

from lab4.models import Entity


class Repository[ModelT: Entity](ABC):
    @abstractmethod
    def get(self, item_id: int) -> ModelT | None: ...

    @abstractmethod
    def list_all(self, **filters: object) -> list[ModelT]: ...

    @abstractmethod
    def create(self, data: BaseModel) -> ModelT: ...

    @abstractmethod
    def update(self, obj: ModelT, data: BaseModel) -> ModelT: ...

    @abstractmethod
    def delete(self, obj: ModelT) -> None: ...
