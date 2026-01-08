import asyncio
import logging
import sys
import os
import time

# Настройка путей
project_root = os.getcwd()
app_path = os.path.join(project_root, "app")
sys.path.insert(0, app_path)

from app.database.engine import async_main
from app.scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)

async def main():
    print("👷 Worker (Парсер) запущен! Жду задач...")
    
    # 1. Инициализируем БД
    await async_main()
    
    # 2. Запускаем планировщик
    setup_scheduler()
    
    # 3. Вечный цикл, чтобы процесс не умирал
    while True:
        await asyncio.sleep(3600) 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Worker остановлен.")