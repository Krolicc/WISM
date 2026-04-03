
import asyncio
import json
from typing import Any, Coroutine

import redis.asyncio as redis
from celery import Task
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.config import settings
from app.schemas import orchestration as schemas
from app.database import db_helper
from app.schemas.orchestration import ProcessGenerationChainParams

from app.services import (
    arc_service,
    chapter_service,
    scene_service,
    frame_service
)

logger = get_task_logger(__name__)

# ===================================================================
# 1. REDIS PUBLISHER
# ===================================================================

try:
    redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    logger.info("Redis client for worker task base initialized.")
except Exception as e:
    logger.error(f"FATAL: Could not create Redis client for worker base: {e}")
    redis_client = None

async def publish_status(story_id: str, status: schemas.TaskStatus):
    """Publishes a task status update to a Redis channel."""
    if not redis_client:
        logger.error("Cannot publish status: Redis client is not available.")
        return
    try:
        channel = f"story:{story_id}:updates"
        payload = {"type": "TASK_STATUS", "data": status.model_dump(mode='json')}
        await redis_client.publish(channel, json.dumps(payload))
    except Exception as e:
        logger.error(f"Failed to publish status for story {story_id}: {e}")

# ===================================================================
# 2. BASE NOTIFICATION TASK
# ===================================================================

class NotificationTask(Task):
    """A base Celery Task that sends status notifications via Redis."""
    
    def run_async(self, coro: Coroutine) -> Any:
        """Helper to run an async coroutine from a sync Celery task."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result()
        else:
            return loop.run_until_complete(coro)

    def on_success(self, retval, task_id, args, kwargs):
        """Handle successful task completion."""
        # The payload is always the first argument.
        story_id = args[0].get('story_id')
        if story_id:
            message = json.dumps(retval) if isinstance(retval, dict) else str(retval)
            status = schemas.TaskStatus(task_id=task_id, status="SUCCESS", task_type=self.name, message=message)
            self.run_async(publish_status(story_id, status))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        story_id = args[0].get('story_id')
        if story_id:
            status = schemas.TaskStatus(
                task_id=task_id, 
                status="FAILURE", 
                task_type=self.name, 
                message=f"{type(exc).__name__}: {str(exc)}"
            )
            self.run_async(publish_status(story_id, status))

    def before_start(self, task_id, args, kwargs):
        """Handle task start."""
        story_id = args[0].get('story_id')
        if story_id:
            status = schemas.TaskStatus(task_id=task_id, status="STARTED", task_type=self.name)
            self.run_async(publish_status(story_id, status))

# ===================================================================
# 3. CHAIN GENERATION TASK
# ===================================================================

SERVICE_REGISTRY = {
    "arc": arc_service,
    "chapter": chapter_service,
    "scene": scene_service,
    "frame": frame_service,
}

@celery_app.task(name="tasks.process_generation_chain")
async def process_generation_chain(payload: ProcessGenerationChainParams):
    """
    The single entry point for all asynchronous, hierarchical generation tasks.

    This Celery task initiates an action chain by finding the top-level service
    and passing it the list of actions to execute recursively.

    Args:
        service_name: The string key for the starting service (e.g., "arc").
        actions: The full list of action dictionaries to be executed.
    """
    print(f"Received generation task for service: {service_name}")

    service_name = payload.service_name
    actions = payload.actions

    ServiceClass = SERVICE_REGISTRY.get(service_name)
    if not ServiceClass:
        raise ValueError(f"Unknown service name provided to Celery task: {service_name}")

    async with db_helper.session_context() as db:
        try:
            service_instance = ServiceClass()
            # Kick off the recursive execution of the action chain.
            results = await service_instance.execute_action_chain(db=db, actions=actions)
            print(f"Chain execution completed successfully. Results: {results}")
            await db.commit()
            return results
        except Exception as e:
            print(f"An error occurred during chain execution: {e}")
            await db.rollback()
            # Re-raise the exception to mark the Celery task as failed.
            raise
        finally:
            await db.close()