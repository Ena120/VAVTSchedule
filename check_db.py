import asyncio
import os
import sys

# Настройка путей
sys.path.insert(0, os.getcwd())

from app.database.engine import async_session
from app.database.models import Lesson, Group
from sqlalchemy import select

# НАЗВАНИЕ ГРУППЫ С ТВОЕГО СКРИНШОТА
TARGET_GROUP = "Б22М-ММВЯ.1"

async def check():
    async with async_session() as session:
        print(f"🔎 Ищу группу: '{TARGET_GROUP}'")
        
        # 1. Ищем ID группы
        res = await session.execute(select(Group).where(Group.title == TARGET_GROUP))
        group = res.scalar()
        
        if not group:
            print("❌ Группа не найдена в базе! Проверь парсер.")
            return
            
        print(f"✅ Группа найдена! ID: {group.group_id}")
        
        # 2. Ищем ВСЕ уроки этой группы
        res = await session.execute(select(Lesson).where(Lesson.group_id == group.group_id))
        lessons = res.scalars().all()
        
        print(f"📊 Всего уроков в базе: {len(lessons)}")
        
        # 3. Ищем 26 декабря
        lessons_26 = [l for l in lessons if "26.12" in l.day]
        
        if lessons_26:
            print(f"✅ На 26.12 найдено уроков: {len(lessons_26)}")
            for l in lessons_26:
                print(f"   -> {l.time} | {l.subject_raw[:30]}...")
        else:
            print("❌ На 26.12 уроков НЕТ.")
            
            # 4. Покажем примеры других дат
            if lessons:
                print("   Примеры других дат:", [l.day for l in lessons[:3]])

if __name__ == "__main__":
    asyncio.run(check())
