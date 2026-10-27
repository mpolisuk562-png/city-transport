"""REST-ресурс /drivers (водії)."""

from collections.abc import Sequence

from fastapi import APIRouter

from lab4.dependencies import DriverRepo, VehicleRepo
from lab4.models import Driver, Vehicle
from lab4.routers.common import Limit, Offset
from lab4.schemas import DriverCreate, DriverRead, DriverUpdate, VehicleRead

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("", response_model=list[DriverRead])
def list_drivers(repo: DriverRepo, limit: Limit = 20, offset: Offset = 0) -> Sequence[Driver]:
    return repo.list(limit=limit, offset=offset)


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, repo: DriverRepo) -> Driver:
    return repo.get(driver_id)


@router.post("", response_model=DriverRead, status_code=201)
def create_driver(data: DriverCreate, repo: DriverRepo) -> Driver:
    return repo.create(data)


@router.put("/{driver_id}", response_model=DriverRead)
def update_driver(driver_id: int, data: DriverUpdate, repo: DriverRepo) -> Driver:
    return repo.update(driver_id, data)


@router.delete("/{driver_id}", status_code=204)
def delete_driver(driver_id: int, repo: DriverRepo) -> None:
    repo.delete(driver_id)


@router.get("/{driver_id}/vehicles", response_model=list[VehicleRead])
def list_driver_vehicles(
    driver_id: int,
    drivers: DriverRepo,
    vehicles: VehicleRepo,
    limit: Limit = 20,
    offset: Offset = 0,
) -> Sequence[Vehicle]:
    """Зв'язок Driver 1:N Vehicle."""
    drivers.get(driver_id)
    return vehicles.list(limit=limit, offset=offset, filters={"driver_id": driver_id})
