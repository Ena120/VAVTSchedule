import asyncio
import sys
import os

# Получаем текущую папку проекта
project_root = os.getcwd()
# Получаем путь к папке app
app_path = os.path.join(project_root, "app")

# ГЛАВНЫЙ ФИКС:
# Добавляем папку app в начало списка путей, где Python ищет модули.
# Теперь Python увидит 'loader', 'services', 'handlers' так, будто они лежат рядом с run.py
sys.path.insert(0, app_path)

# Импортируем main только ПОСЛЕ того, как настроили пути
from app.__main__ import main

if __name__ == "__main__":
    try:
        print("🤖 Запускаю бота...")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")