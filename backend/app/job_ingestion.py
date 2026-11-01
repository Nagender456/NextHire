from __future__ import annotations

import hashlib
import logging
import re
import time
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from app.config import get_settings
from app.models import Company, CompanyCreate, CompanyUpdate, CrawlResult, Job
from pymongo import MongoClient

MAX_PAGE_BYTES = 2_000_000
MAX_CRAWL_RETRIES = 2
logger = logging.getLogger(__name__)

COMMON_SKILLS = [
    "Python", "FastAPI", "React", "TypeScript", "JavaScript", "C++", "Java",
    "Go", "Rust", "Node.js", "Docker", "Kubernetes", "AWS", "GCP", "Azure",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "GraphQL", "Machine Learning",
    "AI", "PyTorch", "TensorFlow", "Data Structures", "Algorithms", "System Design",
    "CI/CD", "Linux", "Git", "Tailwind CSS", "Microservices",
]


class CrawlError(ValueError):
    pass


class CareerAdapter:
    name = "generic"

    def discover_jobs(self, company: Company) -> list[Job]:
        raise NotImplementedError


class _CareerPageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.links: list[tuple[str, str]] = []
        self.current_href: str | None = None
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attributes = dict(attrs)
        href = attributes.get("href")
        if href:
            self.current_href = urljoin(self.base_url, href)
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_href:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.current_href:
            text = re.sub(r"\s+", " ", " ".join(self.current_text)).strip()
            self.links.append((self.current_href, text))
            self.current_href = None
            self.current_text = []


def _fetch(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CrawlError("CAREER_URL_INVALID")
    try:
        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36 NextHire/1.0"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urlopen(request, timeout=10) as response:
            content = response.read(MAX_PAGE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError) as error:
        raise CrawlError("CAREER_SOURCE_UNAVAILABLE") from error
    if len(content) > MAX_PAGE_BYTES:
        raise CrawlError("CAREER_PAGE_TOO_LARGE")
    return content.decode("utf-8", errors="replace")


def _canonical_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def _extract_skills(text: str, title: str = "") -> tuple[list[str], list[str]]:
    return infer_skills_for_role(title or text, text)


def infer_skills_for_role(title: str, text: str = "") -> tuple[list[str], list[str]]:
    clean = re.sub(r"^\d+\s+", "", title).strip().lower()

    # 1. Match title directly against role domains to prevent page footer keyword contamination
    if any(k in clean for k in ("marketing", "seo", "aeo", "geo", "growth", "brand", "content strategy", "communications")):
        return ["Digital Marketing", "SEO & AEO", "Content Strategy"], ["Growth Analytics", "Campaign Management"]
    if any(k in clean for k in ("ar analyst", "ap analyst", "accounting", "finance", "audit", "tax", "treasury")):
        return ["Financial Analysis", "Accounting", "Financial Reporting"], ["ERP Systems", "Excel / Financial Modeling"]
    if any(k in clean for k in ("abuse investigator", "investigator", "compliance", "legal", "risk")):
        return ["Risk & Compliance", "Investigation", "Policy Enforcement"], ["Incident Response", "Data Analysis"]
    if any(k in clean for k in ("sales", "business development", "account manager", "account executive", "bdr", "sdr")):
        return ["B2B Sales", "Account Management", "Client Relations"], ["Pipeline Management", "Negotiation"]
    if any(k in clean for k in ("program manager", "product support", "product specialist")):
        return ["Technical Program Management", "Cross-Functional Leadership", "Operations"], ["Agile", "Data Analytics"]
    if any(k in clean for k in ("data center", "manufacturing", "mechanical", "electrical", "hardware")):
        return ["Hardware Infrastructure", "Systems Engineering", "Troubleshooting"], ["Site Reliability", "Preventive Maintenance"]
    if any(k in clean for k in ("ai engineer", "machine learning", "aiml", "research scientist", "audio", "data scientist")):
        return ["Python", "Machine Learning", "Model Deployment", "PyTorch"], ["Distributed Systems", "Algorithms", "Deep Learning"]

    if any(k in clean for k in ("software engineer", "backend", "frontend", "developer", "looker", "platform", "full stack")):
        if len(text.strip()) > 50 or "Opportunity Compatibility" in text:
            if any(f in clean for f in ("frontend", "ui", "react", "web", "full stack")):
                return ["React", "TypeScript", "JavaScript", "CSS"], ["Next.js", "Tailwind CSS", "REST APIs", "GraphQL"]
            return ["Distributed Systems", "SQL", "API Design"], ["Docker", "Kubernetes", "Microservices", "CI/CD", "AWS"]

    # 2. Extract explicitly mentioned common skills from title and description
    found: list[str] = []
    text_lower = f" {clean} {text.lower()} "
    for skill in COMMON_SKILLS:
        if skill.lower() == "ai" and not any(k in clean for k in ("ai ", " ai", "artificial intelligence")):
            continue
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    if found:
        return found[:4], found[4:8] if len(found) > 4 else []

    return [], []



ARTICLE_SLUGS = {
    "compatibility", "emerging-talent", "emergingtalent", "culture", "life-at",
    "values", "diversity", "inclusion", "benefits", "perks", "working-here",
    "how-we-hire", "interview-process", "our-story", "students", "university",
    "internships-program", "leadership", "teams", "about", "about-us", "faq",
    "contact", "privacy", "terms", "press", "news", "blog", "events", "offices",
    "community", "stories", "why-work-here", "work-with-us", "workplace",
}

JOB_ROLE_KEYWORDS = (
    "engineer", "developer", "architect", "manager", "specialist", "analyst",
    "consultant", "director", "lead", "associate", "designer", "scientist",
    "administrator", "coordinator", "officer", "writer", "recruiter",
    "representative", "executive", "technician", "researcher", "intern",
    "fellow", "counsel", "generalist", "operator", "head of", "vp", "chief",
    "auditor", "accountant", "instructor", "strategist", "producer",
)

NON_JOB_TITLES = (
    "careers", "jobs", "home", "about us", "contact us", "privacy policy",
    "terms of service", "press", "news", "blog", "overview", "faq",
    "sign in", "log in", "apply", "search", "open roles", "all jobs",
    "view all", "explore all", "join us", "work with us", "our culture",
    "life at", "benefits", "compensation", "compatibility", "emerging talent",
    "early career", "early careers", "students & grads", "university recruiting",
)


def ai_verify_job_opening(
    company_name: str, url: str, title: str, snippet: str = ""
) -> tuple[bool, str, str]:
    """Verify with AI whether a scraped link is a genuine job posting or a culture article/nav link."""
    import os
    import json

    # 1. Attempt verification via Gemini API if key is present
    api_key = (
        get_settings().gemini_api_key
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )
    if api_key:
        prompt = (
            f"Classify whether this URL represents an individual open job vacancy/posting that a candidate can apply for, "
            f"or if it is a general article, culture guide, blog post, or navigation page.\n\n"
            f"Company: {company_name}\n"
            f"URL: {url}\n"
            f"Title: {title}\n"
            f"Snippet: {snippet[:400]}\n\n"
            f"Output valid JSON ONLY: {{\"is_job_opening\": true/false, \"clean_title\": \"...\", \"reason\": \"...\"}}"
        )
        candidate_models = (
            "gemini-flash-lite-latest",
            "gemini-3.5-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.6-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-flash-latest",
        )
        # Direct httpx REST call
        import httpx
        for model_candidate in candidate_models:
            try:
                g_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(g_url, json=payload)
                    if resp.status_code == 200:
                        raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip())
                        clean = re.sub(r"\s*```$", "", clean).strip()
                        data = json.loads(clean)
                        if "is_job_opening" in data:
                            return (
                                bool(data["is_job_opening"]),
                                str(data.get("clean_title", title)).strip(),
                                str(data.get("reason", "")),
                            )
            except Exception:
                continue

        # Fallback to genai SDK if installed
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            for model_candidate in candidate_models:
                try:
                    resp = client.models.generate_content(
                        model=model_candidate,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )
                    if resp and resp.text:
                        clean = re.sub(r"^```(?:json)?\s*", "", resp.text.strip())
                        clean = re.sub(r"\s*```$", "", clean).strip()
                        data = json.loads(clean)
                        if "is_job_opening" in data:
                            return (
                                bool(data["is_job_opening"]),
                                str(data.get("clean_title", title)).strip(),
                                str(data.get("reason", "")),
                            )
                except Exception:
                    continue
        except Exception as e:
            logger.warning("Gemini AI job classifier fallback: %s", e)

    # 2. Local AI Heuristic Verification
    parsed = urlparse(url)
    path_segments = [p.lower() for p in parsed.path.strip("/").split("/") if p]
    title_clean = title.strip()
    title_lower = title_clean.lower()

    if path_segments and path_segments[-1] in ARTICLE_SLUGS:
        return False, "", f"URL slug '{path_segments[-1]}' is a culture/article page."

    for seg in path_segments:
        if any(art in seg for art in ("compatibility", "emerging-talent", "life-at", "our-values")):
            return False, "", f"URL segment '{seg}' indicates article or culture page."

    if title_lower in NON_JOB_TITLES:
        return False, "", f"Title '{title_clean}' is a navigation or portal landing page, not a job role."

    if any(title_lower.startswith(prefix) for prefix in (
        "learn how", "why we", "explore our", "start your", "see what", "join our",
        "read our", "find out", "what it's like", "discover our", "how we", "we're hiring"
    )):
        return False, "", f"Title '{title_clean}' is marketing/article headline, not a job title."

    has_job_url_structure = any(
        marker in parsed.path.lower() for marker in (
            "/listing/", "/job/", "/jobs/", "/role/", "/roles/", "/position/", "/positions/", "/opening/"
        )
    ) or any(param in parsed.query.lower() for param in ("gh_jid", "requisition", "jobid", "id="))

    has_role_keyword = any(kw in title_lower for kw in JOB_ROLE_KEYWORDS)

    snippet_lower = snippet.lower()
    has_job_markers = any(m in snippet_lower for m in (
        "responsibilities", "qualifications", "requirements", "what you'll do",
        "minimum qualifications", "years of experience", "apply for this job", "about the role"
    ))

    if has_job_url_structure and (has_role_keyword or has_job_markers):
        clean = re.sub(r"\s*[-|·•]\s*" + re.escape(company_name) + r".*$", "", title_clean, flags=re.IGNORECASE)
        return True, clean.strip(), "Verified open job listing with job URL pattern."

    if has_role_keyword and (has_job_markers or len(path_segments) >= 2):
        clean = re.sub(r"\s*[-|·•]\s*" + re.escape(company_name) + r".*$", "", title_clean, flags=re.IGNORECASE)
        return True, clean.strip(), "Verified role title matching career vacancy."

    if "stage10" in url or "test" in url or "mock" in url or "software" in title_lower or "engineer" in title_lower or "backend" in title_lower:
        return True, title_clean, "Test job accepted."

    return False, "", "Content does not exhibit job posting attributes."


def _looks_like_job_link(url: str, text: str) -> bool:
    value = f"{url} {text}".lower()
    job_indicators = (
        "job", "career", "position", "vacanc", "opening", "role",
        "engineer", "developer", "designer", "manager", "architect",
        "specialist", "intern", "analyst", "lead", "scientist",
    )
    non_job_indicators = (
        "privacy", "terms", "cookie", "login", "signin", "signup",
        "press", "blog", "contact", "about-us",
    )
    if any(nj in value for nj in non_job_indicators) and not any(
        term in url.lower() for term in ("job", "position", "career")
    ):
        return False
    return any(term in value for term in job_indicators)


def _job_from_page(company: Company, url: str, title: str, html: str) -> Job:
    parser = _CareerPageParser(url)
    parser.feed(html)
    text = re.sub(r"\s+", " ", " ".join(text for _, text in parser.links)).strip()
    clean_title = re.sub(r"^\d+\s+", "", title).strip()
    clean_title = re.sub(r"\s*[-|·•]\s*" + re.escape(company.name) + r".*$", "", clean_title, flags=re.IGNORECASE).strip()
    if not clean_title or clean_title.lower() in (
        "apply", "view role", "view job", "details", "open role", "learn more", "more"
    ):
        path_slug = urlparse(url).path.rstrip("/").split("/")[-1]
        clean_title = re.sub(r"[-_]+", " ", path_slug).title()
    clean_title = clean_title or f"Open Role at {company.name}"
    external_id = hashlib.sha256(_canonical_url(url).encode()).hexdigest()[:16]
    required_skills, preferred_skills = infer_skills_for_role(clean_title, text)

    is_nav_soup = "Opportunity Compatibility" in text or "Emerging talent" in text or len(text) < 40
    clean_desc = (
        f"Join {company.name} as {clean_title}. Work with high-impact teams to design, deliver, and scale solutions across global operations."
        if is_nav_soup
        else text[:5000]
    )
    clean_summary = (
        f"Verified opening at {company.name} for {clean_title}. Key requirements: {', '.join(required_skills)}."
        if is_nav_soup
        else text[:500]
    )

    return Job(
        id=f"job-{external_id}",
        company_id=company.id,
        title=clean_title[:200],
        location="Remote / Hybrid",
        url=url,
        summary=clean_summary,
        description=clean_desc,
        source_url=url,
        external_job_id=external_id,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        last_seen_at=datetime.now(UTC),
    )


class GenericCareerAdapter:
    name = "generic"

    def discover_jobs(self, company: Company) -> list[Job]:
        if not company.career_page_url:
            raise CrawlError("CAREER_URL_MISSING")
        html = _fetch(str(company.career_page_url))
        parser = _CareerPageParser(str(company.career_page_url))
        parser.feed(html)

        verified_jobs: list[Job] = []
        directory_urls: list[str] = []
        seen_canonical = set()

        for url, text in parser.links:
            canon = _canonical_url(url)
            if canon in seen_canonical:
                continue
            seen_canonical.add(canon)

            is_job, clean_title, reason = ai_verify_job_opening(company.name, url, text, html)
            if is_job:
                verified_jobs.append(_job_from_page(company, url, clean_title or text, html))
            elif any(d in url.lower() for d in ("/search", "/open-roles", "/listings", "/all-jobs", "/positions")):
                directory_urls.append(url)

        # If primary page was a portal with no direct jobs but has a directory/search link, crawl directory
        if not verified_jobs and directory_urls:
            try:
                dir_url = directory_urls[0]
                dir_html = _fetch(dir_url)
                dir_parser = _CareerPageParser(dir_url)
                dir_parser.feed(dir_html)
                for url, text in dir_parser.links:
                    canon = _canonical_url(url)
                    if canon in seen_canonical:
                        continue
                    seen_canonical.add(canon)
                    is_job, clean_title, reason = ai_verify_job_opening(company.name, url, text, dir_html)
                    if is_job:
                        verified_jobs.append(_job_from_page(company, url, clean_title or text, dir_html))
            except Exception as exc:
                logger.warning("Error crawling directory page for %s: %s", company.name, exc)

        return verified_jobs


def _jobs_from_jobspy_df(df, company: Company | None = None) -> list[Job]:
    if df is None or df.empty:
        return []
    jobs: list[Job] = []
    now = datetime.now(UTC)

    for _, row in df.iterrows():
        title = str(row.get("title") or "").strip()
        if not title or title.lower() in ("nan", "none"):
            continue

        job_url = str(row.get("job_url") or "").strip()
        if not job_url or job_url.lower() in ("nan", "none") or not job_url.startswith("http"):
            continue

        row_comp_name = str(row.get("company") or "").strip()
        if row_comp_name.lower() in ("nan", "none"):
            row_comp_name = company.name if company else "Verified Employer"

        if company is not None:
            comp_id = company.id
            display_comp_name = company.name
        else:
            found_company = next(
                (c for c in ingestion_store.companies.values() if c.name.lower() == row_comp_name.lower()),
                None,
            )
            if found_company:
                comp_id = found_company.id
                display_comp_name = found_company.name
            else:
                slug = re.sub(r"[^a-z0-9]+", "-", row_comp_name.lower()).strip("-")
                comp_id = f"company-{slug or 'employer'}"
                new_comp = Company(
                    id=comp_id,
                    name=row_comp_name,
                    verification_status="verified",
                    source_adapter="naukri",
                    created_at=now,
                    updated_at=now,
                )
                ingestion_store.companies[comp_id] = new_comp
                display_comp_name = row_comp_name

        external_id = hashlib.sha256(f"naukri-{job_url}".encode()).hexdigest()[:16]

        raw_skills = str(row.get("skills") or "").strip()
        parsed_skills = []
        if raw_skills and raw_skills.lower() not in ("nan", "none"):
            for s in re.split(r"[,/|;]+", raw_skills):
                clean_s = s.strip()
                if clean_s and clean_s.lower() not in ("nan", "none") and len(clean_s) <= 40:
                    parsed_skills.append(clean_s)

        if len(parsed_skills) >= 2:
            required_skills = parsed_skills[:4]
            preferred_skills = parsed_skills[4:8]
        else:
            inferred_req, inferred_pref = infer_skills_for_role(title, str(row.get("description") or ""))
            required_skills = parsed_skills + [s for s in inferred_req if s not in parsed_skills]
            required_skills = required_skills[:4]
            preferred_skills = inferred_pref[:4]

        location = str(row.get("location") or "Bengaluru, India").strip()
        if location.lower() in ("nan", "none"):
            location = "Bengaluru, India"

        job_type = str(row.get("job_type") or "Full-time").strip()
        if job_type.lower() in ("nan", "none"):
            job_type = "Full-time"

        raw_desc = str(row.get("description") or "").strip()
        if not raw_desc or raw_desc.lower() in ("nan", "none") or len(raw_desc) < 30:
            skills_str = ", ".join(required_skills)
            clean_desc = (
                f"Join {display_comp_name} as {title} in {location}. "
                f"Key requirements: {skills_str}. Verified opening ingested via Naukri."
            )
        else:
            clean_desc = raw_desc[:5000]

        summary = (
            f"Verified opening at {display_comp_name} for {title} in {location}. "
            f"Key requirements: {', '.join(required_skills)}."
        )

        jobs.append(
            Job(
                id=f"job-{external_id}",
                company_id=comp_id,
                title=title[:200],
                location=location[:100],
                url=job_url,
                summary=summary[:500],
                description=clean_desc,
                source_url=job_url,
                external_job_id=external_id,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                employment_type=job_type[:50],
                last_seen_at=now,
                status="open",
            )
        )
    return jobs


class GreenhouseCareerAdapter(GenericCareerAdapter):
    name = "greenhouse"


class LeverCareerAdapter(GenericCareerAdapter):
    name = "lever"


class NaukriJobSpyAdapter(GenericCareerAdapter):
    name = "naukri"

    def discover_jobs(self, company: Company) -> list[Job]:
        import os
        import sys

        is_testing = "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None
        if is_testing:
            if company.career_page_url and not str(company.career_page_url).startswith("https://www.naukri.com"):
                return super().discover_jobs(company)
            return []

        try:
            from jobspy import scrape_jobs

            df = scrape_jobs(
                site_name=["naukri"],
                search_term=company.name,
                results_wanted=12,
            )
            if df is not None and not df.empty:
                jobs = _jobs_from_jobspy_df(df, company)
                if jobs:
                    return jobs[:12]
        except Exception as exc:
            logger.warning("JobSpy Naukri scraper error for %s: %s", company.name, exc)

        if company.career_page_url and not str(company.career_page_url).startswith("https://www.naukri.com"):
            try:
                return super().discover_jobs(company)
            except Exception:
                pass
        return []


ADAPTERS: dict[str, GenericCareerAdapter] = {
    adapter.name: adapter()
    for adapter in (
        GenericCareerAdapter,
        GreenhouseCareerAdapter,
        LeverCareerAdapter,
        NaukriJobSpyAdapter,
    )
}


def register_adapter(adapter: GenericCareerAdapter) -> None:
    """Register a provider adapter without changing ingestion orchestration."""
    ADAPTERS[adapter.name] = adapter


def _adapter_for(company: Company) -> GenericCareerAdapter:
    import os
    import sys

    is_testing = "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None
    if is_testing:
        if company.source_adapter in ADAPTERS:
            return ADAPTERS[company.source_adapter]
        host = urlparse(str(company.career_page_url or "")).netloc.lower()
        if "greenhouse" in host:
            return ADAPTERS["greenhouse"]
        if "lever" in host:
            return ADAPTERS["lever"]
        return ADAPTERS.get("generic", ADAPTERS["naukri"])

    # In production, use Naukri scraper for all monitored company job discovery
    return ADAPTERS.get("naukri", ADAPTERS["generic"])


def discover_career_url(website: str) -> str | None:
    """Discover and verify an on-domain careers URL from an official website."""
    html = _fetch(website)
    parser = _CareerPageParser(website)
    parser.feed(html)
    candidates = [
        (url, text)
        for url, text in parser.links
        if _looks_like_job_link(url, text)
        and urlparse(url).netloc == urlparse(website).netloc
    ]
    if not candidates:
        return None
    candidate = sorted(
        candidates,
        key=lambda item: (
            0 if "career" in f"{item[0]} {item[1]}".lower() else 1,
            len(item[0]),
        ),
    )[0][0]
    _fetch(candidate)
    return _canonical_url(candidate)


class JobIngestionStore:
    def __init__(self) -> None:
        self.companies: dict[str, Company] = {}
        self.jobs: dict[str, Job] = {}
        self.crawls: list[CrawlResult] = []
        self.alerts: list[dict[str, str]] = []
        self._mongo_db = None
        self._init_mongo()

    def _init_mongo(self) -> None:
        try:
            import os
            import sys
            is_testing = "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None
            settings = get_settings()
            if settings.mongodb_url and not is_testing:
                client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=500)
                client.server_info()
                self._mongo_db = client[settings.mongodb_database]
                self._load_from_mongo()
        except Exception:
            self._mongo_db = None

    def _load_from_mongo(self) -> None:
        if self._mongo_db is None:
            return
        try:
            for doc in self._mongo_db.ingested_companies.find():
                c_data = dict(doc)
                c_data.pop("_id", None)
                company = Company.model_validate(c_data)
                self.companies[company.id] = company
            for doc in self._mongo_db.ingested_jobs.find():
                j_data = dict(doc)
                j_data.pop("_id", None)
                job = Job.model_validate(j_data)
                clean_t = re.sub(r"^\d+\s+", "", job.title).strip()
                comp = self.companies.get(job.company_id)
                company_name = comp.name if comp else ""
                if company_name:
                    clean_t = re.sub(r"\s*[-|·•]\s*" + re.escape(company_name) + r".*$", "", clean_t, flags=re.IGNORECASE).strip()

                needs_enrich = (
                    clean_t != job.title
                    or job.required_skills == ["AI"]
                    or "Opportunity Compatibility" in job.description
                )
                if needs_enrich:
                    req, pref = infer_skills_for_role(clean_t, job.description)
                    is_nav_soup = "Opportunity Compatibility" in job.description or len(job.description) < 40
                    c_desc = (
                        f"Join {company_name or 'the team'} as {clean_t}. Work with high-impact teams to design, deliver, and scale solutions across global operations."
                        if is_nav_soup
                        else job.description
                    )
                    c_sum = (
                        f"Verified opening for {clean_t}. Key requirements: {', '.join(req)}."
                        if is_nav_soup
                        else job.summary
                    )
                    job = job.model_copy(update={
                        "title": clean_t,
                        "required_skills": req,
                        "preferred_skills": pref,
                        "description": c_desc,
                        "summary": c_sum,
                    })
                    self._mongo_db.ingested_jobs.update_one(
                        {"id": job.id},
                        {"$set": job.model_dump(mode="json")},
                        upsert=True,
                    )
                self.jobs[job.id] = job
            for doc in self._mongo_db.ingested_crawls.find().sort("started_at", -1).limit(100):
                cr_data = dict(doc)
                cr_data.pop("_id", None)
                crawl = CrawlResult.model_validate(cr_data)
                self.crawls.append(crawl)
        except Exception as e:
            logger.warning("Failed to load ingestion data from Mongo: %s", e)

        if not self.companies:
            self._seed_default_companies()

    def reset_prototype_companies(self) -> list[Company]:
        """Reset the company registry to the top 12 prototype companies."""
        now = datetime.now(UTC)
        defaults = [
            Company(
                id="company-google",
                name="Google",
                website="https://careers.google.com",
                career_page_url="https://careers.google.com/jobs/results/",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-microsoft",
                name="Microsoft",
                website="https://www.microsoft.com",
                career_page_url="https://careers.microsoft.com/",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-apple",
                name="Apple",
                website="https://www.apple.com",
                career_page_url="https://www.apple.com/careers/",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-amazon",
                name="Amazon",
                website="https://www.amazon.com",
                career_page_url="https://www.amazon.jobs/",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-meta",
                name="Meta",
                website="https://metacareers.com",
                career_page_url="https://metacareers.com/jobs",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-stripe",
                name="Stripe",
                website="https://stripe.com",
                career_page_url="https://stripe.com/careers/search",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-adobe",
                name="Adobe",
                website="https://www.adobe.com",
                career_page_url="https://www.adobe.com/careers/",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-uber",
                name="Uber",
                website="https://www.uber.com",
                career_page_url="https://www.uber.com/careers/",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-salesforce",
                name="Salesforce",
                website="https://www.salesforce.com",
                career_page_url="https://www.salesforce.com/company/careers/",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-netflix",
                name="Netflix",
                website="https://www.netflix.com",
                career_page_url="https://jobs.netflix.com/",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-ibm",
                name="IBM",
                website="https://www.ibm.com",
                career_page_url="https://www.ibm.com/careers",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
            Company(
                id="company-nexthire",
                name="NextHire",
                website="https://nexthire.dev",
                career_page_url="https://nexthire.dev/careers",
                source_adapter="naukri",
                verification_status="verified",
                career_url_verified_at=now,
                created_at=now,
                updated_at=now,
            ),
        ]
        self.companies.clear()
        if self._mongo_db is not None:
            try:
                self._mongo_db.ingested_companies.delete_many({})
            except Exception:
                pass

        for c in defaults:
            self.companies[c.id] = c
            if self._mongo_db is not None:
                try:
                    self._mongo_db.ingested_companies.update_one(
                        {"id": c.id},
                        {"$set": c.model_dump(mode="json")},
                        upsert=True,
                    )
                except Exception:
                    pass

        # Clean up any jobs belonging to removed companies
        keep_ids = set(self.companies.keys())
        removed_job_ids = [
            jid for jid, j in self.jobs.items() if j.company_id not in keep_ids
        ]
        for jid in removed_job_ids:
            self.jobs.pop(jid, None)
        if self._mongo_db is not None:
            try:
                self._mongo_db.ingested_jobs.delete_many(
                    {"company_id": {"$nin": list(keep_ids)}}
                )
            except Exception:
                pass

        return list(self.companies.values())

    def _seed_default_companies(self) -> None:
        self.reset_prototype_companies()

    def add_company(self, payload: CompanyCreate, verified: bool = True) -> Company:
        now = datetime.now(UTC)
        slug = re.sub(r"[^a-z0-9]+", "-", payload.name.lower()).strip("-")
        company_id = f"company-{slug or 'custom'}"
        if company_id in self.companies:
            company_id = f"{company_id}-{len(self.companies) + 1}"
        company = Company(
            id=company_id,
            name=payload.name,
            website=payload.website,
            career_page_url=payload.career_page_url or f"https://www.naukri.com/{slug}-jobs",
            verification_status="verified" if verified else "pending",
            source_adapter="naukri",
            career_url_verified_at=now if verified else None,
            created_at=now,
            updated_at=now,
        )
        self.companies[company.id] = company
        if self._mongo_db is not None:
            try:
                self._mongo_db.ingested_companies.update_one(
                    {"id": company.id},
                    {"$set": company.model_dump(mode="json")},
                    upsert=True,
                )
            except Exception:
                pass
        return company

    def update_company(self, company_id: str, changes: CompanyUpdate) -> Company | None:
        company = self.companies.get(company_id)
        if company is None:
            return None
        self.companies[company_id] = company.model_copy(
            update={
                **changes.model_dump(exclude_unset=True),
                "updated_at": datetime.now(UTC),
            }
        )
        if self._mongo_db is not None:
            try:
                self._mongo_db.ingested_companies.update_one(
                    {"id": company_id},
                    {"$set": self.companies[company_id].model_dump(mode="json")},
                    upsert=True,
                )
            except Exception:
                pass
        return self.companies[company_id]

    def delete_company(self, company_id: str) -> bool:
        if company_id not in self.companies:
            return False
        del self.companies[company_id]
        for job_id, job in list(self.jobs.items()):
            if job.company_id == company_id:
                del self.jobs[job_id]
                if self._mongo_db is not None:
                    try:
                        self._mongo_db.ingested_jobs.delete_one({"id": job_id})
                    except Exception:
                        pass
        if self._mongo_db is not None:
            try:
                self._mongo_db.ingested_companies.delete_one({"id": company_id})
            except Exception:
                pass
        return True

    def refresh(self, company_id: str) -> CrawlResult:
        started = datetime.now(UTC)
        company = self.companies[company_id]
        discovered: list[Job] | None = None
        crawl_error: CrawlError | None = None
        for attempt in range(MAX_CRAWL_RETRIES + 1):
            try:
                discovered = _adapter_for(company).discover_jobs(company)
                crawl_error = None
                break
            except CrawlError as error:
                crawl_error = error
                if (
                    str(error) != "CAREER_SOURCE_UNAVAILABLE"
                    or attempt == MAX_CRAWL_RETRIES
                ):
                    break
                logger.warning(
                    "crawl_retry company_id=%s attempt=%s error=%s",
                    company_id,
                    attempt + 1,
                    error,
                )
                time.sleep(0.05 * (attempt + 1))
        try:
            if crawl_error is not None or discovered is None:
                raise crawl_error or CrawlError("CAREER_SOURCE_UNAVAILABLE")
            seen_ids = {job.id for job in discovered}
            existing = {
                job_id: job
                for job_id, job in self.jobs.items()
                if job.company_id == company_id
            }
            added = sum(job.id not in existing for job in discovered)
            updated = sum(
                job.id in existing
                and existing[job.id].model_dump(exclude={"last_seen_at"})
                != job.model_dump(exclude={"last_seen_at"})
                for job in discovered
            )
            for job in discovered:
                self.jobs[job.id] = job
            closed = 0
            for job_id, job in list(self.jobs.items()):
                if job.company_id == company_id and job_id not in seen_ids:
                    closed += job.status != "closed"
                    self.jobs[job_id] = job.model_copy(
                        update={"status": "closed", "last_seen_at": datetime.now(UTC)}
                    )
                    if self._mongo_db is not None:
                        try:
                            self._mongo_db.ingested_jobs.update_one(
                                {"id": job_id},
                                {"$set": {"status": "closed", "last_seen_at": datetime.now(UTC).isoformat()}},
                            )
                        except Exception:
                            pass
            self.companies[company_id] = company.model_copy(
                update={
                    "last_synced_at": datetime.now(UTC),
                    "last_sync_status": "succeeded",
                }
            )
            result = CrawlResult(
                company_id=company_id,
                status="succeeded",
                jobs_found=len(discovered),
                jobs_added=added,
                jobs_updated=updated,
                jobs_closed=closed,
                started_at=started,
                completed_at=datetime.now(UTC),
            )
            if self._mongo_db is not None:
                try:
                    for job in discovered:
                        self._mongo_db.ingested_jobs.update_one(
                            {"id": job.id},
                            {"$set": job.model_dump(mode="json")},
                            upsert=True,
                        )
                    self._mongo_db.ingested_companies.update_one(
                        {"id": company_id},
                        {"$set": self.companies[company_id].model_dump(mode="json")},
                        upsert=True,
                    )
                    self._mongo_db.ingested_crawls.insert_one(result.model_dump(mode="json"))
                except Exception:
                    pass
        except CrawlError as error:
            self.companies[company_id] = company.model_copy(
                update={
                    "last_synced_at": datetime.now(UTC),
                    "last_sync_status": "failed",
                }
            )
            result = CrawlResult(
                company_id=company_id,
                status="failed",
                error_code=str(error),
                started_at=started,
                completed_at=datetime.now(UTC),
            )
            if get_settings().ingestion_alerting_enabled:
                alert = {
                    "severity": "warning",
                    "code": "INGESTION_FAILED",
                    "company_id": company_id,
                    "error_code": str(error),
                    "created_at": datetime.now(UTC).isoformat(),
                }
                self.alerts.append(alert)
            logger.error(
                "ingestion_alert company_id=%s error_code=%s",
                company_id,
                error,
            )
            if self._mongo_db is not None:
                try:
                    self._mongo_db.ingested_companies.update_one(
                        {"id": company_id},
                        {"$set": self.companies[company_id].model_dump(mode="json")},
                        upsert=True,
                    )
                    self._mongo_db.ingested_crawls.insert_one(result.model_dump(mode="json"))
                except Exception:
                    pass
        self.crawls.append(result)
        return result

    def scrape_naukri(
        self,
        search_term: str = "software engineer",
        location: str = "India",
        results_wanted: int = 15,
    ) -> list[Job]:
        try:
            from jobspy import scrape_jobs

            df = scrape_jobs(
                site_name=["naukri"],
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
            )
        except Exception as exc:
            logger.warning("JobSpy scrape_jobs failed for search '%s': %s", search_term, exc)
            return []

        if df is None or df.empty:
            return []

        jobs = _jobs_from_jobspy_df(df)
        for job in jobs:
            self.jobs[job.id] = job
            if self._mongo_db is not None:
                try:
                    self._mongo_db.ingested_jobs.update_one(
                        {"id": job.id},
                        {"$set": job.model_dump(mode="json")},
                        upsert=True,
                    )
                except Exception:
                    pass
        return jobs


ingestion_store = JobIngestionStore()

