from celery import Celery
from kombu import Queue
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

# Define the default queue
celery_app.conf.task_default_queue = 'celery'

# Define all queues for clarity and separation. This is the source of truth for queue definitions.
celery_app.conf.task_queues = (
    Queue('celery', routing_key='task.#'),
)

# The import below is sometimes used to ensure task modules are loaded,
# but `include` is the more standard way.
# from app.worker import tasks
