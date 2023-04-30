import enum
import re
from datetime import datetime, timedelta

from ttrack.configs import settings
from ttrack.structs import TimeEntityDetail
from ttrack.stryle import Stryle


class LogValidationError(enum.Enum):
    ISSUE_KEY = "The issue key not found. Should be like DEV-123"
    DESCRIPTION = "The description should not be empty"
    RU_DESCRIPTION = "The description should not be in russian"
    CLIENT = "The client not set. You need to set client in toggl"


def _format_log(entry: TimeEntityDetail, color: Stryle) -> str:
    duration = f"duration: {(datetime(1, 1, 1) + timedelta(seconds=entry.duration)):%H:%M}"
    start_str = f"{entry.start:%y-%m-%d %H:%M}"
    return color @ f"{start_str} | {duration} | [{entry.issue_key}] {entry.clean_description}"


def _format_error_log(entry: TimeEntityDetail, error: LogValidationError) -> str:
    return f"{_format_log(entry, Stryle.yellow)} | {Stryle.red @ error.value}"


def print_work_logs(time_entities: list[TimeEntityDetail]) -> bool:
    has_incorrect_logs = False
    for log_entity in time_entities:
        if not log_entity.issue_key:
            formatted_log = _format_error_log(log_entity, LogValidationError.ISSUE_KEY)
            has_incorrect_logs = True
        elif not log_entity.description:
            formatted_log = _format_error_log(log_entity, LogValidationError.DESCRIPTION)
            has_incorrect_logs = True
        elif re.findall(settings.ru_regex, log_entity.description):
            formatted_log = _format_error_log(log_entity, LogValidationError.RU_DESCRIPTION)
            has_incorrect_logs = True
        elif not log_entity.client:
            formatted_log = _format_error_log(log_entity, LogValidationError.CLIENT)
            has_incorrect_logs = True
        else:
            formatted_log = _format_log(log_entity, Stryle.green)

        print(formatted_log)

    if has_incorrect_logs:
        print()
        print(Stryle.red @ ("-" * 100))
        print(Stryle.red @ "You have work logs that do not conform to the logging format!")
        return False

    return True


def print_and_wait_request_to_track() -> bool:
    input_text = (
            Stryle.cyan @ "Move these logs to Jira (["
            + Stryle.green @ "y"
            + Stryle.cyan @ "/"
            + Stryle.red @ "N"
            + Stryle.cyan @ "])? "
    )
    answer = input(input_text)
    return answer.lower() in ["y", "yes"]
