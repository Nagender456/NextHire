from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class ApplicationStatus(StrEnum):
    SAVED = "saved"
    APPLIED = "applied"
    ASSESSMENT = "assessment"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class UserRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


class SkillPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class User(BaseModel):
    id: str
    email: str
    display_name: str
    role: UserRole = UserRole.USER


class CareerProfile(BaseModel):
    user_id: str
    display_name: str = ""
    email: str = ""
    headline: str = ""
    location: str = ""
    skills: list[str] = Field(default_factory=list)
    preferred_roles: list[str] = Field(default_factory=list)
    preferred_skills: dict[str, SkillPriority] = Field(default_factory=dict)
    preferred_locations: list[str] = Field(default_factory=list)
    target_companies: list[str] = Field(default_factory=list)
    dismissed_job_ids: list[str] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    headline: str | None = Field(default=None, max_length=240)
    location: str | None = Field(default=None, max_length=120)
    skills: list[str] | None = None
    preferred_roles: list[str] | None = None
    preferred_skills: dict[str, SkillPriority] | None = None
    preferred_locations: list[str] | None = None
    target_companies: list[str] | None = None
    dismissed_job_ids: list[str] | None = None


class CareerEntity(BaseModel):
    id: str
    user_id: str
    source_type: str = "manual"
    source_id: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    confirmed_by_user: bool = True
    created_at: datetime
    updated_at: datetime


class Skill(CareerEntity):
    name: str = Field(min_length=1, max_length=120)
    priority: SkillPriority = SkillPriority.MEDIUM
    description: str = Field(default="", max_length=500)


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    priority: SkillPriority = SkillPriority.MEDIUM
    description: str = Field(default="", max_length=500)
    source_type: str = Field(default="manual", min_length=1, max_length=40)
    source_id: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    confirmed_by_user: bool = True


class SkillUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    priority: SkillPriority | None = None
    description: str | None = Field(default=None, max_length=500)
    confirmed_by_user: bool | None = None


class Project(CareerEntity):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    technologies: list[str] = Field(default_factory=list)
    url: HttpUrl | None = None


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    technologies: list[str] = Field(default_factory=list)
    url: HttpUrl | None = None
    source_type: str = Field(default="manual", min_length=1, max_length=40)
    source_id: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    confirmed_by_user: bool = True


class Experience(CareerEntity):
    company: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    start_date: str | None = None
    end_date: str | None = None


class ExperienceCreate(BaseModel):
    company: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    start_date: str | None = None
    end_date: str | None = None
    source_type: str = Field(default="manual", min_length=1, max_length=40)
    source_id: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    confirmed_by_user: bool = True


class Education(CareerEntity):
    institution: str = Field(min_length=1, max_length=160)
    degree: str = Field(min_length=1, max_length=160)
    field_of_study: str = Field(default="", max_length=160)
    start_date: str | None = None
    end_date: str | None = None


class EducationCreate(BaseModel):
    institution: str = Field(min_length=1, max_length=160)
    degree: str = Field(min_length=1, max_length=160)
    field_of_study: str = Field(default="", max_length=160)
    start_date: str | None = None
    end_date: str | None = None
    source_type: str = Field(default="manual", min_length=1, max_length=40)
    source_id: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    confirmed_by_user: bool = True


class Certification(CareerEntity):
    name: str = Field(min_length=1, max_length=160)
    issuer: str = Field(default="", max_length=160)
    issued_date: str | None = None
    expires_date: str | None = None


class CertificationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    issuer: str = Field(default="", max_length=160)
    issued_date: str | None = None
    expires_date: str | None = None
    source_type: str = Field(default="manual", min_length=1, max_length=40)
    source_id: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    confirmed_by_user: bool = True


class Achievement(CareerEntity):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    achieved_date: str | None = None


class AchievementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    achieved_date: str | None = None
    source_type: str = Field(default="manual", min_length=1, max_length=40)
    source_id: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    confirmed_by_user: bool = True


class CareerDocument(BaseModel):
    id: str
    user_id: str
    filename: str
    content_type: str
    size: int
    extracted_text: str = ""
    status: str = "processed"
    extraction_engine: str = "Gemini AI"
    created_at: datetime


class ExtractedEntity(BaseModel):
    id: str
    document_id: str
    entity_type: str
    data: dict[str, str | list[str]]
    confidence: float = Field(ge=0, le=1)
    confirmed_by_user: bool = False


class EmbeddingChunk(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    text: str
    embedding_status: str = "pending"


class VectorMetadata(BaseModel):
    user_id: str | None = None
    entity_type: str
    entity_id: str
    company_id: str | None = None
    job_id: str | None = None
    source: str
    updated_at: datetime


class VectorRecord(BaseModel):
    id: str
    text: str
    embedding: list[float]
    metadata: VectorMetadata


class ExternalSourceType(StrEnum):
    GITHUB = "github"
    LINKEDIN = "linkedin"
    PORTFOLIO = "portfolio"


class ExternalCandidateStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ExternalCandidate(BaseModel):
    id: str
    user_id: str
    source_type: ExternalSourceType
    source_id: str
    source_url: HttpUrl | None = None
    entity_type: str
    data: dict[str, str | list[str]]
    status: ExternalCandidateStatus = ExternalCandidateStatus.PENDING
    created_at: datetime


class GitHubSourceRequest(BaseModel):
    username: str = Field(min_length=1, max_length=39, pattern=r"^[A-Za-z0-9-]+$")


class PortfolioSourceRequest(BaseModel):
    url: HttpUrl


class LinkedInSourceRequest(BaseModel):
    profile_text: str = Field(min_length=1, max_length=100_000)


class ExternalCandidateReview(BaseModel):
    status: ExternalCandidateStatus


class Credentials(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)


class SignupRequest(Credentials):
    display_name: str = Field(min_length=1, max_length=120)


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


class Company(BaseModel):
    id: str
    name: str
    website: HttpUrl | str | None = None
    career_page_url: HttpUrl | str | None = None
    active: bool = True
    verification_status: str = "verified"
    source_adapter: str = "naukri"
    requested_by_user_id: str | None = None
    career_url_verified_at: datetime | None = None
    last_synced_at: datetime | None = None
    last_sync_status: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Job(BaseModel):
    id: str
    company_id: str
    title: str
    location: str
    url: HttpUrl | str
    summary: str = ""
    description: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    employment_type: str | None = None
    experience: str | None = None
    source_url: HttpUrl | str | None = None
    external_job_id: str | None = None
    posted_at: datetime | None = None
    last_seen_at: datetime | None = None
    status: str = "open"


class SearchRequest(BaseModel):
    query: str = Field(default="", max_length=500)
    company_id: str | None = None
    location: str | None = Field(default=None, max_length=160)
    limit: int = Field(default=20, ge=1, le=100)


class NaukriScrapeRequest(BaseModel):
    search_term: str = Field(default="software engineer", max_length=120)
    location: str = Field(default="India", max_length=120)
    results_wanted: int = Field(default=15, ge=1, le=50)


class SearchResult(BaseModel):
    job: Job
    score: float = Field(ge=0, le=1)
    matched_terms: list[str] = Field(default_factory=list)
    source: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
    indexed_jobs: int
    indexed_profile_chunks: int
    embedding_model: str
    retrieval_version: str = "hybrid-v1"


class RetrievalEvaluationCase(BaseModel):
    query: str = Field(default="", max_length=500)
    relevant_job_ids: list[str] = Field(default_factory=list)
    company_id: str | None = None
    location: str | None = Field(default=None, max_length=160)
    limit: int = Field(default=10, ge=1, le=100)


class RetrievalEvaluationRequest(BaseModel):
    cases: list[RetrievalEvaluationCase] = Field(min_length=1, max_length=500)


class RetrievalEvaluation(BaseModel):
    cases: int = Field(ge=0)
    precision_at_k: float = Field(ge=0, le=1)
    recall_at_k: float = Field(ge=0, le=1)
    mean_reciprocal_rank: float = Field(ge=0, le=1)
    retrieval_version: str
    embedding_model: str


class LearningOpportunity(BaseModel):
    skill: str
    reason: str
    resources: list[str] = Field(default_factory=list)
    progression: list[str] = Field(default_factory=list)


class JobIntelligence(BaseModel):
    job: Job
    fit_score: int = Field(ge=0, le=100)
    recommendation: str
    recommendation_reason: str
    matched_required_skills: list[str] = Field(default_factory=list)
    matched_preferred_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    relevant_projects: list[Project] = Field(default_factory=list)
    learning_opportunities: list[LearningOpportunity] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    model_version: str = "skills-grounded-v1"


class ResumeItem(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    source_entity_ids: list[str] = Field(default_factory=list)


class ResumeContent(BaseModel):
    summary: str = Field(default="", max_length=1000)
    skills: list[str] = Field(default_factory=list)
    experience: list[ResumeItem] = Field(default_factory=list)
    projects: list[ResumeItem] = Field(default_factory=list)
    education: list[ResumeItem] = Field(default_factory=list)
    certifications: list[ResumeItem] = Field(default_factory=list)
    section_order: list[str] = Field(default_factory=list)


class ResumeVersion(BaseModel):
    id: str
    user_id: str
    job_id: str
    version: int = Field(ge=1)
    status: str = "draft"
    template: str = "default"
    content: ResumeContent
    created_at: datetime
    updated_at: datetime


class ResumeTemplate(BaseModel):
    id: str
    name: str
    description: str = ""


class ResumeExport(BaseModel):
    id: str
    resume_id: str
    format: str
    created_at: datetime


class ResumeUpdate(BaseModel):
    content: ResumeContent
    status: str | None = Field(default=None, pattern="^(draft|approved)$")
    template: str | None = None


class RecommendationFeedback(BaseModel):
    relevant: bool


class RecommendationFeedbackRecord(BaseModel):
    job_id: str
    relevant: bool
    created_at: datetime


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    website: HttpUrl | str | None = None
    career_page_url: HttpUrl | str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    website: HttpUrl | str | None = None
    career_page_url: HttpUrl | str | None = None
    active: bool | None = None
    verification_status: str | None = None


class CrawlResult(BaseModel):
    company_id: str
    status: str
    jobs_found: int = 0
    jobs_added: int = 0
    jobs_updated: int = 0
    jobs_closed: int = 0
    sync_mode: str = "incremental"
    error_code: str | None = None
    started_at: datetime
    completed_at: datetime


class JobRefreshRequest(BaseModel):
    job_links: list[HttpUrl] | None = None


class CareerUrlDiscovery(BaseModel):
    career_page_url: HttpUrl
    verified: bool = True


class Application(BaseModel):
    id: str
    user_id: str
    job_id: str
    status: ApplicationStatus = ApplicationStatus.SAVED
    applied_at: datetime | None = None
    resume_version_id: str | None = None
    company_id: str | None = None
    job_title: str = ""
    application_url: HttpUrl | str | None = None
    notes: str = Field(default="", max_length=5000)
    deadline: datetime | None = None
    next_action: str = Field(default="", max_length=500)
    next_action_at: datetime | None = None
    interview_at: datetime | None = None
    job_snapshot: dict[str, str] = Field(default_factory=dict)
    activity: list["ApplicationActivity"] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApplicationCreate(BaseModel):
    job_id: str | None = None
    job_title: str | None = None
    company_id: str | None = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    resume_version_id: str | None = None
    application_url: HttpUrl | str | None = None
    notes: str = Field(default="", max_length=5000)
    deadline: datetime | None = None
    next_action: str = Field(default="", max_length=500)
    next_action_at: datetime | None = None
    interview_at: datetime | None = None


class ApplicationUpdate(BaseModel):
    job_title: str | None = None
    company_id: str | None = None
    status: ApplicationStatus | None = None
    resume_version_id: str | None = None
    application_url: HttpUrl | str | None = None
    notes: str | None = Field(default=None, max_length=5000)
    deadline: datetime | None = None
    next_action: str | None = Field(default=None, max_length=500)
    next_action_at: datetime | None = None
    interview_at: datetime | None = None


class ApplicationActivity(BaseModel):
    id: str
    application_id: str
    action: str
    details: str = ""
    created_at: datetime


class Notification(BaseModel):
    id: str
    user_id: str
    application_id: str
    kind: str
    title: str
    message: str
    due_at: datetime
    read_at: datetime | None = None
    delivery_status: str = "pending"
    delivered_at: datetime | None = None
    created_at: datetime
    attempts: int = 0


class NotificationUpdate(BaseModel):
    read: bool


class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    in_app_enabled: bool = True


class DashboardSummary(BaseModel):
    profile: CareerProfile
    recommended_jobs: list[Job] = Field(default_factory=list)
    applications: list[Application] = Field(default_factory=list)
    profile_completeness: int = Field(default=0, ge=0, le=100)
    jobs_discovered: int = Field(default=0, ge=0)
    active_applications: int = Field(default=0, ge=0)


class SkillGap(BaseModel):
    skill: str
    jobs: int = Field(ge=0)


class UserAnalytics(BaseModel):
    jobs_discovered: int = Field(default=0, ge=0)
    matching_jobs: int = Field(default=0, ge=0)
    saved_jobs: int = Field(default=0, ge=0)
    applications: int = Field(default=0, ge=0)
    interviews: int = Field(default=0, ge=0)
    offers: int = Field(default=0, ge=0)
    rejected_applications: int = Field(default=0, ge=0)
    skill_gaps: list[SkillGap] = Field(default_factory=list)
    target_companies: list[str] = Field(default_factory=list)


class AdminOverview(BaseModel):
    users: int = Field(ge=0)
    companies: int = Field(ge=0)
    active_companies: int = Field(ge=0)
    pending_companies: int = Field(default=0, ge=0)
    jobs: int = Field(ge=0)
    open_jobs: int = Field(ge=0)
    crawls: int = Field(ge=0)
    successful_crawls: int = Field(ge=0)
    failed_crawls: int = Field(ge=0)
    recent_crawls: list[CrawlResult] = Field(default_factory=list)


class AdminJobSummary(BaseModel):
    job: Job
    company_name: str


class AuditEvent(BaseModel):
    id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime


class ActivitySummary(BaseModel):
    event: str
    count: int = Field(ge=0)
    last_seen_at: datetime | None = None


class PrivacySettings(BaseModel):
    analytics_enabled: bool = True
    retention_days: int = Field(default=365, ge=30, le=3650)


class PrivacySettingsUpdate(BaseModel):
    analytics_enabled: bool | None = None


class RetentionPolicy(BaseModel):
    audit_retention_days: int = Field(default=365, ge=30, le=3650)
    activity_retention_days: int = Field(default=90, ge=30, le=3650)


class RetentionPolicyUpdate(BaseModel):
    audit_retention_days: int | None = Field(default=None, ge=30, le=3650)
    activity_retention_days: int | None = Field(default=None, ge=30, le=3650)


class RetentionPurgeResult(BaseModel):
    audit_events_removed: int = Field(ge=0)
    activity_events_removed: int = Field(ge=0)


class UserDataExport(BaseModel):
    exported_at: datetime
    user: User
    profile: CareerProfile
    career_entities: dict[str, list[dict[str, object]]]
    documents: list[dict[str, object]]
    applications: list[Application]
    resumes: list[ResumeVersion]
    notifications: list[Notification]
    privacy: PrivacySettings
