from celery import shared_task
import time
from datetime import datetime

@shared_task
def simple_task():
    print("Запущена обычная задача...")
    time.sleep(5)
    print("Обычная задача завершена!")

@shared_task
def scheduled_task():
    now = datetime.now()
    print(f"Запланированная задача выполнена в {now}")
