"""Доменні класи предметної області «Міський транспорт» (таблиці SQLModel).

Зв'язки:
    Route 1:N Vehicle   (машина працює на одному маршруті)
    Driver 1:N Vehicle  (за водієм може бути закріплено кілька машин)
    Route N:M Stop      (через асоціативну таблицю RouteStop з порядковим номером)
"""

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Entity(SQLModel):
    """Спільний предок усіх таблиць: у кожної є числовий id, який видає БД."""

    id: int | None = Field(default=None, primary_key=True)


class Route(Entity, table=True):
    __tablename__ = "routes"
    # Номер «1» може бути і в трамвая, і в автобуса, тому унікальна саме пара.
    __table_args__ = (UniqueConstraint("number", "transport_type"),)

    number: str = Field(max_length=4)
    transport_type: str = Field(max_length=16)  # bus / tram / trolleybus
    name: str = Field(max_length=255)


class Stop(Entity, table=True):
    __tablename__ = "stops"

    name: str = Field(max_length=255)
    latitude: float
    longitude: float


class RouteStop(Entity, table=True):
    """Асоціативна таблиця Route N:M Stop: один рядок — одна зупинка на маршруті."""

    __tablename__ = "route_stops"
    __table_args__ = (UniqueConstraint("route_id", "seq"),)

    # Видалили маршрут — його список зупинок видаляється разом із ним.
    route_id: int = Field(foreign_key="routes.id", ondelete="CASCADE")
    # Зупинку, через яку проходить маршрут, видалити не можна.
    stop_id: int = Field(foreign_key="stops.id", ondelete="RESTRICT")
    seq: int  # порядковий номер зупинки на маршруті


class Driver(Entity, table=True):
    __tablename__ = "drivers"

    full_name: str = Field(max_length=150)
    phone: str = Field(max_length=13, unique=True)
    email: str = Field(max_length=255, unique=True)


class Vehicle(Entity, table=True):
    __tablename__ = "vehicles"

    plate_number: str = Field(max_length=8, unique=True)
    model: str = Field(max_length=100)
    year: int
    # Маршрут, на якому ще є машини, видалити не можна.
    route_id: int = Field(foreign_key="routes.id", ondelete="RESTRICT")
    # Видалили водія — машина лишається, але без водія.
    driver_id: int | None = Field(default=None, foreign_key="drivers.id", ondelete="SET NULL")
