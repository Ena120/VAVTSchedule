from aiogram import Router

# --- НОВЫЕ ХЕНДЛЕРЫ ---
from .start import start_router
from .menu import menu_router
from .groups.schedule import schedule_router
from .admin import admin_router
from .support import support_router

# --- СТАРЫЕ ХЕНДЛЕРЫ (Legacy) ---
# Оставляем только рассадку (siting), если она нужна. 
# Рейтинг удален.
from .private.siting import get_siting_router

def get_handlers_router() -> Router:
    root_router = Router()

    # 1. Новая логика (Приоритет)
    root_router.include_router(admin_router)
    root_router.include_router(support_router)
    root_router.include_router(start_router)
    root_router.include_router(menu_router)
    root_router.include_router(schedule_router)
    
    # 2. Старая логика
    # root_router.include_router(get_rating_router()) <--- УДАЛЕНО
    root_router.include_router(get_siting_router())

    return root_router