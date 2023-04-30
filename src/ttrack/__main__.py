#!/usr/bin/env python3
import logging
import os
import sys

from .__version__ import __version__
from .configs import settings
from .console.application import get_application
from .resources import JiraClient, TogglClient
from .services import print_and_wait_request_to_track, print_work_logs
from .stryle import Stryle

logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(filename)s::%(lineno)s | %(message)s",
    level=logging.INFO,
)


def main() -> int:
    # app = get_application(__version__)
    # return app.run()

    toggl_client = TogglClient(token=settings.toggl.token, project_id=settings.toggl.project_id)
    jira_client = JiraClient(jira_clients=settings.jira_clients)

    print(Stryle.cyan @ f"Start date: {settings.start}; end date: {settings.end}")
    time_entities = toggl_client.get_detail_time_entries(
        start=settings.quote_start,
        end=settings.quote_end,
    )

    has_incorrect_logs = not print_work_logs(time_entities)
    if has_incorrect_logs:
        return 1

    yes = print_and_wait_request_to_track()
    if not yes:
        return 0

    jira_client.async_create_work_logs(time_entities)
    return 0


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_path, "tracker"))
    sys.exit(main())
