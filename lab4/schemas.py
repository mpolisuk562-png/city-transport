"""Pydantic-схеми API: що клієнт надсилає (Create/Update) і що отримує (Read).

Доменні моделі (lab4.models) описують таблиці, а схеми — контракт REST API.
Завдяки розділенню клієнт не може, наприклад, передати власний id.
"""

from datetime import date
from typing import Annotated, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from lab4.models import TransportType

# --- Регулярні вирази для валідації -------------------------------------------------
# Держномер: 2 літери, 4 цифри, 2 літери (кирилиця або латиниця), напр. ВС1234АВ.
# Діапазон А-Я не містить українських І, Ї, Є — тому вони дописані окремо.
PLATE_NUMBER_RE = r"^[A-ZА-ЯІЇЄ]{2}\d{4}[A-ZА-ЯІЇЄ]{2}$"
# Номер маршруту: 1–3 цифри і, можливо, літера: 6, 47, 3А.
ROUTE_NUMBER_RE = r"^\d{1,3}[А-ЯA-Z]?$"
# Телефон у міжнародному форматі України: +380 і ще 9 цифр.
PHONE_RE = r"^\+380\d{9}$"
# Email: локальна частина, @, домен із зоною щонайменше з 2 літер.
EMAIL_RE = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

# Зрозумілі повідомлення для 422, коли значення не відповідає regex.
PATTERN_HINTS: dict[str, str] = {
    "plate_number": "Держномер має формат АА1234ВВ: 2 великі літери, 4 цифри, 2 великі літери",
    "number": "Номер маршруту: від 1 до 3 цифр і, за потреби, одна велика літера (напр. 47, 3А)",
    "phone": "Телефон має формат +380XXXXXXXXX (код країни і 9 цифр)",
    "email": "Некоректний email, очікується формат name@example.com",
}

PlateNumber = Annotated[str, Field(pattern=PLATE_NUMBER_RE, examples=["ВС1234АВ"])]
RouteNumber = Annotated[str, Field(pattern=ROUTE_NUMBER_RE, examples=["3А"])]
Phone = Annotated[str, Field(pattern=PHONE_RE, examples=["+380671234567"])]
Email = Annotated[str, Field(pattern=EMAIL_RE, max_length=255, examples=["driver@lvivtrans.ua"])]
Name = Annotated[str, Field(min_length=1, max_length=255)]
Year = Annotated[int, Field(ge=1950, le=date.today().year + 1)]
Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]
Id = Annotated[int, Field(ge=1)]


class InputSchema(BaseModel):
    # Невідоме поле (наприклад, одруківка "phon") — це помилка клієнта, а не тиша.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UpdateSchema(InputSchema):
    """PUT оновлює лише передані поля.

    Явний null дозволено тільки для полів, що в БД можуть бути NULL (nullable),
    інакше {"name": null} дійшов би до БД і впав на NOT NULL.
    """

    nullable: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def _forbid_null(self) -> Self:
        bad = sorted(
            f for f in self.model_fields_set if getattr(self, f) is None and f not in self.nullable
        )
        if bad:
            raise ValueError(f"поля не можуть бути null: {', '.join(bad)}")
        return self


class ReadSchema(BaseModel):
    # Дозволяє будувати схему з ORM-об'єкта (атрибути, а не dict).
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Route ---------------------------------------------------------------------------
class RouteCreate(InputSchema):
    number: RouteNumber
    transport_type: TransportType
    name: Name


class RouteUpdate(UpdateSchema):
    number: RouteNumber | None = None
    transport_type: TransportType | None = None
    name: Name | None = None


class RouteRead(ReadSchema):
    number: str
    transport_type: TransportType
    name: str


# --- Stop ----------------------------------------------------------------------------
class StopCreate(InputSchema):
    name: Name
    latitude: Latitude
    longitude: Longitude


class StopUpdate(UpdateSchema):
    name: Name | None = None
    latitude: Latitude | None = None
    longitude: Longitude | None = None


class StopRead(ReadSchema):
    name: str
    latitude: float
    longitude: float


class RouteStopDetail(StopRead):
    """Зупинка в складі маршруту: дані зупинки + її порядковий номер."""

    seq: int


# --- RouteStop -----------------------------------------------------------------------
class RouteStopCreate(InputSchema):
    route_id: Id
    stop_id: Id
    seq: Id


class RouteStopUpdate(UpdateSchema):
    route_id: Id | None = None
    stop_id: Id | None = None
    seq: Id | None = None


class RouteStopRead(ReadSchema):
    route_id: int
    stop_id: int
    seq: int


# --- Driver --------------------------------------------------------------------------
class DriverCreate(InputSchema):
    full_name: Annotated[str, Field(min_length=3, max_length=150)]
    phone: Phone
    email: Email


class DriverUpdate(UpdateSchema):
    full_name: Annotated[str, Field(min_length=3, max_length=150)] | None = None
    phone: Phone | None = None
    email: Email | None = None


class DriverRead(ReadSchema):
    full_name: str
    phone: str
    email: str


# --- Vehicle -------------------------------------------------------------------------
class VehicleCreate(InputSchema):
    plate_number: PlateNumber
    model: Annotated[str, Field(min_length=1, max_length=100)]
    year: Year
    route_id: Id
    driver_id: Id | None = None


class VehicleUpdate(UpdateSchema):
    # null для driver_id означає «відкріпити водія».
    nullable: ClassVar[frozenset[str]] = frozenset({"driver_id"})

    plate_number: PlateNumber | None = None
    model: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    year: Year | None = None
    route_id: Id | None = None
    driver_id: Id | None = None


class VehicleRead(ReadSchema):
    plate_number: str
    model: str
    year: int
    route_id: int
    driver_id: int | None
