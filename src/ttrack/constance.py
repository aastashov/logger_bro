from pathlib import Path

from platformdirs import user_config_dir

CONFIG_DIR = Path(user_config_dir(".ttrack", appauthor=False, roaming=True))
CONFIG_FILE_PATH = CONFIG_DIR / "config.json"
