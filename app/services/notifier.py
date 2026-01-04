import asyncio
from aiogram.types import FSInputFile
from aiogram import Bot

import app.database.requests as rq

async def notify_students(bot: Bot, faculty: str, course: str, file_path: str):
    """
    Рассылает уведомление и файл всем студентам этого курса.
    """
    # 1. Получаем список студентов
    users = await rq.get_users_by_filter(faculty, course)
    
    if not users:
        print(f"🔕 Нет студентов для уведомления ({faculty}, {course})")
        return

    print(f"🔔 Рассылка для {faculty} {course} (Студентов: {len(users)})...")
    
    # Подготавливаем файл для отправки
    file_to_send = FSInputFile(file_path)
    caption_text = f"⚡️ <b>Новое расписание!</b>\n\nФакультет: {faculty}\nКурс: {course}\n\nФайл загружен автоматически."

    count = 0
    for user_id in users:
        try:
            # Отправляем документ
            await bot.send_document(
                chat_id=user_id,
                document=file_to_send,
                caption=caption_text,
                parse_mode="HTML"
            )
            count += 1
            # Небольшая задержка, чтобы Телеграм не забанил за спам (если студентов много)
            await asyncio.sleep(0.05) 
        except Exception as e:
            # Если пользователь заблокировал бота - просто пропускаем
            print(f"   ⚠️ Не удалось отправить {user_id}: {e}")

    print(f"✅ Рассылка завершена. Доставлено: {count}/{len(users)}")