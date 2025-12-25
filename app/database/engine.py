import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# ИСПРАВЛЕНО: теперь ищем PG_URL, как у тебя в .env
db_url = os.getenv("PG_URL")

if not db_url:
    print("⚠️ ОШИБКА: Не найдена переменная PG_URL в файле .env")

# Создаем движок
engine = create_async_engine(db_url, echo=False)

# Создаем фабрику сессий
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Функция создания таблиц
async def async_main():
    """Создает все таблицы в базе данных (если их нет)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)