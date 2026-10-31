import logging
import secrets
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from redis import Redis

from contextlib import asynccontextmanager

from app.auth_store import auth_store
from app.config import get_settings
from app.health import router as health_router
from app.logging import configure_logging
from app.metrics import metrics
from app.rate_limit import RedisRateLimiter, rate_limiter
from app.routes import auth_router, router as application_router
from app.scheduler import scraper_scheduler

configure_logging()
logger = logging.getLogger("nexthire.requests")
settings = get_settings()
distributed_rate_limiter = (
    RedisRateLimiter(Redis.from_url(settings.redis_url))
    if settings.rate_limit_backend == "redis"
    else None
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    import os
    import sys
    is_testing = "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None
    if not is_testing:
        auth_store.ensure_admin("admin@nexthire.dev", "Admin12345!", "Administrator")
        auth_store.ensure_admin("admin@example.com", "Admin12345!", "Admin")
        scraper_scheduler.start()
    yield
    if not is_testing:
        scraper_scheduler.stop()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="NextHire career management API",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

CSRF_COOKIE = "nexthire_csrf"
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
RATE_LIMITS = {
    "/api/v1/auth/login": (10, 60),
    "/api/v1/auth/signup": (5, 60),
    "/api/v1/auth/password-reset/request": (5, 60),
    "/api/v1/jobs/%s/resumes": (5, 60),
    "/api/v1/jobs/%s/intelligence": (20, 60),
    "/api/v1/admin/companies/%s/refresh": (5, 60),
    "/api/v1/admin/jobs/refresh": (5, 60),
    "/api/v1/career/sources/github": (5, 60),
    "/api/v1/career/sources/portfolio": (5, 60),
}


def _rate_limit_bucket(path: str) -> tuple[str, tuple[int, int]] | None:
    for template, limits in RATE_LIMITS.items():
        prefix, suffix = template.split("%s")
        if path.startswith(prefix) and path.endswith(suffix):
            return template, limits
    return (path, RATE_LIMITS[path]) if path in RATE_LIMITS else None


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    started_at = perf_counter()
    rate_limit = (
        _rate_limit_bucket(request.url.path)
        if settings.app_env.lower() in {"production", "prod"}
        else None
    )
    if rate_limit:
        bucket, (limit, window) = rate_limit
        client = request.client.host if request.client else "unknown"
        limiter = distributed_rate_limiter or rate_limiter
        if not limiter.allow(client, bucket, limit, window):
            response = JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Too many requests. Try again later.",
                    }
                },
                headers={"Retry-After": str(window)},
            )
            logger.warning("rate_limited path=%s client=%s", request.url.path, client)
        else:
            response = None
    else:
        response = None
    csrf_token = request.cookies.get(CSRF_COOKIE)
    if response is None and (
        settings.app_env.lower() in {"production", "prod"}
        and request.method in UNSAFE_METHODS
        and (
            not csrf_token
            or not secrets.compare_digest(
                csrf_token, request.headers.get("X-CSRF-Token", "")
            )
        )
    ):
        response = JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "CSRF_TOKEN_INVALID",
                    "message": "A valid CSRF token is required.",
                }
            },
        )
    elif response is None:
        response = await call_next(request)
    if not csrf_token:
        response.set_cookie(
            CSRF_COOKIE,
            secrets.token_urlsafe(32),
            httponly=False,
            secure=settings.session_cookie_secure,
            samesite=settings.session_cookie_samesite,
            max_age=60 * 60 * 24 * 7,
            path="/",
        )
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    if settings.app_env.lower() in {"production", "prod"}:
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    if settings.metrics_enabled:
        metrics.increment("requests_total")
        metrics.increment(f"responses_{response.status_code}")
        metrics.increment("request_duration_ms_total", int(duration_ms))
    if response.status_code >= 500:
        logger.error(
            "request_failed method=%s path=%s status=%s duration_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
    else:
        logger.info(
            "request_completed method=%s path=%s status=%s duration_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", uuid4().hex)
    return response


app.include_router(health_router)
app.include_router(application_router)
app.include_router(auth_router)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_exception method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=error,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
    )


@app.get("/api/v1/health", tags=["system"])
async def versioned_health() -> dict[str, str]:
    return {"status": "ok", "service": "nexthire-api", "version": "v1"}


@app.get("/metrics", tags=["system"], include_in_schema=False)
async def metrics_endpoint() -> str:
    """Expose low-cardinality Prometheus metrics without external services."""
    return metrics.prometheus()
