from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    builder.button(text="📅 Сегодня")
    builder.button(text="🗓 Завтра")
    builder.button(text="📅 На неделю")
    builder.button(text="📂 Файл PDF") # Новая кнопка
    builder.button(text="🔄 Сменить группу")
    
    # Сетка: 
    # 2 кнопки (Сегодня, Завтра)
    # 2 кнопки (На неделю, Файл)
    # 1 кнопка (Сменить группу)
    builder.adjust(2, 2, 1)
    
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите действие...")