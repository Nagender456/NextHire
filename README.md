# NextHire

NextHire is an AI-powered career management and job discovery platform. The
project is being delivered incrementally according to
[`agiledev.md`](./agiledev.md) and the product specification in
[`projectDescription.md`](./projectDescription.md).

## Repository layout

```text
frontend/       React/Vite web application
backend/        FastAPI HTTP API
workers/        Background-job process boundary
infrastructure/ Local runtime notes
tests/           Cross-service test documentation and fixtures
```

## Local development

1. Copy `.env.example` to `.env`.
2. Start the API:

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

   The API uses deterministic in-memory storage by default. To use a locally
   running MongoDB instance for foundation entities, set
   `REPOSITORY_BACKEND=mongo` in `.env`; configure `MONGODB_URL`,
   `MONGODB_DATABASE`, and `REDIS_URL` for the corresponding services.

3. Start the frontend in another terminal:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Keep the API process running while using the frontend. The Vite development
   proxy forwards `/api` requests to `http://127.0.0.1:8000`; if the API is
   stopped, the frontend now reports a timeout instead of waiting indefinitely.
   Start this command only once. If the terminal reports
   `address already in use`, an API process is already listening on port 8000;
   reuse that process or stop it before starting another one:

   ```bash
   lsof -nP -iTCP:8000 -sTCP:LISTEN
   kill <PID>
   ```

The API liveness endpoint is available at <http://localhost:8000/health>, the
infrastructure readiness endpoint is available at
<http://localhost:8000/health/ready>, and the interactive API documentation is
available at <http://localhost:8000/docs>.
The worker liveness endpoint is available at
<http://localhost:8010/health> when the worker is started separately.

To run the complete local infrastructure stack (MongoDB, Redis, API, worker,
and production-like frontend container), copy `.env.example` to `.env` and
run:

```bash
docker compose -f infrastructure/docker-compose.yml up --build
```

The compose stack uses named volumes for MongoDB and Redis. In hosted
environments, inject the same settings through the platform secret manager
and replace the local services with managed equivalents.

For production deployments, set a unique `SESSION_SECRET`, set
`SESSION_COOKIE_SECURE=true`, and provide a comma-separated
`CORS_ALLOWED_ORIGINS` list containing only the deployed frontend origins. The
API rejects production configuration that uses the local development secret,
insecure session cookies, wildcard CORS, or an empty origin list.

## Quality commands

```bash
make test
make lint
make format-check
```

The first sprint intentionally provides infrastructure and service boundaries
only. Authentication, profiles, and career-domain entities are introduced in
later stages.

## Foundation status

Stage 0 establishes the local services, configuration, health checks, API
conventions, worker boundary, and quality commands. Stage 1 provides the
frontend shell, navigation, API service layer, foundation entities, dashboard
summary, and explicit loading/error/empty states. Stage 2 provides email
authentication, secure sessions, password reset, profile preferences, and a
Google OAuth integration that activates when credentials are configured.
Stage 6 now provides a replaceable local embedding/index boundary, tenant-safe
personalized job retrieval, metadata filters, re-indexing, and deletion
propagation. A hosted embedding provider and durable vector store can be
configured behind the same interfaces without changing the API contract.
Stage 7 adds explainable job intelligence: normalized required/preferred skill
matching, fit percentages, explicit skill gaps, relevant projects, grounded
learning opportunities, and user recommendation feedback.
Stage 8 now provides a fact-grounded structured resume boundary: job-specific
draft generation from confirmed career entities, versioning, validated edits,
approval, deterministic LaTeX export, and approved resume linking to
applications.
Stage 9 now provides application details and lifecycle tracking, including
assessment/interview/withdrawn statuses, job snapshots, notes, deadlines,
next actions, interview dates, resume linkage, and idempotent in-app reminders.
Stage 10 now provides an admin-gated operational overview for users, companies,
jobs, and crawl health, plus user-scoped application and recurring skill-gap
analytics. It also includes company management, job/ingestion monitoring,
AI/workflow activity summaries, audit logs, privacy controls, retention
purges, and user data exports.
