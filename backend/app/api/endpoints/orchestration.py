
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import db_helper
from app.schemas.orchestration import OrchestrationRequest
# We'll need a way to find Celery tasks. This is a common pattern.
from app.core.celery_app import celery_app

router = APIRouter()

@router.post("/{story_id}/orchestrate", status_code=status.HTTP_202_ACCEPTED)
async def execute_orchestration(
    *, 
    story_id: uuid.UUID,
    request: OrchestrationRequest,
    db: AsyncSession = Depends(db_helper.session_getter),
) -> Any:
    """
    Receives a list of long-running tasks for a specific story and dispatches
    them to background workers.
    """
    # 1. Validate that the story exists (your brilliant suggestion in action)
    story = await crud.crud_story.get(db=db, id=story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Story with id {story_id} not found."
        )

    if not request.tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The tasks list cannot be empty."
        )

    # 2. Dispatch each task to the corresponding Celery worker
    task_ids = []
    for task in request.tasks:
        # Construct the full task name, e.g., "app.worker.tasks.generate_arcs_skeleton"
        task_name = task.task.value
        
        celery_task = celery_app.tasks.get(task_name)
        
        if not celery_task:
            # Log this critical error. The system is misconfigured.
            print(f"CRITICAL: Celery task '{task_name}' is not registered!")
            # Optionally, raise an error to stop the entire request
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Task {task_name} is not configured correctly."
            )

        # 3. Combine story_id and task-specific params before sending to worker
        full_payload = {
            "params": task.params.model_dump(mode='json')
        }

        async_result = celery_task.delay(full_payload)
        task_ids.append(str(async_result.id))

    return {
        "message": "Orchestration tasks have been successfully queued.",
        "story_id": str(story_id),
        "num_tasks_queued": len(task_ids),
        "task_ids": task_ids
    }
