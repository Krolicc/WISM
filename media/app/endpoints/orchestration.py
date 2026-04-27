
import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field

from app.schemas.orchestration import OrchestrationRequest
from app.core.celery_app import celery_app

router = APIRouter()

@router.post("/orchestrate", status_code=status.HTTP_202_ACCEPTED)
async def execute_orchestration(
    *, 
    request: OrchestrationRequest = Body(...),
) -> Any:
    """
    Receives a list of long-running tasks and dispatches them to background workers.
    """
    if not request.tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The tasks list cannot be empty."
        )

    task_ids = []
    for task_item in request.tasks:
        task_name = task_item.task
        
        celery_task = celery_app.tasks.get("app.worker.tasks." + task_name)
        
        if not celery_task:
            print(f"CRITICAL: Celery task '{task_name}' is not registered!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Task {task_name} is not configured correctly."
            )

        full_payload = {"ids": task_item.ids}

        async_result = celery_task.delay(full_payload)
        task_ids.append(str(async_result.id))

    return {
        "message": "Orchestration tasks have been successfully queued.",
        "num_tasks_queued": len(task_ids),
        "task_ids": task_ids
    }
