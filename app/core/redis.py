import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(
    settings.redis_url or f"redis://{settings.redis_host}:{settings.redis_port}",
    decode_responses=True
)




# import redis.asyncio as redis
# from app.core.config import settings

# redis_client = redis.Redis(
#     host=settings.redis_host,
#     port=settings.redis_port,
#     decode_responses=True
# )