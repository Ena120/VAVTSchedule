import os
from aiogram.types import FSInputFile 
from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime, timedelta

import app.database.requests as rq
from app.keyboard.default.reply_menu import main_menu_kb

schedule_router = Router()

# --- ХЕНДЛЕРЫ ---

@schedule_router.message(F.text == "📅 Сегодня")
async def get_today_schedule(message: Message):
    await send_schedule(message, mode="today")

@schedule_router.message(F.text == "🗓 Завтра")
async def get_tomorrow_schedule(message: Message):
    await send_schedule(message, mode="tomorrow")

@schedule_router.message(F.text == "📅 На неделю")
async def get_week_schedule(message: Message):
    await send_schedule(message, mode="week")

@schedule_router.message(F.text == "🔄 Сменить группу")
async def change_group(message: Message):
    await message.answer("Чтобы выбрать новую группу, нажми: /start")


# --- ГЛАВНАЯ ЛОГИКА ---

@schedule_router.message(F.text == "📂 Файл PDF")
async def send_pdf_schedule(message: Message):
    tg_id = message.from_user.id
    
    # 1. Узнаем, где искать (Факультет, Курс)
    user_info = await rq.get_user_info(tg_id)
    if not user_info:
        await message.answer("⚠️ Группа не выбрана. Нажми /start")
        return

    # 2. Вычисляем понедельник текущей недели
    # Файлы названы так: "... (22.12.2025-27.12.2025).pdf"
    # Нам достаточно найти файл, содержащий дату понедельника
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    monday_str = monday.strftime("%d.%m.%Y") # Например "22.12.2025"

    # 3. Путь к папке курса
    # downloads/ФМФ/1 курс
    folder_path = os.path.join("downloads", user_info['faculty'], user_info['course'])
    
    target_file = None
    
    # 4. Ищем файл
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            # Проверяем, есть ли дата понедельника в названии файла
            if monday_str in file and file.endswith(".pdf"):
                target_file = os.path.join(folder_path, file)
                break
    
    # 5. Отправляем
    if target_file:
        await message.answer_document(
            document=FSInputFile(target_file),
            caption=f"📂 Расписание на неделю с {monday_str}"
        )
    else:
        await message.answer(
            f"❌ Не нашел файл расписания на неделю (с {monday_str}).\n"
            f"Возможно, оно еще не загружено или сейчас каникулы."
        )

async def send_schedule(message: Message, mode: str):
    tg_id = message.from_user.id
    
    # 1. Получаем инфо о пользователе (Группа, Факультет, Курс)
    user_info = await rq.get_user_info(tg_id)
    
    if not user_info:
        await message.answer("⚠️ Группа не выбрана. Нажми /start")
        return

    # 2. Формируем "Шапку" сообщения
    header = (
        f"🎓 <b>{user_info['faculty']}</b> | {user_info['course']}\n"
        f"👥 Группа: <b>{user_info['group']}</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
    )

    # 3. Определяем даты для поиска
    today = datetime.now()
    dates_to_search = []
    title_text = ""

    if mode == "today":
        target_date = today
        dates_to_search.append(target_date.strftime("%d.%m"))
        title_text = f"📅 <b>На сегодня ({target_date.strftime('%d.%m')}):</b>\n\n"

    elif mode == "tomorrow":
        target_date = today + timedelta(days=1)
        dates_to_search.append(target_date.strftime("%d.%m"))
        title_text = f"🗓 <b>На завтра ({target_date.strftime('%d.%m')}):</b>\n\n"

    elif mode == "week":
        # Берем текущую неделю (с Понедельника по Субботу)
        # today.weekday(): 0 = Пн, 6 = Вс
        start_of_week = today - timedelta(days=today.weekday()) # Понедельник этой недели
        
        # Генерируем даты на 6 дней (Пн-Сб)
        for i in range(6): 
            day = start_of_week + timedelta(days=i)
            dates_to_search.append(day.strftime("%d.%m"))
        
        title_text = f"📅 <b>Расписание на неделю:</b>\n\n"

    # 4. Ищем уроки в базе
    group_id = await rq.get_user_group_id(tg_id) # Нам всё еще нужен чистый ID
    lessons = await rq.get_lessons_for_dates(group_id, dates_to_search)

    if not lessons:
        await message.answer(
            f"{header}🎉 <b>Пар нет!</b>\nОтдыхай.", 
            parse_mode="HTML", 
            reply_markup=main_menu_kb()
        )
        return

    # 5. Формируем тело сообщения
    # Если это неделя, нам нужно группировать уроки по дням
    
    # Словарь для группировки: { "Пн 26.12": ["текст урока", "текст урока"] }
    schedule_text = ""
    current_day_str = ""
    
    # Сортируем уроки по дате (чтобы Пн шел перед Вт), если они перемешаны
    # (Хотя usually они идут в порядке добавления, но для надежности можно не сортировать, если парсер ок)
    
    for lesson in lessons:
        # Если день сменился (или первый раз), пишем заголовок дня
        if lesson.day != current_day_str:
            current_day_str = lesson.day
            schedule_text += f"\n📌 <b>{current_day_str}</b>\n"
        
        schedule_text += f"   🕒 <b>{lesson.time}</b>\n   📚 {lesson.subject_raw}\n\n"

    # 6. Отправляем всё вместе
    full_response = header + title_text + schedule_text
    
    # Телеграм имеет лимит 4096 символов. На всякий случай обрезаем, если вдруг неделя гигантская
    if len(full_response) > 4000:
        full_response = full_response[:4000] + "\n...(слишком длинное сообщение)..."

    await message.answer(full_response, parse_mode="HTML", reply_markup=main_menu_kb())