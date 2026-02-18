from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import db_helper

router = APIRouter()

@router.post("/", response_model=schemas.PanelRead)
async def create_panel(*, db: AsyncSession = Depends(db_helper.session_getter), panel_in: schemas.PanelCreate) -> Any:
    scene = await crud.scene.get(db=db, id=panel_in.scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene with id {panel_in.scene_id} not found")
    panel = await crud.panel.create(db=db, obj_in=panel_in)
    return panel


@router.get("/", response_model=List[schemas.PanelRead])
async def read_panels(db: AsyncSession = Depends(db_helper.session_getter), skip: int = 0, limit: int = 100) -> Any:
    panels = await crud.panel.get_multi(db, skip=skip, limit=limit)
    return panels


@router.get("/{id}", response_model=schemas.PanelRead)
async def read_panel(*, db: AsyncSession = Depends(db_helper.session_getter), id: str) -> Any:
    panel = await crud.panel.get(db=db, id=id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    return panel


@router.put("/{id}", response_model=schemas.PanelRead)
async def update_panel(*, db: AsyncSession = Depends(db_helper.session_getter), id: str, panel_in: schemas.PanelUpdate) -> Any:
    panel = await crud.panel.get(db=db, id=id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    panel = await crud.panel.update(db=db, db_obj=panel, obj_in=panel_in)
    return panel


@router.delete("/{id}", response_model=schemas.PanelRead)
async def delete_panel(*, db: AsyncSession = Depends(db_helper.session_getter), id: str) -> Any:
    panel = await crud.panel.get(db=db, id=id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    panel = await crud.panel.remove(db=db, id=id)
    return panel
