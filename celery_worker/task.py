import time
from celery_worker.worker import celery_app

@celery_app.task(name='add_numbers', queue= "fast")
def add(x, y):
    """A simple task to add two numbers."""
    return x + y

@celery_app.task(name='simulate_long_task_for_a_while', queue= "slow")
def simulate_long_task(seconds):
    """A task that simulates a long-running process."""
    time.sleep(seconds)  # Simulate a long-running task
    return f"Task completed after {seconds} seconds."