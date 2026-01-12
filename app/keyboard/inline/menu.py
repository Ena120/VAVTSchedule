from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def main_menu_inline(user_info: dict) -> InlineKeyboardMarkup:
    """Главный экран бота (Дашборд)"""
    kb = InlineKeyboardBuilder()
    
    # 1 ряд: Управление днями
    kb.button(text="📅 Сегодня", callback_data="sch_today")
    kb.button(text="🗓 Завтра", callback_data="sch_tomorrow")
    
    # 2 ряд: Доп. функции
    kb.button(text="📆 Вся неделя", callback_data="sch_week")
    kb.button(text="📂 Файл PDF", callback_data="sch_pdf")
    
    # 3 ряд: Внешние ссылки и сервисы
    kb.button(text="↗️ ЛК ВАВТ", url="https://lk.vavt.ru/")
    kb.button(text="🆘 Поддержка", callback_data="support_open")
    
    # 4 ряд: Настройки
    kb.button(text="⚙️ Настройки", callback_data="settings_menu")
    
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()

def settings_kb() -> InlineKeyboardMarkup:
    """Экран настроек"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Сменить группу", callback_data="reselect_group")
    kb.button(text="🔙 Назад в меню", callback_data="nav_main_menu")
    kb.adjust(1)
    return kb.as_markup()

def schedule_nav_kb(current_offset: int) -> InlineKeyboardMarkup:
  
    kb = InlineKeyboardBuilder()
    
    # Добавляем кнопки по порядку
    # 1. Кнопка Вчера (Слева)
    kb.button(text="⬅️ Вчера", callback_data=f"sch_day_{current_offset - 1}")
    
    # 2. Кнопка Завтра (Справа)
    kb.button(text="Завтра ➡️", callback_data=f"sch_day_{current_offset + 1}")
    
    # 3. Кнопка Меню (Снизу)
    kb.button(text="🔙 Назад в меню", callback_data="nav_main_menu")
    
    # Настраиваем сетку: 
    # 2 кнопки в первом ряду, 1 кнопка во втором
    kb.adjust(2, 1)
    
    return kb.as_markup()

def back_to_menu_kb() -> InlineKeyboardMarkup:
    """Простая кнопка назад"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Назад в меню", callback_data="nav_main_menu")
    return kb.as_markup()