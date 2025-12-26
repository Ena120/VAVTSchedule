import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("PG_URL")

if not db_url:
    print("⚠️ ОШИБКА: Не найдена переменная PG_URL в файле .env")

engine = create_async_engine(db_url, echo=False)

# Создаем фабрику сессий
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# --- ИСПРАВЛЕНИЕ ТУТ ---
# Мы делаем копию переменной с именем 'session', чтобы старый код (crud) мог её найти
session = async_session 
# -----------------------

class Base(DeclarativeBase):
    pass

async def async_main():
    """Создает все таблицы в базе данных (если их нет)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)