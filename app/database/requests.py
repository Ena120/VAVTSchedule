from sqlalchemy import select, delete, distinct
from app.database.models import User, Group, Lesson
from app.database.engine import async_session

# ==========================================
# 🛠 АДМИНСКИЕ ФУНКЦИИ
# ==========================================

async def clear_schedule_table():
    async with async_session() as session:
        await session.execute(delete(Lesson))
        await session.commit()

async def save_schedule_to_db(schedule_data: list, faculty: str, course: str):
    if not schedule_data: return

    async with async_session() as session:
        # Кэшируем группы для скорости
        existing_groups_cache = {}
        all_groups = await session.execute(select(Group))
        for g in all_groups.scalars():
            existing_groups_cache[g.title] = g.group_id

        new_lessons = []

        for item in schedule_data:
            group_title = item['group']
            
            # Создаем группу, если её нет
            if group_title not in existing_groups_cache:
                new_group = Group(title=group_title, faculty=faculty, course=course)
                session.add(new_group)
                await session.flush()
                existing_groups_cache[group_title] = new_group.group_id
            
            # Добавляем урок
            new_lesson = Lesson(
                group_id=existing_groups_cache[group_title],
                day=item['day'],
                time=item['time'],
                subject_raw=item['subject_raw']
            )
            new_lessons.append(new_lesson)
        
        session.add_all(new_lessons)
        await session.commit()


# ==========================================
# 📱 ФУНКЦИИ ДЛЯ МЕНЮ
# ==========================================

async def get_faculties():
    async with async_session() as session:
        # distinct - только уникальные названия
        result = await session.execute(select(distinct(Group.faculty)).order_by(Group.faculty))
        return [r for r in result.scalars().all() if r]

async def get_courses_by_faculty(faculty: str):
    async with async_session() as session:
        result = await session.execute(
            select(distinct(Group.course))
            .where(Group.faculty == faculty)
            .order_by(Group.course)
        )
        return result.scalars().all()

async def get_groups_by_filter(faculty: str, course: str):
    async with async_session() as session:
        result = await session.execute(
            select(Group)
            .where(Group.faculty == faculty, Group.course == course)
            .order_by(Group.title)
        )
        return result.scalars().all()


# ==========================================
# 👤 ПОЛЬЗОВАТЕЛЬСКИЕ ФУНКЦИИ
# ==========================================

async def set_user_group(tg_id: int, group_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == tg_id))
        if not user:
            user = User(user_id=tg_id, group_id=group_id)
            session.add(user)
        else:
            user.group_id = group_id
        await session.commit()

async def get_user_group_id(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == tg_id))
        return user.group_id if user else None

async def get_lessons_by_date(group_id: int, date_part: str):
    async with async_session() as session:
        result = await session.execute(
            select(Lesson)
            .where(Lesson.group_id == group_id)
            .where(Lesson.day.ilike(f"%{date_part}%"))
        )
        return result.scalars().all()