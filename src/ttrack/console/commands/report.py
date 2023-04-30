from __future__ import annotations

from datetime import datetime, timedelta

from workdays import networkdays

from ttrack.console.commands.command import BaseCommand
from ttrack.resources import TogglClient


def _round_to_zero(number) -> int:
    return int((abs(number) + number) / 2)


class ReportCommand(BaseCommand):
    name = "report"
    description = "Use this command to get your toggl report"
    minute = 60 * 60

    def _parse_to_str_time(self, duration: int) -> str:
        if _round_to_zero(duration) == 0:
            return "00:00:00"
        logged_hours = _round_to_zero(duration // self.minute)
        logged_minutes = _round_to_zero(duration % self.minute // 60)
        logged_seconds = _round_to_zero(duration % self.minute % 60)
        return ":".join(map(lambda x: str(x).zfill(2), [logged_hours, logged_minutes, logged_seconds]))

    def handle(self) -> int:
        first_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_date = (first_date + timedelta(days=32)).replace(day=1)
        last_date -= timedelta(seconds=1)

        start = self.date_to_quote(first_date)
        end = self.date_to_quote(last_date)

        toggl_token = self.config.get("toggl.token")
        toggl_project_id = self.config.get("toggl.project_id")
        toggl_client = TogglClient(token=toggl_token, project_id=toggl_project_id)

        # TODO: Need to change to get_detail_time_entries and check
        entries = toggl_client.get_time_entries(start=start, end=end)
        logged_duration = sum((entry.duration for entry in entries if entry.stop))

        hours_in_month = self.config.get("report.hours_in_month")
        left_logged_seconds = hours_in_month * self.minute - logged_duration

        # I assume that the user starts his work day after 6AM and finishes before 6PM
        today = datetime.now() + timedelta(hours=6)
        lef_working_days = networkdays(today, last_date)

        rate = self.config.get("report.rate")
        amount = round(rate / self.minute * logged_duration, 2)

        every_day = self._parse_to_str_time(left_logged_seconds / lef_working_days) if lef_working_days else "0"
        left_hours = self._parse_to_str_time(duration=left_logged_seconds)

        # TODO: Need to implement
        # if hours_in_day != 0:
        #     amount += round(settings.rate * lef_working_days * hours_in_day, 2)
        #     every_day = _parse_to_str_time(hours_in_day * minute)

        self.line(f"<comment>Total:</comment> {hours_in_month}h")
        self.line(f"<comment>Logged:</comment> {self._parse_to_str_time(duration=logged_duration)}")
        self.line(f"<comment>Left hours:</comment> {left_hours}")

        self.line(f"<comment>Left working days:</comment> {lef_working_days}")
        self.line(f"<comment>Every day:</comment> {every_day}")
        self.line(f"<comment>Rate:</comment> {rate}$")
        self.line(f"<comment>Amount:</comment> {amount}$")
        return 0
