"""REST-ресурс /route-stops (асоціативна таблиця Route N:M Stop)."""

from collections.abc import Sequence

from fastapi import APIRouter

from lab4.dependencies import RouteStopRepo
from lab4.models import RouteStop
from lab4.routers.common import Limit, Offset
from lab4.schemas import RouteStopCreate, RouteStopRead, RouteStopUpdate

router = APIRouter(prefix="/route-stops", tags=["route-stops"])


@router.get("", response_model=list[RouteStopRead])
def list_route_stops(
    repo: RouteStopRepo, limit: Limit = 20, offset: Offset = 0
) -> Sequence[RouteStop]:
    return repo.list(limit=limit, offset=offset)


@router.get("/{item_id}", response_model=RouteStopRead)
def get_route_stop(item_id: int, repo: RouteStopRepo) -> RouteStop:
    return repo.get(item_id)


@router.post("", response_model=RouteStopRead, status_code=201)
def create_route_stop(data: RouteStopCreate, repo: RouteStopRepo) -> RouteStop:
    return repo.create(data)


@router.put("/{item_id}", response_model=RouteStopRead)
def update_route_stop(item_id: int, data: RouteStopUpdate, repo: RouteStopRepo) -> RouteStop:
    return repo.update(item_id, data)


@router.delete("/{item_id}", status_code=204)
def delete_route_stop(item_id: int, repo: RouteStopRepo) -> None:
    repo.delete(item_id)
