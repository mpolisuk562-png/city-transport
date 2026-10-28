from collections.abc import Iterator

import psycopg
from sqlmodel import Session, create_engine

from lab4.config import settings

engine = create_engine(settings.database_url)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


def check_connection() -> str:
    with psycopg.connect(settings.psycopg_dsn) as conn:
        row = conn.execute("SELECT version()").fetchone()
    return str(row[0]) if row else "невідомо"


if __name__ == "__main__":
    print("Підключено до:", check_connection())
