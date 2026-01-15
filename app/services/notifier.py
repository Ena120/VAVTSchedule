import asyncio
from aiogram.types import FSInputFile
from aiogram import Bot
import app.database.requests as rq

async def notify_students(bot: Bot, groups_in_file: list, file_path: str):
    """
    Рассылает уведомление только тем студентам, чьи группы есть в обновленном файле.
    """
    # 1. Получаем список студентов конкретных групп
    users = await rq.get_users_by_group_titles(groups_in_file)
    
    if not users:
        # Это нормально, может быть файл для групп, где еще никто не зарегистрировался
        return

    print(f"🔔 Рассылка для групп {groups_in_file} (Студентов: {len(users)})...")
    
    file_to_send = FSInputFile(file_path)
    # Можно сделать подпись короче, так как студент и так знает свою группу
    caption_text = "⚡️ <b>Вышло новое расписание!</b>"

    count = 0
    for user_id in users:
        try:
            await bot.send_document(
                chat_id=user_id,
                document=file_to_send,
                caption=caption_text,
                parse_mode="HTML"
            )
            count += 1
            await asyncio.sleep(0.05) 
        except Exception as e:
            print(f"   ⚠️ Не удалось отправить {user_id}: {e}")

    print(f"✅ Рассылка завершена. Доставлено: {count}/{len(users)}")