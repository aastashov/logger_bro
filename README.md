# tracker_bro
Telegram bot for receiving reports from Toggl

So far, the CLI tool for transferring my working hours from Toggl to Jira. It can create duplicates in case you run it twice.

I will help you once if you create an issue with a suggestion or find a bug. Thanks :)

## Usages
For starters, you need to get in the habit of keeping tracker_bro vorlogs in a usable state. He needs to know
 which URL to send logs to and to which task. Here is an example of how to do it:

![worklog example](docs/example_worklog.png)

Here is the *DEV-123* task number and the server address *test.jira.com* that can be configured in the *clients*.

```shell
mkvirtualenv tracker_bro --python=python3.9
workon tracker_bro
pip install -r requirements.txt


cp .env.example .env
# and change .env

# Build report for current month
./manage.py --report

# Demo feature, shows how much you earn if you work 8 hours a day
./manage.py --report  --hours=8

# Build a stand-up based on yesterday's logs
./manage.py --standup

# It'll transfer your work logs to JIRA.
./manage.py --start=2021-08-09 --end=2021-08-15
```


## TODO:
- Add Telegram bot ...
- Save Cookie after login by password
- Починить стендап за пятницу
- Добавить что-то типа pipenv
- Добавить tox
- Добавить тесты + больше документации
- Проверка на ru текст
- Проверка на issue_key в toggle
