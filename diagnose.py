import asyncio
import os
import sys
from sqlalchemy import select, func

sys.path.insert(0, os.getcwd())

from app.database.engine import async_session
from app.database.models import Lesson, Group

SEARCH_NAME = "ММВЯ" 

async def diagnose():
    async with async_session() as session:
        print(f"🔎 Ищем все группы, похожие на '{SEARCH_NAME}'...")
        
        result = await session.execute(select(Group).where(Group.title.ilike(f"%{SEARCH_NAME}%")))
        groups = result.scalars().all()
        
        if not groups:
            print("❌ Групп не найдено вообще!")
            return

        print(f"Найдено групп: {len(groups)}")
        print("-" * 30)

        for g in groups:
            # ИСПРАВЛЕНО: Lesson.lesson_id вместо Lesson.id
            lesson_count = await session.scalar(
                select(func.count(Lesson.lesson_id)).where(Lesson.group_id == g.group_id)
            )
            
            # Ищем 26.12
            lessons_26 = await session.execute(
                select(Lesson).where(Lesson.group_id == g.group_id).where(Lesson.day.ilike("%26.12%"))
            )
            lessons_26_count = len(lessons_26.scalars().all())

            print(f"🆔 ID: {g.group_id}")
            print(f"📛 Название: '{g.title}'")
            print(f"📊 Всего уроков: {lesson_count}")
            print(f"📅 Уроков на 26.12: {lessons_26_count}")
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(diagnose())