from __future__ import annotations

from typing import Self, TYPE_CHECKING

from ttrack.config.config import config_map
from ttrack.console.commands.command import BaseConfigCommand
from ttrack.constance import CONFIG_FILE_PATH

if TYPE_CHECKING:
    from typing import Any
    from ttrack.config.types import Validator


class InitCommand(BaseConfigCommand):
    name = "init"
    description = "A command to instantiate the tracker. This will help you set up the tracker."

    default_try_again = 3

    def define_config(self: Self, config_name: str, status_of_property_definition: dict[str, tuple[Any, bool]]):
        for property_path, (value, is_default) in status_of_property_definition.items():
            if not property_path.startswith(config_name):
                continue

            property_config_name, property_name = property_path.split(".")
            question_text = config_map[property_config_name][property_name]["question"]
            validator = config_map[property_config_name][property_name]["validator"]

            question_text = f"[<fg=blue>{property_path}</>] - {question_text}"
            if is_default:
                question_text = f"{question_text} <comment>[{value}]</comment>"

            property_value = self.define_property(question_text, value, is_default, validator)
            if property_value is None:
                continue

            self.config.set(property_path, property_value)

    def define_property(
        self: Self, question_text: str, value: Any, is_default: bool, validate_answer: Validator
    ) -> Any:
        try_again_count = self.default_try_again

        while try_again_count >= 0:
            question = self.create_question(question_text, **({"default": value} if is_default else {}))
            answer = str(self.ask(question))
            if answer.lower() == "n":
                break

            answer = validate_answer(answer)
            if answer is None:
                try_again_count -= 1
                self.line("Try again.")
                continue

            return answer
        return None

    def handle(self: Self) -> int:
        if CONFIG_FILE_PATH.exists():
            self.line(
                "The config for your <info>ttrack</info> are already defined."
                " Use `<fg=yellow>ttrack config</>` to change them.",
            )
            return 0

        self.line("Hi. We're going to set up your <info>ttrack</info> now.")
        self.line("\nYou need the following config to use <info>ttrack</info>:")

        status_of_config = self.config.status_of_config
        self.display_config_list(status_of_config)

        self.define_config("toggl", status_of_config)

        jira_definition_question = self.create_question(
            "Do you want to set up a Jira client to synchronize work logs?",
            type="confirmation",
        )
        if self.ask(jira_definition_question) is True:
            self.define_config("jira_client", status_of_config)

        hours_in_month = self.config.report.hours_in_month
        if hours_in_month == self.config.get_default_for_config_key("report.hours_in_month"):
            hours_in_month_question = self.create_question(
                f"report.hours_in_month <comment>[{hours_in_month}]</comment>",
                default=hours_in_month,
            )
            hours_in_month_answer = str(self.ask(hours_in_month_question))
            if hours_in_month_answer.isdigit():
                self.config.set("report.hours_in_month", int(hours_in_month_answer))

        rate = self.config.report.rate
        if rate == self.config.get_default_for_config_key("report.rate"):
            rate_question = self.create_question(
                f"report.rate <comment>[{rate}]</comment>",
                default=rate,
            )
            rate_answer = str(self.ask(rate_question))
            if rate_answer.isdigit():
                self.config.set("report.rate", int(rate_answer))

        # self.define_config(status_of_property_definition["report"], "report")
        # self.config.save()
        return 0
