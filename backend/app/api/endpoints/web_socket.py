from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.websocket_manager import manager

router = APIRouter()

@router.post("/")
async def send_message():
    await manager.send_info_message("3928b0d3-296d-4da6-8e56-4d17d0a5774e", "!Just a message")
