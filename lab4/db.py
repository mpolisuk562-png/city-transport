"""Підключення до PostgreSQL: engine для ORM і перевірка з'єднання."""

from collections.abc import Iterator

import psycopg
from sqlmodel import Session, create_engine

from lab4.config import settings

engine = create_engine(settings.database_url)


def get_session() -> Iterator[Session]:
    """FastAPI-залежність: одна сесія на запит, закривається автоматично."""
    with Session(engine) as session:
        yield session


def check_connection() -> str:
    """Виконує простий запит сирим psycopg і повертає версію сервера."""
    with psycopg.connect(settings.psycopg_dsn) as conn:
        row = conn.execute("SELECT version()").fetchone()
    return str(row[0]) if row else "невідомо"


if __name__ == "__main__":
    print("Підключено до:", check_connection())
