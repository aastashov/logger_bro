import asyncio
import base64
from typing import TYPE_CHECKING

import aiohttp
import requests
from pydantic import parse_obj_as

from tracker.configs import settings
from tracker.structs import JiraWorkLog, TimeEntityDetail

if TYPE_CHECKING:  # pragma: no cover
    from typing import List, Optional


class JiraClient:
    """
    API doc
    https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-worklogs/
    """
    session_url = "{}/rest/auth/1/session"
    issue_url = "{}/rest/api/2/issue/{}/worklog?adjustEstimate=AUTO"

    def __init__(self):
        self._domains = {
            settings.JIRA_URL_1: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            settings.JIRA_URL_2: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        }
        self.auth_by_token(settings.JIRA_URL_2)
        self.auth_by_pass(settings.JIRA_URL_1)

    def auth_by_pass(self, domain) -> bool:
        resp = requests.post(self.session_url.format(domain), json={
            "username": settings.JIRA_USER_1,
            "password": settings.JIRA_PASS_1,
        })
        if resp.status_code != 200:
            print(resp.status_code, resp.content)
            return False
        session = resp.json()["session"]

        # todo: save authentication
        self._domains[domain]['Cookie'] = f'{session["name"]}={session["value"]}'
        return True

    def auth_by_token(self, domain) -> bool:
        u = f"{settings.JIRA_USER_2}:{settings.JIRA_TOKEN_2}".encode()
        self._domains[domain]["Authorization"] = f"Basic {base64.b64encode(u).decode()}"
        return True

    async def _create_work_log(
            self,
            session: "aiohttp.ClientSession",
            time_entry: "TimeEntityDetail",
    ) -> "Optional[JiraWorkLog]":
        if time_entry.issue_key == "":
            print("[jira.create_work_log] issue_key not found in entry %s.", time_entry)
            return None

        if time_entry.client in settings.JIRA_URL_1:
            domain, headers = settings.JIRA_URL_1, self._domains[settings.JIRA_URL_1]
        elif time_entry.client in settings.JIRA_URL_2:
            domain, headers = settings.JIRA_URL_2, self._domains[settings.JIRA_URL_2]
        else:
            print("[jira.create_work_log] client %s not found.", time_entry.client)
            return None

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

    async def _async_create_work_logs(self, time_entries: "List[TimeEntityDetail]"):
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(self._create_work_log(session, i)) for i in time_entries]
            result = await asyncio.gather(*tasks)
        return result

    def async_create_work_logs(self, time_entries: "List[TimeEntityDetail]"):
        asyncio.run(self._async_create_work_logs(time_entries))
