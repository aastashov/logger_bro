import logging

from tracker.configs import settings
from tracker.helpers import cli_user, create_work_logs, get_report, make_stand_up
from tracker.http import toggl_client
from tracker.tg_bot import start_bot

logging.basicConfig(
    format=u'%(levelname)s [%(asctime)s] %(filename)s::%(lineno)s | %(message)s',
    level=logging.DEBUG,
)


def execute_from_command_line():
    if settings.runbot:
        start_bot()
        return

    if settings.standup:
        make_stand_up(cli_user)
        return

    if settings.report:
        report = get_report(cli_user, settings.hours_in_day)
        print(report)
        return

    print(f"Start date: {settings.start}; end date: {settings.end}")
    time_entity = toggl_client.get_detail_time_entries(
        token=cli_user.toggl.token,
        pid=cli_user.toggl.project_id,
        start=settings.quote_start,
        end=settings.quote_end,
    )
    for entry in time_entity:
        print(f"[{entry.issue_key}] ({entry.start_str}) duration: {entry.duration}; {entry.clean_description}")

    answer = input("Move these logs to Jira ([y/N])? ")
    yes = answer.lower() in ["y", "yes"]

    if not yes:
        print("Okay")
        return

    create_work_logs(cli_user, time_entity)
