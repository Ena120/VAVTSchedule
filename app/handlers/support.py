import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

import app.database.requests as rq
from app.keyboard.inline.menu import main_menu_inline

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

support_router = Router()

class SupportState(StatesGroup):
    text = State()

def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_support")]
    ])

@support_router.callback_query(F.data == "support_open")
async def start_support(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "✍️ <b>Напиши сообщение админу.</b>\n\n"
        "Нажми кнопку ниже, если передумал.",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )
    await state.set_state(SupportState.text)

@support_router.callback_query(F.data == "cancel_support")
async def cancel_support(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_info = await rq.get_user_info(callback.from_user.id)
    if not user_info:
        await callback.message.edit_text("❌ Ошибка: Группа не найдена. Нажми /start")
        return
    text = (
        f"🎓 <b>{user_info['faculty']} | {user_info['course']}</b>\n"
        f"👥 Группа: <b>{user_info['group']}</b>\n"
        f"👇 Выберите действие:"
    )
    await callback.message.edit_text(text, reply_markup=main_menu_inline(user_info), parse_mode="HTML")

@support_router.message(SupportState.text)
async def forward_to_admin(message: Message, state: FSMContext, bot: Bot):
    # Если нажали кнопку меню в режиме поддержки - выходим
    if message.text == "📱 Меню":
        await state.clear()
        # Позволяем другому хендлеру (menu.py) обработать это сообщение
        return 

    if ADMIN_ID:
        # --- ВОТ ТУТ ИСПРАВЛЕНИЕ НИКА ---
        username = f"@{message.from_user.username}" if message.from_user.username else "Без юзернейма"
        
        admin_text = (
            f"📩 <b>Сообщение от студента!</b>\n"
            f"👤 Имя: {message.from_user.full_name}\n"
            f"🔗 Ник: {username}\n"
            f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
            f"📝 Текст:\n{message.text}"
        )
        # --------------------------------
        try:
            await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
            await message.answer("✅ Сообщение отправлено! Жди ответа.")
        except Exception:
            await message.answer("❌ Ошибка отправки.")
    else:
        await message.answer("❌ Админ не настроен.")
    
    await state.clear()
    
    # Возвращаем меню
    user_info = await rq.get_user_info(message.from_user.id)
    if user_info:
        text = (
            f"🎓 <b>{user_info['faculty']} | {user_info['course']}</b>\n"
            f"👥 Группа: <b>{user_info['group']}</b>\n"
            f"👇 Выберите действие:"
        )
        await message.answer(text, reply_markup=main_menu_inline(user_info), parse_mode="HTML")

@support_router.message(F.reply_to_message)
async def admin_reply(message: Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    
    original = message.reply_to_message.text or message.reply_to_message.caption
    if not original or "🆔 ID:" not in original: return

    try:
        # Ищем строку с ID
        user_id_line = [line for line in original.split('\n') if "🆔 ID:" in line][0]
        user_id = int(user_id_line.split(":")[1].strip().replace("</code>", ""))
        
        await bot.send_message(user_id, f"🔔 <b>Ответ поддержки:</b>\n\n{message.text}", parse_mode="HTML")
        await message.answer("✅ Ответ ушел.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")