"""Спільні параметри запитів для всіх роутерів."""

from typing import Annotated

from fastapi import Query

Limit = Annotated[int, Query(ge=1, le=100, description="Скільки записів повернути")]
Offset = Annotated[int, Query(ge=0, description="Скільки записів пропустити")]
