# Local infrastructure

NextHire supports MongoDB for durable foundation data and Redis for cache and
worker integrations. The repeatable local stack is defined in
`docker-compose.yml` and uses named volumes so service restarts do not discard
data.

```bash
cp .env.example .env
docker compose -f infrastructure/docker-compose.yml up --build
```

The API, worker, and frontend each have a container health check. Production
deployments should provide `.env` through the platform secret store rather than
committing it. Replace the local MongoDB and Redis services with managed
equivalents and configure backups/retention before production use.

The API accepts the same environment variables in local and managed runtimes:

- `REPOSITORY_BACKEND=memory|mongo`, `MONGODB_URL`, and `MONGODB_DATABASE`
  select the persistence boundary without embedding credentials.
- `REDIS_URL` configures the cache/worker service; `JOB_QUEUE_PATH` points the
  local durable queue at a persistent volume.
- `SESSION_SECRET`, `SESSION_COOKIE_SECURE`, and `CORS_ALLOWED_ORIGINS` are
  required security settings in production. Supply them through the platform
  secret store or process environment, never in compose files or source.
- `METRICS_ENABLED` and `INGESTION_ALERTING_ENABLED` can be disabled for a
  constrained local process. `/metrics` exposes low-cardinality counters and
  admin users can poll `/api/v1/admin/ingestion/alerts` for crawl failures.

These integrations intentionally do not require cloud credentials: local
development continues to use in-memory repositories and SQLite queue state,
while managed MongoDB/Redis and centralized alert routing remain deployment
responsibilities.
