from typing import Any, Self

import yaml

from ttrack.config.config_storage import ConfigStorage
from ttrack.config.entity import UserConfig


class YmlConfigStorage(ConfigStorage):
    def __repr__(self: Self) -> str:
        return f"YmlConfigStorage(config_path={self.config_path})"

    def read_properties(self: Self) -> dict[str, Any]:
        with self.config_path.open(mode="r") as file_stream:
            loaded_user_config = yaml.full_load(file_stream)

        return loaded_user_config

    def flush(self: Self, user_config: UserConfig) -> None:
        # I know it's not readable code, but I can and want to
        config_dict = {
            conf_name: {
                prop_name: getattr(prop_obj, prop_name) for prop_name in prop_obj.__annotations__.keys()
                if not prop_name.startswith("_")
            } for conf_name in user_config.__annotations__.keys()
            if not conf_name.startswith("_") and (prop_obj := getattr(user_config, conf_name))
        }

        with self.config_path.open(mode="w+") as file_stream:
            yaml.dump(config_dict, file_stream)
