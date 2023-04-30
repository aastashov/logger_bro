from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from cleo.commands.command import Command
from dateutil.parser import parse

from ttrack.config.config import Config

if TYPE_CHECKING:
    from typing import Any
    from ttrack.config.types import ConfigLiteral
    from datetime import date


class BaseCommand(Command):
    _config: Config | None = None

    @property
    def config(self) -> Config:
        if self._config is None:
            self._config = Config.create()
        return self._config

    def str_date_to_quote(self, incoming: str) -> str:
        return self.date_to_quote(parse(incoming))

    def date_to_quote(self, incoming: date) -> str:
        return quote(incoming.strftime("%Y-%m-%dT%H:%M:%S+06:00"))


class BaseConfigCommand(BaseCommand):

    def get_config_display_message(self, property_name: str, value: Any, is_default=False) -> str:
        fg = "red" if not value else "yellow" if is_default else "default"
        if isinstance(value, str):
            value = f'"{value}"'
        elif isinstance(value, bool):
            value = f"{value}".lower()

        value = f"<fg={fg}>{value}</> (default)" if is_default else f"<fg={fg}>{value}</>"
        return f"<fg=cyan>{property_name}</> = {value}"

    def display_config_list(self, status_of_config: dict[ConfigLiteral, tuple[Any, bool]]):
        for property_name, (value, is_default) in status_of_config.items():
            self.line(self.get_config_display_message(property_name, value, is_default))
