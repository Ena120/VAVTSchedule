from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.database.requests as rq
from app.keyboard.default.reply_menu import get_main_reply_kb
from app.keyboard.inline.menu import main_menu_inline

start_router = Router()

# --- ГЕНЕРАТОРЫ КЛАВИАТУР (Локально) ---
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
    faculties = await rq.get_faculties()
    text = "👋 Привет! Выбери свой факультет:"
    kb = list_kb(faculties, "fac")
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@start_router.callback_query(F.data.startswith("fac_"))
async def select_course(callback: CallbackQuery):
    faculty = callback.data.split("_")[1]
    courses = await rq.get_courses_by_faculty(faculty)
    await callback.message.edit_text(f"Факультет: {faculty}\nВыберите курс:", reply_markup=list_kb(courses, f"course_{faculty}"))

@start_router.callback_query(F.data.startswith("course_"))
async def select_group(callback: CallbackQuery):
    _, faculty, course = callback.data.split("_")
    groups = await rq.get_groups_by_filter(faculty, course)
    await callback.message.edit_text(f"Факультет: {faculty}, {course}\nВыберите группу:", reply_markup=groups_kb(groups))

@start_router.callback_query(F.data.startswith("setgroup_"))
async def finish_setup(callback: CallbackQuery):
    group_id = int(callback.data.split("_")[1])
    await rq.set_user_group(callback.from_user.id, group_id)
    user_info = await rq.get_user_info(callback.from_user.id)
    
    await callback.message.delete() # Удаляем выбор групп
    
    # 1. Отправляем "Вечную кнопку" (Reply)
    await callback.message.answer("✅ Настройка завершена!", reply_markup=get_main_reply_kb())
    
    # 2. Отправляем Главное Меню (Inline)
    text = (
        f"🎓 <b>{user_info['faculty']} | {user_info['course']}</b>\n"
        f"👥 Группа: <b>{user_info['group']}</b>\n"
        f"👇 Выберите действие:"
    )
    await callback.message.answer(text, reply_markup=main_menu_inline(user_info), parse_mode="HTML")