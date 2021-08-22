from typing import List

import requests
from pydantic import parse_obj_as

from tracker.configs import settings
from tracker.structs import TimeEntity, TimeEntityDetail


class TogglClient:
    auth = (settings.TOGGL_TOKEN, "api_token")

    def get_time_entries(self, start: str, end: str) -> List[TimeEntity]:
        resp = requests.get(url=f'{settings.TOGGL_URL}/time_entries?start_date={start}&end_date={end}', auth=self.auth)
        return parse_obj_as(List[TimeEntity], resp.json()) if resp.status_code == 200 else []

    def get_detail_time_entries(self, start: str, end: str) -> List[TimeEntityDetail]:
        params = "workspace_id={}&since={}&until={}&user_agent={}&per_page=50".format(
            settings.TOGGL_PROJECT_ID,
            start,
            end,
            "worklogger",
        )
        resp = requests.get(url=f'https://api.track.toggl.com/reports/api/v2/details?{params}', auth=self.auth)
        return parse_obj_as(List[TimeEntityDetail], resp.json()["data"]) if resp.status_code == 200 else []
