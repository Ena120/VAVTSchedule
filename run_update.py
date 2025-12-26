import os
import asyncio
import logging

# Импортируем создание таблиц
from app.database.engine import async_main

# Импортируем функции работы с БД (сохранение и очистка)
from app.database.requests import save_schedule_to_db, clear_schedule_table

# Импортируем сервисы (конвертер и парсер)
from app.services.pdf_converter import convert_pdf_to_xlsx
from app.services.schedule_parser import parse_schedule

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Папка, где лежат скачанные файлы
DOWNLOAD_DIR = "downloads"

async def process_all_files():
    """
    Главная функция: 
    1. Готовит БД.
    2. Ищет файлы в папках.
    3. Конвертирует и Парсит.
    4. Загружает в БД с учетом Факультета и Курса.
    """
    print("🛠  [1/4] Инициализация Базы Данных...")
    await async_main()
    
    print("🧹 [2/4] Очистка старого расписания...")
    await clear_schedule_table()
    
    print("🚀 [3/4] Начинаю обработку файлов...")

    # os.walk рекурсивно проходит по всем папкам
    for root, dirs, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            # Нас интересуют только PDF файлы
            if file.endswith(".pdf"):
                
                # --- ОПРЕДЕЛЯЕМ ФАКУЛЬТЕТ И КУРС ПО ПАПКЕ ---
                # root - это текущий путь, например: "downloads/ФМФ/1 курс"
                # Используем os.sep, чтобы работало и на Windows, и на Mac
                path_parts = root.split(os.sep)
                
                # Проверяем, что файл лежит достаточно глубоко (downloads -> Факультет -> Курс)
                if len(path_parts) >= 3:
                    # Предпоследняя папка - это Факультет (ФМФ)
                    faculty_name = path_parts[-2]
                    # Последняя папка - это Курс (1 курс)
                    course_name = path_parts[-1]
                else:
                    print(f"⚠️ Файл {file} лежит не в папке курса. Пропускаю.")
                    continue

                pdf_path = os.path.join(root, file)
                xlsx_path = pdf_path.replace(".pdf", ".xlsx")

                print(f"\n📄 Обработка: {file}")
                print(f"   🏛  Факультет: {faculty_name} | 🎓 Курс: {course_name}")

                # --- ШАГ 1: Конвертация (PDF -> Excel) ---
                if not os.path.exists(xlsx_path):
                    print("   🔄 Конвертация PDF в Excel...")
                    success = convert_pdf_to_xlsx(pdf_path, xlsx_path)
                    if not success:
                        print("   ❌ Ошибка конвертации. Пропускаю.")
                        continue
                else:
                    print("   ⏭️  Excel уже существует.")

                # --- ШАГ 2: Парсинг (Excel -> Данные) ---
                try:
                    schedule_data = parse_schedule(xlsx_path)
                    
                    if not schedule_data:
                        print("   ⚠️ Парсер не нашел занятий в этом файле.")
                        continue
                    
                    print(f"   ✅ Найдено занятий: {len(schedule_data)}")

                    # --- ШАГ 3: Сохранение в БД ---
                    # Теперь передаем также faculty_name и course_name
                    await save_schedule_to_db(schedule_data, faculty_name, course_name)

                except Exception as e:
                    print(f"   ❌ Критическая ошибка при обработке: {e}")

    print("\n🏁 [4/4] ВСЁ ГОТОВО! Расписание успешно обновлено.")

if __name__ == "__main__":
    try:
        # Запускаем асинхронный цикл
        asyncio.run(process_all_files())
    except (KeyboardInterrupt, SystemExit):
        print("Скрипт остановлен.")