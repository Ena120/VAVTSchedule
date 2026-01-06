from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import app.database.requests as rq
from app.keyboard.inline.menu import main_menu_inline, settings_kb

menu_router = Router()

# Вход в меню (по кнопке или команде)
@menu_router.message(F.text == "📱 Меню")
@menu_router.message(Command("menu"))
async def show_main_menu(message: Message):
    user_info = await rq.get_user_info(message.from_user.id)
    
    if not user_info:
        await message.answer("⚠️ Группа не выбрана. Нажми /start")
        return

    text = (
        f"🎓 <b>{user_info['faculty']} | {user_info['course']}</b>\n"
        f"👥 Группа: <b>{user_info['group']}</b>\n"
        f"👇 Выберите действие:"
    )
    await message.answer(text, reply_markup=main_menu_inline(user_info), parse_mode="HTML")

# Возврат в меню (кнопка "Назад")
@menu_router.callback_query(F.data == "nav_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    user_info = await rq.get_user_info(callback.from_user.id)
    text = (
        f"🎓 <b>{user_info['faculty']} | {user_info['course']}</b>\n"
        f"👥 Группа: <b>{user_info['group']}</b>\n"
        f"👇 Выберите действие:"
    )
    # Редактируем сообщение (магия App-style)
    await callback.message.edit_text(text, reply_markup=main_menu_inline(user_info), parse_mode="HTML")

# Настройки
@menu_router.callback_query(F.data == "settings_menu")
async def open_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\nЗдесь можно изменить параметры бота.",
        reply_markup=settings_kb(),
        parse_mode="HTML"
    )

# Триггер смены группы
@menu_router.callback_query(F.data == "reselect_group")
async def trigger_reselect(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Нажми /start для выбора новой группы.")