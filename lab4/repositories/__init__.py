from lab4.repositories.base import Repository
from lab4.repositories.memory import InMemoryRepository
from lab4.repositories.postgres import PostgresRepository

__all__ = ["InMemoryRepository", "PostgresRepository", "Repository"]
