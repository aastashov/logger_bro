from collections.abc import Callable
from typing import Any, TypedDict

from ttrack.config.entity import ConfigProperty


class ConfigMap(TypedDict):
    report: dict[str, int]
    toggl: dict[str, str | int]
    jira: list[dict[str, str]]
    validator: dict[str, str]


Validator = Callable[[str], Any]


class ConfigPropertyMapDef(TypedDict):
    question: str
    default: Any
    validator: Validator


ConfigMapDef = dict[str, dict[str, ConfigPropertyMapDef | ConfigProperty]]
