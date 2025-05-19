from abc import ABC, abstractmethod
from typing import Any

from src.core.config import config
from src.core.database.connection import DBConnection


class UnitOfWorkABC(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class UnitOfWork(UnitOfWorkABC):
    def __init__(self) -> None:
        self.async_session = DBConnection(config.db.url).async_session

    async def __aenter__(self) -> None:
        self.session = self.async_session()

    async def __aexit__(self, *args: Any) -> None:
        await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
