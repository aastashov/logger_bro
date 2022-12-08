#!/usr/bin/env python3
import logging
import os
import sys

from .__version__ import __version__
from .commands import create_work_logs, get_report, make_stand_up
from .configs import settings
from .resources import JiraClient, TogglClient

logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(filename)s::%(lineno)s | %(message)s",
    level=logging.INFO,
)


def main() -> int:
    if settings.version:
        print(f"ttrack version {__version__}")
        return 0

    toggl_client = TogglClient(token=settings.toggl.token, project_id=settings.toggl.project_id)

    if settings.standup:
        make_stand_up(toggl_client)
        return 0

    if settings.report:
        report = get_report(toggl_client, settings, settings.hours_in_day)
        print(report)
        return 0

    jira_client = JiraClient(jira_clients=settings.jira_clients)

    print(f"Start date: {settings.start}; end date: {settings.end}")
    time_entity = toggl_client.get_detail_time_entries(
        start=settings.quote_start,
        end=settings.quote_end,
    )
    for entry in time_entity:
        print(f"[{entry.issue_key}] ({entry.start_str}) duration: {entry.duration}; {entry.clean_description}")

    answer = input("Move these logs to Jira ([y/N])? ")
    yes = answer.lower() in ["y", "yes"]

    if not yes:
        print("Okay")
        return 0

    create_work_logs(jira_client, time_entity)
    return 0


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_path, "tracker"))
    sys.exit(main())
