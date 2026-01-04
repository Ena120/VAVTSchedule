import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from run_update import process_all_files

# Указываем часовой пояс Москвы
msk_tz = pytz.timezone('Europe/Moscow')

async def update_schedule_job():
    """Обёртка для запуска обновления"""
    print("⏰ [Scheduler] Запуск планового обновления расписания...")
    try:
        await process_all_files()
        print("⏰ [Scheduler] Обновление завершено успешно.")
    except Exception as e:
        print(f"⏰ [Scheduler] Ошибка при обновлении: {e}")

def setup_scheduler():
    """Настройка и запуск планировщика"""
    scheduler = AsyncIOScheduler(timezone=msk_tz)
    
    # Добавляем задачи (Cron-style)
    # hour=9, minute=0 means 09:00:00
    
    # Утро (09:00 МСК)
    scheduler.add_job(update_schedule_job, trigger='cron', hour=9, minute=0)
    
    # Вечер (17:00 МСК)
    scheduler.add_job(update_schedule_job, trigger='cron', hour=17, minute=0)
    
    # Запускаем планировщик
    scheduler.start()
    print("✅ Планировщик запущен (09:00 и 17:00 MSK)")