from collections.abc import Callable
from typing import Any, Literal, TypedDict

Validator = Callable[[str], Any]

ConfigPropertyMapDef = TypedDict(
    "ConfigPropertyMapDef",
    {
        "question": str,
        "default": Any,
        "validator": Validator,
    },
)

ConfigMapDef = dict[str, ConfigPropertyMapDef]

ConfigLiteral = Literal[
    "report.hours_in_month",
    "report.rate",
    "toggl.token",
    "toggl.project_id",
    "jira_clients.url",
    "jira_clients.username",
    "jira_clients.password",
    "jira_clients.token",
    "validators.issue_regex",
    "validators.ru_text_regex",
]

FlatConfigType = dict[ConfigLiteral, str | int]
NestedConfigType = dict[str, dict[str, Any]]
