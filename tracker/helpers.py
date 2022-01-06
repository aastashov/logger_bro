from datetime import date, datetime, timedelta
from typing import List

import pyperclip
from workdays import networkdays

from tracker.configs import settings
from tracker.http import jira_client, toggl_client
from tracker.structs import Client, TimeEntityDetail, Toggl, User
from tracker.utils import date_to_quote

minute = 60 * 60


def make_stand_up(user: User):
    today = date.today()
    yesterday = today - timedelta(days=1)
    time_entity = list(toggl_client.get_time_entries(
        token=user.toggl.token,
        start=date_to_quote(yesterday),
        end=date_to_quote(today),
    ))
    stand_up = '@comedian\nYesterday\n'
    for time_entry in time_entity:
        stand_up += f' - {time_entry.clean_description}\n'
    stand_up += 'Today\n - \nProblems\n - no'
    pyperclip.copy(stand_up)
    print('In clipboard!')


def create_work_logs(user: User, time_entity: List[TimeEntityDetail]):
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


def get_report(user: User, hours_in_day: int) -> str:
    first_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_date = (first_date + timedelta(days=32)).replace(day=1)
    last_date -= timedelta(seconds=1)

    start = date_to_quote(first_date)
    end = date_to_quote(last_date)

    entries = toggl_client.get_time_entries(token=user.toggl.token, start=start, end=end)
    logged_duration = sum((entry.duration for entry in entries))
    left_logged_seconds = user.total * minute - logged_duration

    # I assume that the user starts his work day after 6AM and finishes before 6PM
    today = datetime.now() + timedelta(hours=6)
    lef_working_days = networkdays(today, last_date)

    amount = round(user.rate / minute * logged_duration, 2)

    every_day = _parse_to_str_time(left_logged_seconds / lef_working_days) if lef_working_days else "0"
    left_hours = _parse_to_str_time(duration=left_logged_seconds)

    if hours_in_day != 0:
        amount += round(user.rate * lef_working_days * hours_in_day, 2)
        every_day = _parse_to_str_time(hours_in_day * minute)

    info = (
        ("Total: ", f"{user.total}h"),
        ("Logged: ", _parse_to_str_time(duration=logged_duration)),
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
