import asyncio
from loguru import logger

# Твои существующие импорты
from loader import dp, bot
from services import set_default_commands
from handlers import get_handlers_router

# --- НОВЫЕ ИМПОРТЫ ---
# 1. Импортируем создание таблиц
from app.database.engine import async_main
# 2. Импортируем наше меню с выбором группы
# (Если main.py лежит внутри папки app, то импорт такой. 
# Если будет ошибка импорта - попробуй: from app.handlers.start import start_router)
from handlers.start import start_router


async def main():
    # --- 1. ЗАПУСК БАЗЫ ДАННЫХ ---
    # Создаем таблицы, если их еще нет
    logger.info("Initializing database...")
    await async_main()

    # --- 2. ПОДКЛЮЧЕНИЕ РОУТЕРОВ ---
    # Подключаем наш новый роутер (команда /start и кнопки)
    dp.include_router(start_router)
    
    # Подключаем остальные роутеры (твои старые)
    dp.include_router(get_handlers_router())

    # --- 3. НАСТРОЙКИ БОТА ---
    await set_default_commands(dp)
    
    # Удаляем старые апдейты (чтобы бот не отвечал на сообщения, присланные, пока он спал)
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Bot started! Ready to accept messages.")
    
    # --- 4. ЗАПУСК ---
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # Используем asyncio.run для корректного запуска в Python 3.10+
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")