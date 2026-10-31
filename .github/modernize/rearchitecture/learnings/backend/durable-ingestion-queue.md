# Durable Ingestion Queue

SQLite is the dependency-free durable queue boundary for scheduled company refreshes.

## What Happened
The post-MVP ingestion scheduler now writes `company_refresh` jobs to a SQLite table,
and workers claim, complete, retry, or dead-letter jobs. The queue path is configurable
through `JOB_QUEUE_PATH`/`JOB_QUEUE_PATH` settings and preserves the existing synchronous
admin refresh route.

## Takeaway
Keep queue state separate from ingestion state and make worker processing idempotent:
company refresh already deduplicates jobs by stable IDs, so retries are safe.

## History
- 2026-10-26 (NextHire/post-mvp-backend-20261026): initial
