import asyncio
from loguru import logger

from loader import dp, bot
from services.default_commands import set_default_commands
from handlers import get_handlers_router
from app.database.engine import async_main

# from app.scheduler import setup_scheduler <-- УДАЛЕНО

async def main():
    logger.info("Initializing database...")
    await async_main()

    # setup_scheduler() <-- УДАЛЕНО (теперь это делает worker.py)

    dp.include_router(get_handlers_router())

    try:
        await set_default_commands(dp)
        logger.info("Default commands set successfully.")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось установить команды: {e}")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhooks deleted.")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить вебхук: {e}")
    
    logger.info("Bot started! Ready to accept messages.")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")