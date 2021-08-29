from telegram import Update
from telegram.ext import CallbackContext

from tracker.db import storage
from tracker.helpers import tracker_bro


def report_handler(update: Update, context: CallbackContext):
    user = storage.get_or_create_user(tid=update.effective_chat.id)
    if user.toggl is None:
        context.bot.send_message(
            chat_id=user.tid,
            text="Ты не авторизован в Toggl. Прости, регистрация еще в разработке :(",
        )
        return

    report = tracker_bro.get_report(user, 0)
    context.bot.send_message(chat_id=user.tid, text=report)
