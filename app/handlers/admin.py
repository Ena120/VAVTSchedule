import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import app.database.requests as rq

load_dotenv()
# Если ADMIN_ID не задан, ставим 0, чтобы бот не падал, но админка не работала
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

admin_router = Router()

class BroadcastState(StatesGroup):
    message = State()

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Сделать рассылку", callback_data="start_broadcast")
    await message.answer("👑 Админ-панель:", reply_markup=kb.as_markup())

@admin_router.callback_query(F.data == "start_broadcast")
async def ask_broadcast_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✍️ Пришли сообщение для рассылки:")
    await state.set_state(BroadcastState.message)

@admin_router.message(BroadcastState.message)
async def perform_broadcast(message: Message, state: FSMContext, bot: Bot):
    users = await rq.get_all_users_ids()
    await message.answer(f"🚀 Рассылка на {len(users)} пользователей...")
    count = 0
    for user_id in users:
        try:
            await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
            count += 1
        except Exception:
            pass
    await message.answer(f"✅ Доставлено: {count} из {len(users)}")
    await state.clear()
