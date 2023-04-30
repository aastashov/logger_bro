from cleo.application import Application

from .commands.init import InitCommand
from .commands.config import ConfigCommand
from .commands.report import ReportCommand
from .commands.standup import StandupCommand
from .commands.sync import SyncCommand
from .commands.version import VersionCommand


def get_application(version: str) -> Application:
    application = Application(name="ttrack", version=version)
    application.add(InitCommand())
    application.add(ConfigCommand())
    application.add(ReportCommand())
    application.add(VersionCommand())
    application.add(StandupCommand())
    application.add(SyncCommand())
    return application

