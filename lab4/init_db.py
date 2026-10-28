"""Скрипт ініціалізації БД: пересоздає таблиці та вставляє тестові дані.

Запуск: uv run python -m lab4.init_db
        uv run python -m lab4.init_db --drivers 50 --vehicles 100 --seed 7

Зупинки вставляються «сирим» SQL через psycopg (п. 6a методички) — параметризованим
запитом, де значення передаються окремо від тексту SQL і драйвер сам їх екранує.
Решта даних вставляється через ORM SQLModel; водії й транспорт генеруються випадково.
"""

import argparse
from random import Random

import psycopg
from sqlmodel import Session, SQLModel, select

from lab4.config import settings
from lab4.db import engine

# Імпорт моделей також реєструє їхні таблиці в SQLModel.metadata.
from lab4.models import Driver, Route, RouteStop, Stop, Vehicle
from lab4.seed_data import (
    ROUTE_STOPS,
    ROUTES,
    STOPS,
    DriverRow,
    VehicleRow,
    generate_drivers,
    generate_vehicles,
)


def recreate_tables() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def insert_stops_raw() -> int:
    """Вставка зупинок сирим SQL. Жодних f-рядків: лише плейсхолдери %s."""
    with psycopg.connect(settings.psycopg_dsn) as conn, conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO stops (name, latitude, longitude) VALUES (%s, %s, %s)",
            STOPS,
        )
        # commit відбувається автоматично при виході з блоку with
    return len(STOPS)


def insert_with_orm(driver_rows: list[DriverRow], vehicle_rows: list[VehicleRow]) -> dict[str, int]:
    with Session(engine) as session:
        drivers = [Driver(full_name=n, phone=p, email=e) for n, p, e in driver_rows]
        routes = {
            (number, kind): Route(number=number, transport_type=kind, name=name)
            for number, kind, name in ROUTES
        }
        session.add_all(drivers)
        session.add_all(routes.values())
        session.flush()  # отримати id без завершення транзакції

        stop_ids = {s.name: s.id for s in session.exec(select(Stop)).all()}

        route_stops = [
            RouteStop(route_id=_id(routes[key]), stop_id=_require(stop_ids[name]), seq=i)
            for key, names in ROUTE_STOPS.items()
            for i, name in enumerate(names, start=1)
        ]
        vehicles = [
            Vehicle(
                plate_number=plate,
                model=model,
                year=year,
                route_id=_id(routes[route_key]),
                driver_id=None if driver_idx is None else _id(drivers[driver_idx]),
            )
            for plate, model, year, route_key, driver_idx in vehicle_rows
        ]
        session.add_all(route_stops)
        session.add_all(vehicles)
        session.commit()

    return {
        "drivers": len(drivers),
        "routes": len(routes),
        "route_stops": len(route_stops),
        "vehicles": len(vehicles),
    }


def _require(value: int | None) -> int:
    if value is None:
        raise RuntimeError("Запис не отримав id після flush()")
    return value


def _id(obj: Driver | Route) -> int:
    return _require(obj.id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Пересоздає таблиці й заповнює БД даними")
    parser.add_argument("--drivers", type=int, default=25, help="скільки водіїв згенерувати")
    parser.add_argument("--vehicles", type=int, default=40, help="скільки машин згенерувати")
    parser.add_argument(
        "--seed", type=int, default=42, help="зерно генератора: той самий seed — ті самі дані"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # Власний екземпляр Random із зерном: дані випадкові, але відтворювані.
    rng = Random(args.seed)
    driver_rows = generate_drivers(rng, args.drivers)
    vehicle_rows = generate_vehicles(rng, args.vehicles, len(driver_rows))

    recreate_tables()
    counts = {"stops": insert_stops_raw(), **insert_with_orm(driver_rows, vehicle_rows)}
    total = sum(counts.values())
    for table, n in counts.items():
        print(f"{table:<12} {n:>4}")
    print(f"{'разом':<12} {total:>4}")


if __name__ == "__main__":
    main()
