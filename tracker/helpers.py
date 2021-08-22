from datetime import date, datetime, timedelta
from typing import List

import pyperclip
from workdays import networkdays

from tracker.clients import JiraClient, TogglClient
from tracker.configs import settings
from tracker.structs import TimeEntity, TimeEntityDetail


class TrackerBro:
    """ It's a proxy model for work with the toggl and jira apis """

    minute = 60 * 60

    def __init__(self):
        self.toggl = TogglClient()
        self.jira = JiraClient()

    def make_stand_up(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        time_entity = list(self.toggl.get_time_entries(
            start=settings.date_to_quote(yesterday),
            end=settings.date_to_quote(today),
        ))
        stand_up = '@comedian\nYesterday\n'
        for time_entry in time_entity:
            stand_up += f' - {time_entry.clean_description}\n'
        stand_up += 'Today\n - \nProblems\n - no'
        pyperclip.copy(stand_up)
        print('In clipboard!')

    def get_time_entries(self, start: str, end: str) -> List[TimeEntity]:
        return self.toggl.get_time_entries(start, end)

    def get_detail_time_entries(self, start: str, end: str) -> List[TimeEntityDetail]:
        return self.toggl.get_detail_time_entries(start, end)

    def create_work_logs(self, time_entity: List[TimeEntityDetail]):
        for time_entry in time_entity:
            work_log = self.jira.create_work_log(time_entry)
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

    def print_report(self, hours_in_month: int, rate: float, hours_in_day: int):
        first_date_in_current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_date_in_current_month = first_date_in_current_month.replace(month=first_date_in_current_month.month + 1)
        last_date_in_current_month -= timedelta(seconds=1)

        start = settings.date_to_quote(first_date_in_current_month)
        end = settings.date_to_quote(last_date_in_current_month)

        logged_duration = sum((entry.duration for entry in self.get_time_entries(start=start, end=end)))
        left_logged_seconds = hours_in_month * self.minute - logged_duration

        lef_working_days = networkdays(datetime.now(), last_date_in_current_month)

        amount = round(rate / self.minute * logged_duration, 2)

        every_day = self._parse_to_str_time(left_logged_seconds / lef_working_days) if lef_working_days else "0"
        left_hours = self._parse_to_str_time(duration=left_logged_seconds)

        if hours_in_day != 0:
            amount += round(rate * lef_working_days * hours_in_day, 2)
            every_day = self._parse_to_str_time(hours_in_day * self.minute)

        info = (
            ("Total: ", f"{hours_in_month}h"),
            ("Logged: ", self._parse_to_str_time(duration=logged_duration)),
            ("Left hours: ", left_hours),
            ("Left working days: ", lef_working_days),
            ("Every day: ", every_day),
            ("Rate: ", f"{rate}$"),
            ("Amount: ", f"{amount}$"),
        )
        message, sep = "", ""
        for key, value in info:
            message += sep + key + str(value)
            sep = "\n"
        print(message)


tracker_bro = TrackerBro()
