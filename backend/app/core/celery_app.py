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
celery_app.conf.task_default_queue = 'default'

# Define all queues for clarity and separation
celery_app.conf.task_queues = (
    Queue('default', routing_key='task.#'),
    Queue('analyzer-queue', routing_key='analyzer.#'),
)

# Route specific tasks to their respective queues
celery_app.conf.task_routes = {
    'app.worker.tasks.run_orchestration_task': {'queue': 'default'},
    'app.worker.tasks.trigger_analysis_task': {'queue': 'analyzer-queue'},
}
