from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import db_helper

router = APIRouter()

@router.post("/", response_model=schemas.CharacterRead)
async def create_character(
    *, db: AsyncSession = Depends(db_helper.session_getter), character_in: schemas.CharacterCreate
) -> Any:
    character = await crud.character.create(db=db, obj_in=character_in)
    return character


@router.get("/", response_model=List[schemas.CharacterRead])
async def read_characters(
    db: AsyncSession = Depends(db_helper.session_getter), skip: int = 0, limit: int = 100
) -> Any:
    characters = await crud.character.get_multi(db, skip=skip, limit=limit)
    return characters
