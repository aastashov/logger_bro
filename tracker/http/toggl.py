from typing import List

import requests
from pydantic import parse_obj_as

from tracker.structs import TimeEntity, TimeEntityDetail


class TogglClient:
    api_url: str = "https://api.track.toggl.com/api/v8"
    reports_url: str = "https://api.track.toggl.com/reports/api/v2/"

    def get_time_entries(self, token: str, start: str, end: str) -> List[TimeEntity]:
        auth = self._auth(token)
        resp = requests.get(url=f'{self.api_url}/time_entries?start_date={start}&end_date={end}', auth=auth)
        return parse_obj_as(List[TimeEntity], resp.json()) if resp.status_code == 200 else []

    def get_detail_time_entries(self, token: str, pid: int, start: str, end: str) -> List[TimeEntityDetail]:
        params = "workspace_id={}&since={}&until={}&user_agent={}&per_page=50".format(pid, start, end, "worklogger")
        resp = requests.get(url=f'{self.reports_url}/details?{params}', auth=self._auth(token))
        return parse_obj_as(List[TimeEntityDetail], resp.json()["data"]) if resp.status_code == 200 else []

    @staticmethod
    def _auth(token: str):
        return token, "api_token"
