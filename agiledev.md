# NextHire — Agile Development Plan

> **Document Status:** Engineering Delivery Plan  
> **Project:** NextHire  
> **Methodology:** Agile, iterative, incremental development  
> **Primary Objective:** Build and validate NextHire through small, independently testable stages, with a working product at the end of every stage.

---

## 1. Purpose

This document defines how NextHire should be developed using an Agile software-development process. It is intended as the developer execution guide after the product requirements in `projectDescription.md` have been agreed upon.

NextHire should not be built as one large implementation. Development should proceed through controlled stages, with every stage producing a working increment.

Core dependency:

```text
Foundation
  ↓
Authentication
  ↓
Career Knowledge Base
  ↓
External Career Data
  ↓
Company & Job Ingestion
  ↓
Embeddings & Retrieval
  ↓
Job Intelligence
  ↓
Resume Intelligence
  ↓
Application Tracking
  ↓
Notifications & Analytics
  ↓
Admin & Hardening
  ↓
End-to-End Validation
```

---

# 2. Agile Development Philosophy

## 2.1 Build the deterministic foundation first

Before complex AI functionality, establish reliable:

- authentication;
- database models;
- APIs;
- file storage;
- background jobs;
- logging;
- error handling;
- authorization.

AI functionality should sit on top of stable product infrastructure.

## 2.2 Every stage produces working software

At the end of each stage:

- code runs;
- implemented features are testable;
- existing functionality remains functional;
- important APIs are documented;
- database changes are documented;
- tests exist for important behavior;
- unfinished work is explicitly recorded.

## 2.3 Prefer vertical slices

Build complete small workflows rather than entire technical layers in isolation.

For example:

```text
User enters skill
  ↓
Frontend
  ↓
API
  ↓
Database
  ↓
Display updated profile
  ↓
Test
```

Then expand the workflow.

## 2.4 Keep AI modular

LLM providers, embedding models, prompts, agents, and retrieval implementations must be replaceable.

The system should not be tightly coupled to one provider.

## 2.5 Human-controlled career data

AI can extract and suggest information, but the user remains the authority over confirmed career facts.

```text
GitHub README
  ↓
AI detects Redis
  ↓
Potential Skill
  ↓
User confirms
  ↓
Confirmed Skill
```

## 2.6 No fabricated resume information

The Resume Agent may:

- rewrite;
- reorder;
- shorten;
- emphasize;
- select;
- optimize.

It must not invent:

- skills;
- projects;
- companies;
- responsibilities;
- achievements;
- certifications;
- metrics;
- technologies;
- experience.

---

# 3. Development Stages

NextHire should be developed in **12 stages**:

```text
Stage 0   Product & Engineering Setup
Stage 1   Application Foundation
Stage 2   Authentication & User Profile
Stage 3   Career Knowledge Base
Stage 4   External Career Data Integration
Stage 5   Company & Job Ingestion
Stage 6   Vector Search & Personalized Retrieval
Stage 7   Job Intelligence & Recommendations
Stage 8   Resume Intelligence
Stage 9   Application Tracking & Notifications
Stage 10  Admin Dashboard & User Analytics
Stage 11  Security, Reliability & Hardening
Stage 12  End-to-End Validation & MVP Release
```

Stages can overlap when their interfaces are stable, but major dependencies should be respected.

---

# 4. Agile Stage Workflow

Each stage should follow:

```text
Stage Planning
  ↓
User Stories
  ↓
Technical Design
  ↓
Implementation
  ↓
Unit Tests
  ↓
Integration Tests
  ↓
Manual Validation
  ↓
Code Review
  ↓
Demo
  ↓
Retrospective
  ↓
Stage Sign-off
```

Do not move forward simply because code exists. The stage must have a usable baseline.

---

# 5. Stage 0 — Product & Engineering Setup

## Goal

Establish the repository, architecture, development environment, coding standards, and engineering conventions.

## Work

### Repository

Recommended structure:

```text
nexthire/
├── frontend/
├── backend/
├── ai/
├── workers/
├── infrastructure/
├── docs/
├── tests/
├── scripts/
├── .env.example
├── README.md
└── docker-compose.yml
```

The exact structure may evolve.

### Git

Use:

```text
main
  ↑
feature/*
bugfix/*
```

Examples:

```text
feature/authentication
feature/career-kb
feature/job-crawler
feature/vector-search
feature/resume-generation
```

### Coding standards

Define:

- naming conventions;
- formatting;
- linting;
- API naming;
- error responses;
- logging conventions;
- environment variables.

### Configuration

Support:

```text
local
development
testing
production
```

Never commit secrets.

### Development infrastructure

Set up required services for local development, such as:

```text
Application
MongoDB / MongoDB Atlas
Redis
AI service
Worker
```

### API conventions

Use versioned APIs:

```text
/api/v1/...
```

Examples:

```text
GET    /api/v1/jobs
GET    /api/v1/jobs/{id}
POST   /api/v1/applications
GET    /api/v1/applications
PATCH  /api/v1/applications/{id}
GET    /api/v1/profile
PATCH  /api/v1/profile
```

### Observability

Create:

```text
GET /health
```

and basic structured logging.

## Definition of Done

- repository created;
- frontend runs;
- backend runs;
- database connectivity works;
- worker infrastructure is reachable;
- CI/test command works;
- formatting/linting works;
- environment configuration documented.

---

# 6. Stage 1 — Application Foundation

## Goal

Create the basic NextHire web application and backend shell.

## Frontend

Implement:

- landing page;
- application layout;
- navigation;
- authenticated layout;
- loading states;
- error states;
- reusable UI components.

## Backend

Implement:

- API application;
- configuration;
- database connection;
- data-access layer;
- service layer;
- API routing;
- global error handling.

## Initial entities

Start with:

```text
User
CareerProfile
Company
Job
Application
```

Add specialized entities when their features are introduced.

## Initial routes

```text
/
 /login
 /signup
 /dashboard
 /profile
 /jobs
 /applications
 /analytics
 /admin
```

## Definition of Done

The website and backend communicate successfully, navigation works, and protected application areas have their initial structure.

---

# 7. Stage 2 — Authentication & User Profile

## Goal

Implement secure authentication and initial personalization.

## Authentication

Implement:

- email/password signup;
- login;
- logout;
- password hashing;
- password recovery/reset;
- Google OAuth;
- session/token management;
- protected APIs.

## Authorization

Initial roles:

```text
USER
ADMIN
```

Every protected endpoint must validate authorization.

## User profile

Support:

```text
Name
Email
Location
Preferred Roles
Preferred Skills
Preferred Locations
Target Companies
```

## Skill prioritization

Allow users to prioritize skills.

Example:

```text
Java         HIGH
Spring Boot  HIGH
AWS          HIGH
Docker       MEDIUM
MongoDB      MEDIUM
```

## Definition of Done

A user can:

1. Register.
2. Log in.
3. Log out.
4. Log in with Google.
5. Edit profile.
6. Set preferred roles.
7. Set preferred skills.
8. Set preferred locations.
9. Set target companies.

---

# 8. Stage 3 — Career Knowledge Base

## Goal

Build the central personalized Career Knowledge Base (CKB).

This is a core domain and should receive careful design.

## CKB structure

```text
CareerProfile
├── Skills
├── Projects
├── Experience
├── Education
├── Certifications
├── Achievements
├── Documents
├── GitHub
├── Portfolio
└── LinkedIn
```

## Manual entry

Users must be able to create/edit:

- skills;
- projects;
- experience;
- education;
- certifications;
- achievements.

## Resume upload

MVP:

```text
PDF
DOCX
```

Pipeline:

```text
Upload
 ↓
Validate
 ↓
Store
 ↓
Parse
 ↓
Extract text
 ↓
Detect sections
 ↓
Extract structured information
 ↓
User review
 ↓
Career Knowledge Base
```

## User review

Show extracted information and allow:

- accept;
- edit;
- delete;
- add.

## Source metadata

Important extracted entities should retain:

```text
sourceType
sourceId
confidence
createdAt
updatedAt
confirmedByUser
```

## Embeddings

Confirmed semantic information can be embedded:

```text
Career Entity
 ↓
Chunking
 ↓
Embedding Service
 ↓
Vector Store
```

Prioritize meaningful semantic content such as project descriptions, experience, resume sections, GitHub README content, portfolio content, and skill descriptions.

## Definition of Done

A user can create and maintain a structured Career Knowledge Base from resume information and manual input, review extracted data, and prepare information for vector retrieval.

---

# 9. Stage 4 — External Career Data Integration

## Goal

Enrich the Career Knowledge Base.

## GitHub

Preferred flow:

```text
Connect GitHub
 ↓
Read-only OAuth
 ↓
Repositories
 ↓
Extract:
  Name
  Description
  README
  Languages
  Topics
 ↓
Analyze
 ↓
Potential skills/projects
 ↓
User confirmation
 ↓
Career Knowledge Base
```

Do not perform full source-code analysis in MVP.

## Portfolio

```text
Portfolio URL
 ↓
Fetch
 ↓
Extract readable content
 ↓
Identify projects/skills/experience
 ↓
User review
 ↓
Career Knowledge Base
```

Start with basic/static pages.

## LinkedIn

Use a replaceable ingestion layer.

Initial reliable implementation may process user-provided LinkedIn profile information/document. If scraping is introduced, isolate it so the method can later be replaced.

## Definition of Done

External sources enrich the CKB without overwriting confirmed manual/user data incorrectly.

---

# 10. Stage 5 — Company & Job Ingestion

## Goal

Create the job-discovery pipeline.

## Company model

Support:

```text
Company
├── Name
├── Official Website
├── Career Page URL
├── Logo
├── Status
├── Verification Status
├── CreatedAt
└── UpdatedAt
```

## Admin company management

Admin can:

- add;
- edit;
- activate/deactivate;
- update career URL;
- view crawl status;
- manually refresh.

## User company discovery

```text
User enters company
 ↓
Search company database
 ↓
Exists?
 ├── Yes → use existing company
 └── No
       ↓
    Web discovery
       ↓
Official career page
       ↓
Verification
       ↓
Add company
```

Only official/verified career sources should be accepted.

## Generic crawler

Build support for:

- career page retrieval;
- job link discovery;
- job page retrieval;
- basic pagination;
- common career-page structures.

## Company-specific adapters

Define a common interface:

```python
class CareerSourceAdapter:
    def discover_jobs(...)
    def parse_job(...)
```

Support:

```text
GenericCareerAdapter
CompanySpecificAdapter
```

## Job normalization

Normalize into:

```text
Job
├── title
├── companyId
├── description
├── responsibilities
├── requiredSkills
├── preferredSkills
├── location
├── employmentType
├── experience
├── applicationUrl
├── sourceUrl
├── externalJobId
├── postedAt
├── lastSeenAt
└── status
```

## Deduplication

Preferred identity:

```text
Company ID + External Job ID
```

Fallback:

```text
Company
+
Normalized Title
+
Location
+
Canonical URL
```

Do not display duplicates.

## Closed jobs

If a previously seen job disappears:

```text
Previously available
 ↓
No longer found
 ↓
Status = CLOSED
```

Do not delete it because applications may reference it.

## Scheduling

Automatic crawling runs twice daily.

Manual refresh uses the same crawling pipeline.

## Definition of Done

Supported company career pages can be crawled, jobs normalized/deduplicated, closed jobs detected, and crawl failures independently recorded.

---

# 11. Stage 6 — Vector Search & Personalized Retrieval

## Goal

Connect user career information to job opportunities semantically.

## Job embeddings

When a job is created/updated:

```text
Normalized Job
 ↓
Prepare semantic text
 ↓
Embedding Model
 ↓
Vector
 ↓
Vector Index
```

## User embeddings

Embed relevant career information:

- resume sections;
- skills;
- projects;
- experience;
- certifications;
- achievements;
- GitHub information;
- portfolio information.

## Metadata

Vectors should be traceable:

```text
embeddingId
entityType
entityId
userId
companyId
jobId
source
createdAt
```

## Retrieval

When a user opens recommendations:

```text
User Career Knowledge
+
Preferred Skills
+
Preferred Roles
+
Preferences
 ↓
Query Representation
 ↓
Vector Search
 ↓
Candidate Jobs
```

## Multi-stage retrieval

Use:

```text
All Jobs
 ↓
Vector Retrieval
 ↓
Candidate Set
 ↓
Skill Matching
 ↓
Detailed Analysis
```

Do not run expensive LLM analysis against every job.

## Preference updates

When preferences change:

```text
Updated Preferences
 ↓
New retrieval query
 ↓
Re-rank existing jobs
```

No new crawl is required for already stored jobs.

## Definition of Done

The recommendation page can retrieve semantically relevant jobs for a specific user.

---

# 12. Stage 7 — Job Intelligence & Recommendations

## Goal

Turn retrieved jobs into explainable recommendations.

## JD analysis

Extract:

- title;
- required skills;
- preferred skills;
- responsibilities;
- qualifications;
- experience requirements where available;
- location;
- relevant requirements.

## Skill normalization

Create a normalization strategy for aliases and equivalent terms.

Examples:

```text
JS → JavaScript
Node → Node.js
ReactJS → React
```

Context should be considered where terms are ambiguous.

## Skill matching

MVP score:

```text
Matched Relevant Skills
----------------------- × 100
Total Relevant Skills
```

Where possible, required and preferred skills should be distinguished.

## Recommendation threshold

```text
Score >= 60%
 ↓
Recommended

Score < 60%
 ↓
Lower Match
 ↓
Still explorable
```

The score must not be artificially changed when the user chooses to pursue a low-fit job.

## Matched skills

Display:

```text
✓ Java
✓ Spring Boot
✓ MongoDB
✓ Docker
```

## Skill gaps

Display:

```text
⚠ Kubernetes
⚠ Redis
```

## Relevant projects

Retrieve the user's projects that support the job requirements.

## RAG explanation

Build grounded context:

```text
User Career Evidence
+
Job Requirements
+
Matched Skills
+
Relevant Projects
+
Skill Gaps
```

Use this context for LLM reasoning and explanation.

## Learning recommendations

Use identified gaps to provide:

- skill/topic;
- why it matters;
- suggested resources;
- recommended progression.

## Definition of Done

A user can inspect a job and understand:

- fit percentage;
- matched skills;
- missing skills;
- relevant projects;
- recommendation reason;
- learning opportunities.

---

# 13. Stage 8 — Resume Intelligence

## Goal

Generate grounded, job-specific versions of the user's resume.

## Entry point

```text
User selects job
 ↓
Generate Tailored Resume
```

## Context

Retrieve:

```text
Existing Resume
+
Career Knowledge Base
+
Job Description
+
Matched Skills
+
Skill Gaps
+
Relevant Projects
+
Relevant Experience
```

## Resume Agent

The agent determines:

- relevant projects;
- relevant experience;
- skills to emphasize;
- content to rewrite;
- content to remove;
- wording improvements.

## Hard factual rule

Every factual statement must be traceable to the user's Career Knowledge Base.

## Structured generation

Do not rely on unrestricted LLM-generated LaTeX.

Prefer:

```text
LLM
 ↓
Structured Resume JSON
 ↓
Validation
 ↓
LaTeX Template Renderer
 ↓
.tex
```

## Templates

Default:

> Jake's Resume LaTeX template.

Optional:

> User-provided LaTeX template.

## LaTeX compilation

```text
Structured Resume
 ↓
Template
 ↓
.tex
 ↓
Controlled LaTeX compiler
 ↓
PDF
```

Compilation must happen in an isolated/controlled environment.

## Validation

Check:

- compilation success;
- required fields;
- valid PDF;
- no placeholders;
- basic ATS keyword coverage;
- obvious formatting failures.

## Versioning

Each generated resume should store:

```text
ResumeVersion
├── userId
├── sourceResumeId
├── targetJobId
├── templateId
├── generatedAt
├── fileReference
├── version
└── metadata
```

## Definition of Done

A user can select a job, generate a grounded tailored resume, receive a valid PDF, and later identify the exact resume version.

---

# 14. Stage 9 — Application Tracking & Notifications

## Goal

Centralize application history and reminders.

## Application creation

MVP:

```text
User finds job
 ↓
Prepares resume
 ↓
User applies manually
 ↓
User confirms application
 ↓
Application record
```

## Statuses

```text
Saved
Applied
Assessment
Interview
Offer
Rejected
Withdrawn
```

## Application details

Store:

- application date;
- job;
- company;
- status;
- application URL;
- resume version;
- notes;
- deadline;
- next action;
- interview date.

## Resume relationship

Every applicable application should reference the exact resume version used.

## Reminder engine

Automatically generate reminders for:

- assessment deadlines;
- interviews;
- application deadlines;
- next actions.

## Email service

Use a notification abstraction:

```text
NotificationService
 ↓
EmailProvider
```

Avoid coupling email logic directly into unrelated services.

## Duplicate notifications

Track notification delivery to prevent unintended repeated reminders.

## Definition of Done

Users can record applications, link resume versions, update statuses, add important dates, and receive automated email reminders.

---

# 15. Stage 10 — Admin Dashboard & User Analytics

## Goal

Provide operational visibility and useful user analytics.

## Admin dashboard

### Company management

- total companies;
- active/inactive companies;
- add/edit companies.

### Crawler monitoring

- last crawl;
- status;
- successful crawls;
- failed crawls;
- jobs discovered.

### AI/system visibility

- AI usage;
- AI workflow activity;
- basic processing information.

## User analytics

Display useful metrics:

```text
Jobs Discovered
Matching Jobs
Saved Jobs
Applications
Interviews
Offers
Rejected Applications
Skill Gaps
Target Companies
```

## Application funnel

```text
Jobs Discovered
 ↓
Relevant Jobs
 ↓
Saved
 ↓
Applied
 ↓
Interview
 ↓
Offer
```

## Skill-gap analytics

Example:

```text
Top Missing Skills

AWS          8 jobs
Kubernetes   6 jobs
Redis        4 jobs
```

## Definition of Done

Admins can manage companies and monitor job ingestion. Users can understand their application activity and recurring skill gaps.

---

# 16. Stage 11 — Security, Reliability & Production Hardening

## Goal

Harden the MVP for reliable use.

Security must also be considered throughout earlier stages; this stage consolidates final hardening.

## Authentication security

Verify:

- secure password hashing;
- secure session/token handling;
- safe OAuth;
- protected endpoints;
- reasonable account-recovery behavior.

## Authorization

Test that:

```text
User A
 ↓
cannot access
 ↓
User B's:
  Career Data
  Documents
  Applications
  Resumes
  Embeddings
```

## File security

Uploaded files should be:

- type validated;
- size limited;
- securely stored;
- access controlled;
- safely processed.

## AI security

Protect against prompt injection from:

- job descriptions;
- GitHub README files;
- portfolio content;
- uploaded documents.

External text is **untrusted data**, not trusted system instructions.

## LLM cost control

Use:

- token limits;
- appropriate model selection;
- caching where useful;
- retrieval before generation;
- batching where useful;
- AI usage logging.

## Rate limiting

Protect endpoints such as:

```text
Login
Signup
Resume Generation
JD Analysis
Manual Crawl
GitHub Sync
Portfolio Analysis
```

## Crawler reliability

A failure in one company must not stop all other companies.

Example:

```text
Company A → SUCCESS
Company B → FAILED
Company C → SUCCESS
```

## Retry policy

Retry transient errors.

Do not endlessly retry persistent failures.

## Observability

Track:

- request failures;
- crawler failures;
- AI failures;
- resume-generation failures;
- queue failures;
- email failures;
- processing latency.

## Definition of Done

Security tests pass, major operations are observable, and isolated failures do not bring down unrelated functionality.

---

# 17. Stage 12 — End-to-End Validation & MVP Release

## Goal

Validate the complete product against the golden workflow.

## Golden user journey

```text
Signup
 ↓
Resume / LinkedIn
 ↓
Manual Career Information
 ↓
GitHub
 ↓
Portfolio
 ↓
Career Knowledge Base
 ↓
User Confirmation
 ↓
Preferences
 ↓
Target Companies
 ↓
Company Discovery
 ↓
Job Crawling
 ↓
Normalization
 ↓
Deduplication
 ↓
Job Embedding
 ↓
Recommendation Retrieval
 ↓
Skill Matching
 ↓
Fit Score
 ↓
JD Analysis
 ↓
Skill Gap
 ↓
Relevant Projects
 ↓
Resume Tailoring
 ↓
LaTeX
 ↓
PDF
 ↓
Resume Version
 ↓
Manual Application
 ↓
Application Tracking
 ↓
Reminder
 ↓
Analytics
```

## Test profiles

Create realistic profiles:

### Backend candidate

```text
Java
Spring Boot
MongoDB
AWS
Docker
```

### Python candidate

```text
Python
FastAPI
Django
PostgreSQL
AWS
```

### Low-match candidate

Use a profile with minimal overlap to validate the 60% threshold.

## Test jobs

Include:

1. high-match;
2. medium-match;
3. low-match;
4. required/preferred skill mix;
5. duplicate job;
6. closed job;
7. malformed job;
8. crawler failure;
9. missing fields.

## Resume tests

Test:

- PDF;
- DOCX;
- incomplete resume;
- long resume;
- missing projects;
- missing experience;
- Jake's Resume template;
- user-provided LaTeX template;
- compilation failure;
- unsupported content.

## AI evaluation

Evaluate:

### Skill extraction

- precision;
- recall;
- correctness.

### Job matching

- relevant jobs rank highly;
- irrelevant jobs rank lower.

### JD analysis

- required skills;
- preferred skills;
- responsibilities;
- skill gaps.

### Resume tailoring

- no fabricated information;
- relevant projects selected;
- target skills emphasized;
- content grounded in CKB.

---

# 18. AI Evaluation Strategy

AI functionality requires dedicated evaluation rather than only unit tests.

Create:

```text
eval/
├── skill_extraction/
├── job_matching/
├── jd_analysis/
├── resume_tailoring/
└── learning_recommendations/
```

Each case should contain:

```text
Input
Expected Behavior
Observed Output
Pass/Fail
Notes
```

## Resume hallucination test

If:

```text
User:
Java
Spring Boot
MongoDB
```

and JD requires:

```text
Kubernetes
AWS
Redis
```

the generated resume must not claim those missing skills as existing user skills.

---

# 19. Crawler Testing

Every crawler should be tested against:

- valid page;
- empty page;
- malformed HTML;
- changed structure;
- duplicate jobs;
- missing job ID;
- missing location;
- closed job;
- timeout;
- HTTP error;
- blocked page.

Each crawler should have independent failure handling.

---

# 20. Background Job Rules

Long-running operations should be asynchronous.

Examples:

- resume parsing;
- GitHub import;
- portfolio extraction;
- company crawling;
- job processing;
- embedding generation;
- resume generation;
- PDF compilation;
- email delivery.

Use states such as:

```text
QUEUED
PROCESSING
COMPLETED
FAILED
```

Workers should:

- be idempotent where possible;
- record failures;
- retry transient failures;
- avoid duplicate processing;
- expose processing status.

---

# 21. API Development Rules

APIs should:

- use versioning;
- validate inputs;
- return consistent errors;
- enforce authorization;
- avoid leaking internal exceptions;
- support pagination;
- use idempotency where appropriate;
- document request/response schemas.

Example:

```json
{
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "The requested job could not be found."
  }
}
```

---

# 22. Database Development Rules

Before changing a database model:

1. Identify dependent services.
2. Update models.
3. Update indexes.
4. Test compatibility.
5. Verify existing data.
6. Update documentation.

Important indexes should cover:

- user IDs;
- company IDs;
- job status;
- company/job relationships;
- application user/job;
- timestamps;
- crawl status.

---

# 23. AI Development Rules

Avoid giant prompts.

Prefer:

```text
Input
 ↓
Validation
 ↓
Retrieval
 ↓
Structured Extraction
 ↓
Deterministic Logic
 ↓
LLM Reasoning
 ↓
Structured Output
 ↓
Validation
 ↓
Persistence
```

Whenever deterministic logic can replace an LLM call, prefer the deterministic implementation.

---

# 24. Prompt Management

Treat prompts as versioned engineering assets.

Example:

```text
prompts/
├── jd_analysis_v1
├── skill_extraction_v1
├── job_explanation_v1
├── resume_selection_v1
├── resume_generation_v1
└── learning_recommendation_v1
```

Where useful, store the prompt/model version alongside AI-generated artifacts for debugging and evaluation.

---

# 25. Retrieval Evaluation

Evaluate the retrieval system separately from the LLM.

Measure:

### Recall

Are relevant jobs retrieved?

### Precision

Are retrieved jobs actually relevant?

### Ranking quality

Do stronger matches appear near the top?

---

# 26. Stage Dependencies

Respect this primary dependency chain:

```text
Authentication
      ↓
Career Knowledge Base
      ↓
Career Embeddings
      ↓
Company Management
      ↓
Job Crawling
      ↓
Job Embeddings
      ↓
Vector Retrieval
      ↓
Skill Matching
      ↓
JD Analysis
      ↓
Resume Tailoring
      ↓
Application Tracking
      ↓
Analytics
```

Parallel development is allowed after stable interfaces are defined.

---

# 27. Do Not Build These Early

Do not prioritize:

- autonomous browser agents;
- browser-based application automation;
- full GitHub source-code analysis;
- many job sources;
- mobile application;
- sophisticated career prediction;
- complicated agent-to-agent conversations;
- platform-wide analytics;
- advanced salary prediction.

The objective is a reliable vertical MVP.

---

# 28. Technical Debt

Maintain a technical-debt backlog.

Examples:

```text
TODO:
- Improve portfolio JS rendering
- Improve skill taxonomy
- Improve duplicate detection
- Add crawler adapters
- Add advanced ATS analysis
- Optimize embedding costs
- Add more job sources
```

Known problems should be documented rather than silently ignored.

---

# 29. Stage Review Template

At the end of each stage:

```text
Stage:
Date:

Completed:
- ...

Not Completed:
- ...

Known Issues:
- ...

Technical Debt:
- ...

Tests:
- ...

AI Evaluation:
- ...

Performance:
- ...

Security:
- ...

Demo Result:
- ...

Decision:
GO / FIX / HOLD
```

---

# 30. Major Milestones

## Milestone 1 — Career Foundation

Stages:

```text
0 → 1 → 2 → 3
```

Result:

> A user can authenticate and build a usable Career Knowledge Base.

## Milestone 2 — Opportunity Intelligence

Stages:

```text
4 → 5 → 6 → 7
```

Result:

> NextHire can discover jobs and determine which opportunities match the user.

## Milestone 3 — Application Preparation

Stages:

```text
8 → 9
```

Result:

> NextHire can tailor resumes and manage application history.

## Milestone 4 — Productization

Stages:

```text
10 → 11 → 12
```

Result:

> NextHire becomes a demonstrable, tested, hardened MVP.

---

# 31. Priority System

If development time becomes constrained:

## P0 — Must Have

```text
Authentication
Career Knowledge Base
Resume parsing
Manual profile editing
Company management
Job crawling
Job storage
Job deduplication
Embeddings
Vector retrieval
Skill matching
Fit score
JD analysis
Skill gaps
Resume tailoring
LaTeX → PDF
Resume versioning
Application tracking
```

## P1 — Important

```text
GitHub integration
Portfolio integration
Learning recommendations
Email notifications
Admin crawl monitoring
User analytics
```

## P2 — Nice to Have

```text
Advanced LinkedIn integration
Advanced ATS validation
Advanced ranking
Advanced portfolio rendering
Additional job sources
```

---

# 32. MVP Feature Freeze

Before the final release period, declare an MVP feature freeze.

After feature freeze:

```text
No new major features.
```

Only:

- bug fixes;
- security fixes;
- reliability fixes;
- performance improvements;
- critical UX corrections.

This prevents scope creep near the final demonstration.

---

# 33. Final Engineering Acceptance Criteria

NextHire MVP is complete when a real test user can:

1. Create an account.
2. Authenticate using supported methods.
3. Provide a resume or LinkedIn information.
4. Add and edit career information manually.
5. Build a Career Knowledge Base.
6. Connect GitHub.
7. Provide a portfolio.
8. Select preferred roles, skills, locations, and companies.
9. Discover supported company career pages.
10. Retrieve jobs.
11. View deduplicated active jobs.
12. Receive personalized recommendations.
13. See an explainable skill-fit percentage.
14. See matched and missing skills.
15. See relevant projects.
16. Receive learning recommendations.
17. Generate a tailored resume.
18. Receive a valid LaTeX-generated PDF.
19. Maintain resume versions.
20. Apply manually through the company website.
21. Record and track the application.
22. Update application status.
23. Receive automated email reminders.
24. View career/application analytics.
25. Allow administrators to manage companies and monitor job ingestion.

---

# 34. Final Engineering Principles

The development team should consistently follow these principles:

1. Build incrementally.
2. Keep every stage demonstrable.
3. Build reliable data foundations before complex AI.
4. Treat the Career Knowledge Base as a first-class domain.
5. Retrieve before generating.
6. Use vector search for semantic retrieval.
7. Use deterministic logic for explainable scoring.
8. Use LLMs for reasoning and generation where they provide real value.
9. Keep agents specialized and modular.
10. Never fabricate career information.
11. Keep user-confirmed facts distinct from AI suggestions.
12. Make recommendations explainable.
13. Preserve resume versions.
14. Preserve application history.
15. Make crawler failures independent.
16. Treat external content as untrusted input.
17. Keep expensive operations asynchronous.
18. Evaluate AI with representative datasets.
19. Test retrieval separately from generation.
20. Control MVP scope.
21. Maintain working software after every stage.
22. Optimize for a reliable end-to-end career workflow rather than disconnected AI demonstrations.

---

# 35. Final Golden MVP Workflow

The final implementation should demonstrate this complete scenario:

```text
User
 ↓
Registration
 ↓
Resume / LinkedIn
 ↓
Manual Career Information
 ↓
GitHub / Portfolio
 ↓
Career Knowledge Base
 ↓
User Confirmation
 ↓
Career Preferences
 ↓
Target Companies
 ↓
Company Career Sources
 ↓
Twice-Daily Job Crawling
 ↓
Job Extraction
 ↓
Normalization
 ↓
Deduplication
 ↓
Job Storage
 ↓
Job Embeddings
 ↓
User Opens Recommendations
 ↓
Vector Retrieval
 ↓
Skill Matching
 ↓
Fit Score
 ↓
JD Analysis
 ↓
Matched Skills
 ↓
Skill Gaps
 ↓
Relevant Projects
 ↓
Learning Recommendations
 ↓
Resume Tailoring
 ↓
Structured Resume
 ↓
Jake's Resume / User LaTeX Template
 ↓
LaTeX Compilation
 ↓
PDF
 ↓
Resume Version
 ↓
User Applies Manually
 ↓
Application Record
 ↓
Status Tracking
 ↓
Automated Reminder
 ↓
User Analytics
```

This workflow is the primary acceptance path for the NextHire MVP.

---

# 36. Post-MVP Direction

After the MVP is stable, future development can proceed through separate Agile epics rather than expanding the MVP indefinitely.

Potential future epics include:

```text
Advanced Job Sources
Advanced Resume & Cover Letters
Browser-Assisted Application
Advanced GitHub Intelligence
Advanced Portfolio Intelligence
Mobile Application
Advanced Notifications
Advanced Privacy Controls
Platform Analytics
Advanced Recommendation Models
```

Each future capability should receive its own discovery, design, user stories, implementation stage, evaluation criteria, and release decision.

---

# 37. Closing Engineering Principle

The objective of this Agile plan is not simply to finish 12 stages.

The objective is to reach a point where:

> **A user can give NextHire an understanding of their career, and NextHire can reliably turn that information into relevant job opportunities, explain why those opportunities matter, identify what the user is missing, prepare a truthful tailored resume, and help the user maintain control over the resulting application workflow.**

Every technical decision should ultimately support that outcome.
