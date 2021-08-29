from telegram.ext import CommandHandler, Dispatcher, Updater

from tracker.configs import settings
from tracker.tg_bot import commands


class TgBot:
    updater: Updater
    dispatcher: Dispatcher

    def __init__(self):
        self.updater = Updater(token=settings.TG_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self._register_commands()

    def _register_commands(self):
        self.dispatcher.add_handler(CommandHandler("report", commands.report_handler))

    def run_listener(self):
        print("[run_listener] start bot")
        self.updater.start_polling()
