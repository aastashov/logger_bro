from __future__ import annotations

from ttrack.console.commands.command import BaseCommand


class VersionCommand(BaseCommand):
    name = "version"
    description = "Use this command to get version of ttrack application"

    def handle(self) -> int:
        self.line(f"ttrack version: <info>{self.application.version}</info>")
        return 0
