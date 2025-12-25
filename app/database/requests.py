from sqlalchemy import select, delete
from app.database.models import User, Group, Lesson
from app.database.engine import async_session

# ==========================================
# ⚙️ ФУНКЦИИ ДЛЯ ОБНОВЛЕНИЯ РАСПИСАНИЯ (АДМИН/СКРИПТ)
# ==========================================

async def clear_schedule_table():
    """
    Полностью очищает таблицу уроков. 
    Нужно вызывать перед загрузкой нового расписания, чтобы избежать дубликатов.
    """
    async with async_session() as session:
        print("🧹 [DB] Очистка старого расписания...")
        await session.execute(delete(Lesson))
        await session.commit()

async def save_schedule_to_db(schedule_data: list):
    """
    Принимает список словарей с расписанием и сохраняет в БД.
    Формат: [{'day': '...', 'time': '...', 'group': '...', 'subject_raw': '...'}, ...]
    """
    if not schedule_data:
        return

    async with async_session() as session:
        print(f"💾 [DB] Сохраняю порцию из {len(schedule_data)} занятий...")
        
        # Кэш для групп, чтобы не делать SELECT на каждую строчку Excel
        # { "Б25Ф-...": 12 (id) }
        existing_groups_cache = {} 

        # Сначала подгрузим все существующие группы в кэш
        all_groups = await session.execute(select(Group))
        for g in all_groups.scalars():
            existing_groups_cache[g.title] = g.group_id

        new_lessons = []

        for item in schedule_data:
            group_title = item['group']
            
            # 1. Определяем ID группы
            if group_title not in existing_groups_cache:
                # Если группы нет в базе и в кэше — создаем
                new_group = Group(title=group_title, course="Unknown") 
                session.add(new_group)
                await session.flush() # Чтобы получить ID до коммита
                
                existing_groups_cache[group_title] = new_group.group_id
                print(f"➕ [DB] Создана новая группа: {group_title}")
            
            group_id = existing_groups_cache[group_title]

            # 2. Подготавливаем урок
            new_lesson = Lesson(
                group_id=group_id,
                day=item['day'],
                time=item['time'],
                subject_raw=item['subject_raw']
            )
            new_lessons.append(new_lesson)
        
        # Массовое добавление уроков (быстрее, чем по одному)
        session.add_all(new_lessons)
        await session.commit()
        print("✅ [DB] Данные сохранены.")


# ==========================================
# 👤 ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
# ==========================================

async def get_all_groups():
    """
    Возвращает список всех групп (объекты), отсортированный по алфавиту.
    Используется для генерации кнопок.
    """
    async with async_session() as session:
        result = await session.execute(select(Group).order_by(Group.title))
        return result.scalars().all()

async def set_user_group(tg_id: int, group_id: int):
    """
    Записывает или обновляет выбранную группу для пользователя.
    """
    async with async_session() as session:
        # Ищем пользователя по Telegram ID
        user = await session.scalar(select(User).where(User.user_id == tg_id))
        
        if not user:
            # Если новый пользователь
            user = User(user_id=tg_id, group_id=group_id)
            session.add(user)
        else:
            # Если старый — обновляем группу
            user.group_id = group_id
        
        await session.commit()

async def get_user_group_id(tg_id: int):
    """
    Получает ID группы, которую выбрал пользователь.
    """
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == tg_id))
        return user.group_id if user else None