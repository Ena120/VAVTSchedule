from sqlalchemy import select
from app.database.models import Lesson, Group
from app.database.engine import async_session

async def save_schedule_to_db(schedule_data: list):
    """
    Принимает список словарей с расписанием и сохраняет в БД.
    """
    async with async_session() as session:
        print(f"💾 [DB] Начинаю сохранение {len(schedule_data)} занятий...")
        
        # Кэш для групп, чтобы не делать лишних запросов
        # (Запоминаем, какие группы мы уже проверили в этой сессии)
        existing_groups = {} 

        for item in schedule_data:
            group_title = item['group']
            
            # 1. Работаем с Группой
            if group_title not in existing_groups:
                # Проверяем, есть ли такая группа в БД
                result = await session.execute(select(Group).where(Group.title == group_title))
                group = result.scalar()
                
                if not group:
                    # Если нет - создаем
                    group = Group(title=group_title, course="Unknown") 
                    session.add(group)
                    await session.flush() # Получаем ID сразу
                    print(f"➕ [DB] Новая группа: {group_title}")
                
                existing_groups[group_title] = group.group_id
            
            group_id = existing_groups[group_title]

            # 2. Добавляем Урок (Пару)
            new_lesson = Lesson(
                group_id=group_id,
                day=item['day'],
                time=item['time'],
                subject_raw=item['subject_raw']
            )
            session.add(new_lesson)
        
        await session.commit()
        print("✅ [DB] Все данные успешно сохранены!")