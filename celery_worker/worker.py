from celery import Celery
from app.config import settings

celery_app = Celery(
    "task-worker",
    broker=f"redis://127.0.0.1:6379/{settings.redis_db}",
    backend=f"redis://127.0.0.1:6379/{settings.redis_db}",
    include=["celery_worker.task"],
    broker_connection_retry_on_startup=True,
)
