"""Абстрактний узагальнений репозиторій — контракт, від якого залежать роутери.

Роутери не знають, де лежать дані (PostgreSQL, пам'ять, щось інше): нове сховище
додається новим класом-нащадком, без змін у роутерах і в цьому класі (OCP).
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from pydantic import BaseModel
from sqlmodel import SQLModel


class Repository[ModelT: SQLModel](ABC):
    """CRUD над однією сутністю. ModelT — доменний клас із lab4.models."""

    @abstractmethod
    def get(self, item_id: int) -> ModelT:
        """Повертає запис або кидає NotFoundError."""

    @abstractmethod
    def list(
        self,
        *,
        limit: int,
        offset: int,
        filters: Mapping[str, object] | None = None,
        order_by: str | None = None,
    ) -> Sequence[ModelT]:
        """Сторінка записів; filters — рівність полів (наприклад, {"route_id": 3})."""

    @abstractmethod
    def create(self, data: BaseModel) -> ModelT:
        """Створює запис зі схеми; при конфлікті кидає ConflictError."""

    @abstractmethod
    def update(self, item_id: int, data: BaseModel) -> ModelT:
        """Оновлює лише передані поля; NotFoundError або ConflictError."""

    @abstractmethod
    def delete(self, item_id: int) -> None:
        """Видаляє запис; NotFoundError або ConflictError (на запис посилаються)."""
