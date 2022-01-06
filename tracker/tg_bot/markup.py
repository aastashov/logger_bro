from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_reply_markup():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("Привет!", callback_data="button1"),
        InlineKeyboardButton("Привет 2!", callback_data="button2"),
    )
