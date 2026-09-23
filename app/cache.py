import json
from typing import Any

import redis

from app.config import settings

# Create a Redis client using the URL from .env
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,  # return str instead of bytes
    socket_connect_timeout=2,
    socket_timeout=2,
)


def cache_get(key: str) -> dict[str, Any] | None:
    """Fetch a JSON-serialized dict from Redis. Returns None on miss or error."""
    try:
        raw = redis_client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except redis.RedisError:
        # Cache is best-effort — if Redis fails, fall back to DB
        return None


def cache_set(key: str, value: dict[str, Any], ttl_seconds: int = 60) -> None:
    """Store a dict as JSON in Redis with a TTL."""
    try:
        redis_client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except redis.RedisError:
        # Log and move on — don't fail the request because Redis is down
        pass


def cache_delete(key: str) -> None:
    """Remove a key from Redis."""
    try:
        redis_client.delete(key)
    except redis.RedisError:
        pass


def driver_latest_key(driver_id: str) -> str:
    """Build a consistent cache key for a driver's latest location."""
    return f"driver:{driver_id}:latest"