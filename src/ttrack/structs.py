from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional

from dateutil.parser import parse
from pydantic import BaseModel, Field, validator

from .config.config import Config


class TimeEntity(BaseModel):
    at: datetime | None = None
    billable: bool
    description: str = ""
    duration: int
    duronly: bool
    guid: str
    id: int = Field(alias="id")
    start: datetime | None = None
    stop: datetime | None = None
    uid: int
    wid: int

    start_str: str = ""
    issue_key: str = ""
    clean_description: str = ""

    @validator("at", "start", "stop", pre=True, always=True)
    def validator_datetime(cls, v):
        return v and parse(v).replace(second=0)

    @validator("issue_key", pre=True, always=True)
    def validator_issue_key(cls, v, values, **kwargs):
        config = Config()
        return res[0] if (res := re.findall(config.validator.issue_regex, values.get("description", ""))) else ""

    @validator("clean_description", pre=True, always=True)
    def validator_clean_description(cls, v, values, **kwargs):
        return values["description"][len(key) + 1:] if (key := values["issue_key"]) else values.get("description", "")

    @validator("start_str", pre=True, always=True)
    def validator_start_str(cls, v, values, **kwargs):
        return values["start"].strftime("%Y-%m-%dT%H:%M:00.000+0000")  # '2020-09-25T05:04:02.280+0000'


class TimeEntityDetail(BaseModel):
    description: str = ""  # "DEV-3448 Discussed the task with Vova and Kylych"
    start: Optional[datetime] = None  # "2021-01-20T13:20:39+06:00"
    end: Optional[datetime] = None  # "2021-01-20T13:50:39+06:00"
    dur: int = 0  # 1800000
    duration: int = 0
    use_stop: bool
    client: Optional[str] = ""  # "jira.clutch.co"
    project: Optional[str] = ""  # "Clutch"

    start_str: str = ""
    issue_key: str = ""
    clean_description: str = ""

    @validator("start", "end", pre=True, always=True)
    def validator_datetime(cls, v):
        # From /details api start and returns in user time (utc+6)
        return parse(v).replace(second=0) - timedelta(hours=6)

    @validator("issue_key", pre=True, always=True)
    def validator_issue_key(cls, v, values, **kwargs):
        config = Config()
        return res[0] if (res := re.findall(config.validator.issue_regex, values["description"])) else ""

    @validator("clean_description", pre=True, always=True)
    def validator_clean_description(cls, v, values, **kwargs):
        return values["description"][len(key) + 1:] if (key := values["issue_key"]) else values["description"]

    @validator("duration", pre=True, always=True)
    def validator_duration(cls, v, values, **kwargs):
        return values["dur"]

    @validator("dur", pre=True, always=True)
    def validator_dur(cls, v, values, **kwargs):
        # From /details api dur returns in milliseconds
        return v / 1000

    @validator("start_str", pre=True, always=True)
    def validator_start_str(cls, v, values, **kwargs):
        return values["start"].strftime("%Y-%m-%dT%H:%M:00.000+0000")  # '2020-09-25T05:04:02.280+0000'

    @property
    def issue_link(self) -> str:
        return f"https://{self.client}/brows/{self.issue_key}"

    def __str__(self):
        return f"{self.description} ({self.start_str})"


class JiraWorkLog(BaseModel):
    id: int
    self: str
    comment: str

    def __str__(self):
        return f"{self.comment} (# {self.id})"
