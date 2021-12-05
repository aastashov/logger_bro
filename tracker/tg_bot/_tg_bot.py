import dataclasses

from aiogram import Bot, Dispatcher

from tracker.tg_bot import commands


@dataclasses.dataclass
class TrackerBro:
    bot: Bot
    dispatcher: Dispatcher

    def __post_init__(self):
        self._register_commands()

    def _register_commands(self):
        self.dispatcher.register_message_handler(commands.report_handler, commands={"report"})

    async def run_listener(self):
        print("[run_listener] start bot")
        try:
            await self.dispatcher.start_polling()
        finally:
            await self.dispatcher.stop_polling()
