from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from tracker.structs import User


class StorageInterface(abc.ABC):
    """Storage interface."""

    @abc.abstractmethod
    def get_or_create_user(self, tid: int) -> "User" | bool:
        ...

    @abc.abstractmethod
    def create_user(self, user: "User") -> "User":
        ...
