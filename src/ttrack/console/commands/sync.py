from __future__ import annotations

import enum
import re
from datetime import datetime, timedelta

from cleo.helpers import argument

from ttrack.console.commands.command import BaseCommand
from ttrack.resources import JiraClient, TogglClient
from ttrack.structs import TimeEntityDetail


class LogValidationError(enum.Enum):
    ISSUE_KEY = "The issue key not found. Should be like DEV-123"
    DESCRIPTION = "The description should not be empty"
    RU_DESCRIPTION = "The description should not be in russian"
    CLIENT = "The client not set. You need to set client in toggl"


class SyncCommand(BaseCommand):
    name = "sync"
    description = ""

    arguments = [
        argument("start", "Start day.", optional=False),
        argument("end", "End date.", optional=False),
    ]

    def _format_log(self, entry: TimeEntityDetail, color: str) -> str:
        duration = f"duration: {(datetime(1, 1, 1) + timedelta(seconds=entry.duration)):%H:%M}"
        start_str = f"{entry.start:%y-%m-%d %H:%M}"
        return f"<fg={color}>{start_str} | {duration} | [{entry.issue_key}] {entry.clean_description}</>"

    def _format_error_log(self, entry: TimeEntityDetail, error: LogValidationError) -> str:
        worklog_message = self._format_log(entry, "yellow")
        return f"{worklog_message} | <fg=red>{error.value}</>"

    def print_work_logs(self, time_entities: list[TimeEntityDetail]) -> bool:
        has_incorrect_logs = False
        for log_entity in time_entities:
            if not log_entity.issue_key:
                formatted_log = self._format_error_log(log_entity, LogValidationError.ISSUE_KEY)
                has_incorrect_logs = True
            elif not log_entity.clean_description:
                formatted_log = self._format_error_log(log_entity, LogValidationError.DESCRIPTION)
                has_incorrect_logs = True
            elif re.findall(self.config.validator.ru_text_regex, log_entity.description):
                formatted_log = self._format_error_log(log_entity, LogValidationError.RU_DESCRIPTION)
                has_incorrect_logs = True
            elif not log_entity.client:
                formatted_log = self._format_error_log(log_entity, LogValidationError.CLIENT)
                has_incorrect_logs = True
            else:
                formatted_log = self._format_log(log_entity, "green")

            self.line(formatted_log)

        if has_incorrect_logs:
            error_message = "You have work logs that do not conform to the logging format!"
            self.line("-" * len(error_message), "error")
            self.line_error(error_message, "error")
            return False

        return True

    def handle(self) -> int:
        toggl_token = self.config.toggl.token
        toggl_project_id = self.config.toggl.project_id
        toggl_client = TogglClient(token=toggl_token, project_id=toggl_project_id)

        jira_clients = self.config.jira
        jira_client = JiraClient(jira_clients=jira_clients)

        start_day = self.argument("start")
        end_day = self.argument("end")
        # TODO: Need to add validator for start_day and end_day

        self.info(f"Start date: {start_day}; end date: {end_day}")
        time_entities = toggl_client.get_detail_time_entries(start=start_day, end=end_day)

        has_incorrect_logs = not self.print_work_logs(time_entities)
        if has_incorrect_logs:
            return 1

        question = self.create_question("Move these logs to Jira? <comment>(No)</comment>")
        answer = str(self.ask(question)).lower()
        if answer in {"y", "yes"}:
            self.line("Start")
            jira_client.async_create_work_logs(time_entities)
            return 0

        return 0
