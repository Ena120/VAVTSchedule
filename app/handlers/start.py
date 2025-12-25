from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

# Импортируем наши функции для БД
import app.database.requests as rq
# Импортируем нашу новую клавиатуру
# Обрати внимание на путь импорта, он зависит от твоей структуры папок
from app.keyboard.inline.groups.keyboards import groups_list_kb

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Срабатывает, когда пользователь пишет /start
    """
    # 1. Получаем список групп из базы данных
    groups = await rq.get_all_groups()
    
    if not groups:
        await message.answer("⚠️ В базе пока нет групп. Попроси администратора обновить расписание.")
        return

    # 2. Отправляем сообщение с нашей клавиатурой
    await message.answer(
        "👋 Привет! Я бот с расписанием ВАВТ.\n"
        "Чтобы продолжить, выбери свою учебную группу:",
        reply_markup=groups_list_kb(groups)
    )

@start_router.callback_query(F.data.startswith("setgroup_"))
async def process_group_selection(callback: CallbackQuery):
    """
    Срабатывает, когда нажимают кнопку с группой
    """
    # data придет в виде "setgroup_5", нам нужно вытащить число 5
    group_id = int(callback.data.split("_")[1])
    
    # Сохраняем выбор в базу
    await rq.set_user_group(callback.from_user.id, group_id)
    
    # Отвечаем телеграму, что кнопка сработала (чтобы часики не крутились)
    await callback.answer("Группа сохранена!")
    
    # Меняем сообщение, чтобы кнопки пропали
    await callback.message.edit_text(
        "✅ Отлично! Твоя группа сохранена.\n"
        "Теперь я буду показывать расписание именно для неё."
    )