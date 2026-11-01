# NextHire — End-to-End Workflow Testing Guide

> **Document Status:** Comprehensive Testing Playbook  
> **Target Version:** NextHire v1.0 (MVP)  
> **Local Services Required:**  
> - Frontend Dev Server: `http://localhost:5173`  
> - Backend API Server: `http://127.0.0.1:8000` (Docs: `http://127.0.0.1:8000/docs`)  
> - Database: Local MongoDB (`mongodb://localhost:27017`) or configured MongoDB Atlas URI  

---

## 1. Quick Access & Credentials

| Role | Email | Password | Primary URL |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@nexthire.dev` *(or `admin@example.com`)* | `Admin12345!` | [http://localhost:5173/admin](http://localhost:5173/admin) |
| **Candidate** | Self-registered at `/signup` | User choice | [http://localhost:5173/login](http://localhost:5173/login) |

---

## 2. Recommended Testing Order

```text
1. Candidate Authentication & Account Setup (/signup, /login)
   ↓
2. Career Knowledge Base (CKB) & AI Resume Parsing (/profile)
   ↓
3. Job Discovery, Filters & Live Scraping (/jobs)
   ↓
4. AI Job-Fit Explainability & Gap Analysis (/jobs -> Modal)
   ↓
5. AI Resume Tailoring & LaTeX Compilation (/jobs or /profile)
   ↓
6. Application Pipeline & Kanban Funnel (/applications)
   ↓
7. Career Analytics & Pipeline Metrics (/analytics)
   ↓
8. Admin Crawler Controls & Prototype Reset (/admin)
   ↓
9. Data Privacy, Governance & JSON Export (/admin -> Settings)
```

---

## 3. Detailed Workflows

### Workflow 1: Authentication & User Management

- **Target URLs:**
  - Candidate Registration: `http://localhost:5173/signup`
  - Sign In: `http://localhost:5173/login`
  - Password Reset: `http://localhost:5173/forgot-password`

#### Step-by-Step Testing Procedure:
1. Navigate to `/signup`.
2. Fill in:
   - **Full Name:** e.g., `Alex Morgan`
   - **Email:** e.g., `alex.morgan@example.com`
   - **Password:** e.g., `TestPassword123!`
   - **Headline:** e.g., `Full Stack & AI Engineer`
3. Click **Create Account**.
   - **Expected Result:** The user is registered, an active session token is issued, and the browser automatically redirects to the **Career Overview** dashboard (`/`).
4. In the bottom sidebar, click **Log Out**.
   - **Expected Result:** Redirects to `/login`. Protected routes become inaccessible until authenticated.
5. Sign back in at `/login` with the newly created credentials.
   - **Expected Result:** Successful login and session restoration.
6. Test Forgot Password:
   - Navigate to `/forgot-password`, input your email, and submit.
   - **Expected Result:** Password reset token is generated and logged/displayed.

---

### Workflow 2: Career Knowledge Base (CKB) & Profile Setup

The Career Knowledge Base acts as the candidate's single source of truth for resume tailoring and job matching.

- **Target URL:** `http://localhost:5173/profile`

#### Step-by-Step Testing Procedure:

#### A. Resume Document Upload & AI Entity Extraction
1. Scroll down to **Resume Documents & AI Extraction**.
2. Upload a sample `.pdf`, `.docx`, or `.txt` resume document.
3. Click **Upload & Extract Entities**.
   - **Expected Result:** The document is securely stored and parsed. Discovered skills, work history, and projects appear in the **Extracted Candidate Entities** staging review table.
4. Review extracted items:
   - Click **Accept All Extracted** or review items individually.
   - **Expected Result:** Approved items are migrated into the official Career Knowledge Base.

#### B. Manual Career Records Entry
1. Under **Career Records & Verification**, select the entity type to add:
   - **Skill:** Enter name (e.g. `FastAPI`, `PostgreSQL`, `React`, `Docker`) and proficiency level.
   - **Project:** Enter project name (e.g. `High-Throughput Distributed API`), technology stack, and description.
   - **Experience:** Add role title, company name, and key bullet points.
   - **Education:** Add degree, institution, and graduation year.
2. Click **Save Entity**.
   - **Expected Result:** Entity is assigned an immutable ID and saved with a `confirmed` status badge.

#### C. External Data Ingestion
1. Under **External Profile Ingestion**:
   - **GitHub:** Enter a public GitHub username (e.g., `octocat` or your handle) and click **Ingest GitHub**.
   - **Expected Result:** Syncs public repositories, detected languages, and contributions.
   - **LinkedIn / Portfolio:** Enter a portfolio URL or paste a profile document.
   - **Expected Result:** Background parser normalizes external text into candidate entity drafts.

---

### Workflow 3: Live Job Discovery, Search & Scraping

- **Target URL:** `http://localhost:5173/jobs`

#### Step-by-Step Testing Procedure:

#### A. Browsing & Filtering
1. Open `/jobs`.
2. Observe the curated company job listings (Stripe, Datadog, Figma, Notion, etc.).
3. Test search and filtering controls:
   - **Search Input:** Type keywords like `Python`, `Frontend`, or `Manager`.
   - **Location Filter:** Filter by cities or regions.
   - **Work Mode:** Select `Remote`, `Hybrid`, or `Onsite`.
   - **Job Type:** Select `Full-time` or `Internship`.
   - **Expected Result:** Job cards update instantly without page reloads.

#### B. Pagination & Bookmarking
1. Scroll to the bottom and use the pagination controls (`Previous`, `Page numbers`, `Next`).
   - **Expected Result:** Clean navigation between pages of 10 items.
2. Click the **Bookmark** icon on any job card.
   - **Expected Result:** Bookmark state is toggled and saved to the candidate profile.

#### C. Running the Live Naukri / JobSpy Scraper
1. In the top action bar on `/jobs`, click **Scrape Naukri Jobs**.
2. Enter search criteria:
   - **Keyword:** e.g., `FastAPI Developer`
   - **Location:** e.g., `Bangalore`
   - **Results Limit:** `10`
3. Click **Run Live Scraper**.
   - **Expected Result:** The backend triggers `JobSpy` to query live job board listings, normalizes and deduplicates the results, and appends them to your active feed.

---

### Workflow 4: Explainable AI Job-Fit & Skill Gap Analysis

- **Target URL:** `http://localhost:5173/jobs` $\rightarrow$ Click **Why this role?**

#### Step-by-Step Testing Procedure:
1. On any job card, locate the **Match Score** badge (e.g., `85% Match`, `42% Match`).
   - **Logic:** The score dynamically balances verified skill overlap, candidate headline, and experience level.
2. Click **Why this role?** on the job card.
3. In the **Job Intelligence Modal**, verify:
   - **Matched Skills:** Green badges indicating skills present in your CKB that match role requirements.
   - **Missing Skills:** Amber/red badges indicating required skills not yet in your CKB.
   - **Suggested Projects:** Recommends which of your verified CKB projects best demonstrate qualifications for this role.
   - **Actionable Learning Advice:** Actionable guidance to help you bridge skill gaps.
4. Test recommendation feedback:
   - Click the **Thumbs Up** or **Thumbs Down** icon.
   - **Expected Result:** User feedback is recorded to calibrate recommendation ranking weights.

---

### Workflow 5: AI Resume Tailoring & LaTeX Compilation

NextHire incorporates an **Anti-Hallucination Provenance Guard**: every bullet point in generated resumes must reference a confirmed entity ID in your Career Knowledge Base.

- **Target URLs:**
  - Direct Action: Click **Tailor Resume** on any job card in `/jobs` or within the "Why this role?" modal.
  - Profile Hub: `http://localhost:5173/profile` $\rightarrow$ **AI Tailored Resumes** section.

#### Step-by-Step Testing Procedure:
1. Click **Tailor Resume** on a selected job card.
2. The **Tailored Resume Modal** opens:
   - **Formatted Resume View (Tab 1):**
     - Professional summary tailored to the job description.
     - Tailored core competencies and skill ordering.
     - Work experience and project bullets featuring **Verified CKB Entity** provenance badges.
   - **LaTeX Source View (.tex) (Tab 2):**
     - Switch to the **LaTeX Source** tab.
     - Verify clean LaTeX document syntax with escaped control characters (e.g., `\&` instead of raw `&`).
     - Click **Copy LaTeX** to copy the code to your clipboard.
     - Click **Download .tex** to save the `.tex` file directly to your machine.
3. Approve Version:
   - In the modal footer, toggle the status from `Draft` to `Approved`.
   - **Expected Result:** Resume record is saved with status `approved` and timestamped.
4. Versioning Check:
   - Tailor a resume again for the same job.
   - **Expected Result:** Generates `Version 2` without overwriting `Version 1`.

---

### Workflow 6: Application Pipeline & Kanban Tracking

- **Target URL:** `http://localhost:5173/applications`

#### Step-by-Step Testing Procedure:
1. Navigate to `/applications`.
2. Inspect the **Simplified Applications Workspace**:
   - By default, applications display in clean, high-density cards highlighting job title, company name, and current status.
   - Click anywhere on an application card to open the drill-down detail modal with full history, notes, compensation, and status updates.
3. **Manual Application Creation:**
   - Click **Add Application Manually** at the top of the applications view.
   - Fill in all application metadata: Custom Company Name, Job Title, Job URL, Job Description, Salary Range, Location, Notes, Deadlines, and Initial Status.
   - Click **Create Application**.
   - **Expected Result:** The new application immediately appears in the list and persists across reloads.
4. Manage stages across the pipeline:
   - `Saved` $\rightarrow$ `Applied` $\rightarrow$ `Interviewing` $\rightarrow$ `Offer` $\rightarrow$ `Rejected`.
5. Update application metadata:
   - Add notes, expected compensation, interview dates, and assessment deadlines.
   - **Expected Result:** Stage transitions and notes persist across page reloads.
6. Verify notification badges:
   - When an interview or assessment deadline is scheduled, check the notification bell in the top navigation bar for automated alerts.
7. Application Deletion:
   - In the application modal, click **Delete Application** to remove it cleanly.

---

### Workflow 7: Career Analytics & Search Funnel

- **Target URL:** `http://localhost:5173/analytics`

#### Step-by-Step Testing Procedure:
1. Navigate to `/analytics`.
2. Inspect the analytics dashboards:
   - **Pipeline Conversion Funnel:** Visualizes conversion rates from `Saved` to `Applied`, `Interview`, and `Offer`.
   - **Skill Demand Matrix:** Compares most-demanded skills across discovered jobs against your verified profile skills.
   - **Discovery Velocity:** Visualizes newly discovered jobs and weekly application activity.

---

### Workflow 8: Admin Console, Scraping & Candidate Whitelist Queue

- **Access Requirement:** Must be logged in as an administrator.
- **Login:** `admin@nexthire.dev` / `Admin12345!`
- **Target URL:** `http://localhost:5173/admin`

#### Step-by-Step Testing Procedure:
1. Log in with admin credentials and open `/admin`.
2. **Candidate Target Company Whitelist Queue:**
   - When a candidate adds a new unmonitored target company in `/profile` (e.g., "Swiggy", "Zomato", "Stripe"), it automatically enters the admin review queue.
   - In the overview cards, observe the amber pill: `{N} pending whitelist`.
   - In the **Candidate Whitelist Queue** panel, review pending requests with candidate badges.
   - Click **Approve & Scrape Naukri**:
     - **Expected Result:** NextHire marks the company as verified and immediately triggers the `JobSpy` background worker to scrape 10–12 verified live roles from Naukri, indexing them into the database.
   - Alternatively, click **Reject** to dismiss and delete the request.
3. **Target Company Whitelist Filtering:**
   - In the Target Companies table, toggle between **All Companies**, **Whitelisted**, and **Pending Whitelist** filters.
4. **Naukri Live Job Ingestion via JobSpy:**
   - In the **JobSpy · Naukri Live Job Ingestion** section, enter a keyword (e.g. `Software Engineer`), location (e.g. `Bengaluru, India`), and limit (e.g. `20`).
   - Click **Scrape from Naukri**.
   - **Expected Result:** Live postings with skills, salary, and direct application links are ingested directly into the global database.
5. **Company Crawler Management & Prototype Reset:**
   - Inspect configured companies, toggle active/paused, or click **Reset to Top 12**.
6. **System Audit Logs & Crawler Status:**
   - Check scheduler status (12-hour automated scraping), crawl frequency, and error logs.

---

### Workflow 9: Data Privacy, Governance & Retention

- **Target URL:** `http://localhost:5173/admin` (displayed as **Settings** for candidate accounts)

#### Step-by-Step Testing Procedure:
1. Log in as a candidate and navigate to `/admin` (or click **Settings** in the sidebar).
2. **Export Personal Data (GDPR/CCPA Compliance):**
   - Click **Export My Data**.
   - **Expected Result:** Downloads a structured `nexthire_user_data_export.json` file containing all profile records, CKB entities, applications, and tailored resumes.
3. **Data Retention Policy:**
   - Configure retention policies (e.g., auto-purge inactive applications or drafts after 90, 180, or 365 days).
4. **Granular Privacy Controls:**
   - Toggle AI analytics tracking, telemetry, and external profile visibility.

---

## 4. Automated Verification Commands

Run these automated commands directly in the terminal to verify system integrity:

```powershell
# 1. Run all Backend Unit & Integration Tests (57 tests)
cd d:\Programs\NextHire(Copilot)\backend
python -m pytest -q

# 2. Run the Whitelist & Scraping Workflow Tests
python -m pytest tests/test_whitelist.py -q

# 3. Run all Frontend Unit Tests (9 tests)
cd d:\Programs\NextHire(Copilot)\frontend
npm test -- --run

# 4. Validate Production Build
npm run build
```
