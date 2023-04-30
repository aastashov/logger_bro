from abc import ABC, abstractmethod
from typing import Any

from ttrack.config.types import FlatConfigType


class ConfigStorage(ABC):

    @abstractmethod
    def read_properties(self) -> FlatConfigType:
        raise NotImplementedError

    @abstractmethod
    def add_property(self, name: str, value: Any) -> FlatConfigType:
        raise NotImplementedError

    @abstractmethod
    def remove_property(self, name: str) -> FlatConfigType:
        raise NotImplementedError
