import os
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command

# Импортируем твою функцию парсинга (убедись, что создал файл в services!)
from app.services.schedule_parser import parse_schedule

# Создаем роутер
router = Router()

# ВСТАВЬ СЮДА СВОЙ ID (чтобы никто другой не мог загружать)
ADMIN_ID = 123456789  

@router.message(F.document)
async def handle_schedule_file(message: Message):
    # 1. Проверка на админа
    if message.from_user.id != ADMIN_ID:
        return

    document = message.document

    # 2. Проверка, что это Excel
    if not document.file_name.endswith('.xlsx'):
        await message.answer("📂 Пожалуйста, отправь файл с расширением .xlsx")
        return

    await message.answer("⏳ Скачиваю и обрабатываю файл...")

    # Создаем папку для загрузок, если её нет
    download_path = "downloads"
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Путь сохранения
    file_path = os.path.join(download_path, document.file_name)
    
    # 3. Скачиваем файл
    bot = message.bot
    await bot.download(document, destination=file_path)

    try:
        # 4. Запускаем твой парсер
        schedule_data = parse_schedule(file_path)
        
        count = len(schedule_data)
        
        # Тут в будущем будет сохранение в БД:
        # await save_to_db(schedule_data)

        # Вывод отчета
        response_text = (
            f"✅ **Успешно обработано!**\n"
            f"Найдено занятий: {count}\n\n"
        )
        
        if count > 0:
            first_lesson = schedule_data[0]
            response_text += (
                f"🧐 **Пример первого занятия:**\n"
                f"📅 {first_lesson.get('date', '-')}\n"
                f"🎓 {first_lesson.get('group', '-')}\n"
                f"⏰ {first_lesson.get('time', '-')}\n"
                f"📖 {first_lesson.get('subject', '-')}"
            )
            
        await message.answer(response_text, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ **Ошибка обработки:**\n{e}", parse_mode="Markdown")
    finally:
        # (Опционально) Удаляем файл после обработки, чтобы не засорять диск
        if os.path.exists(file_path):
            os.remove(file_path)