import redis
import uuid
from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import db_helper
from app.services.generation.story_service import story_service
from app.worker.tasks import send_analysis_task


router = APIRouter()

class StoryCreateRequest(BaseModel):
    prompt: str
    child_count: int = 3

@router.get("/", response_model=List[schemas.StoryRead])
async def read_stories(
    db: AsyncSession = Depends(db_helper.session_getter), 
    skip: int = 0, 
    limit: int = 100
) -> Any:
    stories = await crud.crud_story.get_multi(db, skip=skip, limit=limit)
    return stories

@router.post("/", response_model=schemas.StoryRead)
async def generate_story(
        *,
        db: AsyncSession = Depends(db_helper.session_getter),
        request: StoryCreateRequest
    ) -> Optional[Any]:
        """Creates a new object and recursively generates its children."""
        print(f"Starting generation for a new {story_service.model_name}...")
        # 1. Generate content for the new object itself (1 item)
        llm_response = await story_service._generate_content_from_prompt(db=db, prompt=request.prompt, count=1, generation_mode='single')

        # 2. Create the new object with the generated data
        create_obj_schema = story_service.create_schema(**llm_response.dict())
        new_obj = await story_service.crud_manager.create(db, obj_in=create_obj_schema)
        print(f"  - Created {story_service.model_name} with title '{new_obj.title}'.")

        # 3. Recursively generate new children
        print(f"  - Generating {request.child_count} new child {story_service.child_service.model_name}(s)...")
        await story_service.child_service.generate(
            db,
            parent_id=new_obj.id,
            idea=new_obj.description, # Use the new description as the prompt for children
            count=request.child_count,
        )
        
        refreshed_obj = await story_service.crud_manager.get(db, id=new_obj.id)
        print(f"Full generation for {story_service.model_name} '{refreshed_obj.title}' complete.")
        return refreshed_obj

@router.post("/{story_id}/analyze", status_code=202)
async def queue_story_analysis(
    *, 
    story_id: uuid.UUID, 
    db: AsyncSession = Depends(db_helper.session_getter)
) -> dict:
    """
    Queues an analysis task for a given story using our reliable sender.
    """
    # 1. Verify that the story exists before queueing a task.
    story = await crud.crud_story.get(db=db, id=story_id)
    if not story:
        raise HTTPException(
            status_code=404, 
            detail=f"Story with id {story_id} not found."
        )
    # 2. Dispatch the Celery task using the reliable sender function.
    send_analysis_task(str(story_id))
    # 3. Return a success message.
    return {
        "message": "Analysis task has been successfully queued.",
        "story_id": story_id
    }