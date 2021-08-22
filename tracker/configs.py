import argparse
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

from dateutil.parser import parse
from pydantic import BaseSettings


class Settings(BaseSettings):
    BASE_DIR = Path(__file__).resolve().parent

    TOGGL_URL: str = "https://api.track.toggl.com/api/v8"
    TOGGL_TOKEN: str
    TOGGL_PROJECT_ID: int = 0

    JIRA_URL_1: str  # example https://jira.example.comJIRA_TOKE_2
    JIRA_PASS_1: str = ""
    JIRA_USER_1: str = ""
    JIRA_TOKEN_1: str = ""

    # todo: need to delete
    JIRA_URL_2: str  # example https://jira_2.example.com
    JIRA_PASS_2: str = ""
    JIRA_USER_2: str = ""
    JIRA_TOKEN_2: str = ""

    ISSUE_REGEX: str = r"^\S{0,5}-\d+"

    HOURS_IN_MONTH: int = 120
    RATE: float = 10.0

    start: str = ""
    end: str = ""
    standup: bool = False
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
        self.hours_in_day = args.hours

        self.quote_start = self.str_date_to_quote(self.start)
        self.quote_end = self.str_date_to_quote(self.end)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __get_args(self):
        date_start, date_end = self.previous_week_range(date.today())

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--start", help="Start date. By default start last week", nargs="?", type=str, default=str(date_start),
        )
        parser.add_argument(
            "--end", help="End date. By default end last week", nargs="?", type=str, default=str(date_end),
        )
        parser.add_argument(
            "--standup", help="Shows yesterday's worklogs and creates drafts of the standup.", action="store_true",
        )
        parser.add_argument(
            "--report", help="Shows how much more work is to be done in the current month.", action="store_true",
        )
        parser.add_argument(
            "--hours", help="Number of hours per day that you can work.", nargs="?", type=int, default=0,
        )
        return parser.parse_args()

    @staticmethod
    def previous_week_range(incoming_date):
        start_date = incoming_date + timedelta(-incoming_date.weekday(), weeks=-1)
        end_date = incoming_date + timedelta(-incoming_date.weekday() - 1)
        return start_date, end_date

    @classmethod
    def str_date_to_quote(cls, incoming: str) -> str:
        return cls.date_to_quote(parse(incoming))

    @classmethod
    def date_to_quote(cls, incoming: date):
        return quote(incoming.strftime("%Y-%m-%dT%H:%M:%S+06:00"))


settings = Settings()
