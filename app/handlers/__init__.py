from aiogram import Router

# ==========================================
# 1. ИМПОРТ НОВЫХ РОУТЕРОВ (С базой данных)
# ==========================================
# Роутер для команды /start, выбора Факультета -> Курса -> Группы
from .start import start_router as new_start_router

# Роутер для кнопок "Сегодня", "Завтра", "Сменить группу"
# (Судя по твоему скрину, файл лежит в папке groups)
from .groups.schedule import schedule_router as new_schedule_router


# ==========================================
# 2. ИМПОРТ СТАРЫХ РОУТЕРОВ (Legacy)
# ==========================================
# Импортируем только то, что НЕ касается расписания и старта,
# чтобы не сломать новую логику.
from .private.menu import get_menu_router
from .private.rating import get_rating_router
from .private.siting import get_siting_router
from .private.admin import get_admin_router

# Эти старые роутеры нам больше не нужны, так как мы написали свои (новые):
# from .private.start import get_start_router  <-- ЗАМЕНЕНО на new_start_router
# from .private.schedule import get_schedule_router <-- ЗАМЕНЕНО на new_schedule_router
# from .private.groups import get_groups_router <-- ЗАМЕНЕНО логикой в start.py


def get_handlers_router() -> Router:
    """
    Собирает все роутеры в один главный.
    Порядок подключения важен!
    """
    root_router = Router()

    # --- ПОДКЛЮЧАЕМ НОВУЮ ЛОГИКУ (ПРИОРИТЕТ) ---
    root_router.include_router(new_start_router)
    root_router.include_router(new_schedule_router)

    # --- ПОДКЛЮЧАЕМ СТАРУЮ ЛОГИКУ (ДОПОЛНИТЕЛЬНО) ---
    # Меню, Рейтинг, Рассадка, Админка
    root_router.include_router(get_menu_router())
    root_router.include_router(get_rating_router())
    root_router.include_router(get_siting_router())
    root_router.include_router(get_admin_router())

    return root_router