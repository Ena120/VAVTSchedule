import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

load_dotenv()
# Если ID админа нет в env, ставим 0 (чтобы не падало, но работать не будет)
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

support_router = Router()

class SupportState(StatesGroup):
    text = State()

# Клавиатура для отмены
def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_support")]
    ])

# --- 1. ВХОД В ПОДДЕРЖКУ (Нажатие кнопки в меню) ---
@support_router.callback_query(F.data == "support_open")
async def start_support(callback: CallbackQuery, state: FSMContext):
    await callback.answer() # Чтобы кнопка перестала мигать
    
    await callback.message.edit_text(
        "✍️ <b>Напиши свое сообщение, отзыв или вопрос.</b>\n"
        "Администратор ответит тебе прямо здесь.\n\n"
        "<i>Нажми Отмена, если передумал.</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )
    # Включаем режим "Жду сообщение"
    await state.set_state(SupportState.text)

# --- 2. ОТМЕНА ---
@support_router.callback_query(F.data == "cancel_support")
async def cancel_support(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    # Можно вернуть главное меню, но проще просто сказать "Ок"
    await callback.message.answer("Режим поддержки выключен. Нажми /start или Меню.")

# --- 3. ПОЛУЧЕНИЕ СООБЩЕНИЯ ОТ СТУДЕНТА ---
@support_router.message(SupportState.text)
async def forward_to_admin(message: Message, state: FSMContext, bot: Bot):
    # Если юзер передумал и жмет команды - выходим
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    if not ADMIN_ID:
        await message.answer("❌ Ошибка: Админ не настроен в .env")
        await state.clear()
        return

    # Формируем красивое сообщение админу
    # ID пользователя прячем, чтобы потом достать для ответа
    admin_text = (
        f"📩 <b>Новое сообщение!</b>\n"
        f"От: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"ID: <code>{message.from_user.id}</code>\n\n"
        f"📝 Текст:\n{message.text}"
    )
    
    try:
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
        await message.answer("✅ Сообщение отправлено! Жди ответа.")
    except Exception as e:
        await message.answer(f"Не удалось отправить: {e}")
    
    # Выходим из состояния, чтобы бот снова работал как обычно
    await state.clear()

# --- 4. АДМИН ОТВЕЧАЕТ (Reply) ---
@support_router.message(F.reply_to_message)
async def admin_reply(message: Message, bot: Bot):
    # Проверка: пишет ли это Админ?
    if message.from_user.id != ADMIN_ID:
        return

    # Проверка: отвечает ли он на сообщение с ID?
    original_text = message.reply_to_message.text or message.reply_to_message.caption
    if not original_text or "ID:" not in original_text:
        return 

    try:
        # Парсим ID студента из текста сообщения
        # Ищем строку, где есть "ID: "
        lines = original_text.split('\n')
        user_id_line = next((line for line in lines if "ID:" in line), None)
        
        if user_id_line:
            # Вырезаем только цифры
            user_id = int(user_id_line.split(":")[1].strip().replace("</code>", ""))
            
            # Отправляем ответ студенту
            await bot.send_message(
                chat_id=user_id,
                text=f"🔔 <b>Ответ поддержки:</b>\n\n{message.text}",
                parse_mode="HTML"
            )
            await message.answer("✅ Ответ доставлен.")
        else:
            await message.answer("❌ Не смог найти ID пользователя в этом сообщении.")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки: {e}")