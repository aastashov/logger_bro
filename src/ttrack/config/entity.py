from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class ConfigProperty(ABC):

    @classmethod
    @abstractmethod
    def default(cls) -> ConfigProperty:
        raise NotImplementedError


@dataclass
class ReportConfig(ConfigProperty):
    hours_in_month: int
    rate: int

    @classmethod
    def default(cls) -> ReportConfig:
        return cls(hours_in_month=140, rate=5)


@dataclass
class TogglConfig:
    token: str
    project_id: int

    @classmethod
    def default(cls) -> TogglConfig:
        return cls(token="", project_id=0)


@dataclass
class JiraConfig:
    url: str
    username: str
    password: str
    token: str

    _index: int

    @classmethod
    def default(cls, index=0) -> JiraConfig:
        return cls(url="", username="", password="", token="", _index=index)


@dataclass
class ValidatorConfig:
    issue_regex: str
    ru_text_regex: str

    @classmethod
    def default(cls) -> ValidatorConfig:
        return cls(issue_regex=r"^\S{0,5}-\d+", ru_text_regex=r"[а-яА-Я]")


@dataclass
class UserConfig:
    report: ReportConfig = field(default_factory=ReportConfig.default)
    toggl: TogglConfig = field(default_factory=TogglConfig.default)
    validator: ValidatorConfig = field(default_factory=ValidatorConfig.default)
    jira: JiraConfig = field(default_factory=JiraConfig.default)
