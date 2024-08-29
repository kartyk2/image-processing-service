from celery import Celery
from app.config import settings

celery_app = Celery(
    'celery_worker_app',
    broker=f"redis://redis:6379/{settings.redis_db}",
    backend=f"redis://redis:6379/{settings.redis_db}"
)


@celery_app.task
def add(x, y):
    return x + y
