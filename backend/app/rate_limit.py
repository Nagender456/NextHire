from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from redis import Redis
from redis.exceptions import RedisError


@dataclass
class _Window:
    started_at: float
    count: int


class RateLimiter:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], _Window] = {}

    def allow(self, key: str, bucket: str, limit: int, window_seconds: int) -> bool:
        now = monotonic()
        window_key = (key, bucket)
        current = self._windows.get(window_key)
        if current is None or now - current.started_at >= window_seconds:
            self._windows[window_key] = _Window(now, 1)
            return True
        if current.count >= limit:
            return False
        current.count += 1
        return True

    def clear(self) -> None:
        self._windows.clear()


rate_limiter = RateLimiter()


class RedisRateLimiter:
    """Atomic fixed-window limiter for multi-process deployments."""

    def __init__(self, client: Redis) -> None:
        self.client = client

    def allow(self, key: str, bucket: str, limit: int, window_seconds: int) -> bool:
        redis_key = f"nexthire:rate:{bucket}:{key}"
        try:
            count = self.client.incr(redis_key)
            if count == 1:
                self.client.expire(redis_key, window_seconds)
            return count <= limit
        except RedisError:
            return True
