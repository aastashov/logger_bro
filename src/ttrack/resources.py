from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass, field
from typing import List

import aiohttp
import requests
from pydantic import parse_obj_as

from .configs import Jira, settings
from .structs import JiraWorkLog, TimeEntity, TimeEntityDetail


@dataclass
class JiraClient:
    """
    API doc
    https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-worklogs/
    """

    jira_clients: list[Jira]
    _domains: dict = field(default_factory=dict)

    session_url = "{}/rest/auth/1/session"
    issue_url = "{}/rest/api/2/issue/{}/worklog?adjustEstimate=AUTO"

    def __post_init__(self):
        for client in self.jira_clients:
            if client.password:
                self.auth_by_pass(client)
            elif client.token:
                self.auth_by_token(client)

    def auth_by_pass(self, client: Jira) -> None:
        url = self.session_url.format(client.url)
        resp = requests.post(url, json={"username": client.username, "password": client.password})
        if resp.status_code != 200:
            print(resp.status_code, resp.content)
            return

        session = resp.json()["session"]
        self._domains[client.url] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": f'{session["name"]}={session["value"]}',
        }

    def auth_by_token(self, client: Jira) -> None:
        u = f"{client.username}:{client.token}".encode()
        self._domains[client.url] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(u).decode()}",
        }

    async def _create_work_log(
        self,
        session: aiohttp.ClientSession,
        time_entry: TimeEntityDetail,
    ) -> JiraWorkLog | None:
        if time_entry.issue_key == "":
            print("[jira.create_work_log] issue_key not found in entry %s.", time_entry)
            return None

        if not time_entry.client:
            print("[jira.create_work_log] client not found in entry %s.", time_entry)
            return None

        domain, headers = "", {}
        for client in settings.jira_clients:
            if time_entry.client in client.url:
                domain, headers = client.url, self._domains[client.url]

        if not domain or not headers:
            raise ValueError(f"Can't find the client for {time_entry.client}")

        target = self.issue_url.format(domain, time_entry.issue_key)
        _json = {
            "timeSpentSeconds": time_entry.duration,
            "comment": time_entry.clean_description,
            "started": time_entry.start_str,
        }
        async with session.post(url=target, headers=headers, json=_json) as resp:
            work_log = await resp.json()
            jira_log = parse_obj_as(JiraWorkLog, work_log)
            print(f'{bool(jira_log)} for log "{time_entry}"')
        return jira_log

    async def _async_create_work_logs(self, time_entries: list[TimeEntityDetail]):
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(self._create_work_log(session, i)) for i in time_entries]
            result = await asyncio.gather(*tasks)
        return result

    def async_create_work_logs(self, time_entries: list[TimeEntityDetail]):
        asyncio.run(self._async_create_work_logs(time_entries))


@dataclass
class TogglClient:
    token: str
    project_id: int

    api_url: str = "https://api.track.toggl.com/api/v8"
    reports_url: str = "https://api.track.toggl.com/reports/api/v2/"

    def get_time_entries(self, start: str, end: str) -> list[TimeEntity]:
        resp = requests.get(url=f"{self.api_url}/time_entries?start_date={start}&end_date={end}", auth=self._auth)
        return parse_obj_as(List[TimeEntity], resp.json()) if resp.status_code == 200 else []

    def get_detail_time_entries(self, start: str, end: str, user_agent: str = "worklogger") -> list[TimeEntityDetail]:
        params = f"workspace_id={self.project_id}&since={start}&until={end}&user_agent={user_agent}&per_page=50"
        resp = requests.get(url=f"{self.reports_url}/details?{params}", auth=self._auth)
        return parse_obj_as(List[TimeEntityDetail], resp.json()["data"]) if resp.status_code == 200 else []

    @property
    def _auth(self) -> tuple[str, str]:
        return self.token, "api_token"
