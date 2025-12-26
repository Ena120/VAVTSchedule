from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime, timedelta

import app.database.requests as rq
# Правильный импорт клавиатуры:
from app.keyboard.default.reply_menu import main_menu_kb

schedule_router = Router()

@schedule_router.message(F.text == "📅 Сегодня")
async def get_today_schedule(message: Message):
    await send_schedule(message, day_offset=0)

@schedule_router.message(F.text == "🗓 Завтра")
async def get_tomorrow_schedule(message: Message):
    await send_schedule(message, day_offset=1)

@schedule_router.message(F.text == "🔄 Сменить группу")
async def change_group(message: Message):
    await message.answer("Чтобы выбрать новую группу, нажми: /start")

async def send_schedule(message: Message, day_offset: int):
    tg_id = message.from_user.id
    group_id = await rq.get_user_group_id(tg_id)
    
    if not group_id:
        await message.answer("⚠️ Группа не выбрана. Нажми /start")
        return

    # Вычисляем дату. 
    # ВАЖНО: Убедись, что дата на сервере совпадает с форматом в Excel
    # В твоем Excel формат "29.12" (день.месяц)
    target_date = datetime.now() + timedelta(days=day_offset)
    date_str = target_date.strftime("%d.%m") 
    
    # Для теста (так как сегодня 26.12, а в файле расписание с 29.12)
    # можешь временно раскомментировать эту строку:
    # date_str = "29.12" 

    lessons = await rq.get_lessons_by_date(group_id, date_str)
    
    if not lessons:
        day_text = "Сегодня" if day_offset == 0 else "Завтра"
        await message.answer(f"🎉 <b>{day_text} ({date_str}) пар нет!</b>", parse_mode="HTML")
        return

    text = f"📅 <b>Расписание на {date_str}:</b>\n\n"
    for lesson in lessons:
        text += f"🕒 <b>{lesson.time}</b>\n📚 {lesson.subject_raw}\n\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())