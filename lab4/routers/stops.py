"""REST-ресурс /stops (зупинки)."""

from fastapi import APIRouter

from lab4.dependencies import StopRepo
from lab4.models import Stop
from lab4.routers.common import get_or_404
from lab4.schemas import StopIn

router = APIRouter(prefix="/stops", tags=["stops"])


@router.get("")
def list_stops(repo: StopRepo) -> list[Stop]:
    return repo.list_all()


@router.get("/{stop_id}")
def get_stop(stop_id: int, repo: StopRepo) -> Stop:
    return get_or_404(repo, stop_id)


@router.post("", status_code=201)
def create_stop(data: StopIn, repo: StopRepo) -> Stop:
    return repo.create(data)


@router.put("/{stop_id}")
def update_stop(stop_id: int, data: StopIn, repo: StopRepo) -> Stop:
    return repo.update(get_or_404(repo, stop_id), data)


@router.delete("/{stop_id}", status_code=204)
def delete_stop(stop_id: int, repo: StopRepo) -> None:
    repo.delete(get_or_404(repo, stop_id))
