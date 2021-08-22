from configs import settings
from helpers import WorkLogger


# todo:
#  - Добавить атовризацию более чем 1 Jira Server
#  - получать Jira сервер с Toggl лога
#  - авторизация в toggl и jira
#  - проверка на ru текст
#  - проверка на issue_key в toggle


def main():
    helper = WorkLogger()
    if settings.standup:
        helper.make_stand_up()
        return

    if settings.report:
        helper.print_report(settings.hours_in_month, settings.rate, settings.hours_in_day)
        return

    print(f'Start date: {settings.start}; end date: {settings.end}')
    time_entries = helper.get_time_entries(start=settings.quote_start, end=settings.quote_end)
    for entry in time_entries:
        print(f'[{entry.issue_key}] ({entry.start_str}) duration: {entry.duration}; {entry.clean_description}')

    answer = input('Move these logs to Jira ([y/N])? ')
    yes = answer.lower() in ['y', 'yes']

    if not yes:
        print('Okay')
        return

    helper.create_work_logs(time_entries)


if __name__ == '__main__':
    main()
