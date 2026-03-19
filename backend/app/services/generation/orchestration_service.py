
import uuid
import json
from typing import Any, Dict, List, Optional
from fastapi import Depends
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app import crud, models, schemas
from app.services import chapter_service, frame_service, scene_service
from app.core.websocket_manager import manager
from app.schemas.orchestration import GenerateActions, OrchestrationError

logger = get_task_logger(__name__)

# Map level strings to the corresponding orchestration service instance
LEVEL_TO_SERVICE_MAP = {
    "chapter": chapter_service,
    "scene": scene_service,
    "frame": frame_service,
}

async def publish_to_redis(story_id: str, message: Dict[str, Any]):
    """Publishes a message to the appropriate Redis channel for a story."""
    redis_url = "redis://redis:6379/0"
    try:
        r = await redis.from_url(redis_url)
        channel = f"story:{story_id}:updates"

        print("Publish to Redis")

        await r.publish(channel, json.dumps(message))
        await r.close()
    except Exception as e:
        # Log the error, but don't let it crash the worker
        print(f"Error publishing to Redis: {e}")

async def _handle_notifications(db: AsyncSession, result: Any, story_id_for_ws: str):
    """
    Analyzes the result of an action and sends the appropriate parent-level
    update via WebSockets.
    """
    item_to_notify = None
    notification_type = ""
    id_to_fetch = None

    # If the result is a list, inspect the first item.
    actual_result = result[0] if isinstance(result, list) and result else result

    if isinstance(actual_result, models.Frame):
        notification_type = "SCENE_UPDATED"
        id_to_fetch = actual_result.scene_id
        item_to_notify = await crud.crud_scene.get(db, id=id_to_fetch)
        Schema = schemas.SceneRead
    elif isinstance(actual_result, models.Scene):
        notification_type = "CHAPTER_UPDATED"
        id_to_fetch = actual_result.chapter_id
        item_to_notify = await crud.crud_chapter.get(db, id=id_to_fetch)
        Schema = schemas.ChapterRead
    elif isinstance(actual_result, models.Chapter):
        notification_type = "STORY_UPDATED"
        id_to_fetch = actual_result.story_id
        item_to_notify = await crud.crud_story.get(db, id=id_to_fetch)
        Schema = schemas.StoryRead
    
    if item_to_notify and notification_type:
        print(f"    - Sending WebSocket notification: {notification_type} for ID {id_to_fetch}")
        validated_data = Schema.model_validate(item_to_notify).model_dump(mode='json')
        await publish_to_redis(
            story_id_for_ws,
            {"type": notification_type, "data": validated_data}
        )

async def run_orchestration(
    *,
    db: AsyncSession,
    story_id: uuid.UUID,
    actions: List[GenerateActions],
) -> Dict[str, Any]:
    """
    Executes a sequence of actions and sends real-time updates via WebSockets.
    The logic of PREVIOUS_RESULT is deprecated. Actions are executed sequentially.
    """
    logger.info(f"Начало оркестрации для story_id: {story_id}")
    print(f"Running orchestration for story {story_id} with {len(actions)} actions.")
    
    story_id_str = str(story_id)

    try:
        for action in actions:
            action_type = getattr(action, 'action_type', None)
            level = getattr(action, 'level', None)

            service = LEVEL_TO_SERVICE_MAP.get(level)
            if not service:
                raise OrchestrationError(f"Invalid level '{level}' in action {i}.")
            
            target_method = getattr(service, action_type, None)
            if not target_method or not callable(target_method):
                raise OrchestrationError(f"Action '{action_type}' is not a valid method for level '{level}'.")

            final_params = {"db": db}
            
            params = action.params.model_dump(exclude_none=True)
            final_params.update(params)

            result = await target_method(**final_params)

            result_type_name = type(result).__name__ if result is not None else "None"
            print(f"    - Success. Result type: {result_type_name}")

            # Send notifications based on the result
            await _handle_notifications(db, result, story_id_str)

    except Exception as e:
        print(f"    - FAILED. Orchestration stopped. Error: {e}")
        await manager.send_error_message(story_id_str, str(e))
        raise OrchestrationError(f"Error during orchestration: {e}") from e

    print("Orchestration completed successfully.")
    return {"status": "success"}
