import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaude_api.settings.production')

app = Celery('applaude_api')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Example of a robust task definition
@app.task(
    bind=True,
    autoretry_for=(Exception,), # Retry on any exception
    retry_kwargs={'max_retries': 5}, # Max 5 retries
    retry_backoff=True, # Exponential backoff
    retry_jitter=True, # Add jitter to avoid thundering herd
    task_acks_late=True, # Acknowledge after task completion
    task_soft_time_limit=60, # Soft time limit 1 minute
    task_time_limit=90 # Hard time limit 1.5 minutes
)
def example_task(self, user_id):
    try:
        # Task logic goes here
        # This task should be idempotent
        print(f"Processing task for user {user_id}")
    except Exception as e:
        # Optionally add to a dead-letter queue here if max retries are exceeded
        print(f"Task failed after multiple retries: {e}")
        # dead_letter_queue.send(self.request)
        raise e
