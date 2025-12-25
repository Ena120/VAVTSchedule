from aiogram import Router

def get_admin_router() -> Router:
    # 1. Импортируем файлы с хендлерами
    from . import newsletter
    from . import upload_schedule  # <--- ДОБАВИЛИ ЭТУ СТРОЧКУ

    router = Router()
    
    # 2. Подключаем их к главному роутеру админа
    router.include_router(newsletter.router)
    router.include_router(upload_schedule.router) # <--- И ЭТУ СТРОЧКУ

    return router