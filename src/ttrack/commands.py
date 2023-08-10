from __future__ import annotations

from datetime import date, datetime, timedelta

import pyperclip
from workdays import networkdays

from .configs import Settings
from .resources import JiraClient, TogglClient
from .structs import TimeEntityDetail
from .utils import date_to_quote

minute = 60 * 60


def make_stand_up(toggl_client: TogglClient) -> None:
    today = date.today()
    yesterday = today - timedelta(days=1)
    time_entity = list(toggl_client.get_time_entries(start=date_to_quote(yesterday), end=date_to_quote(today)))
    stand_up = "@comedian\nYesterday\n"
    for time_entry in time_entity:
        stand_up += f" - {time_entry.clean_description}\n"
    stand_up += "Today\n - \nProblems\n - no"
    pyperclip.copy(stand_up)
    print("In clipboard!")


def create_work_logs(jira_client: JiraClient, time_entity: list[TimeEntityDetail]) -> None:
    jira_client.async_create_work_logs(time_entity)


def _round_to_zero(number) -> int:
    return int((abs(number) + number) / 2)


def _parse_to_str_time(duration: int) -> str:
    if _round_to_zero(duration) == 0:
        return "00:00:00"
    logged_hours = _round_to_zero(duration // minute)
    logged_minutes = _round_to_zero(duration % minute // 60)
    logged_seconds = _round_to_zero(duration % minute % 60)
    return ":".join(map(lambda x: str(x).zfill(2), [logged_hours, logged_minutes, logged_seconds]))


def get_report(toggl_client: TogglClient, settings: Settings, hours_in_day: int) -> str:
    first_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_date = (first_date + timedelta(days=32)).replace(day=1)
    last_date -= timedelta(seconds=1)

    start = date_to_quote(first_date)
    end = date_to_quote(last_date)

    entries = toggl_client.get_time_entries(start=start, end=end)
    logged_duration = sum((entry.duration for entry in entries))
    left_logged_seconds = settings.hours_in_month * minute - logged_duration

    # I assume that the user starts his work day after 6AM and finishes before 6PM
    today = datetime.now() + timedelta(hours=6)
    lef_working_days = networkdays(today, last_date)

    amount = round(settings.rate / minute * logged_duration, 2)

    every_day = _parse_to_str_time(left_logged_seconds / lef_working_days) if lef_working_days else "0"
    left_hours = _parse_to_str_time(duration=left_logged_seconds)

    if hours_in_day != 0:
        amount += round(settings.rate * lef_working_days * hours_in_day, 2)
        every_day = _parse_to_str_time(hours_in_day * minute)

    info = (
        ("Total: ", f"{settings.hours_in_month}h"),
        ("Logged: ", _parse_to_str_time(duration=logged_duration)),
        ("Left hours: ", left_hours),
        ("Left working days: ", lef_working_days),
        ("Every day: ", every_day),
        ("Rate: ", f"{settings.rate}$"),
        ("Amount: ", f"{amount}$"),
    )
    message, sep = "", ""
    for key, value in info:
        message += sep + key + str(value)
        sep = "\n"
    return message
