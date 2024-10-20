from django.apps import AppConfig
from evapp.scheduler import start_scheduler

class EvappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evapp'

    def ready(self):
        # 스케줄러 시작
        start_scheduler()
