from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import db_helper

router = APIRouter()

@router.post("/", response_model=schemas.SceneRead)
async def create_scene(*, db: AsyncSession = Depends(db_helper.session_getter), scene_in: schemas.SceneCreate) -> Any:
    story = await crud.story.get(db=db, id=scene_in.story_id)
    if not story:
        raise HTTPException(status_code=404, detail=f"Story with id {scene_in.story_id} not found")
    scene = await crud.scene.create(db=db, obj_in=scene_in)
    return scene


@router.get("/", response_model=List[schemas.SceneRead])
async def read_scenes(db: AsyncSession = Depends(db_helper.session_getter), skip: int = 0, limit: int = 100) -> Any:
    scenes = await crud.scene.get_multi(db, skip=skip, limit=limit)
    return scenes


@router.get("/{id}", response_model=schemas.SceneRead)
async def read_scene(*, db: AsyncSession = Depends(db_helper.session_getter), id: str) -> Any:
    scene = await crud.scene.get(db=db, id=id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene


@router.put("/{id}", response_model=schemas.SceneRead)
async def update_scene(*, db: AsyncSession = Depends(db_helper.session_getter), id: str, scene_in: schemas.SceneUpdate) -> Any:
    scene = await crud.scene.get(db=db, id=id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    scene = await crud.scene.update(db=db, db_obj=scene, obj_in=scene_in)
    return scene


@router.delete("/{id}", response_model=schemas.SceneRead)
async def delete_scene(*, db: AsyncSession = Depends(db_helper.session_getter), id: str) -> Any:
    scene = await crud.scene.get(db=db, id=id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    scene = await crud.scene.remove(db=db, id=id)
    return scene
