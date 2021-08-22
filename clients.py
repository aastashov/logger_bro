import base64
from typing import List, Union

import requests

from configs import settings
from objects import JiraUser, JiraWorkLog, TimeEntries, ToggleUser


class TogglClient:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(settings. TOGGL_TOKEN).decode()}',
    }

    def get_me(self) -> Union[None, ToggleUser]:
        resp = requests.get(f'{settings.TOGGL_URL}/me', headers=self.headers)
        if resp.status_code != 200:
            print(f'[toggl.get_me] status_code: {resp.status_code}; context: {resp.content}')
            return None
        return ToggleUser(resp.json())

    def get_time_entries(self, start: str, end: str) -> List[TimeEntries]:
        resp = requests.get(
            url=f'{settings.TOGGL_URL}/time_entries?start_date={start}&end_date={end}',
            headers=self.headers,
        )
        return [TimeEntries(entry) for entry in resp.json()] if resp.status_code == 200 else []

    def get_detail_time_entries(self, start: str, end: str) -> List[TimeEntries]:
        base_url = 'https://api.track.toggl.com/reports/api/v2/details?workspace_id={}&since={}&until={}&user_agent={}'
        resp = requests.get(
            url=base_url.format(settings.TOGGL_PROJECT_ID, start, end, 'worklogger'),
            headers=self.headers,
        )
        return [TimeEntries(entry) for entry in resp.json()["data"]] if resp.status_code == 200 else []


class JiraClient:
    """
    API doc
    https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-worklogs/
    """
    session_url = f'{settings.JIRA_URL}/rest/auth/1/session'
    issue_url = f'{settings.JIRA_URL}/rest/api/2/issue'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def __init__(self):
        self.auth()

    def auth(self) -> bool:
        resp = requests.post(f'{self.session_url}', json={
            'username': settings.JIRA_USER,
            'password': settings.JIRA_PASS,
        })
        if resp.status_code != 200:
            print(resp.status_code, resp.content)
            return False
        session = resp.json()['session']

        # todo: save authentication
        self.headers['Cookie'] = f'{session["name"]}={session["value"]}'
        return True

    def get_me(self) -> Union[None, JiraUser]:
        resp = requests.get(f'{self.session_url}/rest/auth/1/session', headers=self.headers)
        if resp.status_code != 200:
            print(f'[jira.get_me] status_code: {resp.status_code}; context: {resp.content}')
            return None
        return JiraUser(resp.json())

    def create_work_log(self, time_entry: TimeEntries) -> Union[None, JiraWorkLog]:
        if time_entry.issue_key == '':
            print('[jira.create_work_log] issue_key not found', time_entry)
            return None

        target = f'{self.issue_url}/{time_entry.issue_key}/worklog?adjustEstimate=AUTO'
        resp = requests.post(target, headers=self.headers, json={
            'timeSpentSeconds': time_entry.duration,
            'comment': time_entry.clean_description,
            'started': time_entry.start_str,
        })

        if resp.status_code != 201:
            print(f'[jira.create_work_log] status_code: {resp.status_code}; context: {resp.content}')
            return None
        return JiraWorkLog(resp.json())
