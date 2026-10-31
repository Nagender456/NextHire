from typing import Any

from fastapi import APIRouter
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from redis import Redis
from redis.exceptions import RedisError

from app.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, Any]:
    """Return a stable liveness response for orchestration and local checks."""
    return {"status": "ok", "service": "nexthire-api"}


@router.get("/health/ready")
async def readiness() -> dict[str, Any]:
    """Report whether configured MongoDB and Redis services are reachable."""
    settings = get_settings()
    dependencies: dict[str, str] = {}

    try:
        with MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=500) as client:
            client.admin.command("ping")
        dependencies["mongodb"] = "ok"
    except PyMongoError:
        dependencies["mongodb"] = "unavailable"

    try:
        redis_client = Redis.from_url(settings.redis_url, socket_connect_timeout=0.5)
        redis_client.ping()
        redis_client.close()
        dependencies["redis"] = "ok"
    except RedisError:
        dependencies["redis"] = "unavailable"

    ready = all(status == "ok" for status in dependencies.values())
    return {
        "status": "ok" if ready else "degraded",
        "service": "nexthire-api",
        "dependencies": dependencies,
    }
