"""Скрипт ініціалізації БД: пересоздає таблиці та вставляє дані.

Запуск: uv run python -m lab4.init_db

Зупинки вставляються «сирим» SQL через psycopg (п. 6a методички) — параметризованим
запитом: значення передаються окремо від тексту SQL через плейсхолдери %s.
Решта даних вставляється через ORM SQLModel; водії й транспорт генеруються випадково.
"""

from random import Random

import psycopg
from sqlmodel import Session, SQLModel, select

from lab4.config import settings
from lab4.db import engine

# Імпорт моделей також реєструє їхні таблиці в SQLModel.metadata.
from lab4.models import Driver, Entity, Route, RouteStop, Stop, Vehicle
from lab4.seed_data import ROUTE_STOPS, ROUTES, SEED, STOPS, generate_drivers, generate_vehicles


def recreate_tables() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def insert_stops_raw() -> None:
    """Вставка зупинок сирим SQL. Жодних f-рядків: лише плейсхолдери %s."""
    with psycopg.connect(settings.psycopg_dsn) as conn, conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO stops (name, latitude, longitude) VALUES (%s, %s, %s)",
            STOPS,
        )
        # commit відбувається автоматично при виході з блоку with


def insert_with_orm() -> None:
    rng = Random(SEED)
    with Session(engine) as session:
        drivers = [Driver(full_name=n, phone=p, email=e) for n, p, e in generate_drivers(rng)]
        routes = {
            (number, kind): Route(number=number, transport_type=kind, name=name)
            for number, kind, name in ROUTES
        }
        session.add_all(drivers)
        session.add_all(routes.values())
        session.flush()  # БД видає id, але транзакція ще не завершена

        stop_ids = {stop.name: _id(stop) for stop in session.exec(select(Stop))}
        for key, names in ROUTE_STOPS.items():
            for seq, name in enumerate(names, start=1):
                session.add(RouteStop(route_id=_id(routes[key]), stop_id=stop_ids[name], seq=seq))

        for plate, model, year, route_key, driver in generate_vehicles(rng):
            driver_id = None if driver is None else drivers[driver - 1].id
            vehicle = Vehicle(
                plate_number=plate,
                model=model,
                year=year,
                route_id=_id(routes[route_key]),
                driver_id=driver_id,
            )
            session.add(vehicle)
        session.commit()


def _id(obj: Entity) -> int:
    """id записа, який уже збережено в БД (після flush id точно є)."""
    assert obj.id is not None
    return obj.id


def main() -> None:
    recreate_tables()
    insert_stops_raw()
    insert_with_orm()
    print("Базу створено й заповнено.")


if __name__ == "__main__":
    main()
