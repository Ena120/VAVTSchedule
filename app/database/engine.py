import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# 1. Загружаем переменные из файла .env
load_dotenv()

# 2. Получаем ссылку на базу
# (Убедись, что в .env файле переменная называется PG_URL)
database_url = os.getenv("PG_URL")

if not database_url:
    raise ValueError("❌ ОШИБКА: Не найдена переменная PG_URL в файле .env")

# 3. Создаем асинхронный движок
engine = create_async_engine(url=database_url, echo=False)

# 4. Создаем фабрику сессий (через неё мы будем делать запросы)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 5. Базовый класс для моделей (User, Group, Lesson наследуются от него)
class Base(DeclarativeBase):
    pass