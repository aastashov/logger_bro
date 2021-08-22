import argparse
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

import environ  # noqa
from dateutil.parser import parse


class Settings:
    def __init__(self):
        env = environ.Env()
        env.read_env()

        self.BASE_DIR = Path(__file__).resolve().parent
        self.TOGGL_TOKEN = (env('TOGGL_TOKEN', default='') + ':api_token').encode()
        self.TOGGL_PROJECT_ID = env.int('TOGGL_PROJECT_ID', default=0)
        self.JIRA_PASS = env('JIRA_PASS', default='')
        self.JIRA_USER = env('JIRA_USER', default='')

        self.JIRA_URL = env('JIRA_URL')  # example https://jira.example.com
        self.TOGGL_URL = 'https://api.track.toggl.com/api/v8'

        self.ISSUE_REGEX = env('ISSUE_REGEX', default=r'^\S{0,5}-\d+')

        self.hours_in_month = env.int("HOURS_IN_MONTH", default=120)
        self.rate = env.float("RATE", default=10.0)

        args = self.__get_args()
        self.start = args.start
        self.end = args.end
        self.standup = args.standup
        self.report = args.report
        self.hours_in_day = args.hours

        self.quote_start = self.str_date_to_quote(self.start)
        self.quote_end = self.str_date_to_quote(self.end)

    def __get_args(self):
        date_start, date_end = self.previous_week_range(date.today())

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--start', help='Start date. By default start last week', nargs='?', type=str, default=str(date_start),
        )
        parser.add_argument(
            '--end', help='End date. By default end last week', nargs='?', type=str, default=str(date_end),
        )
        parser.add_argument(
            '--standup',
            help='Shows yesterday\'s worklogs and creates drafts of the standup.',
            action='store_true',
        )
        parser.add_argument(
            '--report',
            help='Shows how much more work is to be done in the current month.',
            action='store_true',
        )
        parser.add_argument(
            '--hours', help='Number of hours per day that you can work.', nargs='?', type=int, default=0,
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
        return quote(incoming.strftime('%Y-%m-%dT%H:%M:%S+06:00'))


settings = Settings()
