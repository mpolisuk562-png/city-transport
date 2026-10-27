"""Реалізація репозиторію поверх PostgreSQL через ORM SQLModel."""

from collections.abc import Mapping, Sequence

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import class_mapper
from sqlmodel import Session, SQLModel, select

from lab4.errors import ConflictError, NotFoundError
from lab4.repositories.base import Repository


class PostgresRepository[ModelT: SQLModel](Repository[ModelT]):
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model
        self._mapper = class_mapper(model)

    def get(self, item_id: int) -> ModelT:
        obj = self.session.get(self.model, item_id)
        if obj is None:
            raise NotFoundError(self.model.__name__, item_id)
        return obj

    def list(
        self,
        *,
        limit: int,
        offset: int,
        filters: Mapping[str, object] | None = None,
        order_by: str | None = None,
    ) -> Sequence[ModelT]:
        columns = self._mapper.columns
        stmt = select(self.model)
        # ORM будує параметризований WHERE: значення фільтрів ідуть окремо від SQL.
        for field, value in (filters or {}).items():
            stmt = stmt.where(columns[field] == value)
        order = [columns[order_by]] if order_by else list(self._mapper.primary_key)
        stmt = stmt.order_by(*order).offset(offset).limit(limit)
        return self.session.exec(stmt).all()

    def create(self, data: BaseModel) -> ModelT:
        obj = self.model(**data.model_dump())
        self.session.add(obj)
        self._commit()
        self.session.refresh(obj)
        return obj

    def update(self, item_id: int, data: BaseModel) -> ModelT:
        obj = self.get(item_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        self._commit()
        self.session.refresh(obj)
        return obj

    def delete(self, item_id: int) -> None:
        obj = self.get(item_id)
        self.session.delete(obj)
        self._commit()

    def _commit(self) -> None:
        """Перетворює IntegrityError БД (UNIQUE / FOREIGN KEY) на доменний ConflictError."""
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            diag = getattr(exc.orig, "diag", None)
            detail = getattr(diag, "message_detail", None) or str(exc.orig)
            raise ConflictError(detail) from exc
