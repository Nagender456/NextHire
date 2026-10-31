## post-mvp-backend-20261026 Backend post-MVP queue and pagination
- Added a SQLite-backed durable queue with claim, bounded retry, and dead-letter states.
- Added admin ingestion scheduling and worker processing without changing synchronous refresh behavior.
- Added bounded offset/limit pagination to jobs, companies, and applications.
- Ruff format-check fails on pre-existing unformatted backend files; changed files pass formatting.
- Learnings consumed: none.

## auth-hardening-20261026 GitHub OAuth and session security
- Added GitHub OAuth with read-only scopes, expiring one-time state, verified email linking, server-side token retention, and provider revocation.
- Added expiring/revocable sessions; logout and password reset now invalidate server-side sessions.
- Focused auth tests are isolated because the application uses global in-memory stores.
- `make test` and `make lint` pass; format-check still reports pre-existing unformatted backend modules.
- Learnings consumed: [backend/durable-ingestion-queue]

## post-mvp-operations-20261026 Local operations support
- Added dependency-free low-cardinality request metrics and ingestion failure alerts.
- Managed Mongo/Redis configuration remains environment-driven; tests must override
  accidental external `.env` values with local endpoints.
- Full backend/frontend tests pass; repository format-check still reports nine
  pre-existing unformatted files outside this change.
- Learnings consumed: [backend/durable-ingestion-queue]

## post-mvp-ingestion-20261026 Incremental ingestion and career URL discovery
- Added incremental job delta accounting, source freshness fields, replaceable named adapters, and verified official career URL discovery.
- Existing full-suite tests can select an unreachable Mongo backend from environment; focused ingestion tests pass with `REPOSITORY_BACKEND=memory`.
- Repository-wide format-check still reports ten pre-existing unformatted modules; changed modules are formatted.
- Learnings consumed: [backend/durable-ingestion-queue].
