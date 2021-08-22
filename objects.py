import re

from attr import dataclass
from dateutil.parser import parse

from configs import settings


class TimeEntries:
    def __init__(self, obj: dict):
        self.at = parse(obj['at'])
        self.billable = bool(obj['billable'])
        self.description = obj["description"]
        self.duration = int(obj['duration'])
        self.duronly = bool(obj['duronly'])
        self.guid = obj['guid']
        self.id = int(obj['id'])
        self.start = parse(obj['start'])
        self.start_str = self.start.strftime('%Y-%m-%dT%H:%M:00.000+0000')  # '2020-09-25T05:04:02.280+0000'
        self.stop = parse(obj["stop"])
        self.uid = int(obj['uid'])
        self.wid = int(obj['wid'])

        res = re.findall(settings.ISSUE_REGEX, self.description)
        self.issue_key = '' if len(res) <= 0 else res[0]

        self.clean_description = self.description[len(self.issue_key) + 1:] if self.issue_key else self.description

    def __str__(self):
        return f'{self.clean_description} (# {self.issue_key})'

    def __repr__(self):
        return f'<{self.__class__.__name__}> {self.description} {self.duration}'


@dataclass
class TimeEntriesDetail:
    id: str  # 1848112923
    pid: str  # 157879391
    uid: str  # 4435751
    description: str  # " DEV-3448 Discussed the task with Vova and Kylych"
    start: str  # "2021-01-20T13:20:39+06:00"
    end: str  # "2021-01-20T13:50:39+06:00"
    updated: str  # "2021-01-21T15:45:19+06:00"
    dur: str  # 1800000
    user: str  # "Alexander Astashov Vl"
    client: str  # "jira.clutch.co"
    project: str  # "Clutch"

    @classmethod
    def from_api(cls, data: dict) -> "TimeEntriesDetail":
        return cls(
            id=data["id"],
            pid=data["pid"],
            uid=data["uid"],
            description=data["description"],
            start=data["start"],
            end=data["end"],
            updated=data["updated"],
            dur=data["dur"],
            user=data["user"],
            client=data["client"],
            project=data["project"],
        )


class JiraWorkLog:
    """
    Example response:
    {
        'self': 'https://jira.clutch.co/rest/api/2/issue/11672/worklog/18028',
        'author': {
            'self': 'https://jira.clutch.co/rest/api/2/user?username=aastashov',
            'name': 'aastashov',
            'key': 'aastashov',
            'emailAddress': 'alexander.astashov.vl@gmail.com',
            'avatarUrls': {
                '48x48': 'https://jira.clutch.co/secure/useravatar?ownerId=aastashov&avatarId=10904',
                '24x24': 'https://jira.clutch.co/secure/useravatar?size=small&ownerId=aastashov&avatarId=10904',
                '16x16': 'https://jira.clutch.co/secure/useravatar?size=xsmall&ownerId=aastashov&avatarId=10904',
                '32x32': 'https://jira.clutch.co/secure/useravatar?size=medium&ownerId=aastashov&avatarId=10904',
            },
            'displayName': 'Aleksandr Astashov',
            'active': True,
            'timeZone': 'Asia/Bishkek',
        },
        'updateAuthor': {
            'self': 'https://jira.clutch.co/rest/api/2/user?username=aastashov',
            'name': 'aastashov',
            'key': 'aastashov',
            'emailAddress': 'alexander.astashov.vl@gmail.com',
            'avatarUrls': {
                '48x48': 'https://jira.clutch.co/secure/useravatar?ownerId=aastashov&avatarId=10904',
                '24x24': 'https://jira.clutch.co/secure/useravatar?size=small&ownerId=aastashov&avatarId=10904',
                '16x16': 'https://jira.clutch.co/secure/useravatar?size=xsmall&ownerId=aastashov&avatarId=10904',
                '32x32': 'https://jira.clutch.co/secure/useravatar?size=medium&ownerId=aastashov&avatarId=10904',
            },
            'displayName': 'Aleksandr Astashov',
            'active': True,
            'timeZone': 'Asia/Bishkek',
        },
        'comment': 'TRAC-28 Team Sync (retrospective)',
        'created': '2020-09-25T00:29:55.197-0700',
        'updated': '2020-09-25T00:29:55.197-0700',
        'started': '2020-09-01T23:00:40.000-0700',
        'timeSpent': '1h',
        'timeSpentSeconds': 3600,
        'id': '18028',
        'issueId': '11672',
    }
    """

    def __init__(self, wl: dict):
        self.id = wl.get('id')
        self.url = wl.get('self')
        self.comment = wl.get('comment')

    def __str__(self):
        return f'{self.comment} (# {self.id})'

    def __repr__(self):
        return self.__str__()


class ToggleUser:
    def __init__(self, me: dict):
        pass


class JiraUser:
    def __init__(self, me: dict):
        pass
