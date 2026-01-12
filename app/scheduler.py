import pytz
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from run_update import process_all_files
from app.loader import bot # Берем бота, чтобы отправлять сообщения
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
msk_tz = pytz.timezone('Europe/Moscow')

async def update_schedule_job():
    """Обёртка для запуска обновления с отчетом Админу"""
    print("⏰ [Scheduler] Запуск планового обновления...")
    try:
        # Запускаем обновление
        await process_all_files()
        print("⏰ [Scheduler] Успех.")
        
        # (Опционально) Можно писать админу, что всё ок
        if ADMIN_ID:
             await bot.send_message(ADMIN_ID, "✅ Расписание успешно обновлено.")
            
    except Exception as e:
        error_msg = f"🆘 <b>CRITICAL ERROR!</b>\n\nВоркер обновления упал:\n<code>{str(e)}</code>"
        print(error_msg)
        
        # Шлем сигнал бедствия Админу
        if ADMIN_ID:
            try:
                await bot.send_message(ADMIN_ID, error_msg, parse_mode="HTML")
            except:
                print("Не удалось отправить сообщение об ошибке админу.")

def setup_scheduler():
    scheduler = AsyncIOScheduler(timezone=msk_tz)
    
    # 09:00 и 17:00
    scheduler.add_job(update_schedule_job, trigger='cron', hour=9, minute=0)
    scheduler.add_job(update_schedule_job, trigger='cron', hour=17, minute=0)
    
    scheduler.start()
    print("✅ Планировщик запущен (09:00 и 17:00 MSK)")