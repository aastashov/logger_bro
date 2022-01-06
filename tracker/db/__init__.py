from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ._postgres import PostgresStorage
from .interface import StorageInterface
from ..configs import settings


def get_storage():
    """Returns storage."""
    engine = create_async_engine(settings.DATABASE, echo=True)
    async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    return PostgresStorage(async_session=async_session(), engine=engine)


storage: StorageInterface = get_storage()

__all__ = [
    "storage",
]
