
import redis.asyncio as redis
from app.core.config import settings

class RedisService:
    def __init__ (self):
        self.redis_pool = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def publish_to_channel(self, channel: str, message: str):
        """Публикует сообщение в указанный канал Redis."""
        await self.redis_pool.publish(channel, message)

    async def set(self, key: str, value: str, expire: int = None):
        """Устанавливает значение ключа. expire — время жизни в секундах."""
        await self.redis_pool.set(key, value, ex=expire)

    async def get(self, key: str) -> str | None:
        """Получает значение ключа. Возвращает None, если ключа нет."""
        return await self.redis_pool.get(key)

    async def delete(self, key: str):
        """Удаляет ключ из Redis."""
        await self.redis_pool.delete(key)

redis_service = RedisService()