from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Self

from ttrack.config.entity import UserConfig


class ConfigStorage(ABC):

    def __init__(self: Self, config_path: Path) -> None:
        self.config_path = config_path

    @abstractmethod
    def read_properties(self: Self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def flush(self: Self, user_config: UserConfig) -> None:
        raise NotImplementedError
