from aiogram import Router  # <--- ЭТА СТРОКА ОБЯЗАТЕЛЬНА!

# --- НОВЫЕ ХЕНДЛЕРЫ ---
from .start import start_router
from .menu import menu_router
from .groups.schedule import schedule_router
from .admin import admin_router
from .support import support_router

# --- СТАРЫЕ ХЕНДЛЕРЫ ---
from .private.siting import get_siting_router

def get_handlers_router() -> Router:
    root_router = Router()

    # 1. Приоритетные (Меню, чтобы работала кнопка отмены/меню)
    root_router.include_router(menu_router)

    # 2. Служебные (Админка, Поддержка)
    root_router.include_router(admin_router)
    root_router.include_router(support_router)

    # 3. Основные (Старт, Расписание)
    root_router.include_router(start_router)
    root_router.include_router(schedule_router)
    
    # 4. Legacy (Рассадка)
    root_router.include_router(get_siting_router())

    return root_router