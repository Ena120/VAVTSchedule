from loguru import logger
from notifiers.logging import NotificationHandler
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
# --- НОВЫЙ ИМПОРТ ---
from aiogram.client.default import DefaultBotProperties 

import config

# * if something happen, bot send a notification to admin
param = {
    'token': config.BOT_TOKEN,
    'chat_id': config.ADMIN
}
handler = NotificationHandler("telegram", defaults=param)
logger.add(handler, level="ERROR")

# * Set up logging, declare the bot and dispatcher
logger.add(
    "logs/logs.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="1 week",
    compression="zip",
    enqueue=True,
    backtrace=False,
    diagnose=False
)

storage = MemoryStorage()

# --- ИСПРАВЛЕННОЕ СОЗДАНИЕ БОТА ---
# В новых версиях aiogram настройки (типа parse_mode) передаются через DefaultBotProperties
bot = Bot(
    token=config.BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=storage)