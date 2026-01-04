import os
import asyncio
import logging
import sys

# --- ФИКС ИМПОРТОВ (Добавляем это в самое начало) ---
# Получаем текущую папку и добавляем папку 'app' в пути поиска
project_root = os.getcwd()
app_path = os.path.join(project_root, "app")
sys.path.insert(0, app_path)
# ----------------------------------------------------

# Теперь импорты заработают
from app.database.engine import async_main
from app.database.requests import save_schedule_to_db, clear_schedule_table
from app.services.pdf_converter import convert_pdf_to_xlsx
from app.services.schedule_parser import parse_schedule
from app.services.notifier import notify_students
from app.loader import bot 

logging.basicConfig(level=logging.INFO)
DOWNLOAD_DIR = "downloads"

async def process_all_files():
    """
    Главная функция обновления расписания.
    """
    print("🛠  [1/4] Инициализация Базы Данных...")
    await async_main()
    
    # Можно раскомментировать, если нужно чистить базу полностью
    # print("🧹 [2/4] Очистка старого расписания...")
    # await clear_schedule_table()
    
    print("🚀 [3/4] Начинаю обработку файлов...")

    for root, dirs, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            if file.endswith(".pdf"):
                path_parts = root.split(os.sep)
                
                # Проверка структуры папок: downloads/Факультет/Курс
                if len(path_parts) >= 3:
                    faculty_name = path_parts[-2]
                    course_name = path_parts[-1]
                else:
                    continue

                pdf_path = os.path.join(root, file)
                xlsx_path = pdf_path.replace(".pdf", ".xlsx")

                print(f"\n📄 {file} | {faculty_name} | {course_name}")

                is_new_file = False

                # --- 1. Конвертация ---
                if not os.path.exists(xlsx_path):
                    print("   🔄 Обнаружен новый файл! Конвертация...")
                    success = convert_pdf_to_xlsx(pdf_path, xlsx_path)
                    if success:
                        is_new_file = True
                    else:
                        print("   ❌ Ошибка конвертации. Пропускаю.")
                        continue
                else:
                    print("   ⏭️  Excel уже есть.")

                # --- 2. Парсинг и сохранение ---
                try:
                    schedule_data = parse_schedule(xlsx_path)
                    
                    if schedule_data:
                        await save_schedule_to_db(schedule_data, faculty_name, course_name)
                        print(f"   ✅ Данные сохранены.")
                        
                        # --- 3. Уведомление ---
                        if is_new_file:
                            print("   🔔 Запуск рассылки уведомлений...")
                            await notify_students(bot, faculty_name, course_name, pdf_path)
                    else:
                        print("   ⚠️ Парсер не нашел занятий.")

                except Exception as e:
                    print(f"   ❌ Критическая ошибка: {e}")

    print("\n🏁 [4/4] ВСЁ ГОТОВО!")

if __name__ == "__main__":
    try:
        asyncio.run(process_all_files())
    except (KeyboardInterrupt, SystemExit):
        print("Скрипт остановлен.")