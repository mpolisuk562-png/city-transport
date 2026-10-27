"""Доменні винятки. Репозиторії кидають їх, а не HTTPException,
щоб шар збереження не залежав від веб-фреймворку."""


class NotFoundError(Exception):
    def __init__(self, entity: str, item_id: int) -> None:
        self.entity = entity
        self.item_id = item_id
        super().__init__(f"{entity} з id={item_id} не знайдено")


class ConflictError(Exception):
    """Порушення унікальності або зовнішнього ключа."""
