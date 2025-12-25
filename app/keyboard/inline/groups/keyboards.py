from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def groups_list_kb(groups: list) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком групп.
    :param groups: Список объектов Group из базы данных.
    """
    kb = InlineKeyboardBuilder()
    
    # Проходим по всем группам из базы
    for group in groups:
        # text - то, что видит студент (название группы)
        # callback_data - то, что получит бот (префикс setgroup_ + ID группы)
        kb.button(text=group.title, callback_data=f"setgroup_{group.group_id}")
    
    # Выстраиваем кнопки:
    # Если групп много, лучше по 2 или 3 в ряд.
    # .adjust(2) сделает 2 колонки.
    kb.adjust(2)
    
    return kb.as_markup()