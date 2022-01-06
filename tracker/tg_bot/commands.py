from typing import TYPE_CHECKING

from tracker.db import constants, storage
from tracker.helpers import get_report

if TYPE_CHECKING:  # pragma: no cover
    from aiogram import types


async def report_handler(event: "types.Message"):
    user, _ = await storage.get_or_create_user(tid=event.from_user.id)
    if user.toggl is None:
        return await event.answer("Ты не авторизован в Toggl. Прости, регистрация еще в разработке :(")

    report = get_report(user, 0)
    return await event.answer(report)


async def start(event: "types.Message"):
    # todo: кажется клиент не получает новые данные из базы, когда добавляю их через idea
    user, _ = await storage.get_or_create_user(tid=event.from_user.id)
    if user.toggl is None:
        await event.answer("Для начала пройди регистрацию. Отправь токен для получения часов из Toggl")
        # await storage.create_last_message(user, constants.last_message_wait_token)
    await event.answer("Oookay")
