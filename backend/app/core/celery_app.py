
from celery import Celery
from kombu import Queue
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

# Define the default queue for generation tasks
celery_app.conf.task_default_queue = 'celery'

# Define all queues for clarity and separation
celery_app.conf.task_queues = (
    Queue('celery', routing_key='task.#'),
)

from app.worker import tasks