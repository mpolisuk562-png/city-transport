"""REST-ресурс /vehicles (транспортні засоби)."""

from fastapi import APIRouter

from lab4.dependencies import VehicleRepo
from lab4.models import Vehicle
from lab4.routers.common import get_or_404
from lab4.schemas import VehicleIn

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("")
def list_vehicles(repo: VehicleRepo) -> list[Vehicle]:
    return repo.list_all()


@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: int, repo: VehicleRepo) -> Vehicle:
    return get_or_404(repo, vehicle_id)


@router.post("", status_code=201)
def create_vehicle(data: VehicleIn, repo: VehicleRepo) -> Vehicle:
    return repo.create(data)


@router.put("/{vehicle_id}")
def update_vehicle(vehicle_id: int, data: VehicleIn, repo: VehicleRepo) -> Vehicle:
    return repo.update(get_or_404(repo, vehicle_id), data)


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, repo: VehicleRepo) -> None:
    repo.delete(get_or_404(repo, vehicle_id))
