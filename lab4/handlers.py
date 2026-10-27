"""Перетворення винятків на HTTP-відповіді: 404, 409 і зрозумілі 422."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from lab4.errors import ConflictError, NotFoundError
from lab4.schemas import PATTERN_HINTS

# Українські повідомлення для найчастіших типів помилок pydantic.
MESSAGES: dict[str, str] = {
    "missing": "Обов'язкове поле",
    "extra_forbidden": "Невідоме поле",
    "int_parsing": "Очікується ціле число",
    "float_parsing": "Очікується число",
    "enum": "Недопустиме значення",
    "json_invalid": "Некоректний JSON",
    # Плейсхолдери підставляються з error["ctx"] (межі, задані у Field).
    "greater_than_equal": "Значення має бути не менше {ge}",
    "less_than_equal": "Значення має бути не більше {le}",
    "string_too_short": "Занадто короткий рядок (мінімум {min_length} симв.)",
    "string_too_long": "Занадто довгий рядок (максимум {max_length} симв.)",
}


def _describe(error: dict[str, Any]) -> dict[str, Any]:
    loc = [str(part) for part in error["loc"] if part != "body"]
    field = loc[-1] if loc else ""
    kind = error["type"]
    if kind == "string_pattern_mismatch" and field in PATTERN_HINTS:
        message = PATTERN_HINTS[field]
    elif kind == "value_error":
        message = str(error["msg"]).removeprefix("Value error, ")
    elif kind in MESSAGES:
        message = MESSAGES[kind].format(**error.get("ctx", {}))
    else:
        message = str(error["msg"])
    # Помилка рівня всієї моделі (наприклад, null у PUT) не має імені поля.
    field_path = ".".join(loc) or "body"
    return {"field": field_path, "message": message, "input": error.get("input")}


async def validation_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errors = [_describe(e) for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"detail": "Некоректні вхідні дані", "errors": errors},
    )


async def not_found_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def conflict_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": f"Конфлікт даних: {exc}"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(ConflictError, conflict_handler)
