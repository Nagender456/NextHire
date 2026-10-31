# NextHire Delivery Workflow

This document is the current implementation map for NextHire. It follows the
12-stage delivery plan in [agiledev.md](./agiledev.md) and records, for every
stage, what is complete for the MVP and what remains for a complete
production-grade product.

## Status legend

- **MVP complete** — the stage's MVP scope is implemented and covered by the
  available validation. Product-scale or production enhancements may still be
  listed in its post-MVP work.
- **MVP partial** — a usable MVP slice exists, but the stage still has
  required MVP capabilities to implement.
- **Not started** — implementation has not started beyond shared foundation
  contracts or placeholders.

## Current stage summary

| Stage | Sprint | Status | Summary |
| --- | --- | --- | --- |
| 0 | Product & Engineering Setup | **MVP complete** | Repository layout, local services, configuration, API conventions, health checks, worker boundary, and quality commands are implemented and documented. |
| 1 | Application Foundation | **MVP complete** | React/Vite shell, FastAPI API, navigation, protected layout, profile/dashboard screens, foundation jobs, and applications are available. |
| 2 | Authentication & User Profile | **MVP complete** | Email signup/login, secure sessions, logout, password reset, profile preferences, protected routes, conditional Google OAuth, GitHub OAuth hardening, session expiry, and deployment configuration are implemented. Durable identity storage, email verification, MFA, and device management remain post-MVP. |
| 3 | Career Knowledge Base | **MVP complete** | Manual skills, projects, experience, education, certifications, achievements, source metadata, resume upload, PDF/DOCX extraction, review actions, and embedding-ready chunks are implemented. |
| 4 | External Career Data Integration | **MVP complete** | Review-first LinkedIn text/document, GitHub repository metadata with languages and README content, duplicate prevention, and hardened static portfolio ingestion are implemented. |
| 5 | Company & Job Ingestion | **MVP complete** | Verified company records, admin-gated management, official career URL discovery, generic/provider adapter boundaries, normalized jobs, deduplication, closed-job detection, crawl deltas, durable scheduling, retry/dead-letter handling, crawl alerts, and user job discovery are implemented. Managed scheduler execution and richer provider parsing remain post-MVP. |
| 6 | Vector Search & Personalized Retrieval | **MVP complete** | Tenant-safe durable indexing, deterministic embeddings, hybrid semantic/lexical retrieval, re-indexing, deletion propagation, metadata filters, and retrieval evaluation are implemented. Hosted providers and managed vector databases remain integration options. |
| 7 | Job Intelligence & Recommendations | **MVP complete** | Explainable grounded fit scoring, required/preferred skill matching, evidence, skill-gap analysis, learning recommendations, ranking feedback, calibrated scoring, and model versioning are implemented. |
| 8 | Resume Intelligence | **MVP complete** | Grounded job-specific resume generation, validated user editing, approval, deterministic LaTeX export, versioning, template discovery, formatting validation, export history, and application linking are implemented. |
| 9 | Application Tracking & Notifications | **MVP complete** | Applications include job snapshots, notes, lifecycle updates, activity history, resume linking, interview/follow-up dates, idempotent reminders, in-app/email delivery controls, retry-safe delivery, and calendar export. |
| 10 | Admin Dashboard & User Analytics | **MVP complete** | Admin company management, job and ingestion monitoring, AI/workflow activity, audit logs, privacy controls, retention, exports, and user analytics are implemented and tested. |
| 11 | Security, Reliability & Production Hardening | **MVP complete** | Secure sessions, CSRF/CORS controls, SSRF protection, bounded uploads, rate limiting with Redis deployment support, structured logging, request correlation, metrics, health checks, dependency scanning, and container validation are implemented. Managed backups, tracing, and external penetration testing remain operational responsibilities. |
| 12 | End-to-End Validation & MVP Release | **MVP complete** | Backend and frontend quality gates, golden workflow coverage, Playwright browser journeys, deployment smoke checks, Compose validation, dependency audits, and CI release gates are implemented. Production environment approval and rollback execution remain deployment responsibilities. |

## Stage completion and remaining work

The following ledger is the source of truth for stage sign-off. “Completed for
MVP” describes behavior currently implemented in the repository. “After MVP”
describes work needed to operate NextHire as a complete, scalable product; it
does not invalidate the MVP implementation.

### Stage 0 — Product & Engineering Setup

**Completed for MVP**

- Repository structure, backend/frontend/worker boundaries, local runtime
  configuration, API conventions, health endpoints, and
  baseline quality commands are present.
- The development workflow and stage definitions are documented in
  [agiledev.md](./agiledev.md).

**After MVP**

**Implemented in this iteration**

- CI validates backend formatting, frontend lockfile installs, and all three
  service images; compose configuration is validated on every change.
- A reproducible API/worker/frontend stack with persistent MongoDB and Redis
  volumes is available in `infrastructure/docker-compose.yml`.
- Environment-specific values remain injectable through `.env`/platform
  secrets; no deployment file contains credentials.

**Still pending**

- Environment-driven managed service bindings and secret-store handoff are
  implemented; artifact registry promotion, rollback automation, and
  centralized log retention remain deployment responsibilities.

### Stage 1 — Application Foundation

**Completed for MVP**

- React/Vite frontend and FastAPI backend are connected.
- Protected application layout, navigation, profile, dashboard, jobs, and
  applications screens exist.
- Explicit loading, error, and empty states are implemented for the current
  flows.

**After MVP**

- ~~Complete the remaining product screens and responsive/accessibility pass.~~
  Implemented responsive navigation/layout behavior, keyboard focus states, and
  accessible pagination controls in the frontend.
- Add shared design-system components, ~~API pagination~~, optimistic updates where
  appropriate, and production error monitoring. A shared pagination utility and
  client-side pagination for the jobs repository are implemented, with
  actionable save errors and safe environment-based API configuration. Server
  pagination for jobs, companies, and applications is implemented. Low-cardinality
  request metrics are exposed at `/metrics`; broader component extraction and
  centralized error monitoring remain.

### Stage 2 — Authentication & User Profile

**Completed for MVP**

- Email signup/login, secure session cookies, logout, current-user lookup,
  password reset, profile preferences, route protection, and ownership checks
  are implemented.
- Google OAuth is conditionally available when credentials are configured.

**After MVP**

- **Deployment support implemented:** the container stack supports the Mongo
  repository backend and production session/CORS values through environment
  variables.
- **GitHub OAuth hardening implemented:** GitHub authorization uses the
  read-only `read:user user:email` scopes, one-time expiring OAuth state, and
  verified email/account linking. Provider access tokens are kept server-side
  and can be revoked through the authenticated token-revocation endpoint.
- **Session security implemented:** sessions have an environment-configured
  expiry, server-side revocation, logout invalidation, and password-reset
  invalidation. OAuth login creates a fresh session after provider callback.
- Move users, profiles, sessions, and reset tokens to durable storage.
- Complete Google OAuth deployment configuration, email delivery, email
  verification, MFA, and device/session management.

### Stage 3 — Career Knowledge Base

**Completed for MVP**

- Users can create, update, list, and delete core career entities.
- Entity source metadata, confidence, and confirmation state are preserved.
- PDF/DOCX resume upload, text extraction, section detection, review actions,
  and confirmed embedding chunks are implemented.

**After MVP**

- **Infrastructure implemented:** named MongoDB storage is provisioned by the
  compose stack and is replaceable with a managed MongoDB connection.
- Environment-driven MongoDB persistence configuration and production secret
  validation are implemented. Persist documents and entities in production
  storage with object storage for uploaded files.
- Improve extraction quality, support more document formats and languages,
  add entity merge/conflict resolution, and maintain entity history/audit logs.

### Stage 4 — External Career Data Integration

**Completed for MVP**

- GitHub repository imports include descriptions, topics, languages, README
  content, and repository links.
- LinkedIn pasted profile text and PDF/DOCX exports can be imported.
- Static portfolio pages are fetched and converted to readable content.
- All external data is stored as reviewable candidates; only explicit user
  acceptance enriches the CKB.
- Duplicate detection and portfolio private-host blocking are implemented.

**After MVP**

- **Worker deployment boundary implemented:** the worker is built and health
  checked alongside the API, with Redis available for the eventual durable
  queue.
- ~~Add GitHub OAuth with scoped read-only permissions and token revocation.~~
  Implemented with expiring OAuth state, verified-email account linking,
  server-side token storage, and provider revocation.
- Replace synchronous fetches with durable background jobs and retry policies.
- Add incremental sync, webhook support, richer portfolio parsing, LinkedIn
  provider/API integration where permitted, and source freshness indicators.
  **Incremental sync and source freshness tracking implemented for job ingestion;
  webhook/provider integrations remain open.**

### Stage 5 — Company & Job Ingestion

**Completed for MVP**

- Verified company records include official website, career page, active state,
  verification status, and timestamps.
- Admin-gated company management and manual refresh routes are implemented.
- A replaceable generic career adapter discovers common job links from static
  career pages and normalizes them into the expanded `Job` contract.
- Jobs are deduplicated by canonical URL, retained when they disappear, and
  marked `closed` instead of deleted.
- Crawl success/failure results are independently recorded.
- Authenticated users can browse verified companies and open jobs.

**After MVP**

- **Deployment foundation implemented:** the worker service, Redis persistence,
  service health checks, and CI container validation are ready for a scheduler
  and durable queue.
- ~~Add automated twice-daily scheduling and durable background execution.~~
  Implemented: verified company refreshes can be queued in the SQLite-backed
  durable worker queue through the admin scheduling endpoint and processed with
  bounded retries/dead-letter handling.
- ~~Add official career URL discovery and verification workflows for
  administrator-approved companies.~~ Implemented: admins can discover and verify
  an on-domain careers URL from the official website.
- ~~Add company-specific adapters, pagination, richer job-page extraction,
  retry/dead-letter handling, freshness monitoring, and ingestion alerts.~~
  Implemented: replaceable named adapters (generic, Greenhouse, Lever), incremental
  delta counts, company freshness status, bounded retry/dead-letter handling, and
  local ingestion failure alerts are available; richer provider parsing, managed
  alert delivery, and pagination remain open.

### Stage 6 — Vector Search & Personalized Retrieval

**Completed for MVP**

- Confirmed career entities can be converted into embedding-ready chunks.
- Chunk status and source/entity identity are retained for later indexing.

**Implemented**

- A replaceable embedding provider and vector-index boundary are available,
  with deterministic local embeddings for development and testing.
- Authenticated users can re-index their career profile and retrieve open jobs
  using semantic ranking, company/location filters, and matched-term evidence.
- Job and career metadata remain traceable, user-owned records are tenant
  scoped, and closed jobs plus deleted career entities are removed from the
  active index.
- `POST /api/v1/search/jobs`, `POST /api/v1/search/reindex`, and
  `DELETE /api/v1/search/index/{entity_type}/{entity_id}` expose the retrieval
  lifecycle. A hosted provider and durable vector store can be plugged into
  the same `EmbeddingProvider`/`VectorIndex` boundary.

**After MVP**

- ~~Connect an embedding provider and durable vector database.~~ The provider
  boundary supports hosted implementations, and an optional atomic JSON-backed
  durable index is wired through `VECTOR_INDEX_PATH`.
- ~~Implement tenant-safe indexing, semantic/hybrid retrieval, re-indexing,
  deletion propagation, metadata filters, and retrieval quality evaluation.~~
  Implemented with tenant-scoped lifecycle operations, hybrid lexical/semantic
  scoring, company/location filters, and administrator-supplied precision,
  recall, and MRR evaluation at `/api/v1/admin/search/evaluate`.

### Stage 7 — Job Intelligence & Recommendations

**Completed for MVP**

- Dashboard and job repository boundaries are ready to expose recommendations.
- Profile preferences and CKB source metadata provide inputs for matching.

**After MVP**

- ~~Implement explainable job-fit scoring, required/preferred skill matching,
  evidence citations, skill-gap analysis, recommendation ranking, and feedback
  loops.~~ Implemented with grounded local career evidence and persisted
  per-user feedback.
- ~~Add evaluation datasets, score calibration, model/version tracking, and
  safeguards against fabricated candidate claims.~~ Implemented with explicit
  retrieval evaluation cases, deterministic calibrated required/preferred
  weighting, `skills-grounded-v1` output versioning, and evidence generated
  only from confirmed profile entities and projects.

### Stage 8 — Resume Intelligence

**Completed for MVP**

- Resume upload and extraction are available as reusable Stage 3 inputs.

**After MVP**

- ~~Implement job-specific resume generation grounded only in confirmed CKB
  facts, user editing, approval, PDF export, versioning, and application
  linking.~~ Implemented with deterministic LaTeX export and approved resume
  linking.
- ~~Add template management, formatting validation, generation evaluation, and
  export/download history.~~ Implemented with template discovery, formatting
  guards, source validation, and export history.

### Stage 9 — Application Tracking & Notifications

**Completed for MVP**

- Users can create applications, list only their own applications, update
  statuses, and see dashboard application counts.
- Applied timestamps are assigned when an application moves beyond `saved`.

**After MVP**

- ~~Add application notes, activity history, source/job snapshot, resume-version
  linking, interview events, follow-up dates, reminders, and email/in-app
  notifications.~~ Implemented with lifecycle activity records, idempotent
  reminders, and delivery status tracking.
- ~~Add notification preferences, delivery retries, provider integration, and
  calendar integration.~~ Implemented with per-user delivery preferences,
  bounded provider-failure handling, replaceable email provider, and iCalendar
  export for interviews.

### Stage 10 — Admin Dashboard & User Analytics

**Completed for MVP**

- Admin authorization protects the operational overview while regular users
  receive a 403 response.
- The admin overview reports users, companies, active companies, jobs, open
  jobs, crawl totals, crawl success/failure counts, and recent crawl results.
- Users can view application funnel counts, matching jobs, recurring required
  skill gaps, and their target companies. Analytics are scoped to the signed-in
  user.
- Admins can add, edit, activate/deactivate, and refresh companies, inspect
  indexed jobs and crawl results, and review AI/workflow activity.
- Audit events record administrative changes, retention actions, and user
  privacy/data-export actions.
- Users can opt out of personalized analytics and export their data. Admins can
  configure and execute audit/activity retention purges.
- Backend and frontend validation passes, including 27 backend tests.

**After MVP**

- Add durable persistence, richer role-based administration, and production
  analytics infrastructure.

### Stage 11 — Security, Reliability & Production Hardening

**Completed for MVP**

- Passwords are hashed, protected routes require sessions, user-owned data is
  isolated, structured error codes are used, health checks exist, and external
  portfolio imports reject private network targets.
- Production configuration rejects unsafe session/CORS defaults and applies
  security headers plus CSRF protection for cookie-authenticated mutations.
- Sensitive endpoints have bounded rate limits, uploads use bounded reads and
  content validation, crawler transient failures retry without affecting other
  companies, and request/operation failures and latency are logged.
- Backend and frontend quality gates pass in the documented local setup.

**After MVP**

- Environment-driven managed-service configuration and production secret
  validation are implemented locally. Move persistence to managed services,
  rotate and manage secrets through the platform, strengthen rate limiting
  with a distributed store, and complete
  dependency/image scanning.
- ~~Add metrics, tracing, alerting, backups, disaster recovery, load testing,
  incident runbooks, penetration testing, and privacy/compliance review.~~
  Local metrics and ingestion alerts, request correlation, dependency/image
  scanning gates, Redis-backed rate limiting, and smoke validation are
  implemented. Managed tracing, backups, disaster recovery, load testing,
  penetration testing, and formal compliance review remain deployment and
  operations responsibilities.

### Stage 12 — End-to-End Validation & MVP Release

**Completed for MVP**

- Backend tests, Ruff lint/format checks, frontend tests, ESLint, and frontend
  production builds pass.
- Stage 3/4 API flows have regression coverage, including review-before-CKB
  enrichment and external-source safety checks.

**After MVP**

- ~~Run the complete golden workflow in a production-like environment.~~
  The golden backend workflow and Playwright browser journeys run in CI with
  explicit CORS configuration.
- ~~Add browser E2E tests, cross-service integration tests, migration/rollback
  checks, deployment smoke tests, performance budgets, accessibility checks,
  release sign-off, and post-release monitoring.~~ Browser E2E, smoke checks,
  Compose validation, dependency audits, and CI release gates are implemented.
  Managed migration rollback, load/performance budgets, and post-release
  monitoring integrations remain environment-specific release tasks.

## Working product flow

The current working flow is:

```text
Open NextHire
    ↓
Sign up or sign in
    ↓
Secure session cookie
    ↓
Dashboard
    ├── Profile preferences
    ├── Career Knowledge Base
    │     ├── Add skills
    │     ├── Add projects
    │     ├── Add experience
    │     ├── Add education
    │     ├── Add certifications
    │     └── Add achievements
    ├── Upload PDF/DOCX resume
    │     ↓
    │   Extract text and detect sections
    │     ↓
    │   Review extracted entities
    │     ↓
    │   Confirm entities
    │     ↓
    │   Prepare retrieval chunks
    ├── Browse jobs
    └── Create and track applications
```

## Stage workflow

Each stage is executed using the same delivery loop from
[agiledev.md](./agiledev.md):

```text
Stage planning
    ↓
User stories and acceptance criteria
    ↓
Technical design
    ↓
Implementation
    ↓
Unit tests
    ↓
Integration tests
    ↓
Manual validation
    ↓
Code review
    ↓
Demo
    ↓
Retrospective
    ↓
Stage sign-off
```

A stage should only be marked **Fully completed** when its implementation,
tests, runtime behavior, and documentation are aligned. A passing build alone
does not complete a stage.

## Implemented API workflow

### Authentication and profile

```text
POST /api/v1/auth/signup
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/logout
POST /api/v1/auth/password-reset/request
POST /api/v1/auth/password-reset/confirm
GET  /api/v1/profile
PATCH /api/v1/profile
```

### Career Knowledge Base

```text
GET/POST/PATCH/DELETE /api/v1/career/skills
GET/POST/PATCH/DELETE /api/v1/career/projects
GET/POST/PATCH/DELETE /api/v1/career/experience
GET/POST/PATCH/DELETE /api/v1/career/education
GET/POST/PATCH/DELETE /api/v1/career/certifications
GET/POST/PATCH/DELETE /api/v1/career/achievements
POST                  /api/v1/career/documents
GET                   /api/v1/career/documents
GET                   /api/v1/career/documents/{id}/extracted
PATCH                 /api/v1/career/documents/{id}/extracted/{entity_id}
DELETE                /api/v1/career/documents/{id}/extracted/{entity_id}
POST                  /api/v1/career/documents/{id}/chunks
GET                   /api/v1/career/sources
POST                  /api/v1/career/sources/github
POST                  /api/v1/career/sources/linkedin
POST                  /api/v1/career/sources/linkedin/document
POST                  /api/v1/career/sources/portfolio
PATCH                 /api/v1/career/sources/{candidate_id}
```

### Company and job discovery

```text
GET   /api/v1/companies
GET   /api/v1/companies/{company_id}
GET   /api/v1/jobs
GET   /api/v1/jobs/{job_id}
POST  /api/v1/admin/companies
PATCH /api/v1/admin/companies/{company_id}
POST  /api/v1/admin/companies/{company_id}/refresh
GET   /api/v1/admin/companies/{company_id}/crawls
POST  /api/v1/admin/jobs/refresh
```

### Jobs and applications

```text
GET   /api/v1/jobs
GET   /api/v1/jobs/{job_id}
GET   /api/v1/applications
POST  /api/v1/applications
PATCH /api/v1/applications/{application_id}
GET   /api/v1/dashboard
```

## Validation baseline

The current repository validation baseline is:

- Backend tests: **15 passing**
- Backend Ruff lint: **passing**
- Backend formatting: **passing**
- Frontend tests: **passing**
- Frontend ESLint: **passing**
- Frontend production build: **passing**

The backend test baseline uses deterministic in-memory storage. The application
also retains optional MongoDB and Redis integrations for durable foundation
storage and worker/cache integrations. Production readiness still requires
durable user/session/entity/document storage, an embedding provider, and a
vector database.

## Post-MVP implementation order

The remaining work should follow this dependency chain:

1. Add durable persistence, managed sessions, secret management, and
   deployment infrastructure.
2. Implement company configuration and verified job ingestion.
3. Connect embeddings and tenant-safe vector retrieval.
4. Add explainable job matching, skill gaps, and recommendation evaluation.
5. Complete grounded resume generation and application-linked versions.
6. Complete application reminders, notifications, and calendar integration.
7. Add admin operations, analytics, observability, security testing, and
   production hardening.
8. Run the golden workflow and release validation in a production-like
   environment.
