"""REST-ресурс /routes (маршрути) і зв'язки маршруту з транспортом і зупинками."""

from fastapi import APIRouter

from lab4.dependencies import RouteRepo, RouteStopRepo, StopRepo, VehicleRepo
from lab4.models import Route, Stop, Vehicle
from lab4.routers.common import get_or_404
from lab4.schemas import RouteIn

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("")
def list_routes(repo: RouteRepo) -> list[Route]:
    return repo.list_all()


@router.get("/{route_id}")
def get_route(route_id: int, repo: RouteRepo) -> Route:
    return get_or_404(repo, route_id)


@router.post("", status_code=201)
def create_route(data: RouteIn, repo: RouteRepo) -> Route:
    return repo.create(data)


@router.put("/{route_id}")
def update_route(route_id: int, data: RouteIn, repo: RouteRepo) -> Route:
    return repo.update(get_or_404(repo, route_id), data)


@router.delete("/{route_id}", status_code=204)
def delete_route(route_id: int, repo: RouteRepo) -> None:
    repo.delete(get_or_404(repo, route_id))


@router.get("/{route_id}/vehicles")
def list_route_vehicles(route_id: int, routes: RouteRepo, vehicles: VehicleRepo) -> list[Vehicle]:
    """Зв'язок Route 1:N Vehicle: машини маршруту."""
    get_or_404(routes, route_id)
    return vehicles.list_all(route_id=route_id)


@router.get("/{route_id}/stops")
def list_route_stops(
    route_id: int, routes: RouteRepo, links: RouteStopRepo, stops: StopRepo
) -> list[Stop]:
    """Зв'язок Route N:M Stop: зупинки маршруту в порядку проходження."""
    get_or_404(routes, route_id)
    ordered = sorted(links.list_all(route_id=route_id), key=lambda link: link.seq)
    return [get_or_404(stops, link.stop_id) for link in ordered]
