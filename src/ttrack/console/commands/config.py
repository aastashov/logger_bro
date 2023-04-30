from __future__ import annotations

from typing import TYPE_CHECKING

from cleo.helpers import argument, option

from ttrack.config.config import config_map
from ttrack.console.commands.command import BaseConfigCommand
from ttrack.constance import CONFIG_FILE_PATH

if TYPE_CHECKING:
    pass


class ConfigCommand(BaseConfigCommand):
    name = "config"
    description = "Use this command to change the specific settings of your tracker."

    arguments = [
        argument("key", "Setting key.", optional=True),
        argument("value", "Setting value.", optional=True),
    ]

    options = [
        option("list", None, "List configuration settings."),
        # option("unset", None, "Unset configuration setting."),
        # option("local", None, "Set/Get from the project's local configuration."),
    ]

    def handle(self) -> int:
        if self.option("list"):
            status_of_config = self.config.status_of_config
            self.display_config_list(status_of_config)
            self.line(self.get_config_display_message("config_file_path", CONFIG_FILE_PATH, True))
            return 0

        config_key = self.argument("key")
        config_value = self.argument("value")
        if config_key and config_value:
            if config_key not in config_map:
                self.config.set(config_key, config_value)
                return 0

            valid_config_value = config_map[config_key]["validator"](config_value)
            if not valid_config_value:
                self.line(f"<fg=red>Wrong value: {config_value}</>")
                return 1

            self.config.set(config_key, valid_config_value)

            config_value = self.config.get(config_key)
            self.line("<fg=green>Updated config:</>")
            self.line(self.get_config_display_message(config_key, config_value))
            return 0

        if config_key and not config_value:
            config_value = self.config.get(config_key)
            self.line(self.get_config_display_message(config_key, config_value))
            return 0

        return 0
