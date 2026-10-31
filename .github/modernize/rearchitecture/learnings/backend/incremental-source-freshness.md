# Incremental Source Freshness

Job ingestion can expose source freshness and adapter choice without changing the existing refresh route.

## What Happened
The ingestion store now records the last sync timestamp/status on each company, reports added/updated/closed job deltas, and selects named adapters with generic fallback. Official-site career URL discovery verifies an on-domain candidate before updating the company.

## Takeaway
Keep provider adapters replaceable at the ingestion boundary and compare normalized job models before replacing records; this preserves idempotent refresh behavior while making incremental outcomes observable.

## History
- 2026-10-26 (NextHire/post-mvp-ingestion-20261026): initial
