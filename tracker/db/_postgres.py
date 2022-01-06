from __future__ import annotations

import dataclasses

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession
from sqlalchemy.orm import Session, selectinload

from tracker.db.interface import StorageInterface
from .models import Base, User


@dataclasses.dataclass
class PostgresStorage(StorageInterface):
    async_session: AsyncSession
    engine: AsyncEngine

    last_message_wait_token = "wait_token"

    async def migrate(self):
        async with self.engine.begin() as conn:  # type: AsyncConnection
            await conn.run_sync(Base.metadata.create_all)

    async def close_connection(self):
        await self.engine.dispose()
        await self.async_session.close()

    async def get_or_create_user(self, tid: int) -> tuple["User", bool]:
        qs = select(User).options(selectinload(User.toggl), selectinload(User.clients))
        result = await self.async_session.execute(qs.where(User.tid == tid))
        user = result.scalars().first() or User(tid=tid)
        if user.id:
            return user, False

        self.async_session.add(user)
        await self.async_session.commit()
        return user, True

    async def create_last_message(self, user: "User", last_message: str):
        return
        await self.async_session.execute(insert())
