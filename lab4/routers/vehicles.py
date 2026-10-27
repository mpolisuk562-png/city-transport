"""REST-ресурс /vehicles (транспортні засоби)."""

from collections.abc import Sequence

from fastapi import APIRouter

from lab4.dependencies import VehicleRepo
from lab4.models import Vehicle
from lab4.routers.common import Limit, Offset
from lab4.schemas import VehicleCreate, VehicleRead, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleRead])
def list_vehicles(repo: VehicleRepo, limit: Limit = 20, offset: Offset = 0) -> Sequence[Vehicle]:
    return repo.list(limit=limit, offset=offset)


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: int, repo: VehicleRepo) -> Vehicle:
    return repo.get(vehicle_id)


@router.post("", response_model=VehicleRead, status_code=201)
def create_vehicle(data: VehicleCreate, repo: VehicleRepo) -> Vehicle:
    return repo.create(data)


@router.put("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(vehicle_id: int, data: VehicleUpdate, repo: VehicleRepo) -> Vehicle:
    return repo.update(vehicle_id, data)


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, repo: VehicleRepo) -> None:
    repo.delete(vehicle_id)
