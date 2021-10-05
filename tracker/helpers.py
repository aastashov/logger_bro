from datetime import date, datetime, timedelta
from typing import List

import pyperclip
from workdays import networkdays

from tracker.configs import settings
from tracker.http import jira_client, toggl_client
from tracker.structs import Client, TimeEntityDetail, Toggl, User


class TrackerBro:
    """ It's a proxy model for work with the toggl and jira apis """

    minute = 60 * 60

    @staticmethod
    def make_stand_up(user: User):
        today = date.today()
        yesterday = today - timedelta(days=1)
        time_entity = list(toggl_client.get_time_entries(
            token=user.toggl.token,
            start=settings.date_to_quote(yesterday),
            end=settings.date_to_quote(today),
        ))
        stand_up = '@comedian\nYesterday\n'
        for time_entry in time_entity:
            stand_up += f' - {time_entry.clean_description}\n'
        stand_up += 'Today\n - \nProblems\n - no'
        pyperclip.copy(stand_up)
        print('In clipboard!')

    @staticmethod
    def create_work_logs(user: User, time_entity: List[TimeEntityDetail]):
        for time_entry in time_entity:
            work_log = jira_client.create_work_log(time_entry)
            print(f'{bool(work_log)} for log "{time_entry}"')

    @staticmethod
    def _round_to_zero(number) -> int:
        return int((abs(number) + number) / 2)

    def _parse_to_str_time(self, duration: int) -> str:
        if self._round_to_zero(duration) == 0:
            return "00:00:00"
        logged_hours = self._round_to_zero(duration // self.minute)
        logged_minutes = self._round_to_zero(duration % self.minute // 60)
        logged_seconds = self._round_to_zero(duration % self.minute % 60)
        return ":".join(map(lambda x: str(x).zfill(2), [logged_hours, logged_minutes, logged_seconds]))

    def get_report(self, user: User, hours_in_day: int) -> str:
        first_date_in_current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_date_in_current_month = first_date_in_current_month.replace(month=first_date_in_current_month.month + 1)
        last_date_in_current_month -= timedelta(seconds=1)

        start = settings.date_to_quote(first_date_in_current_month)
        end = settings.date_to_quote(last_date_in_current_month)

        entries = toggl_client.get_time_entries(token=user.toggl.token, start=start, end=end)
        logged_duration = sum((entry.duration for entry in entries))
        left_logged_seconds = user.total * self.minute - logged_duration

        lef_working_days = networkdays(datetime.now(), last_date_in_current_month)

        amount = round(user.rate / self.minute * logged_duration, 2)

        every_day = self._parse_to_str_time(left_logged_seconds / lef_working_days) if lef_working_days else "0"
        left_hours = self._parse_to_str_time(duration=left_logged_seconds)

        if hours_in_day != 0:
            amount += round(user.rate * lef_working_days * hours_in_day, 2)
            every_day = self._parse_to_str_time(hours_in_day * self.minute)

        info = (
            ("Total: ", f"{user.total}h"),
            ("Logged: ", self._parse_to_str_time(duration=logged_duration)),
            ("Left hours: ", left_hours),
            ("Left working days: ", lef_working_days),
            ("Every day: ", every_day),
            ("Rate: ", f"{user.rate}$"),
            ("Amount: ", f"{amount}$"),
        )
        message, sep = "", ""
        for key, value in info:
            message += sep + key + str(value)
            sep = "\n"
        return message


tracker_bro = TrackerBro()
cli_user = User(
    tid=-1,
    rate=settings.RATE,
    total=settings.HOURS_IN_MONTH,
    toggl=Toggl(
        token=settings.TOGGL_TOKEN,
        project_id=settings.TOGGL_PROJECT_ID,
    ),
    clients=[
        Client(
            url=settings.JIRA_URL_1,
            password=settings.JIRA_PASS_1,
            username=settings.JIRA_USER_1,
            token=settings.JIRA_TOKEN_1,
        ),
        Client(
            url=settings.JIRA_URL_2,
            password=settings.JIRA_PASS_2,
            username=settings.JIRA_USER_2,
            token=settings.JIRA_TOKEN_2,
        ),
    ],
)
