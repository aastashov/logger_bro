# tracker_bro
Telegram bot for receiving reports from Toggl

So far, the CLI tool for transferring my working hours from Toggl to Jira. It can create duplicates in case you run it twice.

I will help you once if you create an issue with a suggestion or find a bug. Thanks :)

## Usages

```shell
mkvirtualenv tracker_bro --python=/Users/$HOME/.pyenv/versions/3.9.0rc1/bin/python
workon tracker_bro
pip install -r requirements.txt


cp .env.example .env
# and change .env

# Build report for current month
./manage.py --report

# Demo feature, shows how much you earn if you work 8 hours a day
./manage.py --report  --hours=8

# Build a standup based on yesterday's logs
./manage.py --standup

# It'll transfer your vorlogs to JIRA.
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
