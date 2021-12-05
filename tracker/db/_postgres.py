from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from tracker.db.interface import StorageInterface

if TYPE_CHECKING:  # pragma: no cover
    from .models import User


@dataclasses.dataclass
class PostgresStorage(StorageInterface):
    session: Session

    def create_user(self, user: "User") -> "User":
        self.session.add(user)
        self.session.flush()
        return user

    def get_or_create_user(self, tid: int) -> tuple["User", bool]:
        user = self.session.query(User).filter(User.tid == tid).first()
        if user is not None:
            return user, False
        return self.create_user(User(tid=tid)), True
