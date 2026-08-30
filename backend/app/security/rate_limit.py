import asyncio
import time
from collections import defaultdict, deque

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import Settings
from app.exceptions.domain import RateLimitExceededError


class AuthRateLimiter:
    def __init__(self, settings: Settings) -> None:
        self.limit = settings.AUTH_RATE_LIMIT
        self.window = settings.AUTH_RATE_WINDOW_SECONDS
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self._fallback: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> None:
        bucket = f"parkgo:auth-rate:{key}"
        try:
            count = await self.redis.incr(bucket)
            if count == 1:
                await self.redis.expire(bucket, self.window)
            if count > self.limit:
                raise RateLimitExceededError()
            return
        except RedisError:
            pass

        now = time.monotonic()
        async with self._lock:
            values = self._fallback[key]
            while values and values[0] < now - self.window:
                values.popleft()
            if len(values) >= self.limit:
                raise RateLimitExceededError()
            values.append(now)
