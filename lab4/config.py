"""Налаштування застосунку зі змінних оточення."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # URL для SQLAlchemy/SQLModel: діалект postgresql + драйвер psycopg (3-го покоління).
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
    )
    # Яке сховище використовують роутери: "postgres" або "memory".
    storage: str = os.getenv("STORAGE", "postgres")

    @property
    def psycopg_dsn(self) -> str:
        """DSN для «сирого» psycopg: той самий URL, але без назви драйвера."""
        return self.database_url.replace("postgresql+psycopg://", "postgresql://", 1)


settings = Settings()
