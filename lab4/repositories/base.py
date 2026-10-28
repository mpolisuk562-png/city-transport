"""Абстрактний репозиторій — «стандарт розетки», від якого залежать роутери.

Роутери не знають, де лежать дані. Нове сховище додається новим класом-нащадком,
без змін у роутерах і в цьому класі (принцип Open/Closed).
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from lab4.models import Entity


class Repository[ModelT: Entity](ABC):
    """CRUD над однією сутністю. ModelT — доменний клас із lab4.models."""

    @abstractmethod
    def get(self, item_id: int) -> ModelT | None:
        """Повертає запис або None, якщо його немає."""

    @abstractmethod
    def list_all(self, **filters: object) -> list[ModelT]:
        """Усі записи; filters — рівність полів, напр. list_all(route_id=3)."""

    @abstractmethod
    def create(self, data: BaseModel) -> ModelT:
        """Створює запис із даних схеми."""

    @abstractmethod
    def update(self, obj: ModelT, data: BaseModel) -> ModelT:
        """Замінює поля запису даними схеми."""

    @abstractmethod
    def delete(self, obj: ModelT) -> None:
        """Видаляє запис."""
