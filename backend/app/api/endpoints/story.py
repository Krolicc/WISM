from typing import Any, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal
from app.services import story_service

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for the generation request body
class StoryGenerationRequest(BaseModel):
    idea: str


@router.post("/", response_model=schemas.StoryRead)
def create_story(
    *, db: Session = Depends(get_db), story_in: schemas.StoryCreate
) -> Any:
    """
    Create new story.
    """
    story = crud.story.create(db=db, obj_in=story_in)
    return story


@router.get("/", response_model=List[schemas.StoryRead])
def read_stories(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve stories.
    """
    stories = crud.story.get_multi(db, skip=skip, limit=limit)
    return stories


@router.get("/{id}", response_model=schemas.StoryRead)
def read_story(*, db: Session = Depends(get_db), id: str) -> Any:
    """
    Get story by ID.
    """
    story = crud.story.get(db=db, id=id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.put("/{id}", response_model=schemas.StoryRead)
def update_story(
    *, db: Session = Depends(get_db), id: str, story_in: schemas.StoryUpdate
) -> Any:
    """
    Update a story.
    """
    story = crud.story.get(db=db, id=id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story = crud.story.update(db=db, db_obj=story, obj_in=story_in)
    return story


@router.delete("/{id}", response_model=schemas.StoryRead)
def delete_story(*, db: Session = Depends(get_db), id: str) -> Any:
    """
    Delete a story.
    """
    story = crud.story.get(db=db, id=id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story = crud.story.remove(db=db, id=id)
    return story


@router.post("/{id}/generate_content", response_model=schemas.StoryRead)
async def generate_story_content(
    *, 
    db: Session = Depends(get_db), 
    id: str,
    request: StoryGenerationRequest
) -> Any:
    """
    Generate and save scenes and panels for a story based on an idea.
    This is a long-running task.
    """
    story = crud.story.get(db=db, id=id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Run the async service function to generate content
    await story_service.generate_and_save_story_content(
        db=db, story=story, story_idea=request.idea
    )

    # Refresh the story object to load the newly created child objects
    db.refresh(story)

    return story
