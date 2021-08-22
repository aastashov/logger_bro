from tracker.configs import settings
from tracker.helpers import tracker_bro


def execute_from_command_line():
    if settings.standup:
        tracker_bro.make_stand_up()
        return

    if settings.report:
        tracker_bro.print_report(settings.HOURS_IN_MONTH, settings.RATE, settings.hours_in_day)
        return

    print(f"Start date: {settings.start}; end date: {settings.end}")
    # time_entity = tracker_bro.get_time_entries(start=settings.quote_start, end=settings.quote_end)
    time_entity = tracker_bro.get_detail_time_entries(start=settings.quote_start, end=settings.quote_end)
    for entry in time_entity:
        print(f"[{entry.issue_key}] ({entry.start_str}) duration: {entry.duration}; {entry.clean_description}")

    answer = input('Move these logs to Jira ([y/N])? ')
    yes = answer.lower() in ["y", "yes"]

    if not yes:
        print("Okay")
        return

    tracker_bro.create_work_logs(time_entity)
