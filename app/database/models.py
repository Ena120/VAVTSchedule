from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, BigInteger, String
# * import Base to declare tables
# Убедись, что импорт engine правильный (как у тебя было)
from app.database.engine import Base 

# * create a table in database
class User(Base):
    # * real table's name for connection
    __tablename__ = "users"
    # * create columns
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id"), nullable=True) # Сделал nullable=True, чтобы не падало, если группы пока нет
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True)


class Group(Base):
    __tablename__ = 'groups'

    group_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True) # Важно: название группы уникально
    course: Mapped[str] = mapped_column(nullable=True)


class Teacher(Base):
    __tablename__ = 'teachers'

    teacher_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    subject: Mapped[str] = mapped_column(nullable=True)


class Quality(Base):
    __tablename__ = 'quality'

    quality_id: Mapped[int] = mapped_column(primary_key=True)
    quality: Mapped[str] = mapped_column(unique=True)


class Rating(Base):
    __tablename__ = 'rating'

    rating_id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.teacher_id"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    quality_id: Mapped[int] = mapped_column(ForeignKey("quality.quality_id"))
    mark: Mapped[int] = mapped_column()


class Squad(Base):
    __tablename__ = 'squads'

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column()


# --- НОВАЯ ТАБЛИЦА ДЛЯ РАСПИСАНИЯ ---
class Lesson(Base):
    __tablename__ = 'lessons'

    lesson_id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id"))
    
    day: Mapped[str] = mapped_column()       # Пример: "Пн 03.11"
    time: Mapped[str] = mapped_column()      # Пример: "09.00-10.20"
    subject_raw: Mapped[str] = mapped_column() # Полный текст: "Математика (л) Иванов Ауд.101"
    
    # Эти поля можно заполнять позже, если подключим ИИ
    subject_name: Mapped[str] = mapped_column(nullable=True)
    teacher_name: Mapped[str] = mapped_column(nullable=True)
    room: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(nullable=True)