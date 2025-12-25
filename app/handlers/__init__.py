from aiogram import Router

# --- ИМПОРТ НАШЕГО НОВОГО РОУТЕРА ---
# Мы берем его из файла app/handlers/start.py
from .start import start_router as db_start_router


def get_handlers_router() -> Router:
    # * import functions with routers
    # Старый старт отключаем, чтобы не мешал новому
    # from .private.start import get_start_router 
    
    from .private.menu import get_menu_router
    from .private.rating import get_rating_router
    from .private.schedule import get_schedule_router
    from .private.groups import get_groups_router
    from .private.siting import get_siting_router
    from .private.admin import get_admin_router

    # * a boss router
    router = Router()

    # --- ПОДКЛЮЧАЕМ НАШ НОВЫЙ РОУТЕР ПЕРВЫМ ---
    # Он будет обрабатывать /start и выдавать кнопки групп из БД
    router.include_router(db_start_router)

    # * made for beauty
    # start_router = get_start_router() # Старый выключен
    menu_router = get_menu_router()
    rating_router = get_rating_router()
    schedule_router = get_schedule_router()
    groups_router = get_groups_router()
    siting_router = get_siting_router()
    admin_router = get_admin_router()

    # * add all routers at the boss router
    # router.include_router(start_router) # Старый выключен
    router.include_router(menu_router)
    router.include_router(rating_router)
    router.include_router(schedule_router)
    router.include_router(groups_router)
    router.include_router(siting_router)
    router.include_router(admin_router)

    return router