from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ._postgres import PostgresStorage
from .interface import StorageInterface
from .models import Base
from ..configs import settings


def get_storage():
    """Returns storage."""
    engine = create_engine(settings.DATABASE, echo=True)
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return PostgresStorage(session=session())


storage: StorageInterface = get_storage()

__all__ = [
    "storage",
]
