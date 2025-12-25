import os
import asyncio
import logging

# Импортируем создание таблиц (чтобы база точно была готова)
from app.database.engine import async_main

# Импортируем наши сервисы
from app.services.pdf_converter import convert_pdf_to_xlsx
from app.services.schedule_parser import parse_schedule
from app.database.requests import save_schedule_to_db, clear_schedule_table

# Настройка логов
logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIR = "downloads"

async def process_all_files():
    """
    Главная функция: ищет PDF, конвертирует, парсит и сохраняет.
    """
    print("🛠 Создаю таблицы в БД (если их нет)...")
    await async_main()

    # ОЧИСТКА ПЕРЕД ЗАГРУЗКОЙ
    await clear_schedule_table()
    
    print("🚀 Начинаю обработку файлов из папки downloads...")

    # Проходим по всем подпапкам в downloads (МПФ/1 курс и т.д.)
    # os.walk возвращает тройку: (текущая_папка, папки_внутри, файлы_внутри)
    for root, dirs, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            # Нас интересуют только PDF
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                xlsx_path = pdf_path.replace(".pdf", ".xlsx")

                print(f"\n------------------------------------------------")
                print(f"📄 Файл: {file}")
                print(f"📂 Путь: {root}")

                # --- ШАГ 1: Конвертация (Adobe API) ---
                # Если XLSX файла нет, создаем его. Если есть — не тратим лимиты Adobe.
                if not os.path.exists(xlsx_path):
                    print("   🔄 Запуск конвертации PDF -> XLSX...")
                    success = convert_pdf_to_xlsx(pdf_path, xlsx_path)
                    if not success:
                        print("   ❌ Пропускаю файл из-за ошибки конвертации.")
                        continue 
                else:
                    print("   ⏭️ Excel уже существует, используем его.")

                # --- ШАГ 2: Парсинг (Excel -> Данные) ---
                try:
                    print("   🧩 Читаю Excel файл...")
                    schedule_data = parse_schedule(xlsx_path)
                    
                    if not schedule_data:
                        print("   ⚠️ Парсер вернул пустой список (возможно, файл пустой или формат не тот).")
                        continue
                        
                    print(f"   ✅ Найдено занятий: {len(schedule_data)}")

                    # --- ШАГ 3: Сохранение в БД ---
                    # Передаем данные в твою функцию из requests.py
                    await save_schedule_to_db(schedule_data)

                except Exception as e:
                    print(f"   ❌ Критическая ошибка при обработке файла: {e}")

    print("\n🏁 ВСЁ ГОТОВО! Обработка завершена.")

if __name__ == "__main__":
    try:
        # Запускаем асинхронный цикл
        asyncio.run(process_all_files())
    except (KeyboardInterrupt, SystemExit):
        print("Остановка скрипта.")