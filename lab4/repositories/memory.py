"""Репозиторій у пам'яті — демонстрація розширення без зміни існуючого коду (OCP).

Цей клас лише наслідує Repository: роутери, моделі та PostgresRepository
для нього не змінювались. Використовується в тестах і при STORAGE=memory.
"""

from collections.abc import Mapping, Sequence
from itertools import count

from pydantic import BaseModel
from sqlalchemy import Table, UniqueConstraint
from sqlalchemy.orm import class_mapper
from sqlmodel import SQLModel

from lab4.errors import ConflictError, NotFoundError
from lab4.repositories.base import Repository


class InMemoryRepository[ModelT: SQLModel](Repository[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model
        self._items: dict[int, ModelT] = {}
        self._ids = count(1)
        mapper = class_mapper(model)
        self._pk: str = mapper.primary_key[0].name
        table = mapper.local_table
        if not isinstance(table, Table):
            raise TypeError(f"{model.__name__} не є таблицею SQLModel")
        # Ті самі обмеження унікальності, що й у БД, читаємо з метаданих моделі.
        self._unique: list[tuple[str, ...]] = [(c.name,) for c in table.columns if c.unique]
        self._unique += [
            tuple(c.name for c in con.columns)
            for con in table.constraints
            if isinstance(con, UniqueConstraint)
        ]

    def get(self, item_id: int) -> ModelT:
        try:
            return self._items[item_id]
        except KeyError:
            raise NotFoundError(self.model.__name__, item_id) from None

    def list(
        self,
        *,
        limit: int,
        offset: int,
        filters: Mapping[str, object] | None = None,
        order_by: str | None = None,
    ) -> Sequence[ModelT]:
        items = [
            obj
            for obj in self._items.values()
            if all(getattr(obj, k) == v for k, v in (filters or {}).items())
        ]
        items.sort(key=lambda obj: getattr(obj, order_by or self._pk))
        return items[offset : offset + limit]

    def create(self, data: BaseModel) -> ModelT:
        obj = self.model(**data.model_dump())
        self._check_unique(obj, exclude_id=None)
        item_id = next(self._ids)
        setattr(obj, self._pk, item_id)
        self._items[item_id] = obj
        return obj

    def update(self, item_id: int, data: BaseModel) -> ModelT:
        obj = self.get(item_id)
        changes = data.model_dump(exclude_unset=True)
        candidate = obj.model_copy(update=changes)
        self._check_unique(candidate, exclude_id=item_id)
        for field, value in changes.items():
            setattr(obj, field, value)
        return obj

    def delete(self, item_id: int) -> None:
        self.get(item_id)
        del self._items[item_id]

    def _check_unique(self, obj: ModelT, exclude_id: int | None) -> None:
        for fields in self._unique:
            key = tuple(getattr(obj, f) for f in fields)
            for other_id, other in self._items.items():
                if other_id != exclude_id and tuple(getattr(other, f) for f in fields) == key:
                    pairs = ", ".join(f"{f}={v}" for f, v in zip(fields, key, strict=True))
                    raise ConflictError(f"Запис з ({pairs}) уже існує.")
