import os
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

import app.database.requests as rq
from app.keyboard.inline.menu import schedule_nav_kb, back_to_menu_kb

schedule_router = Router()

# --- Обработка навигации ---
@schedule_router.callback_query(F.data == "sch_today")
async def sch_today(callback: CallbackQuery):
    await show_day_schedule(callback, day_offset=0)

@schedule_router.callback_query(F.data == "sch_tomorrow")
async def sch_tomorrow(callback: CallbackQuery):
    await show_day_schedule(callback, day_offset=1)

@schedule_router.callback_query(F.data.startswith("sch_day_"))
async def sch_navigation(callback: CallbackQuery):
    offset = int(callback.data.split("_")[2])
    await show_day_schedule(callback, day_offset=offset)


# --- ОТОБРАЖЕНИЕ ДНЯ (С МАШИНОЙ ВРЕМЕНИ) ---
async def show_day_schedule(callback: CallbackQuery, day_offset: int):
    user_info = await rq.get_user_info(callback.from_user.id)
    group_id = await rq.get_user_group_id(callback.from_user.id)
    
    # === 🕒 МАШИНА ВРЕМЕНИ (ТЕСТ) ===
    # Притворяемся, что сегодня 26 декабря 2025 (Пятница)
    fake_today = datetime(2025, 12, 26)
    target_date = fake_today + timedelta(days=day_offset)
    
    # === 🛑 РЕАЛЬНОЕ ВРЕМЯ (Снято для тестов) ===
    # target_date = datetime.now() + timedelta(days=day_offset)
    # ============================================
    
    date_str = target_date.strftime("%d.%m")
    
    # Красивое название дня (относительно нашей фейковой даты)
    day_label = "Сегодня" if day_offset == 0 else "Завтра" if day_offset == 1 else "Вчера" if day_offset == -1 else target_date.strftime("%A")

    lessons = await rq.get_lessons_by_date(group_id, date_str)
    
    header = f"🎓 <b>{user_info['group']}</b> | {day_label} ({date_str})\n➖➖➖➖➖➖➖➖➖➖\n\n"
    
    if not lessons:
        text = header + "🎉 <b>Пар нет!</b>\nМожно отдыхать."
    else:
        text = header
        for lesson in lessons:
            text += f"🕒 <b>{lesson.time}</b>\n📚 {lesson.subject_raw}\n\n"

    try:
        await callback.message.edit_text(
            text, 
            parse_mode="HTML", 
            reply_markup=schedule_nav_kb(day_offset)
        )
    except Exception:
        await callback.answer()


# --- РАСПИСАНИЕ НА НЕДЕЛЮ (С МАШИНОЙ ВРЕМЕНИ) ---
@schedule_router.callback_query(F.data == "sch_week")
async def sch_week(callback: CallbackQuery):
    group_id = await rq.get_user_group_id(callback.from_user.id)
    
    # === 🕒 МАШИНА ВРЕМЕНИ (ТЕСТ) ===
    fake_today = datetime(2025, 12, 26)
    today = fake_today
    # === 🛑 РЕАЛЬНОЕ ВРЕМЯ (Снято) ===
    # today = datetime.now()
    # ================================

    # Вычисляем понедельник ЭТОЙ (фейковой) недели
    start_of_week = today - timedelta(days=today.weekday())
    
    # Генерируем даты на 6 дней (Пн-Сб)
    dates = [(start_of_week + timedelta(days=i)).strftime("%d.%m") for i in range(6)]
    
    lessons = await rq.get_lessons_for_dates(group_id, dates)
    
    text = "📅 <b>Расписание на неделю:</b>\n\n"
    if not lessons:
        text += "Пар на этой неделе нет."
    
    current_day = ""
    for lesson in lessons:
        if lesson.day != current_day:
            current_day = lesson.day
            text += f"\n📌 <b>{current_day}</b>\n"
        text += f"   🕒 {lesson.time} — {lesson.subject_raw}\n"

    if len(text) > 4000: text = text[:4000] + "..."
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_to_menu_kb())


# --- PDF ФАЙЛ (С МАШИНОЙ ВРЕМЕНИ) ---
@schedule_router.callback_query(F.data == "sch_pdf")
async def sch_pdf(callback: CallbackQuery):
    user_info = await rq.get_user_info(callback.from_user.id)
    
    # === 🕒 МАШИНА ВРЕМЕНИ (ТЕСТ) ===
    fake_today = datetime(2025, 12, 26)
    today = fake_today
    # === 🛑 РЕАЛЬНОЕ ВРЕМЯ (Снято) ===
    # today = datetime.now()
    # ================================
    
    # Ищем понедельник (22.12.2025)
    monday_str = (today - timedelta(days=today.weekday())).strftime("%d.%m.%Y")
    
    folder_path = os.path.join("downloads", user_info['faculty'], user_info['course'])
    target_file = None
    
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if monday_str in file and file.endswith(".pdf"):
                target_file = os.path.join(folder_path, file)
                break
    
    if target_file:
        await callback.answer("Загружаю файл...")
        await callback.message.answer_document(FSInputFile(target_file), caption="📂 Ваше расписание")
    else:
        await callback.answer(f"Файл за {monday_str} не найден 😔", show_alert=True)