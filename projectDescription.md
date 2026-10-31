# NextHire — Project Description

> **Document Status:** Product and Technical Specification  
> **Project:** NextHire  
> **Version:** 1.0  
> **Scope:** MVP + planned future phases  
> **Primary Goal:** Build an AI-powered career management and job discovery platform that continuously connects a user's career information with relevant opportunities and helps the user move from job discovery to tailored resume preparation and application tracking.

---

## 1. Project Overview

NextHire is an AI-powered career management and job discovery platform designed to reduce the repetitive, fragmented, and time-consuming work involved in searching and applying for jobs and internships.

Traditional job portals primarily help users search, filter, and apply for openings. However, the user is still responsible for repeatedly searching multiple company career pages, determining whether a job matches their skills, identifying missing skills, tailoring their resume, remembering which version of the resume was used, and maintaining a record of applications and deadlines.

NextHire addresses this problem by maintaining a personalized **Career Knowledge Base (CKB)** for every user. The CKB acts as the central source of career-related information supplied or approved by the user. It can contain information from resumes, manually entered profile data, LinkedIn information, GitHub repositories, portfolio websites, projects, experience, certifications, achievements, and other relevant career information.

The platform continuously monitors a curated set of company career pages. Newly discovered job openings are normalized, deduplicated, stored, and embedded. When a user opens their recommendation page, NextHire retrieves potentially relevant jobs using vector similarity and then performs skill-based matching to calculate an explainable job-fit percentage.

For relevant jobs, NextHire can:

- explain why the job matches the user;
- identify matched and missing skills;
- identify relevant projects from the user's Career Knowledge Base;
- provide learning recommendations for skill gaps;
- tailor the user's existing resume to the job;
- generate the tailored resume using LaTeX;
- compile the LaTeX document into a PDF;
- preserve the user's selected/default resume template;
- record the generated resume version against an application;
- maintain an application-tracking dashboard; and
- generate automated email reminders and notifications.

NextHire is intentionally designed as an **AI Agent system with human control**. The AI can retrieve, analyze, reason, rank, recommend, and generate content, but it must not fabricate user information or autonomously make consequential application decisions.

Browser-based automatic form filling and application submission are **not part of the MVP**.

---

# 2. Problem Statement

Job seekers often face the same repetitive workflow:

1. Search several job portals and company career pages.
2. Look for roles matching their preferred technologies and job titles.
3. Open individual job descriptions.
4. Manually compare requirements against their skills.
5. Determine whether they are sufficiently qualified.
6. Identify skills they are missing.
7. Modify their resume for each relevant job.
8. Submit applications.
9. Remember which resume was used.
10. Track application status.
11. Remember assessment, interview, and application deadlines.
12. Repeat the process across multiple companies.

This becomes especially difficult when a candidate targets many companies simultaneously.

The core problem addressed by NextHire is therefore:

> **Job seekers waste significant time repeatedly searching for opportunities, determining job relevance, tailoring resumes, and tracking applications across different companies and career pages.**

NextHire aims to consolidate and intelligently automate as much of this workflow as possible while keeping the user in control.

---

# 3. Product Vision

The vision of NextHire is to become an intelligent career management system that continuously understands:

- who the user is professionally;
- what the user knows;
- what the user has built;
- what skills the user wants to prioritize;
- which companies the user wants to work for;
- which opportunities are available; and
- how well each opportunity aligns with the user's current career profile.

Instead of requiring the user to repeatedly search for opportunities, NextHire should make the workflow increasingly proactive:

```text
User Career Information
        +
User Preferences
        ↓
Continuous Opportunity Discovery
        ↓
Personalized Retrieval
        ↓
Job Fit Analysis
        ↓
Skill Gap Identification
        ↓
Resume Tailoring
        ↓
Application Tracking
```

The platform should function as an **AI-powered career assistant/agent**, rather than simply another job listing website.

---

# 4. Product Positioning

NextHire is positioned as:

> **An AI-powered career management and job discovery platform that continuously connects a user's Career Knowledge Base with relevant opportunities, analyzes job fit using hybrid retrieval and deterministic skill matching, identifies skill gaps, generates tailored LaTeX-based resumes, and helps users manage their applications throughout the job-search lifecycle.**

The primary differentiator is not any single feature. It is the integration of:

- Career Knowledge Base;
- personalized job discovery;
- vector-based retrieval;
- explainable skill matching;
- JD analysis;
- skill-gap analysis;
- GitHub and portfolio context;
- AI-assisted resume tailoring;
- resume versioning; and
- application tracking.

---

# 5. Target Users

## 5.1 Primary Users

NextHire targets:

- college students;
- final-year students;
- recent graduates;
- freshers;
- internship seekers;
- full-time job seekers;
- early-career professionals; and
- experienced professionals.

The platform supports both:

- **internship opportunities**, and
- **full-time employment (FTE) opportunities**.

The initial implementation should not be restricted to one academic or professional background.

---

# 6. Core Objectives

The MVP should achieve the following objectives:

1. Provide secure user authentication.
2. Build a personalized Career Knowledge Base.
3. Allow users to provide career information manually or through supported sources.
4. Parse uploaded resumes and LinkedIn profile information.
5. Optionally analyze GitHub repositories.
6. Optionally analyze portfolio websites.
7. Allow users to define career preferences.
8. Maintain a curated set of company career sources.
9. Discover jobs from company career pages.
10. Crawl company career pages twice daily.
11. Support manual job-refresh operations.
12. Normalize and deduplicate discovered jobs.
13. Generate embeddings for career and job information.
14. Retrieve potentially relevant jobs using vector search.
15. Calculate an explainable skill-based job-fit percentage.
16. Recommend jobs with a configurable threshold, initially 60%.
17. Explain matched skills and relevant projects.
18. Identify missing skills.
19. Recommend learning resources for skill gaps.
20. Tailor an existing resume to a selected job description.
21. Generate the tailored resume using LaTeX.
22. Compile the LaTeX resume into PDF.
23. Preserve the default Jake's Resume template or a user-provided LaTeX template.
24. Maintain generated resume versions.
25. Allow users to apply manually to the company.
26. Track applications and resume versions used.
27. Generate automatic email notifications and reminders.
28. Provide user-level analytics.
29. Provide an admin dashboard for company/source management and operational visibility.

---

# 7. MVP Scope

The MVP includes the following.

## 7.1 Authentication

- Email/password authentication.
- Google OAuth.
- Account creation.
- Login/logout.
- Password recovery/reset.
- Basic session management.
- Role-based access for USER and ADMIN.

## 7.2 Career Knowledge Base

- Resume upload and parsing.
- Manual career information entry.
- Manual skill entry.
- Manual project entry.
- Manual experience entry.
- Manual certification entry.
- Manual achievement entry.
- LinkedIn profile ingestion.
- GitHub integration.
- Portfolio extraction.
- User review and correction of extracted information.
- Structured career information.
- Original source documents.
- Vector embeddings for relevant information.

## 7.3 Job Discovery

- Company career pages only in MVP.
- Admin-managed company catalogue.
- Automatic company discovery when a user enters a new target company.
- Official career-page verification.
- Generic crawler.
- Company-specific adapters when required.
- Twice-daily crawling.
- Manual refresh.
- Job normalization.
- Duplicate detection/removal.
- Closed-job detection.

## 7.4 Job Intelligence

- Job-description parsing.
- Skill extraction.
- Vector retrieval.
- Skill-based matching.
- Job-fit percentage.
- Matched skills.
- Missing skills.
- Relevant project identification.
- Explanation of job relevance.
- User-specific ranking.

## 7.5 Resume Intelligence

- Tailoring of existing resume.
- Automatic selection of relevant projects/experience.
- ATS-oriented content optimization.
- No fabricated information.
- LaTeX-based generation.
- PDF output.
- Jake's Resume as default template.
- User-provided LaTeX template as an alternative.
- Resume versioning.

## 7.6 Skill Gap and Learning

- Missing skill identification.
- Required/preferred skill distinction where available.
- Learning recommendations.
- User decision on whether to pursue lower-fit opportunities.

## 7.7 Application Tracking

- Saved.
- Applied.
- Assessment.
- Interview.
- Offer.
- Rejected.
- Withdrawn.
- Manual status updates.
- Application notes.
- Application dates.
- Deadlines.
- Next actions.
- Resume version used.
- Job reference.

## 7.8 Notifications

- Email notifications.
- New matching job notifications.
- Application reminders.
- Deadline reminders.
- Other automatically generated application-related reminders.

## 7.9 Admin Dashboard

- Company management.
- Career-page URLs.
- Active/inactive companies.
- Crawl status.
- Last crawl information.
- Jobs discovered.
- Failed crawls.
- AI usage visibility.
- Operational job statistics.

## 7.10 User Analytics

- Applications.
- Application status distribution.
- Application activity over time.
- Target companies.
- Relevant jobs.
- Skill gaps.
- Other useful career-search metrics.

---

# 8. Explicitly Excluded From MVP

The following are intentionally outside the MVP:

- autonomous job application submission;
- browser automation for filling application forms;
- automatic CAPTCHA solving/bypassing;
- storing company-portal passwords;
- automatic company-portal status scraping;
- automatic email-based application status inference;
- WhatsApp notifications;
- native mobile application;
- platform-wide analytics for administrators;
- advanced privacy/data-export controls;
- automatic full source-code analysis of GitHub repositories;
- advanced OCR for scanned resumes;
- advanced portfolio rendering for complex JavaScript applications;
- multi-source job aggregation from LinkedIn, Indeed, Naukri, etc.;
- autonomous application agent.

These can be considered in future phases.

---

# 9. User Onboarding

The onboarding process should collect enough information to begin personalized job discovery.

## 9.1 Mandatory Career Starting Point

At least one of the following is required:

- Resume; or
- LinkedIn profile information.

Users may additionally manually enter career information.

## 9.2 Optional Sources

Users may connect:

- GitHub;
- portfolio;
- additional projects;
- certifications;
- achievements;
- work experience;
- skills.

## 9.3 Career Preferences

The user specifies:

### Preferred Roles

Examples:

- Software Engineer
- Backend Developer
- Java Developer
- Data Analyst

### Preferred Technologies/Skills

Examples:

- Java
- Spring Boot
- Python
- AWS
- Docker

### Preferred Locations

Examples:

- Bengaluru
- Hyderabad
- Mumbai
- Remote

### Target Companies

Examples:

- Google
- Microsoft
- Amazon
- Accenture

These four preference categories form the initial personalization layer.

---

# 10. Career Knowledge Base

The Career Knowledge Base is one of the central components of NextHire.

It represents the user's career information in a form that can be:

- stored;
- searched;
- retrieved;
- analyzed;
- validated;
- embedded;
- used for job matching; and
- used for resume generation.

## 10.1 Sources

The CKB may contain information from:

- uploaded resumes;
- manually entered data;
- LinkedIn profile information;
- GitHub repositories;
- portfolio websites;
- projects;
- work experience;
- education;
- certifications;
- achievements;
- skills;
- previously generated resumes;
- other user-approved career documents.

## 10.2 Hybrid Storage Model

NextHire should maintain both:

### Structured information

Example:

```text
User
 ├── Skills
 ├── Projects
 ├── Experience
 ├── Education
 ├── Certifications
 ├── Achievements
 ├── GitHub
 └── Portfolio
```

### Unstructured source information

Examples:

- original resume;
- LinkedIn document;
- GitHub README;
- portfolio text;
- generated resume documents.

### Vector representation

Relevant chunks are converted into embeddings to support semantic retrieval.

---

# 11. Career Knowledge Base Trust Model

NextHire must distinguish between:

- information directly supplied by the user;
- information extracted from a source;
- information inferred by AI.

The system must not silently convert an AI inference into a confirmed user fact.

For example:

```text
GitHub analysis
      ↓
Potential skill: Redis
      ↓
User confirmation
      ↓
Confirmed Career Knowledge Base skill
```

The system may suggest information, but the user remains the authority over their career profile.

---

# 12. Resume Parsing

The MVP should support:

- PDF;
- DOCX.

Processing pipeline:

```text
Resume
   ↓
Document Parser
   ↓
Text Extraction
   ↓
Section Detection
   ↓
Entity/Information Extraction
   ↓
Structured Career Profile
   ↓
User Review
   ↓
Career Knowledge Base
```

The parser should attempt to identify:

- name;
- contact information;
- summary;
- education;
- experience;
- projects;
- skills;
- certifications;
- achievements;
- links.

The extracted information should be editable by the user.

---

# 13. LinkedIn Integration

The MVP should support LinkedIn information as a career-data source.

The preferred baseline implementation is profile information supplied by the user, such as a LinkedIn profile document/export.

If technically and legally feasible, controlled LinkedIn scraping may be explored. The implementation must remain replaceable so the ingestion mechanism can later be changed to another supported method.

The extracted LinkedIn information should become part of the Career Knowledge Base after processing and user validation where necessary.

---

# 14. GitHub Integration

GitHub is an optional enrichment source.

## 14.1 Integration

The preferred mechanism is GitHub OAuth with read-only access.

NextHire should not request unnecessary write permissions.

## 14.2 MVP Analysis

The MVP analyzes:

- repository name;
- repository description;
- README;
- programming languages;
- topics.

The MVP does **not** perform full source-code analysis.

## 14.3 GitHub → Career Knowledge Base

Pipeline:

```text
GitHub OAuth
     ↓
Repository Discovery
     ↓
Repository Metadata
     ↓
README Extraction
     ↓
Skill/Project Identification
     ↓
Candidate Career Information
     ↓
User Confirmation
     ↓
Career Knowledge Base
```

When a GitHub-derived project is relevant to a job, NextHire should explicitly show it as supporting evidence.

Example:

```text
Matched Project:
Expense Management API

Relevant Skills:
✓ Java
✓ Spring Boot
✓ MongoDB
```

---

# 15. Portfolio Integration

The user can provide a portfolio URL.

MVP processing:

```text
Portfolio URL
      ↓
Web Retrieval
      ↓
Readable Content Extraction
      ↓
Project / Skill / Experience Extraction
      ↓
Career Knowledge Base
```

The initial implementation targets basic/static portfolio sites.

Complex JavaScript-heavy websites may be supported later using browser rendering.

---

# 16. Company Management

Companies are centrally managed by NextHire.

## 16.1 Admin-Added Companies

An administrator can add:

- company name;
- official career-page URL;
- basic company metadata;
- active/inactive status.

## 16.2 User-Requested Companies

When a user enters a target company:

```text
User enters company
       ↓
Search existing company database
       ↓
Company exists?
   ├── Yes → use existing company
   └── No
         ↓
     Search web
         ↓
     Find official career page
         ↓
     Verify
         ↓
     Add company
```

Only an official/verified company career source should be accepted.

---

# 17. Job Source Strategy

The MVP intentionally focuses on **company career pages**.

The platform does not initially aggregate from:

- LinkedIn Jobs;
- Indeed;
- Naukri;
- Unstop;
- Internshala;
- other third-party job portals.

This keeps the MVP technically manageable and reduces dependency on fragile or restricted third-party scraping.

Additional sources may be introduced in later phases.

---

# 18. Job Crawling Architecture

The crawler should use a hybrid strategy.

```text
Scheduler
    ↓
Company Manager
    ↓
Generic Career Page Crawler
    ↓
Successful?
 ├── Yes → Parse Jobs
 └── No
       ↓
Company-Specific Adapter
       ↓
Parse Jobs
       ↓
If failure → Mark Crawl Failed
       ↓
Admin Visibility
```

The system should never attempt to bypass CAPTCHAs or anti-bot protections.

---

# 19. Crawl Frequency

Automatic crawling occurs:

> **Twice per day.**

The system also supports manual refresh.

Manual refresh can be used to update jobs without waiting for the next scheduled crawl.

---

# 20. Raw Job Data

For reliability and debugging, the crawler should retain relevant raw source information where practical.

The raw data can be used to:

- reprocess jobs after parser improvements;
- debug extraction failures;
- compare source changes;
- investigate crawler errors.

The system should separate raw source content from normalized job records.

---

# 21. Job Normalization

Raw job listings should be converted into a common schema.

A normalized job should contain, where available:

```text
Job ID
Company ID
Title
Description
Responsibilities
Required Skills
Preferred Skills
Location
Employment Type
Experience Requirement
Education Requirement
Application URL
Source URL
External Job ID
Posted Date
Last Seen Date
Status
```

---

# 22. Job Identity and Deduplication

Every job should have an internal NextHire Job ID.

Preferred external identity:

```text
Company ID + External Job ID
```

When an external job ID is unavailable, the system can use a combination of:

```text
Company
+
Normalized Title
+
Location
+
Canonical URL
```

Duplicate listings should be removed/merged.

The system should preserve the canonical job record rather than presenting duplicates to users.

---

# 23. Closed Jobs

If a previously discovered job is no longer available on the company career page, NextHire should mark it:

> **Closed**

rather than treating it as permanently deleted.

This preserves historical application records and allows the system to understand what happened to previously tracked opportunities.

---

# 24. Job Embeddings

Job descriptions should be converted into vector embeddings.

Possible embedded information includes:

- title;
- description;
- responsibilities;
- required skills;
- preferred skills;
- qualifications;
- technology information;
- relevant company context.

The embedding should reference the corresponding job record.

---

# 25. Company Embeddings

Company-level information may also be embedded.

Company embeddings can contain:

- company description;
- career-page information;
- technology information;
- career-related content.

Company embeddings provide additional semantic context, while individual job embeddings remain the primary retrieval mechanism for job recommendations.

---

# 26. User Embeddings

Relevant user information can be embedded, including:

- resume sections;
- skills;
- projects;
- experience;
- certifications;
- achievements;
- GitHub project information;
- portfolio information.

The system should maintain metadata connecting each vector to its original Career Knowledge Base entity.

---

# 27. Hybrid RAG Architecture

NextHire uses a hybrid architecture combining:

1. structured user data;
2. vector retrieval;
3. deterministic skill matching;
4. LLM reasoning/generation;
5. agent orchestration.

The conceptual pipeline is:

```text
Career Knowledge Base
        ↓
Embedding Generation
        ↓
User Representation

Job Database
        ↓
Job Embeddings
        ↓
Vector Retrieval
        ↓
Candidate Jobs
        ↓
Deterministic Skill Matching
        ↓
Job Fit Score
        ↓
RAG Context Construction
        ↓
LLM Analysis
        ↓
Explanation + Skill Gaps + Resume Context
```

RAG should not be treated as synonymous with the entire matching system.

---

# 28. Multi-Stage Job Retrieval

To control computational cost, NextHire should use staged retrieval.

Conceptually:

```text
All Available Jobs
        ↓
Vector Similarity Retrieval
        ↓
Top Candidate Jobs
        ↓
Skill-Based Matching
        ↓
Relevant Candidates
        ↓
Detailed JD Analysis
        ↓
User Recommendations
```

The exact number of candidates at each stage can be tuned during implementation.

---

# 29. User-Specific Job Matching

When a user opens their recommendation page:

```text
User Preferences
      +
Career Knowledge Base
      ↓
Vector Retrieval
      ↓
Candidate Jobs
      ↓
Skill Matching
      ↓
Fit Percentage
      ↓
Ranking
```

Recommendations are therefore personalized per user.

A global job database does not mean that every user receives the same ranking.

---

# 30. User Preference Weighting

Users explicitly select and prioritize their desired skills.

Example:

```text
Primary:
Java
Spring Boot
AWS

Secondary:
Docker
MongoDB
```

The system uses these preferences to personalize retrieval and ranking.

NextHire should not automatically redefine a user's preferred skills based solely on external "trending skill" assumptions.

---

# 31. Dream Companies

Target companies are a user preference.

They should influence recommendation prioritization but should not artificially inflate the actual technical job-fit percentage.

For example:

```text
Technical Skill Fit = 82%
Target Company = Yes
```

The user may see the job ranked highly because it is a target company, while the displayed skill-fit score remains 82%.

This keeps the score semantically meaningful.

---

# 32. Job-Fit Score

For MVP, job-fit scoring is intentionally simple and explainable.

The primary factor is:

> **Skill matching.**

A basic conceptual calculation is:

```text
Skill Match Percentage =
Matched Relevant Skills / Total Relevant Job Skills × 100
```

The exact implementation may account for required and preferred skills separately where reliable information is available.

Example:

```text
User:
Java
Spring Boot
MongoDB
Docker

Job:
Java
Spring Boot
MongoDB
Docker
Kubernetes
AWS

Matched = 4
Relevant Skills = 6

Fit = 4 / 6 × 100
    = 66.67%
```

The implementation should use normalized skill names and synonym handling where appropriate.

---

# 33. Job Recommendation Threshold

The initial recommendation threshold is:

> **60%**

Conceptually:

```text
Score >= 60%
       ↓
Recommended
```

Jobs below 60% are not recommended by default.

However, they remain discoverable if the user chooses to explore them.

```text
Score < 60%
       ↓
Lower Match
       ↓
User can still inspect
       ↓
Proceed Anyway
```

The system must never artificially increase the score merely because a user chooses to pursue a lower-fit job.

---

# 34. Job Recommendation Explanation

A recommendation should be explainable.

Example:

```text
Job Fit: 82%

Matched Skills
✓ Java
✓ Spring Boot
✓ MongoDB
✓ Docker

Skill Gaps
⚠ Kubernetes

Relevant Projects
✓ Project Management API
✓ E-Commerce Backend

Why this job matches:
Your backend development experience and Java/Spring Boot
projects align strongly with the technical requirements of
this role.
```

The system should identify the actual Career Knowledge Base evidence used to support the recommendation.

---

# 35. Relevant Project Identification

When a job is analyzed, NextHire should retrieve the most relevant user projects.

Example:

```text
Job requires:
Java
Spring Boot
AWS

Career Knowledge Base:
Project A → Java + Spring Boot
Project B → Python
Project C → AWS + Docker

Selected:
Project A
Project C
```

Only relevant projects should be prioritized for the tailored resume.

---

# 36. Skill Gap Analysis

The system compares the user's confirmed career skills with job requirements.

Output:

```text
Matched Skills
✓ Java
✓ Spring Boot
✓ AWS

Skill Gaps
⚠ Kubernetes
⚠ Redis
```

Required skills should receive greater importance than preferred skills where the source job description distinguishes them.

---

# 37. Learning Recommendations

For identified skill gaps, NextHire should provide learning recommendations.

The MVP may provide:

- learning topic;
- short explanation;
- suggested learning resources;
- recommended progression.

The recommendation should focus on helping the user close the specific gap identified for the selected job.

Advanced personalized learning plans can be introduced later.

---

# 38. Resume Tailoring

Resume tailoring is part of the MVP.

The user starts with their existing resume.

Pipeline:

```text
Existing Resume
       +
Selected Job Description
       ↓
JD Analysis
       ↓
Relevant Skill Retrieval
       ↓
Relevant Project Retrieval
       ↓
Relevant Experience Retrieval
       ↓
Resume Agent
       ↓
Tailored Resume Content
       ↓
LaTeX Generation
       ↓
Compilation
       ↓
PDF
```

---

# 39. Resume Tailoring Rules

NextHire may:

- reorder content;
- remove irrelevant content;
- emphasize relevant skills;
- rewrite descriptions;
- optimize wording;
- select relevant projects;
- select relevant experience;
- improve ATS keyword alignment;
- restructure sections within the chosen template.

NextHire must **never fabricate career information**.

The AI cannot invent:

- projects;
- skills;
- technologies;
- employers;
- job responsibilities;
- achievements;
- certifications;
- metrics;
- experience.

It may only transform, reorganize, or emphasize information supported by the user's Career Knowledge Base.

---

# 40. Resume Template Strategy

The default resume template is:

> **Jake's Resume LaTeX template**

Users may optionally provide their own LaTeX template.

Therefore:

```text
No user template
       ↓
Jake's Resume template

User provides LaTeX template
       ↓
Use user's template
```

The resume content is dynamically generated while the selected template controls the presentation structure.

---

# 41. LaTeX Resume Generation

The generation pipeline is:

```text
Career Knowledge Base
        +
Job Description
        ↓
Resume Agent
        ↓
Structured Resume Content
        ↓
LaTeX Template
        ↓
Generated .tex
        ↓
LaTeX Compiler
        ↓
PDF
```

The generated PDF becomes a versioned career artifact.

---

# 42. Resume Validation

Before presenting a generated resume, the system should perform basic validation.

Possible checks:

- successful LaTeX compilation;
- required sections present;
- required contact information present;
- no unsupported placeholder text;
- basic ATS keyword coverage;
- no fabricated information according to source constraints;
- no obvious formatting failure.

Future versions can implement deeper ATS simulation.

---

# 43. Resume Versioning

Every generated resume should be versioned.

Example:

```text
Original Resume
     ↓
Google Resume — V1
     ↓
Amazon Resume — V2
     ↓
Microsoft Resume — V3
```

Each version should retain:

- user;
- source resume;
- target job;
- creation date;
- template used;
- selected skills;
- selected projects;
- generated file;
- generation metadata.

This allows an application record to identify the exact resume used.

---

# 44. Application Tracking

NextHire provides a centralized application tracker.

Initial statuses:

```text
Saved
Applied
Assessment
Interview
Offer
Rejected
Withdrawn
```

The user can manually update statuses.

When a user applies manually after using NextHire's preparation workflow, the application record can be marked as **Applied** by the user.

---

# 45. Application Record

An application should maintain information such as:

```text
Application ID
User ID
Job ID
Company ID
Status
Applied Date
Application URL
Resume Version ID
Notes
Deadline
Next Action
Interview Date
Created At
Updated At
```

Future versions may add cover-letter versions and more external application metadata.

---

# 46. No Browser Automation in MVP

Browser automation/form filling is explicitly removed from the MVP.

The MVP therefore does not:

- automatically open company application forms for filling;
- fill application fields;
- upload documents automatically;
- submit applications;
- bypass CAPTCHA;
- manage external application credentials.

The user remains responsible for submitting the application through the company's application system.

Browser automation can be considered in a future phase.

---

# 47. Automated Reminders

NextHire automatically generates reminders based on application information.

Examples:

```text
Assessment deadline tomorrow
Interview tomorrow
Application follow-up required
Upcoming application deadline
```

The user should not need to manually create every reminder.

---

# 48. Email Notifications

Email is the MVP notification channel.

Potential notifications include:

### New matching jobs

```text
We found 5 new jobs matching your profile.
```

### Application reminders

```text
Your assessment deadline is tomorrow.
```

### Deadline reminders

```text
Your application deadline is approaching.
```

A notification system should avoid repeatedly sending duplicate notifications for the same event.

---

# 49. Recommendation Page

A recommendation card should expose enough information for the user to make a decision.

Example:

```text
Company
Job Title
Location

Job Fit: 82%

Matched Skills
Missing Skills

Relevant Projects

Why this job matches

[View Job]
[Analyze JD]
[Generate Resume]
[Save]
[Apply / Track Application]
```

The UI should prioritize explainability rather than presenting a score without context.

---

# 50. User Dashboard

The MVP dashboard should focus on the user's career-search activity.

Potential sections:

## Career Profile

- profile completeness;
- skills;
- projects;
- experience;
- GitHub connection;
- portfolio status.

## Recommended Jobs

- top matching opportunities;
- fit score;
- matched skills;
- skill gaps.

## Applications

- current application statuses;
- upcoming deadlines;
- recent applications.

## Analytics

- applications;
- application status distribution;
- job discovery;
- target companies;
- skill gaps.

Additional dashboard modules may be introduced later.

---

# 51. User Analytics

MVP analytics are user-focused.

Possible metrics:

- jobs discovered;
- jobs matching profile;
- jobs viewed;
- jobs saved;
- applications;
- application status distribution;
- interviews;
- offers;
- rejected applications;
- top target companies;
- common skill gaps.

A simple funnel can be represented as:

```text
Jobs Discovered
      ↓
Relevant Jobs
      ↓
Jobs Viewed
      ↓
Applications
      ↓
Interviews
      ↓
Offers
```

Platform-wide analytics are not part of the MVP user experience.

---

# 52. Admin Dashboard

The admin dashboard is intended primarily for operational management.

Admin capabilities include:

### Company Management

- add company;
- edit company;
- activate/deactivate company;
- manage career-page URL.

### Crawler Monitoring

- last crawl;
- crawl status;
- crawl failures;
- number of jobs discovered.

### AI/System Visibility

- AI usage;
- jobs discovered;
- processing activity.

Platform-wide business analytics may be expanded in future versions.

---

# 53. Roles

The initial access model contains two roles:

```text
USER
ADMIN
```

### USER

Can:

- manage career profile;
- manage preferences;
- receive recommendations;
- generate resumes;
- manage applications;
- view analytics.

### ADMIN

Can:

- manage companies;
- monitor crawlers;
- inspect system-level operational metrics.

---

# 54. AI Agent Architecture

NextHire should use a multi-agent architecture orchestrated through LangGraph.

The initial logical agents are:

```text
                 Agent Orchestrator
                        │
       ┌────────────────┼────────────────┐
       │                │                │
       ▼                ▼                ▼
Career Knowledge     Job Analysis      Resume Agent
     Agent               Agent
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
                  Skill Gap Agent
                        │
                        ▼
                Learning Agent
```

The exact implementation can evolve as the system is developed.

---

# 55. Career Knowledge Agent

Responsibilities:

- process career information;
- retrieve relevant user information;
- reason over Career Knowledge Base content;
- identify relevant projects;
- identify relevant experience;
- assist in organizing career information.

It must respect the source-of-truth rules and avoid creating unsupported facts.

---

# 56. Job Analysis Agent

Responsibilities:

- interpret job descriptions;
- identify skills;
- distinguish required/preferred skills when possible;
- summarize responsibilities;
- prepare JD context for matching;
- identify relevant job attributes.

---

# 57. Skill Gap Agent

Responsibilities:

- compare user skills against job requirements;
- identify missing skills;
- distinguish major and minor gaps where possible;
- provide skill-gap explanations;
- trigger learning recommendations.

---

# 58. Resume Agent

Responsibilities:

- retrieve relevant Career Knowledge Base content;
- select relevant projects;
- select relevant experience;
- tailor resume content;
- optimize wording for the target JD;
- generate structured resume content;
- generate LaTeX using the selected template;
- ensure no unsupported facts are introduced.

---

# 59. Learning Agent

Responsibilities:

- receive identified skill gaps;
- explain what should be learned;
- recommend appropriate learning resources;
- connect learning recommendations to the target role.

---

# 60. Agent Orchestration

LangGraph should coordinate multi-step workflows.

Example resume workflow:

```text
User selects Job
      ↓
Job Analysis Agent
      ↓
Skill Extraction
      ↓
Career Knowledge Agent
      ↓
Relevant Projects / Experience
      ↓
Resume Agent
      ↓
Validation
      ↓
LaTeX Generation
      ↓
PDF Compilation
      ↓
User
```

The orchestrator should manage state and make each agent's responsibility explicit.

---

# 61. LLM Provider Abstraction

The system should not tightly couple business logic to one LLM provider.

Potential providers include:

- OpenAI;
- Anthropic Claude;
- Google Gemini.

The application should use an abstraction layer so the model can be changed without redesigning the complete system.

The final provider/model selection should consider:

- quality;
- cost;
- latency;
- structured-output support;
- embedding availability;
- deployment requirements.

---

# 62. Recommended Technical Architecture

The preferred implementation direction is a Python-centric architecture because the project has substantial AI, RAG, crawling, and agent requirements.

A recommended architecture is:

```text
                         ┌──────────────────┐
                         │   Next.js / Web   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   FastAPI API    │
                         └────────┬─────────┘
                                  │
            ┌─────────────────────┼────────────────────┐
            │                     │                    │
            ▼                     ▼                    ▼
       MongoDB Atlas            Redis              AI Services
            │                     │                    │
            │                     │                    ▼
            │                     │              LangGraph
            │                     │                    │
            │                     │          ┌─────────┼─────────┐
            │                     │          ▼         ▼         ▼
            │                     │       Career     Job      Resume
            │                     │       Agent     Agent      Agent
            │                     │
            │                     ▼
            │              Background Workers
            │
            ▼
       Vector Search
```

This is a recommended starting architecture, not an immutable implementation requirement.

---

# 63. Frontend

A modern web framework such as Next.js/React is recommended.

Frontend responsibilities:

- authentication UI;
- onboarding;
- Career Knowledge Base;
- job recommendations;
- job details;
- resume generation;
- resume preview/download;
- applications;
- reminders;
- analytics;
- admin dashboard.

---

# 64. Backend

FastAPI is recommended for:

- REST APIs;
- authentication integration;
- user/profile management;
- job APIs;
- application APIs;
- AI workflow initiation;
- document processing orchestration;
- crawler control;
- admin APIs.

---

# 65. Primary Database

MongoDB Atlas is recommended as the primary data store.

Potential collections/entities:

```text
users
career_profiles
skills
projects
experiences
educations
certifications
achievements
documents
github_profiles
github_repositories
portfolios
companies
jobs
job_embeddings
user_embeddings
resume_versions
applications
notifications
learning_resources
crawl_runs
```

The exact collection structure can be optimized during implementation.

---

# 66. Vector Search

MongoDB Atlas Vector Search is preferred initially because it can reduce infrastructure complexity by keeping structured data and vector-search metadata in the same platform.

The architecture should still abstract vector operations so another vector database such as ChromaDB can be introduced if required.

---

# 67. Embedding Service

Embedding generation should be abstracted behind a service interface.

Conceptually:

```text
EmbeddingService
      ↓
Embedding Provider
      ↓
Vector
```

This allows embedding models to be changed without rewriting the retrieval layer.

---

# 68. Background Processing

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

Conceptual workflow:

```text
API Request
    ↓
Create Processing Task
    ↓
Background Worker
    ↓
Execute
    ↓
Update Status
    ↓
Frontend retrieves result
```

Redis-backed workers can be used for MVP-scale background processing.

---

# 69. Crawler Scheduling

A scheduler should trigger company crawls twice daily.

Conceptually:

```text
Scheduler
   ↓
Select active companies
   ↓
Create crawl tasks
   ↓
Workers
   ↓
Crawler
   ↓
Parser
   ↓
Normalizer
   ↓
Deduplicator
   ↓
Database
   ↓
Embedding
```

Manual refresh should use the same pipeline rather than a separate implementation.

---

# 70. Data Flow — New Job

```text
Company Career Page
        ↓
Crawler
        ↓
Raw Job
        ↓
Parser
        ↓
Normalized Job
        ↓
Duplicate Check
        ↓
Store Job
        ↓
Generate Embedding
        ↓
Vector Index
```

---

# 71. Data Flow — Recommendation

```text
User Opens Recommendations
        ↓
Load User Profile
        ↓
Load User Preferences
        ↓
Retrieve User Embeddings
        ↓
Vector Search Against Jobs
        ↓
Candidate Jobs
        ↓
Skill Normalization
        ↓
Skill Match Calculation
        ↓
Job Fit Score
        ↓
Ranking
        ↓
Recommendation Cards
```

---

# 72. Data Flow — JD Analysis

```text
Selected Job
     ↓
Job Analysis Agent
     ↓
Extract:
  Skills
  Requirements
  Responsibilities
  Preferred Skills
     ↓
Career Knowledge Retrieval
     ↓
Compare With User
     ↓
Matched Skills
     ↓
Skill Gaps
     ↓
Relevant Projects
     ↓
Explanation
```

---

# 73. Data Flow — Resume Generation

```text
Selected Job
      +
Existing Resume
      +
Career Knowledge Base
      ↓
Job Analysis
      ↓
Relevant Content Retrieval
      ↓
Resume Agent
      ↓
Structured Tailored Resume
      ↓
Selected LaTeX Template
      ↓
.tex File
      ↓
LaTeX Compiler
      ↓
PDF
      ↓
Validation
      ↓
Resume Version
      ↓
User
```

---

# 74. Data Flow — Application Tracking

```text
User Finds Job
      ↓
Save / Decide to Apply
      ↓
Generate Tailored Resume
      ↓
Download PDF
      ↓
User Applies on Company Website
      ↓
User Records/Confirms Application
      ↓
Application Record
      ↓
Resume Version Linked
      ↓
Tracker
      ↓
Reminder Engine
```

---

# 75. Application and Resume Relationship

The application record should reference the exact resume version used.

Example:

```text
Application:
Google — Software Engineer
Status: Applied

Resume:
Google_Backend_Resume_V3.pdf
```

This ensures users can understand what information they submitted for each opportunity.

---

# 76. Security Principles

The platform handles sensitive professional information.

Baseline security requirements include:

- secure authentication;
- password hashing;
- authorization checks;
- private user career data;
- protected document access;
- secure API authentication;
- read-only GitHub permissions;
- no storage of external company passwords;
- input validation;
- secure file handling;
- protection against unauthorized cross-user data access.

---

# 77. User Data Ownership

The user's career data belongs to the user.

NextHire should treat Career Knowledge Base data as private by default.

The system should not:

- expose one user's career profile to another user;
- sell user career data;
- use private career data as public training data.

Advanced controls such as full export and complete account/data deletion are planned for a later phase.

---

# 78. GitHub Security

GitHub integration should use the minimum permissions necessary.

The preferred scope is read-only access.

NextHire should not:

- modify repositories;
- create commits;
- delete repositories;
- alter GitHub data.

---

# 79. AI Safety and Data Integrity Rules

The AI layer must obey strict career-data constraints.

### Rule 1 — No fabrication

Never invent user career facts.

### Rule 2 — Source grounding

Resume generation must be grounded in Career Knowledge Base data.

### Rule 3 — User authority

Potentially inferred career information should require confirmation before becoming a confirmed profile fact.

### Rule 4 — Explainability

Job recommendations should expose the main reasons for the match.

### Rule 5 — Human control

The user remains responsible for deciding whether to apply.

---

# 80. Error Handling

The system must gracefully handle:

## Resume parsing failure

```text
Parsing failed
   ↓
Notify user
   ↓
Allow manual entry
```

## GitHub unavailable

```text
GitHub integration failed
   ↓
Continue using existing Career Knowledge Base
```

## Portfolio unavailable

```text
Portfolio extraction failed
   ↓
Keep URL
   ↓
Allow retry
```

## Career page crawler failure

```text
Crawler failure
   ↓
Retry / adapter
   ↓
Mark failed
   ↓
Admin visibility
```

## Job parsing failure

The raw source should be retained where possible for debugging/reprocessing.

## LaTeX compilation failure

```text
Generated LaTeX
      ↓
Compilation failure
      ↓
Validation/error handling
      ↓
Do not present invalid PDF
      ↓
Retry or report generation error
```

---

# 81. Non-Functional Requirements

## Performance

Common user operations should return quickly where possible, while expensive operations should be asynchronous.

## Scalability

The architecture should support adding:

- more users;
- more companies;
- more jobs;
- more embeddings;
- more AI workflows.

## Reliability

A failure in one company crawler should not stop all other company crawls.

## Maintainability

Crawler adapters, AI agents, embedding providers, and LLM providers should be modular.

## Observability

Important operations should be logged:

- crawler runs;
- failures;
- AI workflows;
- resume generation;
- processing status;
- notification delivery.

## Extensibility

Future versions should be able to add:

- more job sources;
- mobile applications;
- browser automation;
- additional LLM providers;
- additional notification channels;
- advanced analytics.

---

# 82. Future Scope

The following features can be introduced after the MVP.

## Phase 2 — Advanced Career Intelligence

- stronger experience-based scoring;
- education matching;
- location weighting;
- seniority matching;
- salary preferences;
- employment type;
- remote/hybrid preferences;
- advanced ATS validation;
- more resume templates;
- cover-letter generation;
- richer GitHub analysis;
- advanced portfolio analysis.

## Phase 3 — Application Intelligence

- browser-assisted application filling;
- Playwright-based automation;
- human approval before submission;
- application-form profile mapping;
- application automation state management.

The browser automation should remain human-in-the-loop.

## Phase 4 — Broader Job Sources

Potential sources:

- LinkedIn;
- Indeed;
- Naukri;
- Unstop;
- Internshala;
- job APIs;
- additional career platforms.

Each source should be integrated only when technically and legally appropriate.

## Phase 5 — Advanced Notifications

- native push notifications;
- mobile notifications;
- richer notification preferences;
- messaging integrations.

## Phase 6 — Advanced Privacy

- complete account deletion;
- Career Knowledge Base deletion;
- data export;
- advanced consent management;
- advanced encryption controls;
- detailed data retention management.

## Phase 7 — Platform Analytics

Admin-level analytics such as:

- active users;
- recommendation statistics;
- application conversion;
- job-source performance;
- crawler reliability;
- AI usage;
- system-wide trends.

---

# 83. Recommended Development Phases

## Phase 1 — Foundation

- project setup;
- authentication;
- user roles;
- MongoDB;
- frontend;
- backend;
- basic deployment;
- document storage.

## Phase 2 — Career Knowledge Base

- resume parsing;
- manual profile editing;
- skills;
- projects;
- experience;
- certifications;
- GitHub;
- LinkedIn;
- portfolio;
- embeddings.

## Phase 3 — Company and Job Pipeline

- admin company management;
- company discovery;
- generic crawler;
- adapters;
- job normalization;
- deduplication;
- closed-job detection;
- job embeddings.

## Phase 4 — AI Recommendation Engine

- vector retrieval;
- skill normalization;
- skill matching;
- fit score;
- JD analysis;
- skill gaps;
- recommendation explanation.

## Phase 5 — Resume Intelligence

- Jake's Resume template;
- user LaTeX template support;
- resume tailoring;
- project selection;
- LaTeX generation;
- PDF compilation;
- validation;
- versioning.

## Phase 6 — Application Tracking

- application records;
- statuses;
- resume linkage;
- reminders;
- email notifications;
- user analytics.

## Phase 7 — Admin and Hardening

- crawler monitoring;
- AI usage;
- job discovery statistics;
- security hardening;
- error handling;
- testing;
- deployment;
- documentation.

---

# 84. MVP Acceptance Scenario

The following scenario represents the golden end-to-end MVP workflow.

```text
1. User creates a NextHire account.

2. User provides a resume or LinkedIn profile.

3. User may manually add skills, projects, experience, etc.

4. User optionally connects GitHub.

5. User optionally provides a portfolio URL.

6. NextHire builds the Career Knowledge Base.

7. User reviews and confirms extracted information.

8. User selects:
   - preferred roles;
   - preferred technologies/skills;
   - preferred locations;
   - target companies.

9. If a target company is not already available:
   NextHire attempts to discover its official career page.

10. The company is added to the company catalogue if a valid
    official career source is found.

11. Active company career pages are crawled twice per day.

12. The system extracts new jobs.

13. Jobs are normalized and deduplicated.

14. Jobs are stored and embedded.

15. User opens the recommendation page.

16. NextHire retrieves semantically relevant jobs.

17. Skill matching calculates a job-fit percentage.

18. Jobs above 60% are recommended.

19. Each recommendation shows:
    - fit score;
    - matched skills;
    - missing skills;
    - relevant projects;
    - explanation.

20. User opens a job.

21. NextHire performs detailed JD analysis.

22. Skill gaps and learning recommendations are shown.

23. User selects "Generate Resume."

24. NextHire retrieves relevant career information.

25. NextHire automatically selects relevant projects and experience.

26. Resume Agent tailors the user's existing resume.

27. The selected LaTeX template is populated.

28. LaTeX is compiled into PDF.

29. Generated resume is validated.

30. Resume is stored as a version.

31. User downloads/reviews the resume.

32. User manually applies on the company's career page.

33. User records/confirms the application in NextHire.

34. The application references the exact resume version used.

35. Application status becomes "Applied."

36. User can later update the status:
    Assessment → Interview → Offer/Rejected/etc.

37. NextHire automatically generates relevant reminders.

38. User views application analytics from the dashboard.
```

This workflow defines the core value proposition of the MVP.

---

# 85. MVP Success Criteria

The MVP should be considered successful if a user can reliably:

1. Create an account.
2. Create a usable Career Knowledge Base.
3. Provide resume/LinkedIn information.
4. Add or confirm skills.
5. Connect GitHub.
6. Provide a portfolio.
7. Define career preferences.
8. Discover supported company career pages.
9. Retrieve available jobs.
10. View personalized job recommendations.
11. Understand why a job is recommended.
12. See matched and missing skills.
13. Identify relevant personal projects.
14. Generate a tailored resume.
15. Receive a valid PDF generated from LaTeX.
16. Maintain multiple resume versions.
17. Record applications.
18. Track application status.
19. Receive relevant email reminders.
20. View useful career-search analytics.
21. Allow administrators to manage companies and monitor job discovery.

---

# 86. Important Architectural Principles

The implementation should follow these principles.

## Principle 1 — Career Knowledge Base First

The Career Knowledge Base is the foundation of personalization.

## Principle 2 — Retrieval Before Generation

The AI should retrieve relevant evidence before generating recommendations or resume content.

## Principle 3 — Deterministic Scoring Where Possible

The job-fit score should be explainable and reproducible rather than being an arbitrary LLM-generated number.

## Principle 4 — LLM for Reasoning and Generation

LLMs should be used where semantic reasoning and natural-language generation provide genuine value.

## Principle 5 — No Hallucinated Career Information

The user's professional identity must never be fabricated.

## Principle 6 — Modular AI

Agents, LLM providers, embeddings, and retrieval systems should be replaceable.

## Principle 7 — Source Reliability

Company job data should originate from verified career sources.

## Principle 8 — User Control

NextHire assists the user but does not autonomously submit applications in the MVP.

## Principle 9 — Preserve History

Jobs, applications, and generated resume versions should retain useful historical relationships.

## Principle 10 — MVP Simplicity

The first implementation should prioritize a reliable end-to-end workflow over excessive automation or feature breadth.

---

# 87. Conceptual System Architecture

```text
                                NEXT HIRE
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│                         Web Application                                   │
│                    Next.js / React Frontend                                │
│                                                                            │
└────────────────────────────────┬───────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                              FastAPI                                       │
│                                                                            │
│ Auth | Users | Career KB | Jobs | Recommendations | Resume | Applications │
│ Admin | Notifications | Analytics                                         │
└───────────────┬─────────────────────────────┬──────────────────────────────┘
                │                             │
                ▼                             ▼
       ┌──────────────────┐          ┌────────────────────┐
       │   MongoDB Atlas  │          │ Background Workers │
       │                  │          │                    │
       │ Users            │          │ Crawlers           │
       │ Career KB        │          │ Parsing            │
       │ Companies        │          │ Embeddings         │
       │ Jobs             │          │ Resume Generation  │
       │ Applications     │          │ Email              │
       │ Resume Versions  │          └─────────┬──────────┘
       └────────┬─────────┘                    │
                │                              ▼
                │                     ┌──────────────────┐
                │                     │   AI Services    │
                │                     │                  │
                │                     │ LangGraph        │
                │                     │ RAG              │
                │                     │ Agents           │
                │                     │ LLM              │
                │                     └────────┬─────────┘
                │                              │
                ▼                              ▼
       ┌──────────────────┐          ┌────────────────────┐
       │ Vector Search    │          │ Resume Pipeline    │
       │                  │          │                    │
       │ User embeddings  │          │ LaTeX              │
       │ Job embeddings   │          │ Compilation        │
       │ Company context  │          │ PDF                │
       └──────────────────┘          └────────────────────┘

                    External Data Sources
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
       Company Career      GitHub           Portfolio
           Pages
```

---

# 88. Summary

NextHire is designed around a simple but powerful idea:

> **Maintain a deep, user-controlled understanding of a candidate's career and continuously connect that knowledge with the job market.**

The platform combines:

- Career Knowledge Base;
- structured career information;
- document processing;
- GitHub and portfolio enrichment;
- vector embeddings;
- hybrid retrieval;
- deterministic skill matching;
- RAG;
- multi-agent AI;
- JD analysis;
- skill-gap analysis;
- learning recommendations;
- AI-assisted resume tailoring;
- LaTeX/PDF generation;
- resume versioning;
- application tracking;
- automated reminders;
- email notifications; and
- operational company/job management.

The MVP deliberately avoids fragile autonomous application automation. Instead, it focuses on making the **discovery → understanding → resume preparation → application tracking** lifecycle intelligent, personalized, and reliable.

The long-term vision is to evolve NextHire into a broader AI career agent capable of supporting increasingly more of the user's career-management workflow while maintaining user control, data privacy, explainability, and factual integrity.
