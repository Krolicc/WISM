from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.endpoints.story import get_db

router = APIRouter()

@router.post("/", response_model=schemas.SceneRead)
def create_scene(*, db: Session = Depends(get_db), scene_in: schemas.SceneCreate) -> Any:
    """
    Create new scene.
    """
    story = crud.story.get(db=db, id=scene_in.story_id)
    if not story:
        raise HTTPException(status_code=404, detail=f"Story with id {scene_in.story_id} not found")
    scene = crud.scene.create(db=db, obj_in=scene_in)
    return scene


@router.get("/", response_model=List[schemas.SceneRead])
def read_scenes(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve scenes.
    """
    scenes = crud.scene.get_multi(db, skip=skip, limit=limit)
    return scenes


@router.get("/{id}", response_model=schemas.SceneRead)
def read_scene(*, db: Session = Depends(get_db), id: str) -> Any:
    """
    Get scene by ID.
    """
    scene = crud.scene.get(db=db, id=id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene


@router.put("/{id}", response_model=schemas.SceneRead)
def update_scene(*, db: Session = Depends(get_db), id: str, scene_in: schemas.SceneUpdate) -> Any:
    """
    Update a scene.
    """
    scene = crud.scene.get(db=db, id=id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    scene = crud.scene.update(db=db, db_obj=scene, obj_in=scene_in)
    return scene


@router.delete("/{id}", response_model=schemas.SceneRead)
def delete_scene(*, db: Session = Depends(get_db), id: str) -> Any:
    """
    Delete a scene.
    """
    scene = crud.scene.get(db=db, id=id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    scene = crud.scene.remove(db=db, id=id)
    return scene
