
from typing import Any, List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app import crud
from app.database import db_helper
from app.schemas.orchestration import OrchestrationActions
from app.worker.tasks import run_orchestration_task
from app.schemas.orchestration import CRUDActions, GenerateAction
from app.services import chapter_service, scene_service, frame_service

LEVEL_TO_SERVICE_MAP = {
    "chapter": chapter_service,
    "scene": scene_service,
    "frame": frame_service,
}

router = APIRouter()

@router.post("/{story_id}/orchestrate")
async def execute_orchestration(
    *, 
    story_id: uuid.UUID,
    request: OrchestrationActions,
    db: AsyncSession = Depends(db_helper.session_getter), 
) -> Any:
    """
    Receives a complex, multi-step generation request, validates it,
    and queues it for background processing.
    """

    story = await crud.crud_story.get(db=db, id=story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    try:
        await run_crud_orchestration(
            db=db, 
            story_id=story_id, 
            actions=request.crud
        )
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка на этапе выполнения CRUD: {e}"
        )

    generate_actions_dict = [action.dict() for action in request.generate]
    run_orchestration_task.delay(generate_actions_dict, str(story_id))

    return {"msg": "Orchestration has been successfully queued."}


async def run_crud_orchestration(
    db: AsyncSession, 
    story_id: uuid.UUID, 
    actions: List[CRUDActions]
):
    for action in actions:
        action_type = getattr(action, 'action_type', None)
        level = getattr(action, 'level', None)
        service = LEVEL_TO_SERVICE_MAP.get(level)
        if not service:
            raise OrchestrationError(f"Не найден сервис для уровня '{level}'.")

        target_method = getattr(service.crud_manager, action_type, None)
        if not callable(target_method):
            raise OrchestrationError(f"Метод 'delete' не найден или не является функцией для сервиса '{level}'.")

        final_params = {"db": db}
        params = action.params.model_dump(exclude_none=True)

        final_params.update(params)
        await target_method(db=db, **final_params)
