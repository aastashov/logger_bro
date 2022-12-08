import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from dateutil.parser import parse
from pydantic import BaseModel, BaseSettings, Field


def date_to_quote(incoming: date):
    return quote(incoming.strftime("%Y-%m-%dT%H:%M:%S+06:00"))


def str_date_to_quote(incoming: str) -> str:
    return date_to_quote(parse(incoming))


def json_config_settings_source(_settings: BaseSettings) -> Dict[str, Any]:
    encoding = _settings.__config__.env_file_encoding
    # todo: need to fix this
    return json.loads(Path("/Users/aastashov/.ttrack/credentials.json").read_text(encoding))


class Toggl(BaseModel):
    token: str
    project_id: int


class Jira(BaseModel):
    url: str
    username: str
    password: str = ""
    token: str = ""


class Settings(BaseSettings):
    hours_in_month: int = 140
    rate: int = 5
    toggl: Toggl
    jira_clients: List[Jira] = Field(default_factory=list)

    issue_regex: str = r"^\S{0,5}-\d+"

    start: str = ""
    end: str = ""
    standup: bool = False
    version: bool = False
    report: bool = False
    hours_in_day: int = 0

    quote_start: str = ""
    quote_end: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        args = self.__get_args()
        self.start = args.start
        self.end = args.end
        self.standup = args.standup
        self.report = args.report
        self.version = args.version
        self.hours_in_day = args.hours

        self.quote_start = str_date_to_quote(self.start)
        self.quote_end = str_date_to_quote(self.end)

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                json_config_settings_source,
                env_settings,
                file_secret_settings,
            )

    def __get_args(self):
        date_start, date_end = self.previous_week_range(date.today())

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--version",
            help="Show version of package",
            action="store_true",
        )
        parser.add_argument(
            "--start",
            help="Start date. By default start last week",
            nargs="?",
            type=str,
            default=str(date_start),
        )
        parser.add_argument(
            "--end",
            help="End date. By default end last week",
            nargs="?",
            type=str,
            default=str(date_end),
        )
        parser.add_argument(
            "--standup",
            help="Shows yesterday's worklogs and creates drafts of the standup.",
            action="store_true",
        )
        parser.add_argument(
            "--report",
            help="Shows how much more work is to be done in the current month.",
            action="store_true",
        )
        parser.add_argument(
            "--hours",
            help="Number of hours per day that you can work.",
            nargs="?",
            type=int,
            default=0,
        )
        return parser.parse_args()

    @staticmethod
    def previous_week_range(incoming_date):
        start_date = incoming_date + timedelta(-incoming_date.weekday(), weeks=-1)
        end_date = incoming_date + timedelta(-incoming_date.weekday() - 1)
        return start_date, end_date


settings = Settings()
