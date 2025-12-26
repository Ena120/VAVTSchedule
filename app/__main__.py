import asyncio
from loguru import logger

from loader import dp, bot
# Исправленный импорт (с указанием файла)
from app.services.default_commands import set_default_commands
from handlers import get_handlers_router

# Импортируем создание таблиц
from app.database.engine import async_main

async def main():
    # --- 1. ЗАПУСК БАЗЫ ДАННЫХ ---
    logger.info("Initializing database...")
    await async_main()

    # --- 2. ПОДКЛЮЧЕНИЕ РОУТЕРОВ ---
    # Мы УБРАЛИ отсюда start_router, так как он уже есть внутри get_handlers_router()
    
    # Подключаем "главный" роутер, который содержит в себе все остальные (включая start)
    dp.include_router(get_handlers_router())

    # --- 3. НАСТРОЙКИ БОТА ---
    await set_default_commands(dp)
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Bot started! Ready to accept messages.")
    
    # --- 4. ЗАПУСК ---
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")