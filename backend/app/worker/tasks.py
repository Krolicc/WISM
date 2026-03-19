import uuid
import asyncio
from celery.utils.log import get_task_logger
from typing import List, Dict, Any
from app.core.celery_app import celery_app
from app.services.generation.orchestration_service import run_orchestration
from app.schemas.orchestration import GenerateActions
from app.database import db_helper

logger = get_task_logger(__name__)

def send_analysis_task(story_id: str):
    """
    Sends a task to the analyzer_service worker via the 'analyzer-queue'.
    This function acts as a proxy, correctly formulating the task message
    so that the backend celery app can send it to a different worker.
    """
    task_name = "app.worker.tasks.trigger_analysis_task"
    queue_name = "analyzer-queue"
    routing_key = "analyzer.trigger"
    logger.info(f"Sending task '{task_name}' for story_id {story_id} to queue '{queue_name}'.")
    
    celery_app.send_task(
        name=task_name,
        args=[story_id],
        queue=queue_name,
        routing_key=routing_key
    )
    logger.info("Task sent successfully.")

@celery_app.task(name="app.worker.tasks.run_orchestration_task")
def run_orchestration_task(actions_data: List[Dict[str, Any]], story_id: str):
    """
    Celery task to run a sequence of content generation actions.
    """
    async def _run_async():
        actions = [GenerateActions.parse_obj(data) for data in actions_data]
        async with db_helper.session_context() as db:
            await run_orchestration(db=db, story_id=uuid.UUID(story_id), actions=actions)
    
    try:
        loop = asyncio.get_event_loop()
        logger.info(f"Starting orchestration for story_id: {story_id}")
        loop.run_until_complete(_run_async())
        logger.info(f"Orchestration finished for story_id: {story_id}")

        # Chain the next step: trigger the analysis task
        # trigger_analysis_task.delay(story_id)

    except Exception as e:
        logger.error(f"Orchestration task failed for story {story_id}: {e}", exc_info=True)
        raise
