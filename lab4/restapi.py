"""Точка входу веб-застосунку: uv run uvicorn lab4.restapi:app --reload"""

from fastapi import FastAPI

from lab4.handlers import register_exception_handlers
from lab4.routers import ALL_ROUTERS

app = FastAPI(
    title="Міський транспорт Львова",
    description="ЛР №4: REST API над PostgreSQL (маршрути, транспорт, зупинки, водії)",
    version="0.1.0",
)

register_exception_handlers(app)
for router in ALL_ROUTERS:
    app.include_router(router)
