from typing import Any, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import db_helper
from app.services import story_service

router = APIRouter()

class StoryGenerationRequest(BaseModel):
    idea: str


@router.post("/", response_model=schemas.StoryRead)
async def create_story(
    *, db: AsyncSession = Depends(db_helper.session_getter), story_in: schemas.StoryCreate
) -> Any:
    story = await crud.story.create(db=db, obj_in=story_in)
    return story


@router.get("/", response_model=List[schemas.StoryRead])
async def read_stories(
    db: AsyncSession = Depends(db_helper.session_getter), skip: int = 0, limit: int = 100
) -> Any:
    stories = await crud.story.get_multi(db, skip=skip, limit=limit)
    return stories


@router.get("/{id}", response_model=schemas.StoryRead)
async def read_story(*, db: AsyncSession = Depends(db_helper.session_getter), id: str) -> Any:
    story = await crud.story.get(db=db, id=id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.put("/{id}", response_model=schemas.StoryRead)
async def update_story(
    *, db: AsyncSession = Depends(db_helper.session_getter), id: str, story_in: schemas.StoryUpdate
) -> Any:
    story = await crud.story.get(db=db, id=id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story = await crud.story.update(db=db, db_obj=story, obj_in=story_in)
    return story


@router.delete("/{id}", response_model=schemas.StoryRead)
async def delete_story(*, db: AsyncSession = Depends(db_helper.session_getter), id: str) -> Any:
    story = await crud.story.get(db=db, id=id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story = await crud.story.remove(db=db, id=id)
    return story


@router.post("/{id}/generate_content", response_model=schemas.StoryRead)
async def generate_story_content(
    *, 
    db: AsyncSession = Depends(db_helper.session_getter), 
    id: str,
    request: StoryGenerationRequest
) -> Any:
    story = await crud.story.get(db=db, id=id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    await story_service.generate_and_save_story_content(
        db=db, story=story, story_idea=request.idea
    )

    await db.refresh(story)

    return story
