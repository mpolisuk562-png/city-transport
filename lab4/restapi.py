"""Точка входу веб-застосунку: uv run uvicorn lab4.restapi:app --reload"""

from fastapi import FastAPI

from lab4.routers import drivers, route_stops, routes, stops, vehicles

app = FastAPI(
    title="Міський транспорт Львова",
    description="ЛР №4: REST API над PostgreSQL (маршрути, транспорт, зупинки, водії)",
)

for module in (routes, vehicles, stops, route_stops, drivers):
    app.include_router(module.router)
