from aiogram import Router

# --- ИМПОРТЫ ---
from .start import start_router
from .menu import menu_router
from .groups.schedule import schedule_router
from .admin import admin_router
from .support import support_router  # <--- ВАЖНО: Импорт файла support

# Старые (если остались)
from .private.siting import get_siting_router

def get_handlers_router() -> Router:
    root_router = Router()

    # --- ПОДКЛЮЧЕНИЕ ---
    # Порядок важен! Support лучше ставить повыше.
    root_router.include_router(admin_router)
    root_router.include_router(support_router) 
    root_router.include_router(start_router)
    root_router.include_router(menu_router)
    root_router.include_router(schedule_router)
    
    # Старое
    root_router.include_router(get_siting_router())

    return root_router