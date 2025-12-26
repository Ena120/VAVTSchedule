from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu_kb() -> ReplyKeyboardMarkup:
    """
    Главное меню с кнопками расписания.
    """
    builder = ReplyKeyboardBuilder()
    
    # Добавляем кнопки
    builder.button(text="📅 Сегодня")
    builder.button(text="🗓 Завтра")
    builder.button(text="🔄 Сменить группу")
    
    # Настраиваем сетку: 
    # 2 кнопки в первом ряду (Сегодня, Завтра)
    # 1 кнопка во втором ряду (Сменить группу)
    builder.adjust(2, 1)
    
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите день...")