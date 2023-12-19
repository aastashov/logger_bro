from __future__ import annotations

import dataclasses
from typing import Any, Self

from ttrack.config.config_storage import ConfigStorage
from ttrack.config.entity import JiraConfig, ReportConfig, TogglConfig, UserConfig, ValidatorConfig
from ttrack.config.types import ConfigMapDef
from ttrack.config.yml_storage import YmlConfigStorage
from ttrack.constance import CONFIG_FILE_PATH
from ttrack.utils import Singleton


def _int_validator(answer: Any) -> int | None:
    return (str(answer).isdigit() or None) and int(answer)


config_map: ConfigMapDef = {
    "report": {
        "_class": ReportConfig,
        "hours_in_month": {
            "question": "",
            "validator": _int_validator,
            "default": 140,
        },
        "rate": {
            "question": "",
            "validator": _int_validator,
            "default": 5,
        },
    },
    "toggl": {
        "_class": TogglConfig,
        "token": {
            "question": "Open the next URL and create a new token https://track.toggl.com/profile if not exist:",
            "validator": lambda answer: (answer != "" or None) and answer,
            "default": None,
        },
        "project_id": {
            "question": (
                "You need to open https://track.toggl.com/projects/ and get the ID from URL."
                " For example: https://track.toggl.com/projects/xxx/list, the xxx is project_id."
            ),
            "validator": _int_validator,
            "default": None,
        },
    },
    "validator": {
        "_class": ValidatorConfig,
        "issue_regex": {
            "question": "",
            "validator": lambda answer: answer,
            "default": r"^\S{0,5}-\d+",
        },
        "ru_text_regex": {
            "question": "",
            "validator": lambda answer: answer,
            "default": r"[а-яА-Я]",
        },
    },
    "jira": {
        "_class": JiraConfig,
        "url": {
            "question": "",
            "validator": lambda answer: answer,
            "default": None,
        },
        "username": {
            "question": "",
            "validator": lambda answer: answer,
            "default": None,
        },
        "password": {
            "question": "",
            "validator": lambda answer: answer,
            "default": None,
        },
        "token": {
            "question": "",
            "validator": lambda answer: answer,
            "default": None,
        },
    },
}


@dataclasses.dataclass
class Config(UserConfig, Singleton):
    _storage: ConfigStorage = dataclasses.field(default=YmlConfigStorage(config_path=CONFIG_FILE_PATH))

    def __post_init__(self: Self) -> None:
        if not CONFIG_FILE_PATH.exists():
            return

        self._merge_config(self._storage.read_properties())

    def set(self, property_path: str, property_value: Any) -> None:
        property_group_name, property_name = property_path.split(".")
        property_group = getattr(self, property_group_name)
        setattr(property_group, property_name, property_value)
        self._storage.flush(self)

    def get(self, property_path: str) -> Any:
        property_group_name, property_name = property_path.split(".")
        default_value = config_map[property_group_name][property_name]["default"]
        return getattr(getattr(self, property_group_name), property_name, default_value)

    def remove(self, property_path: str) -> Any:
        property_group_name, property_name = property_path.split(".")
        default_value = config_map[property_group_name][property_name]["default"]
        setattr(getattr(self, property_group_name), property_name, default_value)
        self._storage.flush(self)

    @property
    def status_of_config(self: Self) -> dict[str, tuple[Any, bool]]:
        status_map = {}
        for config_name, config_obj in config_map.items():
            _config = getattr(self, config_name)

            if not _config:
                continue

            for property_name, property_field in config_obj.items():
                if property_name.startswith("_"):
                    continue

                property_value = getattr(_config, property_name)
                is_default = property_value == property_field["default"]

                full_config_name = f"{config_name}.{property_name}"
                status_map[full_config_name] = (property_field["default"], is_default)

        return status_map

    def _merge_config(self: Self, new_config: dict[str, Any]) -> None:
        for config_name, config_obj in self.__dict__.items():
            if config_name not in config_map or config_name not in new_config:
                continue

            user_config_obj = new_config[config_name] or {}
            for property_name, property_value in config_obj.__dict__.items():
                if property_name not in config_map[config_name] or property_name not in user_config_obj:
                    continue

                validator = config_map[config_name][property_name]["validator"]

                user_property_value = validator(user_config_obj[property_name])
                default_property_value = config_map[config_name][property_name]["default"]

                setattr(getattr(self, config_name), property_name, user_property_value or default_property_value)

    def get_default_for_config_key(self: Self, config_key: str) -> Any:
        config_name, config_property = config_key.split(".")
        if config_name not in config_map:
            return None

        return config_map[config_name][config_property]["default"]
