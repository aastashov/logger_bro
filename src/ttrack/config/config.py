from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from ttrack.config.config_storage import ConfigStorage
from ttrack.config.json_config_storage import JsonConfigStorage
from ttrack.config.types import ConfigLiteral, ConfigMapDef, FlatConfigType
from ttrack.constance import CONFIG_FILE_PATH


def _int_validator(answer: Any) -> int | None:
    return (str(answer).isdigit() or None) and int(answer)


config_map: ConfigMapDef = {
    "report.hours_in_month": {
        "question": "",
        "validator": _int_validator,
        "default": 140,
    },
    "report.rate": {
        "question": "",
        "validator": _int_validator,
        "default": 5,
    },
    "toggl.token": {
        "question": "Open the next URL and create a new token https://track.toggl.com/profile if not exist:",
        "validator": lambda answer: (answer != "" or None) and answer,
        "default": None,
    },
    "toggl.project_id": {
        "question": (
            "You need to open https://track.toggl.com/projects/ and get the ID from URL."
            " For example: https://track.toggl.com/projects/xxx/list, the xxx is project_id."
        ),
        "validator": _int_validator,
        "default": None,
    },
    "jira_clients.url": {
        "question": "",
        "validator": lambda answer: answer,
        "default": None,
    },
    "jira_clients.username": {
        "question": "",
        "validator": lambda answer: answer,
        "default": None,
    },
    "jira_clients.password": {
        "question": "",
        "validator": lambda answer: answer,
        "default": None,
    },
    "jira_clients.token": {
        "question": "",
        "validator": lambda answer: answer,
        "default": None,
    },
    "validators.issue_regex": {
        "question": "",
        "validator": lambda answer: answer,
        "default": r"^\S{0,5}-\d+",
    },
    "validators.ru_text_regex": {
        "question": "",
        "validator": lambda answer: answer,
        "default": r"[а-яА-Я]",

    },
}

_default_config: Config | None = None


def get_default_config() -> FlatConfigType:
    return {key: value.get("default", None) for key, value in config_map.items()}


@dataclass
class Config:
    _config_storage: ConfigStorage

    default_config: FlatConfigType = field(default_factory=get_default_config)

    _config: FlatConfigType = field(default_factory=get_default_config)

    def get(self, config_name: ConfigLiteral, default=None) -> Any:
        if config_name not in self._config:
            return default
        return self._config[config_name]

    def set(self, config_name: ConfigLiteral, value: Any):
        new_config = self._config_storage.add_property(config_name, value)
        self._merge_config(new_config)

    def remove(self, config_name: ConfigLiteral):
        new_config = self._config_storage.remove_property(config_name)
        self._merge_config(new_config)

    @property
    def status_of_config(self) -> dict[ConfigLiteral, tuple[Any, bool]]:
        status_map = {}
        for config_key, value in self._config.items():
            if config_key not in config_map:
                continue

            is_default = value is not None and value == config_map[config_key]["default"]
            status_map[config_key] = (value, is_default)

        return status_map

    def _merge_config(self, new_config: dict[ConfigLiteral, Any]):
        _config = deepcopy(self._config)
        self._merge_dicts(_config, new_config)
        self._config = _config

    def _merge_dicts(self, old_dict: dict[str, Any], new_dict: dict[str, Any]) -> None:
        for key, value in new_dict.items():
            if isinstance(value, dict) and key in old_dict:
                self._merge_dicts(old_dict[key], value)
                continue

            old_dict[key] = value

    @classmethod
    def create(cls) -> Config:
        global _default_config

        if _default_config is None:
            _default_config = cls(_config_storage=JsonConfigStorage())

            if not CONFIG_FILE_PATH.exists():
                return _default_config

            new_config = _default_config._config_storage.read_properties()
            _default_config._merge_config(new_config)

        return _default_config


if __name__ == "__main__":
    config = Config.create()
    print(config)
