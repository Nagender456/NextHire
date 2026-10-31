# Local Operations Observability

Local-safe metrics and ingestion alerts should remain dependency-free and environment-configurable.

## What Happened
NextHire gained a small in-process metrics registry exposed as Prometheus text at
`/metrics`, plus bounded in-memory ingestion failure alerts exposed to admins.
Configuration uses Pydantic environment variables, so managed MongoDB/Redis and
platform secret stores can be bound without source or compose credentials.

## Takeaway
Keep operational signals low-cardinality and safe by default. Local tests should
explicitly override any developer `.env` managed-service URLs to avoid network
timeouts and nondeterminism.

## History
- 2026-10-26 (NextHire/post-mvp-operations-20261026): initial
