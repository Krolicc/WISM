import asyncio
import json
from typing import Dict, List

import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        # active_connections: { story_id: [WebSocket, ...] }
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, story_id: str):
        await websocket.accept()
        if story_id not in self.active_connections:
            self.active_connections[story_id] = []
        self.active_connections[story_id].append(websocket)

    def disconnect(self, websocket: WebSocket, story_id: str):
        if story_id in self.active_connections:
            try:
                self.active_connections[story_id].remove(websocket)
            except ValueError:
                pass           

            if not self.active_connections[story_id]:
                del self.active_connections[story_id]

    async def broadcast_to_story(self, story_id: str, message: dict):
        """Sends a message to all connected clients for a specific story."""
        if story_id in self.active_connections:
            for connection in self.active_connections[story_id][:]:
                try:
                    message["story_id"] = story_id
                    await connection.send_json(message)
                except (WebSocketDisconnect, RuntimeError):
                    self.disconnect(connection, story_id)

    async def send_error_message(self, story_id: str, error_message: str):
        payload = {"type": "ERROR", "data": error_message}
        await self.broadcast_to_story(story_id, payload)

    async def send_info_message(self, story_id: str, info_message: str):
        payload = {"type": "INFO", "data": info_message}
        await self.broadcast_to_story(story_id, payload)

manager = ConnectionManager()

async def redis_listener(manager: ConnectionManager):
    """
    Listens to Redis Pub/Sub and calls the manager to broadcast messages.
    This function should be started as a background task when the FastAPI app starts.
    """
    redis_url = "redis://redis:6379/0"
    try:
        r = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        pubsub = r.pubsub()
        # Subscribe to a pattern matching all story update channels
        await pubsub.psubscribe("story:*:updates")
        print("Redis listener connected and subscribed to 'story:*:updates'.")
    except Exception as e:
        print(f"FATAL: Could not connect Redis listener: {e}")
        return
    while True:
        try:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=None)
            if message:
                channel = message['channel']    # e.g., "story:some-uuid-string:updates"
                story_id = channel.split(':')[1]
                data = json.loads(message['data'])
                # Tell the manager to broadcast the message to the right clients
                await manager.broadcast_to_story(story_id, data)
        except Exception as e:
            # Log the error but don't crash the long-running listener
            print(f"Error in Redis listener loop: {e}")
            await asyncio.sleep(1)  # Prevent rapid-fire errors

