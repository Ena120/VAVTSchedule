import asyncio
from loguru import logger

from loader import dp, bot
from services.default_commands import set_default_commands
from handlers import get_handlers_router
from app.database.engine import async_main
from app.scheduler import setup_scheduler 

async def main():
    # 1. ЗАПУСК БАЗЫ ДАННЫХ
    logger.info("Initializing database...")
    await async_main()

    # 2. ЗАПУСК ПЛАНИРОВЩИКА
    setup_scheduler()

    # 3. ПОДКЛЮЧЕНИЕ РОУТЕРОВ
    dp.include_router(get_handlers_router())

    # 4. НАСТРОЙКИ БОТА (С ЗАЩИТОЙ ОТ СБОЕВ СЕТИ)
    try:
        await set_default_commands(dp)
        logger.info("Default commands set successfully.")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось установить команды меню (проблемы с сетью?): {e}")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhooks deleted.")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить вебхук: {e}")
    
    logger.info("Bot started! Ready to accept messages.")
    
    # 5. ЗАПУСК ПОЛЛИНГА
    # start_polling сам умеет переподключаться, если сеть падает
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")