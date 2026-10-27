"""REST-ресурс /stops (зупинки)."""

from collections.abc import Sequence

from fastapi import APIRouter

from lab4.dependencies import StopRepo
from lab4.models import Stop
from lab4.routers.common import Limit, Offset
from lab4.schemas import StopCreate, StopRead, StopUpdate

router = APIRouter(prefix="/stops", tags=["stops"])


@router.get("", response_model=list[StopRead])
def list_stops(repo: StopRepo, limit: Limit = 20, offset: Offset = 0) -> Sequence[Stop]:
    return repo.list(limit=limit, offset=offset)


@router.get("/{stop_id}", response_model=StopRead)
def get_stop(stop_id: int, repo: StopRepo) -> Stop:
    return repo.get(stop_id)


@router.post("", response_model=StopRead, status_code=201)
def create_stop(data: StopCreate, repo: StopRepo) -> Stop:
    return repo.create(data)


@router.put("/{stop_id}", response_model=StopRead)
def update_stop(stop_id: int, data: StopUpdate, repo: StopRepo) -> Stop:
    return repo.update(stop_id, data)


@router.delete("/{stop_id}", status_code=204)
def delete_stop(stop_id: int, repo: StopRepo) -> None:
    repo.delete(stop_id)
