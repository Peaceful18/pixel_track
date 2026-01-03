from redis import asyncio as aioredis
from app_config.config import settings

from contextlib import asynccontextmanager


class RedisProvider:
    def __init__(self):
        self.pool = None
        
    def init_pool(self):
        """
        Ініціалізація пулу з'єднань Redis
        """
        self.pool = aioredis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_timeout=5,
            decode_responses=True,
            max_connections=20,
        )
        
    async def close_pool(self):
        """
        Закриття пулу з'єднань Redis
        """
        if self.pool:
            await self.pool.disconnect()
    
    @asynccontextmanager
    async def get_client(self):
        """
        Отримання клієнта Redis з пулу
        """
        if self.pool is None:
            self.init_pool()
        client = aioredis.Redis(connection_pool=self.pool)
        try:
            yield client
        finally:
            await client.aclose()
                
                
redis_provider = RedisProvider()