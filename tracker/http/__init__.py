from .jira import JiraClient
from .toggl import TogglClient

jira_client = JiraClient()
toggl_client = TogglClient()

__all__ = [
    "jira_client",
    "toggl_client",
]
