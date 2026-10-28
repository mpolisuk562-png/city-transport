"""Тут вирішується, яке сховище отримають роутери.

Роутери просять лише абстрактний Repository (через Depends) і не знають,
PostgreSQL під ним чи пам'ять. Сховище обирається змінною оточення STORAGE.
"""

from typing import Annotated, Any

from fastapi import Depends
from sqlmodel import Session

from lab4.config import settings
from lab4.db import get_session
from lab4.models import Driver, Entity, Route, RouteStop, Stop, Vehicle
from lab4.repositories import InMemoryRepository, PostgresRepository, Repository

SessionDep = Annotated[Session, Depends(get_session)]

# Дані в пам'яті мають жити між запитами, тому один репозиторій на модель.
_memory_repos: dict[type[Entity], InMemoryRepository[Any]] = {}


def make_repository[M: Entity](model: type[M], session: Session) -> Repository[M]:
    if settings.storage == "memory":
        if model not in _memory_repos:
            _memory_repos[model] = InMemoryRepository(model)
        return _memory_repos[model]
    return PostgresRepository(session, model)


def get_route_repo(session: SessionDep) -> Repository[Route]:
    return make_repository(Route, session)


def get_stop_repo(session: SessionDep) -> Repository[Stop]:
    return make_repository(Stop, session)


def get_route_stop_repo(session: SessionDep) -> Repository[RouteStop]:
    return make_repository(RouteStop, session)


def get_driver_repo(session: SessionDep) -> Repository[Driver]:
    return make_repository(Driver, session)


def get_vehicle_repo(session: SessionDep) -> Repository[Vehicle]:
    return make_repository(Vehicle, session)


# Короткі імена для параметрів роутерів: repo: VehicleRepo.
RouteRepo = Annotated[Repository[Route], Depends(get_route_repo)]
StopRepo = Annotated[Repository[Stop], Depends(get_stop_repo)]
RouteStopRepo = Annotated[Repository[RouteStop], Depends(get_route_stop_repo)]
DriverRepo = Annotated[Repository[Driver], Depends(get_driver_repo)]
VehicleRepo = Annotated[Repository[Vehicle], Depends(get_vehicle_repo)]
