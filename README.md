# ЛР №4 «Data Persistence & Web Interfaces» — «Міський транспорт» (варіант 15)

REST API на FastAPI + SQLModel + PostgreSQL 18 (Docker).

## Запуск

```bash
uv sync
docker compose up -d
uv run python -m lab4.init_db
uv run uvicorn lab4.restapi:app --reload
```

Документація API: http://127.0.0.1:8000/docs

## Перевірка якості коду

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
```
