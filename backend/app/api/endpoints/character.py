from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.endpoints.story import get_db

router = APIRouter()


@router.post("/", response_model=schemas.CharacterRead)
def create_character(
    *, db: Session = Depends(get_db), character_in: schemas.CharacterCreate
) -> Any:
    """
    Create new character.
    """
    # Ensure the story exists
    story = crud.story.get(db=db, id=character_in.story_id)
    if not story:
        raise HTTPException(status_code=404, detail=f"Story with id {character_in.story_id} not found")
    character = crud.character.create(db=db, obj_in=character_in)
    return character


@router.get("/", response_model=List[schemas.CharacterRead])
def read_characters(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve characters.
    """
    characters = crud.character.get_multi(db, skip=skip, limit=limit)
    return characters


@router.get("/{id}", response_model=schemas.CharacterRead)
def read_character(*, db: Session = Depends(get_db), id: str) -> Any:
    """
    Get character by ID.
    """
    character = crud.character.get(db=db, id=id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.put("/{id}", response_model=schemas.CharacterRead)
def update_character(
    *, db: Session = Depends(get_db), id: str, character_in: schemas.CharacterUpdate
) -> Any:
    """
    Update a character.
    """
    character = crud.character.get(db=db, id=id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    character = crud.character.update(db=db, db_obj=character, obj_in=character_in)
    return character


@router.delete("/{id}", response_model=schemas.CharacterRead)
def delete_character(*, db: Session = Depends(get_db), id: str) -> Any:
    """
    Delete a character.
    """
    character = crud.character.get(db=db, id=id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    character = crud.character.remove(db=db, id=id)
    return character

