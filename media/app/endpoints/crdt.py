
import logging
import pycrdt
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.y_service import get_root_document_bootstrap, load_entity_data
from app.core.database import db_helper
from app.core.redis_service import redis_service

router = APIRouter()

MESSAGE_SYNC = 0
SYNC_STEP_1 = 1
SYNC_STEP_2 = 2

# Создаем логгер для текущего файла
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Настраиваем вывод в консоль
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, doc_id: str):
        await websocket.accept()
        if doc_id not in self.active_connections:
            self.active_connections[doc_id] = []
        self.active_connections[doc_id].append(websocket)

    def disconnect(self, websocket: WebSocket, doc_id: str):
        if doc_id in self.active_connections:
            self.active_connections[doc_id].remove(websocket)

    async def broadcast(self, message: bytes, doc_id: str, sender: WebSocket):
        if doc_id in self.active_connections:
            for connection in self.active_connections[doc_id]:
                if connection is not sender:
                    await connection.send_bytes(message)


manager = ConnectionManager()


@router.websocket("/ws/media/{doc_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        doc_id: str,
        token: str = None,
        db: Session = Depends(db_helper.session_getter)
):
    redis_key = f"ws_auth_token:{token}"
    stored_story_id = await redis_service.get(redis_key)

    if not stored_story_id:
        raise HTTPException(status_code=401, detail="Unauthorized WebSocket connection")

    await redis_service.delete(redis_key)

    await manager.connect(websocket, doc_id)

    # 1. On connect, get the server's document and send SyncStep1
    root_doc = await get_root_document_bootstrap(db)
    state_vector = root_doc.get_state()

    await websocket.send_bytes(b'\x00\x01' + state_vector)

    try:
        while True:
            # 2. Listen for incoming messages (updates or sync step 2)
            data = await websocket.receive_bytes()
            if not data or len(data) < 2: continue

            message_type = data[0]

            if message_type == MESSAGE_SYNC:
                sync_type = data[1]
                payload = data[2:]

                if sync_type == SYNC_STEP_1:
                    update = root_doc.get_update(payload)
                    if update and len(update) > 0:
                        await websocket.send_bytes(b'\x00\x02' + update)
                    else:
                        pass

                elif sync_type == SYNC_STEP_2:
                    root_doc.apply_update(payload)
                    await manager.broadcast(data, doc_id, websocket)

            elif message_type == 1: continue
            else:
                logger.debug(f"Unknown message type: {message_type}")

                root_doc.apply_update(data)
                await manager.broadcast(data, doc_id, websocket)

    except WebSocketDisconnect:
        # Это то самое место! Просто логируем и выходим из цикла
        print(f"Client disconnected from doc {doc_id} (Normal close)")
    finally:
        # Обязательно удаляем клиента, чтобы не слать broadcast в "никуда"
        manager.disconnect(websocket, doc_id)


@router.get("/yjs/load/{entity_id}")
async def load_entity(entity_id: str, db: Session = Depends(db_helper.session_getter)):
    # Вызывает твою функцию из y_service
    doc = load_entity_data(db, entity_id)
    # Возвращает текущий апдейт этого субдокумента клиенту
    return pycrdt.encode_state_as_update(doc)
