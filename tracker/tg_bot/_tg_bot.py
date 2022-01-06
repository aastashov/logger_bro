import dataclasses
from functools import wraps

from aiogram import Bot, Dispatcher

from tracker.tg_bot import callbacks, commands


@dataclasses.dataclass
class TrackerBro:
    bot: Bot
    dp: Dispatcher

    def __post_init__(self):
        self._register_commands()

    def _register_commands(self):
        self.dp.register_message_handler(commands.report_handler, commands={"report"})
        self.dp.register_message_handler(commands.start, commands={"start"})

        self._register_callback(callbacks.process_callback_button1, "button1")
        self._register_callback(callbacks.process_callback_button2, "button2")

    def _register_callback(self, callback, button: str):
        self.dp.register_callback_query_handler(self._embed_bot(callback), lambda c: c.data == button)

    def _embed_bot(self, func):
        @wraps(func)
        def wrap(*args, **kwargs):
            return func(self.bot, *args, **kwargs)

        return wrap

    async def run_listener(self):
        print("[run_listener] start bot")
        try:
            await self.dp.start_polling()
        finally:
            await self.dp.stop_polling()
