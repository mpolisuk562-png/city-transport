"""REST-ресурс /route-stops (асоціативна таблиця Route N:M Stop)."""

from fastapi import APIRouter

from lab4.dependencies import RouteStopRepo
from lab4.models import RouteStop
from lab4.routers.common import get_or_404
from lab4.schemas import RouteStopIn

router = APIRouter(prefix="/route-stops", tags=["route-stops"])


@router.get("")
def list_route_stops(repo: RouteStopRepo) -> list[RouteStop]:
    return repo.list_all()


@router.get("/{item_id}")
def get_route_stop(item_id: int, repo: RouteStopRepo) -> RouteStop:
    return get_or_404(repo, item_id)


@router.post("", status_code=201)
def create_route_stop(data: RouteStopIn, repo: RouteStopRepo) -> RouteStop:
    return repo.create(data)


@router.put("/{item_id}")
def update_route_stop(item_id: int, data: RouteStopIn, repo: RouteStopRepo) -> RouteStop:
    return repo.update(get_or_404(repo, item_id), data)


@router.delete("/{item_id}", status_code=204)
def delete_route_stop(item_id: int, repo: RouteStopRepo) -> None:
    repo.delete(get_or_404(repo, item_id))
