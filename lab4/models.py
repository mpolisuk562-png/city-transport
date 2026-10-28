from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Entity(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class Route(Entity, table=True):
    __tablename__ = "routes"
    __table_args__ = (UniqueConstraint("number", "transport_type"),)

    number: str = Field(max_length=4)
    transport_type: str = Field(max_length=16)
    name: str = Field(max_length=255)


class Stop(Entity, table=True):
    __tablename__ = "stops"

    name: str = Field(max_length=255)
    latitude: float
    longitude: float


class RouteStop(Entity, table=True):
    __tablename__ = "route_stops"
    __table_args__ = (UniqueConstraint("route_id", "seq"),)

    route_id: int = Field(foreign_key="routes.id", ondelete="CASCADE")
    stop_id: int = Field(foreign_key="stops.id", ondelete="RESTRICT")
    seq: int


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
    route_id: int = Field(foreign_key="routes.id", ondelete="RESTRICT")
    driver_id: int | None = Field(default=None, foreign_key="drivers.id", ondelete="SET NULL")
