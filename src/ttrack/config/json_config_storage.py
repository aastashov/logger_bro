import json
from typing import Any, Iterator

from ttrack.config.config_storage import ConfigStorage
from ttrack.config.types import FlatConfigType, NestedConfigType
from ttrack.constance import CONFIG_FILE_PATH


class JsonConfigStorage(ConfigStorage):

    def _get_nested_generator(
        self,
        previous_keys: list[str],
        nested_json: dict[str, Any],
    ) -> Iterator[tuple[str, str | int]]:
        for k, v in nested_json.items():
            if not isinstance(v, dict):
                yield ".".join([*previous_keys, k]), v
                continue
            yield from self._get_nested_generator([*previous_keys, k], v)

    def nested_to_flat_json(self, nested_json: dict[str, dict]) -> FlatConfigType:
        config: FlatConfigType = {}
        for k, v in nested_json.items():
            previous_keys = [k]
            if not isinstance(v, dict):
                config[k] = v
                continue

            for property_key, property_value in self._get_nested_generator(previous_keys, v):
                config[property_key] = property_value

        return config

    def read_properties(self) -> FlatConfigType:
        if not CONFIG_FILE_PATH.exists():
            return {}

        with CONFIG_FILE_PATH.open(mode="r") as _config_file:
            config_json: NestedConfigType = json.load(_config_file)

        flat_json = self.nested_to_flat_json(config_json)
        return flat_json

    def _merge_dicts(self, old_dict: dict[str, Any], new_dict: dict[str, Any]) -> None:
        for key, value in new_dict.items():
            if isinstance(value, dict) and key in old_dict:
                self._merge_dicts(old_dict[key], value)
                continue

            old_dict[key] = value

    def flat_to_nested_json(self, flat_json: dict[str, int | str]) -> dict[str, dict[str, Any]]:
        config: dict[str, dict[str, Any]] = {}
        for full_path, value in flat_json.items():
            path_key = full_path.split(".")
            new_config: dict[str, Any] = {path_key.pop(-1): value}
            path_key.reverse()

            for key in path_key:
                new_config = {key: new_config}

            self._merge_dicts(config, new_config)
        return config

    def add_property(self, name: str, value: Any) -> FlatConfigType:
        if not CONFIG_FILE_PATH.exists():
            CONFIG_FILE_PATH.parent.mkdir(exist_ok=True)
            CONFIG_FILE_PATH.touch(exist_ok=True)

        with CONFIG_FILE_PATH.open(mode="r") as _config_file:
            try:
                config_json: NestedConfigType = json.load(_config_file)
            except json.decoder.JSONDecodeError:
                config_json: NestedConfigType = {}

        new_config = self.flat_to_nested_json({name: value})
        self._merge_dicts(config_json, new_config)

        with CONFIG_FILE_PATH.open(mode="w+") as _config_file:
            json.dump(config_json, _config_file)

        return self.nested_to_flat_json(config_json)

    def remove_property(self, name: str) -> FlatConfigType:
        pass
