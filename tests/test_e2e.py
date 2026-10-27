"""E2E-тести REST API через REST-клієнт TestClient (httpx поверх ASGI-застосунку).

Кожен тест виконується двічі: на InMemoryRepository (завжди) і на PostgreSQL
(якщо база запущена, інакше тест пропускається). Однакова поведінка обох
реалізацій показує, що роутери справді залежать лише від абстракції Repository.
"""

import secrets
from collections.abc import Callable, Iterator
from typing import Any

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from lab4 import dependencies as deps
from lab4.db import check_connection
from lab4.models import Driver, Route, RouteStop, Stop, Vehicle
from lab4.repositories import InMemoryRepository
from lab4.restapi import app
from lab4.schemas import PATTERN_HINTS

REPO_DEPENDENCIES: dict[Callable[..., Any], type[SQLModel]] = {
    deps.get_route_repo: Route,
    deps.get_stop_repo: Stop,
    deps.get_route_stop_repo: RouteStop,
    deps.get_driver_repo: Driver,
    deps.get_vehicle_repo: Vehicle,
}


def _postgres_available() -> bool:
    try:
        check_connection()
    except psycopg.OperationalError:
        return False
    return True


def _memory_override(model: type[SQLModel]) -> Callable[[], InMemoryRepository[Any]]:
    repo = InMemoryRepository(model)  # один екземпляр на тест — стан живе між запитами
    return lambda: repo


@pytest.fixture(params=["memory", "postgres"])
def client(request: pytest.FixtureRequest) -> Iterator[TestClient]:
    if request.param == "memory":
        # Підміна реалізації без жодної зміни в роутерах — суть OCP.
        for dependency, model in REPO_DEPENDENCIES.items():
            app.dependency_overrides[dependency] = _memory_override(model)
    elif not _postgres_available():
        pytest.skip("PostgreSQL не запущено (docker compose up -d)")
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _digits(n: int) -> str:
    """Випадкові цифри, щоб тести на реальній БД не конфліктували з даними."""
    return "".join(str(secrets.randbelow(10)) for _ in range(n))


def _driver_payload() -> dict[str, str]:
    suffix = _digits(7)
    return {
        "full_name": "Тестовий Петро Іванович",
        "phone": f"+38099{suffix}",
        "email": f"test.{suffix}@lvivtrans.ua",
    }


# --- Повний CRUD-цикл однієї сутності (Driver) ---------------------------------------
def test_driver_crud_cycle(client: TestClient) -> None:
    payload = _driver_payload()

    # CREATE
    created = client.post("/drivers", json=payload)
    assert created.status_code == 201, created.text
    driver = created.json()
    driver_id = driver["id"]
    assert driver == {"id": driver_id, **payload}

    # READ (за id і в списку)
    assert client.get(f"/drivers/{driver_id}").json() == driver
    page = client.get("/drivers", params={"limit": 100, "offset": 0})
    assert page.status_code == 200
    assert driver in page.json()

    # UPDATE (лише передане поле)
    updated = client.put(f"/drivers/{driver_id}", json={"full_name": "Оновлений Петро"})
    assert updated.status_code == 200
    assert updated.json() == {**driver, "full_name": "Оновлений Петро"}

    # DELETE
    assert client.delete(f"/drivers/{driver_id}").status_code == 204
    missing = client.get(f"/drivers/{driver_id}")
    assert missing.status_code == 404
    assert str(driver_id) in missing.json()["detail"]
    assert client.delete(f"/drivers/{driver_id}").status_code == 404


def test_duplicate_phone_returns_409(client: TestClient) -> None:
    payload = _driver_payload()
    first = client.post("/drivers", json=payload).json()
    duplicate = {**payload, "email": f"other.{_digits(6)}@lvivtrans.ua"}

    response = client.post("/drivers", json=duplicate)

    assert response.status_code == 409
    assert "Конфлікт" in response.json()["detail"]
    client.delete(f"/drivers/{first['id']}")


def test_put_with_null_for_required_field_returns_422(client: TestClient) -> None:
    driver = client.post("/drivers", json=_driver_payload()).json()

    response = client.put(f"/drivers/{driver['id']}", json={"phone": None})

    assert response.status_code == 422
    client.delete(f"/drivers/{driver['id']}")


# --- Regex-валідація -----------------------------------------------------------------
@pytest.mark.parametrize(
    ("url", "payload", "field"),
    [
        ("/drivers", {"phone": "0671234567"}, "phone"),  # без +380
        ("/drivers", {"phone": "+38067123456"}, "phone"),  # 8 цифр замість 9
        ("/drivers", {"email": "driver.lvivtrans.ua"}, "email"),  # без @
        ("/drivers", {"email": "driver@lviv"}, "email"),  # без доменної зони
        ("/vehicles", {"plate_number": "вс1234ав"}, "plate_number"),  # малі літери
        ("/vehicles", {"plate_number": "ВС123АВ"}, "plate_number"),  # 3 цифри
        ("/vehicles", {"plate_number": "ВС12345АВ"}, "plate_number"),  # 5 цифр
        ("/routes", {"number": "1234"}, "number"),  # 4 цифри
        ("/routes", {"number": "3АБ"}, "number"),  # дві літери
        ("/routes", {"number": "А3"}, "number"),  # літера попереду
    ],
)
def test_regex_validation_returns_422_with_hint(
    client: TestClient, url: str, payload: dict[str, str], field: str
) -> None:
    valid: dict[str, dict[str, Any]] = {
        "/drivers": _driver_payload(),
        "/vehicles": {"plate_number": "ВС0000АА", "model": "Test", "year": 2020, "route_id": 1},
        "/routes": {"number": "99", "transport_type": "bus", "name": "Тест"},
    }

    response = client.post(url, json={**valid[url], **payload})

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Некоректні вхідні дані"
    assert {"field": field, "message": PATTERN_HINTS[field], "input": payload[field]} in body[
        "errors"
    ]


@pytest.mark.parametrize("plate", ["ВС1234АВ", "AA1234BB", "ВІ0001ЄЇ"])
def test_valid_plate_numbers_are_accepted(client: TestClient, plate: str) -> None:
    route = client.post(
        "/routes", json={"number": _digits(3), "transport_type": "bus", "name": "Тест"}
    ).json()
    # Випадкові цифри в номері, щоб не зіткнутися з даними в реальній БД.
    plate = plate[:2] + _digits(4) + plate[6:]

    created = client.post(
        "/vehicles",
        json={"plate_number": plate, "model": "Тест", "year": 2020, "route_id": route["id"]},
    )

    assert created.status_code == 201, created.text
    client.delete(f"/vehicles/{created.json()['id']}")
    client.delete(f"/routes/{route['id']}")


# --- Пагінація та зв'язки ------------------------------------------------------------
def test_pagination_limits(client: TestClient) -> None:
    assert client.get("/stops", params={"limit": 101}).status_code == 422
    assert client.get("/stops", params={"offset": -1}).status_code == 422


def test_route_relations(client: TestClient) -> None:
    route = client.post(
        "/routes", json={"number": _digits(3), "transport_type": "tram", "name": "Тестовий"}
    ).json()
    stops = [
        client.post("/stops", json={"name": name, "latitude": 49.84, "longitude": 24.03}).json()
        for name in ("Тест А", "Тест Б", "Тест В")
    ]
    # Додаємо зупинки у зворотному порядку: API має віддати їх за seq.
    for seq, stop in reversed(list(enumerate(stops, start=1))):
        link = {"route_id": route["id"], "stop_id": stop["id"], "seq": seq}
        assert client.post("/route-stops", json=link).status_code == 201
    vehicle = client.post(
        "/vehicles",
        json={
            "plate_number": f"ВС{_digits(4)}ТТ",
            "model": "Electron T5L64",
            "year": 2022,
            "route_id": route["id"],
        },
    ).json()

    route_stops = client.get(f"/routes/{route['id']}/stops").json()
    assert [s["name"] for s in route_stops] == ["Тест А", "Тест Б", "Тест В"]
    assert [s["seq"] for s in route_stops] == [1, 2, 3]
    assert client.get(f"/routes/{route['id']}/vehicles").json() == [vehicle]
    assert client.get("/routes/999999/stops").status_code == 404

    # Прибирання: спершу машина, потім маршрут (RouteStop видаляться каскадом у БД).
    client.delete(f"/vehicles/{vehicle['id']}")
    client.delete(f"/routes/{route['id']}")
    for stop in stops:
        client.delete(f"/stops/{stop['id']}")
