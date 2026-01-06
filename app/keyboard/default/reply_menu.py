from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_reply_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    # Единственная кнопка, которая вызывает интерфейс
    builder.button(text="📋 Меню")
    return builder.as_markup(resize_keyboard=True)