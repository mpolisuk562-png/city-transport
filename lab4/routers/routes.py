"""REST-ресурс /routes (маршрути) і зв'язки маршруту з транспортом і зупинками."""

from collections.abc import Sequence

from fastapi import APIRouter

from lab4.dependencies import RouteRepo, RouteStopRepo, StopRepo, VehicleRepo
from lab4.models import Route, Vehicle
from lab4.routers.common import Limit, Offset
from lab4.schemas import (
    RouteCreate,
    RouteRead,
    RouteStopDetail,
    RouteUpdate,
    StopRead,
    VehicleRead,
)

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=list[RouteRead])
def list_routes(repo: RouteRepo, limit: Limit = 20, offset: Offset = 0) -> Sequence[Route]:
    return repo.list(limit=limit, offset=offset)


@router.get("/{route_id}", response_model=RouteRead)
def get_route(route_id: int, repo: RouteRepo) -> Route:
    return repo.get(route_id)


@router.post("", response_model=RouteRead, status_code=201)
def create_route(data: RouteCreate, repo: RouteRepo) -> Route:
    return repo.create(data)


@router.put("/{route_id}", response_model=RouteRead)
def update_route(route_id: int, data: RouteUpdate, repo: RouteRepo) -> Route:
    return repo.update(route_id, data)


@router.delete("/{route_id}", status_code=204)
def delete_route(route_id: int, repo: RouteRepo) -> None:
    repo.delete(route_id)


@router.get("/{route_id}/vehicles", response_model=list[VehicleRead])
def list_route_vehicles(
    route_id: int,
    routes: RouteRepo,
    vehicles: VehicleRepo,
    limit: Limit = 20,
    offset: Offset = 0,
) -> Sequence[Vehicle]:
    """Зв'язок Route 1:N Vehicle."""
    routes.get(route_id)  # 404, якщо маршруту немає
    return vehicles.list(limit=limit, offset=offset, filters={"route_id": route_id})


@router.get("/{route_id}/stops", response_model=list[RouteStopDetail])
def list_route_stops(
    route_id: int,
    routes: RouteRepo,
    links: RouteStopRepo,
    stops: StopRepo,
    limit: Limit = 100,
    offset: Offset = 0,
) -> list[RouteStopDetail]:
    """Зв'язок Route N:M Stop: зупинки маршруту в порядку проходження."""
    routes.get(route_id)
    items = links.list(limit=limit, offset=offset, filters={"route_id": route_id}, order_by="seq")
    return [
        RouteStopDetail(
            **StopRead.model_validate(stops.get(link.stop_id)).model_dump(), seq=link.seq
        )
        for link in items
    ]
