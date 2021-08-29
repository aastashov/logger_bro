from tracker.configs import settings
from tracker.helpers import cli_user, tracker_bro
from tracker.http import toggl_client
from tracker.tg_bot.tg_bot import TgBot


def execute_from_command_line():
    if settings.runbot:
        TgBot().run_listener()
        return

    if settings.standup:
        tracker_bro.make_stand_up(cli_user)
        return

    if settings.report:
        report = tracker_bro.get_report(cli_user, settings.hours_in_day)
        print(report)
        return

    print(f"Start date: {settings.start}; end date: {settings.end}")
    # time_entity = toggl_client.get_time_entries(
    #     token=cli_user.toggl.token,
    #     start=settings.quote_start,
    #     end=settings.quote_end,
    # )
    time_entity = toggl_client.get_detail_time_entries(
        token=cli_user.toggl.token,
        pid=cli_user.toggl.project_id,
        start=settings.quote_start,
        end=settings.quote_end,
    )
    for entry in time_entity:
        print(f"[{entry.issue_key}] ({entry.start_str}) duration: {entry.duration}; {entry.clean_description}")

    answer = input('Move these logs to Jira ([y/N])? ')
    yes = answer.lower() in ["y", "yes"]

    if not yes:
        print("Okay")
        return

    tracker_bro.create_work_logs(cli_user, time_entity)
