"""Репозиторій у пам'яті — демонстрація принципу Open/Closed.

Цей клас лише наслідує Repository: роутери та PostgresRepository
для нього не змінювались. Вмикається змінною оточення STORAGE=memory.
"""

from pydantic import BaseModel

from lab4.models import Entity
from lab4.repositories.base import Repository


class InMemoryRepository[ModelT: Entity](Repository[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model
        self.items: dict[int, ModelT] = {}  # id -> запис
        self.next_id = 1

    def get(self, item_id: int) -> ModelT | None:
        return self.items.get(item_id)

    def list_all(self, **filters: object) -> list[ModelT]:
        return [
            obj
            for obj in self.items.values()
            if all(getattr(obj, field) == value for field, value in filters.items())
        ]

    def create(self, data: BaseModel) -> ModelT:
        obj = self.model(**data.model_dump())
        obj.id = self.next_id
        self.items[obj.id] = obj
        self.next_id += 1
        return obj

    def update(self, obj: ModelT, data: BaseModel) -> ModelT:
        for field, value in data.model_dump().items():
            setattr(obj, field, value)
        return obj

    def delete(self, obj: ModelT) -> None:
        if obj.id is not None:
            del self.items[obj.id]
