import asyncio

from aiogram import Bot, Dispatcher

from ._tg_bot import TrackerBro
from ..configs import settings


def start_bot():
    bot = Bot(token=settings.TG_TOKEN)
    dispatcher = Dispatcher(bot=bot)
    tracker_bro_bot = TrackerBro(bot=bot, dp=dispatcher)
    asyncio.run(tracker_bro_bot.run_listener())


__all__ = [
    "start_bot",
]
