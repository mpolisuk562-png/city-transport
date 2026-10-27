"""Доменні класи предметної області «Міський транспорт» (таблиці SQLModel).

Зв'язки:
    Route 1:N Vehicle   (транспортний засіб працює на одному маршруті)
    Driver 1:N Vehicle  (за водієм закріплено кілька машин; у машини — один водій)
    Route N:M Stop      (через асоціативну таблицю RouteStop з порядковим номером)
"""

from enum import StrEnum

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

# Зв'язки ORM лише для читання: правила видалення (CASCADE / RESTRICT / SET NULL)
# виконує сама БД. Інакше SQLAlchemy перед DELETE маршруту спробує обнулити
# vehicles.route_id і замість зрозумілого порушення FK ми отримаємо NOT NULL.
VIEW_ONLY = {"viewonly": True}


class TransportType(StrEnum):
    BUS = "bus"
    TRAM = "tram"
    TROLLEYBUS = "trolleybus"


class RouteStop(SQLModel, table=True):
    """Асоціативна таблиця Route N:M Stop.

    Сурогатний id замість складеного ключа дозволяє працювати з нею тим самим
    узагальненим репозиторієм і REST-шляхом /route-stops/{id}, що й з іншими сутностями.
    Унікальність пари (маршрут, зупинка) і (маршрут, порядок) гарантує сама БД.
    """

    __tablename__ = "route_stops"
    __table_args__ = (
        UniqueConstraint("route_id", "stop_id", name="uq_route_stop"),
        UniqueConstraint("route_id", "seq", name="uq_route_seq"),
    )

    id: int | None = Field(default=None, primary_key=True)
    # Видалили маршрут — його список зупинок більше не потрібен.
    route_id: int = Field(foreign_key="routes.id", ondelete="CASCADE", index=True)
    # Зупинку, через яку їде хоч один маршрут, видалити не можна (409).
    stop_id: int = Field(foreign_key="stops.id", ondelete="RESTRICT", index=True)
    seq: int = Field(ge=1, description="Порядковий номер зупинки на маршруті")


class Driver(SQLModel, table=True):
    __tablename__ = "drivers"

    id: int | None = Field(default=None, primary_key=True)
    full_name: str = Field(max_length=150)
    phone: str = Field(max_length=13, unique=True)
    email: str = Field(max_length=255, unique=True)

    vehicles: list["Vehicle"] = Relationship(
        back_populates="driver", sa_relationship_kwargs=VIEW_ONLY
    )


class Route(SQLModel, table=True):
    __tablename__ = "routes"
    # Номер «1» може бути і в трамвая, і в автобуса, тому унікальна саме пара.
    __table_args__ = (UniqueConstraint("number", "transport_type", name="uq_route_number_type"),)

    id: int | None = Field(default=None, primary_key=True)
    number: str = Field(max_length=4)
    transport_type: TransportType
    name: str = Field(max_length=255)

    vehicles: list["Vehicle"] = Relationship(
        back_populates="route", sa_relationship_kwargs=VIEW_ONLY
    )
    stops: list["Stop"] = Relationship(
        back_populates="routes", link_model=RouteStop, sa_relationship_kwargs=VIEW_ONLY
    )


class Stop(SQLModel, table=True):
    __tablename__ = "stops"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    routes: list[Route] = Relationship(
        back_populates="stops", link_model=RouteStop, sa_relationship_kwargs=VIEW_ONLY
    )


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicles"

    id: int | None = Field(default=None, primary_key=True)
    plate_number: str = Field(max_length=8, unique=True)
    model: str = Field(max_length=100)
    year: int
    # Маршрут, на якому ще є машини, видалити не можна (409).
    route_id: int = Field(foreign_key="routes.id", ondelete="RESTRICT", index=True)
    # Звільнили водія — машина лишається, просто без закріпленого водія.
    driver_id: int | None = Field(
        default=None, foreign_key="drivers.id", ondelete="SET NULL", index=True
    )

    route: Route | None = Relationship(back_populates="vehicles", sa_relationship_kwargs=VIEW_ONLY)
    driver: Driver | None = Relationship(
        back_populates="vehicles", sa_relationship_kwargs=VIEW_ONLY
    )
