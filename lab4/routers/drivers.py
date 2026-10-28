"""REST-ресурс /drivers (водії)."""

from fastapi import APIRouter

from lab4.dependencies import DriverRepo
from lab4.models import Driver
from lab4.routers.common import get_or_404
from lab4.schemas import DriverIn

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("")
def list_drivers(repo: DriverRepo) -> list[Driver]:
    return repo.list_all()


@router.get("/{driver_id}")
def get_driver(driver_id: int, repo: DriverRepo) -> Driver:
    return get_or_404(repo, driver_id)


@router.post("", status_code=201)
def create_driver(data: DriverIn, repo: DriverRepo) -> Driver:
    return repo.create(data)


@router.put("/{driver_id}")
def update_driver(driver_id: int, data: DriverIn, repo: DriverRepo) -> Driver:
    return repo.update(get_or_404(repo, driver_id), data)


@router.delete("/{driver_id}", status_code=204)
def delete_driver(driver_id: int, repo: DriverRepo) -> None:
    repo.delete(get_or_404(repo, driver_id))
