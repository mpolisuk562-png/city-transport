from enum import StrEnum

from pydantic import BaseModel, Field

PLATE_NUMBER_RE = r"^[A-ZА-ЯІЇЄ]{2}\d{4}[A-ZА-ЯІЇЄ]{2}$"
ROUTE_NUMBER_RE = r"^\d{1,3}[А-ЯA-Z]?$"
PHONE_RE = r"^\+380\d{9}$"
EMAIL_RE = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"


class TransportType(StrEnum):
    BUS = "bus"
    TRAM = "tram"
    TROLLEYBUS = "trolleybus"


class RouteIn(BaseModel):
    number: str = Field(pattern=ROUTE_NUMBER_RE, examples=["3А"])
    transport_type: TransportType
    name: str = Field(min_length=1, max_length=255)


class StopIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class RouteStopIn(BaseModel):
    route_id: int
    stop_id: int
    seq: int = Field(ge=1)


class DriverIn(BaseModel):
    full_name: str = Field(min_length=3, max_length=150)
    phone: str = Field(pattern=PHONE_RE, examples=["+380671234567"])
    email: str = Field(pattern=EMAIL_RE, examples=["driver@lvivtrans.ua"])


class VehicleIn(BaseModel):
    plate_number: str = Field(pattern=PLATE_NUMBER_RE, examples=["ВС1234АВ"])
    model: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1950)
    route_id: int
    driver_id: int | None = None
