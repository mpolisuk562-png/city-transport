from pydantic import BaseModel
from sqlalchemy import column
from sqlmodel import Session, select

from lab4.models import Entity
from lab4.repositories.base import Repository


class PostgresRepository[ModelT: Entity](Repository[ModelT]):
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def get(self, item_id: int) -> ModelT | None:
        return self.session.get(self.model, item_id)

    def list_all(self, **filters: object) -> list[ModelT]:
        query = select(self.model)
        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)
        return list(self.session.exec(query.order_by(column("id"))).all())

    def create(self, data: BaseModel) -> ModelT:
        obj = self.model(**data.model_dump())
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: ModelT, data: BaseModel) -> ModelT:
        for field, value in data.model_dump().items():
            setattr(obj, field, value)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.session.delete(obj)
        self.session.commit()
