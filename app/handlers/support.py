import os
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from app.keyboard.default.reply_menu import get_main_reply_kb

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

support_router = Router()

class SupportState(StatesGroup):
    text = State()

@support_router.message(F.text == "🆘 Поддержка")
async def start_support(message: Message, state: FSMContext):
    await message.answer("✍️ Напиши сообщение админу:", reply_markup=get_main_reply_kb())
    await state.set_state(SupportState.text)

@support_router.message(SupportState.text)
async def forward_to_admin(message: Message, state: FSMContext, bot: Bot):
    if message.text in ["📱 Меню", "📅 Сегодня", "🆘 Поддержка"]:
        await state.clear()
        return
    
    if ADMIN_ID:
        admin_text = f"📩 <b>Сообщение от юзера!</b>\nID: <code>{message.from_user.id}</code>\n\n{message.text}"
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
        await message.answer("✅ Отправлено!")
    else:
        await message.answer("❌ Админ не настроен.")
    
    await state.clear()

@support_router.message(F.reply_to_message)
async def admin_reply(message: Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    original = message.reply_to_message.text or message.reply_to_message.caption
    if not original or "ID:" not in original: return
    
    try:
        user_id = int(original.split("ID:")[1].split("\n")[0].strip().replace("</code>", ""))
        await bot.send_message(user_id, f"🔔 <b>Ответ:</b>\n{message.text}", parse_mode="HTML")
        await message.answer("✅ Ответ ушел.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
