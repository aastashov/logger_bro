from aiogram import types

from tracker.db import storage
from tracker.helpers import tracker_bro


async def report_handler(event: types.Message):
    user = storage.get_or_create_user(tid=event.from_user.id)
    if user.toggl is None:
        return await event.answer("Ты не авторизован в Toggl. Прости, регистрация еще в разработке :(")

    report = tracker_bro.get_report(user, 0)
    return await event.answer(report)
