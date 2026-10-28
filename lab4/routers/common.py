from fastapi import HTTPException

from lab4.models import Entity
from lab4.repositories import Repository


def get_or_404[M: Entity](repo: Repository[M], item_id: int) -> M:
    obj = repo.get(item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"Запис з id={item_id} не знайдено")
    return obj
