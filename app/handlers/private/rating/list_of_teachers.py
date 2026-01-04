from aiogram import Router
from aiogram.types import Message

# Создаем пустой роутер, чтобы система не ломалась при импорте
router = Router()

# Можно добавить временный ответ, если кто-то наткнется на эту функцию
async def get_teachers_name():
    return []

# Если вдруг кто-то попробует вызвать список учителей
@router.message()
async def teachers_stub(message: Message):
    # Просто ничего не делаем или говорим, что функция в разработке
    pass