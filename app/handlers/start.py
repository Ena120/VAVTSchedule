from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboard.default.reply_menu import main_menu_kb


import app.database.requests as rq

start_router = Router()

# --- КЛАВИАТУРЫ ПРЯМО ТУТ (для простоты) ---

def list_kb(items, prefix):
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.button(text=str(item), callback_data=f"{prefix}_{item}")
    kb.adjust(2)
    return kb.as_markup()

def groups_kb(groups):
    kb = InlineKeyboardBuilder()
    for g in groups:
        kb.button(text=g.title, callback_data=f"setgroup_{g.group_id}")
    kb.adjust(2)
    kb.row(InlineKeyboardBuilder().button(text="🔙 Назад", callback_data="start").as_markup().inline_keyboard[0][0])
    return kb.as_markup()

# --- ХЕНДЛЕРЫ ---

@start_router.message(CommandStart())
@start_router.callback_query(F.data == "start")
async def cmd_start(event: Message | CallbackQuery):
    # 1. Спрашиваем Факультет
    faculties = await rq.get_faculties()
    
    text = "👋 Привет! Выбери свой факультет:"
    kb = list_kb(faculties, "fac")
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@start_router.callback_query(F.data.startswith("fac_"))
async def select_course(callback: CallbackQuery):
    # 2. Спрашиваем Курс
    faculty = callback.data.split("_")[1]
    courses = await rq.get_courses_by_faculty(faculty)
    
    await callback.message.edit_text(
        f"Факультет: {faculty}\nТеперь выбери курс:",
        reply_markup=list_kb(courses, f"course_{faculty}")
    )

@start_router.callback_query(F.data.startswith("course_"))
async def select_group(callback: CallbackQuery):
    # 3. Спрашиваем Группу
    _, faculty, course = callback.data.split("_") # course_ФМФ_1 курс
    
    groups = await rq.get_groups_by_filter(faculty, course)
    
    await callback.message.edit_text(
        f"Факультет: {faculty}, {course}\nВыбери группу:",
        reply_markup=groups_kb(groups)
    )

@start_router.callback_query(F.data.startswith("setgroup_"))
async def finish_setup(callback: CallbackQuery):
    # 1. Получаем ID группы и сохраняем в базу
    group_id = int(callback.data.split("_")[1])
    await rq.set_user_group(callback.from_user.id, group_id)
    
    # 2. Отвечаем, что все ок (убираем часики загрузки)
    await callback.answer("Готово!")
    
    # 3. УДАЛЯЕМ старое сообщение с выбором групп (чтобы не мусорить в чате)
    await callback.message.delete()
    
    # 4. Отправляем НОВОЕ сообщение с нижними кнопками (Reply Keyboard)
    await callback.message.answer(
        "✅ Группа сохранена!\nТеперь выбери день, чтобы увидеть расписание:",
        reply_markup=main_menu_kb()
    )