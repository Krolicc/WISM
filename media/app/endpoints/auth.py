
import uuid
from fastapi import APIRouter, Depends, HTTPException
from app.core.redis_service import redis_service

router = APIRouter()

@router.post("/ws-token", response_model=str)
async def create_ws_auth_token(
    story_id: str,
    db: any = Depends(get_db),
    # current_user: any = Depends(get_current_user)
) -> str:
    """
    Generate a short-lived, single-use token for WebSocket authentication.
    """
    # story = await crud_story.get(db, id=story_id)
    # #  or story.user_id != current_user.id
    # if not story:
    #     raise HTTPException(status_code=404, detail="Story not found or access denied")

    token = str(uuid.uuid4())
    # Сохраняем токен в Redis с коротким временем жизни (e.g., 15 seconds)
    # Ключ: ws_auth_token:<token>, Значение: <story_id>
    await redis_service.set(f"ws_auth_token:{token}", story_id, expire=15)
    
    return token
