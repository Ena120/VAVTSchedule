import os
import asyncio
import logging
import sys
import re
from datetime import datetime
from dotenv import load_dotenv

# Настройка путей
project_root = os.getcwd()
app_path = os.path.join(project_root, "app")
sys.path.insert(0, app_path)

from app.database.engine import async_main
from app.database.requests import save_schedule_to_db, clear_schedule_table
from app.services.pdf_converter import convert_pdf_to_xlsx
from app.services.schedule_parser import parse_schedule
from app.services.notifier import notify_students
from app.loader import bot 

logging.basicConfig(level=logging.INFO)
DOWNLOAD_DIR = "downloads"

# Загружаем ID админа для уведомлений
load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

async def send_admin_alert(text: str):
    """Отправляет сообщение админу, если что-то пошло не так"""
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, f"🚨 <b>SYSTEM ALERT</b>\n\n{text}", parse_mode="HTML")
        except Exception as e:
            logging.error(f"Не удалось отправить алерт админу: {e}")

def is_schedule_relevant(filename: str) -> bool:
    match = re.search(r'(\d{2}\.\d{2}\.\d{4})-(\d{2}\.\d{2}\.\d{4})', filename)
    if match:
        try:
            end_date_str = match.group(2)
            end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
            # Если расписание закончилось вчера или раньше - оно старое
            if end_date.date() < datetime.now().date():
                return False
        except ValueError:
            pass
    return True

async def process_all_files():
    print("🛠  [1/4] Инициализация Базы Данных...")
    await async_main()
    
    print("🧹 [2/4] Очистка старого расписания...")
    await clear_schedule_table()
    
    print("🚀 [3/4] Начинаю обработку файлов...")

    errors_count = 0
    updated_count = 0

    for root, dirs, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            if file.endswith(".pdf"):
                path_parts = root.split(os.sep)
                if len(path_parts) >= 3:
                    faculty_name = path_parts[-2]
                    course_name = path_parts[-1]
                else:
                    continue

                pdf_path = os.path.join(root, file)
                xlsx_path = pdf_path.replace(".pdf", ".xlsx")

                print(f"\n📄 {file}")

                is_new_file = False

                # 1. Конвертация (Adobe)
                if not os.path.exists(xlsx_path):
                    print("   🔄 Файл новый! Конвертация...")
                    success = convert_pdf_to_xlsx(pdf_path, xlsx_path)
                    
                    if not success:
                        print("   ❌ Ошибка конвертации.")
                        errors_count += 1
                        # 🔥 УВЕДОМЛЕНИЕ АДМИНУ О СБОЕ ADOBE 🔥
                        await send_admin_alert(
                            f"❌ <b>Ошибка Adobe API!</b>\n"
                            f"Не удалось конвертировать файл:\n<code>{file}</code>\n\n"
                            f"Возможно, кончились лимиты или упал VPN."
                        )
                        continue
                    
                    is_new_file = True
                else:
                    print("   ⏭️  Excel уже существует.")

                # 2. Парсинг
                try:
                    schedule_data = parse_schedule(xlsx_path)
                    
                    if schedule_data:
                        await save_schedule_to_db(schedule_data, faculty_name, course_name)
                        print(f"   ✅ Сохранено пар: {len(schedule_data)}")
                        
                        if is_new_file:
                            if is_schedule_relevant(file):
                                groups_in_file = list(set(item['group'] for item in schedule_data))
                                if groups_in_file:
                                    print(f"   🔔 Рассылка...")
                                    await notify_students(bot, groups_in_file, pdf_path)
                                    updated_count += 1
                            else:
                                print("   🔕 Файл старый. Без рассылки.")
                    else:
                        print("   ⚠️ Парсер вернул 0 занятий.")

                except Exception as e:
                    print(f"   ❌ Ошибка: {e}")
                    errors_count += 1
                    await send_admin_alert(f"⚠️ Ошибка парсинга файла:\n{file}\n\nОшибка: {e}")

    print("\n🏁 [4/4] ВСЁ ГОТОВО!")
    
    # Итоговый отчет админу (чтобы ты знал, что бот жив)
    if errors_count > 0:
         await send_admin_alert(f"🏁 <b>Обновление завершено с ошибками.</b>\nОшибок: {errors_count}\nРассылок: {updated_count}")

if __name__ == "__main__":
    try:
        asyncio.run(process_all_files())
    except (KeyboardInterrupt, SystemExit):
        print("Стоп.")