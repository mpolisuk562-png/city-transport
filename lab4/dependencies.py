"""Корінь композиції: єдине місце, де абстрактний Repository зв'язується з реалізацією.

Роутери імпортують лише аліаси на кшталт RouteRepo = Repository[Route]; яку саме
реалізацію вони отримають, визначає реєстр STORAGES і змінна оточення STORAGE.
Нове сховище = новий клас Repository + один рядок у STORAGES; роутери не змінюються.
"""

from collections.abc import Callable
from typing import Annotated, Any, Protocol

from fastapi import Depends
from sqlmodel import Session, SQLModel

from lab4.config import settings
from lab4.db import get_session
from lab4.models import Driver, Route, RouteStop, Stop, Vehicle
from lab4.repositories import InMemoryRepository, PostgresRepository, Repository


class StorageFactory(Protocol):
    def __call__[M: SQLModel](self, model: type[M], session: Session) -> Repository[M]: ...


def postgres_storage[M: SQLModel](model: type[M], session: Session) -> Repository[M]:
    return PostgresRepository(session, model)


# Дані в пам'яті мають жити між запитами, тому один репозиторій на модель.
_memory_repos: dict[type[SQLModel], InMemoryRepository[Any]] = {}


def memory_storage[M: SQLModel](model: type[M], session: Session) -> Repository[M]:
    if model not in _memory_repos:
        _memory_repos[model] = InMemoryRepository(model)
    return _memory_repos[model]


STORAGES: dict[str, StorageFactory] = {
    "postgres": postgres_storage,
    "memory": memory_storage,
}


def repository_for[M: SQLModel](model: type[M]) -> Callable[[Session], Repository[M]]:
    """Створює FastAPI-залежність, що повертає репозиторій для моделі."""
    storage = STORAGES[settings.storage]

    # Сесія створюється ліниво: для memory-сховища з'єднання з БД не відкривається.
    def dependency(session: Annotated[Session, Depends(get_session)]) -> Repository[M]:
        return storage(model, session)

    return dependency


get_route_repo = repository_for(Route)
get_stop_repo = repository_for(Stop)
get_route_stop_repo = repository_for(RouteStop)
get_driver_repo = repository_for(Driver)
get_vehicle_repo = repository_for(Vehicle)

RouteRepo = Annotated[Repository[Route], Depends(get_route_repo)]
StopRepo = Annotated[Repository[Stop], Depends(get_stop_repo)]
RouteStopRepo = Annotated[Repository[RouteStop], Depends(get_route_stop_repo)]
DriverRepo = Annotated[Repository[Driver], Depends(get_driver_repo)]
VehicleRepo = Annotated[Repository[Vehicle], Depends(get_vehicle_repo)]
