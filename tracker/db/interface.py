from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from tracker.db.models import User


class StorageInterface(abc.ABC):
    """Storage interface."""

    @abc.abstractmethod
    async def migrate(self):
        ...

    @abc.abstractmethod
    async def close_connection(self):
        ...

    @abc.abstractmethod
    async def get_or_create_user(self, tid: int) -> tuple["User", bool]:
        ...

    @abc.abstractmethod
    async def create_last_message(self, user: "User", last_message: str):
        ...
