from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: call_command('oil'),  # oil 명령 실행
        CronTrigger(hour=0, minute=5),  # 매일 새벽 00시 05분에 실행
        id='oil_price_fetch_job',
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()

if __name__ == "__main__":
    start_scheduler()
