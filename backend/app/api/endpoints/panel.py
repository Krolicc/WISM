from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.endpoints.story import get_db

router = APIRouter()


@router.post("/", response_model=schemas.PanelRead)
def create_panel(*, db: Session = Depends(get_db), panel_in: schemas.PanelCreate) -> Any:
    """
    Create new panel.
    """
    scene = crud.scene.get(db=db, id=panel_in.scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene with id {panel_in.scene_id} not found")
    panel = crud.panel.create(db=db, obj_in=panel_in)
    return panel


@router.get("/", response_model=List[schemas.PanelRead])
def read_panels(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve panels.
    """
    panels = crud.panel.get_multi(db, skip=skip, limit=limit)
    return panels


@router.get("/{id}", response_model=schemas.PanelRead)
def read_panel(*, db: Session = Depends(get_db), id: str) -> Any:
    """
    Get panel by ID.
    """
    panel = crud.panel.get(db=db, id=id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    return panel


@router.put("/{id}", response_model=schemas.PanelRead)
def update_panel(*, db: Session = Depends(get_db), id: str, panel_in: schemas.PanelUpdate) -> Any:
    """
    Update a panel.
    """
    panel = crud.panel.get(db=db, id=id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    panel = crud.panel.update(db=db, db_obj=panel, obj_in=panel_in)
    return panel


@router.delete("/{id}", response_model=schemas.PanelRead)
def delete_panel(*, db: Session = Depends(get_db), id: str) -> Any:
    """
    Delete a panel.
    """
    panel = crud.panel.get(db=db, id=id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    panel = crud.panel.remove(db=db, id=id)
    return panel
