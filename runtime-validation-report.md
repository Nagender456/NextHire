# Runtime Validation Report

**Generated**: 2026-10-26T22:02:00+05:30  
**Target**: `/Users/harshsingh/IdeaProjects/NextHire(Copilot)`

## Summary

| Step | Status | Exit Code | Details |
|------|--------|-----------|---------|
| Startup | PASS | 0 | API and worker started with Uvicorn; `/health`, `/api/v1/health`, and worker `/health` responded successfully |
| Backend integration | PASS | 0 | 55 pytest tests passed |
| Frontend unit tests | PASS | 0 | 3 Vitest tests passed with Vitest 5.0.5 |
| Backend/frontend lint and format | PASS | 0 | Ruff, Ruff format check, and ESLint passed |
| Frontend build | PASS | 0 | Vite production build passed |
| Browser E2E | PASS | 0 | 2 Playwright journeys passed against the live API and Vite server |
| Deployment smoke | PASS | 0 | `smoke.sh` validated API and worker health endpoints; `/metrics` responded with counters |
| Dependency audit | PASS | 0 | `npm audit --audit-level=high` reports 0 vulnerabilities |
| Container validation | UNVERIFIED | 127 | Docker daemon/CLI unavailable in the execution environment |

**Overall**: PASS for all non-Docker checks

## Environment and capability evidence

- Docker: **UNAVAILABLE** — `docker` command is not installed; Compose/image validation was not executable.
- Node.js: **AVAILABLE** — `v26.11.0`.
- Playwright: **AVAILABLE** — Chromium installation and browser tests succeeded.
- Infrastructure tier: **FALLBACK (local in-memory/SQLite)** — Docker was explicitly excluded; API and worker ran locally.
- Browser tier: **PRIMARY (Playwright)** — Node.js and Chromium were available.

## Critical journeys

| Journey | Evidence | Result |
|---------|----------|--------|
| Signup → protected dashboard | `frontend/e2e/stage12.spec.js` | PASS |
| Unauthenticated route guard | `frontend/e2e/stage12.spec.js` | PASS |
| Signup → career entities → search → intelligence → resume → application → analytics | `backend/tests/test_stage12_golden_workflow.py` | PASS |
| Cross-user authorization and session security | `backend/tests/test_stage12_authorization.py`, `backend/tests/test_stage11.py` | PASS |
| External-source review, LaTeX export, and notification delivery | `backend/tests/test_stage12_integrations.py` | PASS |
| API and worker startup smoke | `smoke.sh` | PASS |

## Security and reliability evidence

- Redis-backed fixed-window rate limiter is available through `RATE_LIMIT_BACKEND=redis`; local memory limiting remains the fallback.
- Production settings reject unsafe session, CORS, repository, and rate-limit configuration.
- Request IDs, low-cardinality metrics, structured request logging, CSRF validation, security headers, upload limits, SSRF protection, and ingestion alerts are covered.
- CI now runs backend formatting, dependency audit, frontend dependency audit, Playwright browser tests, and smoke-oriented API startup.

## Known gaps

- Docker-based MongoDB/Redis/container image validation requires a Docker-enabled runner.
- Managed backups, distributed tracing, disaster recovery exercises, load testing, penetration testing, and production rollback execution remain environment-specific operational tasks.
- External GitHub/portfolio/email providers use deterministic local test doubles in automated tests.
- PDF compilation is not installed; deterministic LaTeX export is validated.
- Docker Compose and image builds were intentionally not executed per request.
