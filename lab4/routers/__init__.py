"""Роутери ресурсів. Новий ресурс = новий модуль + один рядок у ALL_ROUTERS."""

from fastapi import APIRouter

from lab4.routers import drivers, route_stops, routes, stops, vehicles

ALL_ROUTERS: list[APIRouter] = [
    routes.router,
    vehicles.router,
    stops.router,
    route_stops.router,
    drivers.router,
]
