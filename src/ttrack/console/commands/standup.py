from __future__ import annotations

from datetime import date, timedelta

import pyperclip

from ttrack.console.commands.command import BaseCommand
from ttrack.resources import TogglClient


class StandupCommand(BaseCommand):
    name = "standup"
    description = ""

    def handle(self) -> int:

        yesterday = date.today() - timedelta(days=1)

        toggl_token = self.config.toggl.token
        toggl_project_id = self.config.toggl.project_id
        toggl_client = TogglClient(token=toggl_token, project_id=toggl_project_id)

        time_entries = toggl_client.get_detail_time_entries(
            start=self.date_to_quote(yesterday),
            end=self.date_to_quote(yesterday),
        )
        time_entity = sorted(time_entries, key=lambda x: x.start)
        stand_up = "@Enji.ai\nYesterday\n"
        for time_entry in time_entity:
            ""
            stand_up += f" - {time_entry.clean_description} ({time_entry.issue_link})\n"

        stand_up += "Today\n - \nProblems\n - no"
        if self.io.is_verbose():
            self.line(stand_up)

        pyperclip.copy(stand_up)
        self.comment("In clipboard!")
        return 0
