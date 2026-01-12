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
        # 1. Собираем уникальные названия групп из файла
        unique_groups_in_file = set(item['group'] for item in schedule_data)
        
        # 2. Кэшируем ID групп (и создаем новые, если их нет)
        groups_cache = {} # { "Б22М...": 15 }
        
        # Получаем все группы из базы
        all_groups_db = await session.execute(select(Group))
        for g in all_groups_db.scalars():
            groups_cache[g.title] = g.group_id

        # Проверяем, все ли группы из файла есть в базе
        for group_title in unique_groups_in_file:
            if group_title not in groups_cache:
                new_group = Group(title=group_title, faculty=faculty, course=course)
                session.add(new_group)
                await session.flush() # Получаем ID сразу
                groups_cache[group_title] = new_group.group_id

        # 3. 🔥 ВАЖНО: Удаляем старое расписание ТОЛЬКО для этих групп
        # Чтобы не стирать всю базу, а обновить только то, что пришло в файле
        target_group_ids = [groups_cache[g] for g in unique_groups_in_file]
        
        if target_group_ids:
            await session.execute(
                delete(Lesson).where(Lesson.group_id.in_(target_group_ids))
            )

        # 4. Записываем новые уроки (теперь дублей не будет)
        new_lessons = []
        for item in schedule_data:
            new_lesson = Lesson(
                group_id=groups_cache[item['group']],
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

async def get_user_info(tg_id: int):
    """
    Возвращает полную информацию о пользователе:
    (Название группы, Факультет, Курс)
    """
    async with async_session() as session:
        # Делаем JOIN таблиц User и Group
        query = select(Group).join(User, User.group_id == Group.group_id).where(User.user_id == tg_id)
        result = await session.execute(query)
        group = result.scalar()
        
        if group:
            return {
                "group": group.title,
                "faculty": group.faculty,
                "course": group.course
            }
        return None

async def get_lessons_for_dates(group_id: int, dates: list):
    """
    Ищет уроки, если день совпадает с одной из дат в списке.
    dates = ['26.12', '27.12', '28.12'...]
    """
    async with async_session() as session:
        # Используем OR для поиска по списку дат
        conditions = [Lesson.day.ilike(f"%{d}%") for d in dates]
        
        # Строим запрос
        query = select(Lesson).where(Lesson.group_id == group_id)
        
        if conditions:
            from sqlalchemy import or_
            query = query.where(or_(*conditions))
        
        # Сортируем по ID (обычно это соответствует хронологии добавления)
        # Или можно не сортировать, если они и так идут по порядку
        result = await session.execute(query)
        return result.scalars().all()

async def get_users_by_filter(faculty: str, course: str):
    """
    Возвращает список user_id студентов, которые подписаны 
    на группы указанного факультета и курса.
    """
    async with async_session() as session:
        # Объединяем таблицы Users и Groups
        query = (
            select(User.user_id)
            .join(Group, User.group_id == Group.group_id)
            .where(Group.faculty == faculty, Group.course == course)
        )
        result = await session.execute(query)
        return result.scalars().all()