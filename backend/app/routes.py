import asyncio
from typing import Any
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi import Query
from datetime import UTC, datetime

from app.auth import (
    SESSION_COOKIE,
    google_callback,
    google_login_url,
    github_callback,
    github_login_url,
    login,
    require_user,
    require_admin,
    set_session_cookie,
    signup,
)
from app.auth_store import auth_store
from app.models import (
    Achievement,
    AdminOverview,
    AdminJobSummary,
    ActivitySummary,
    AuditEvent,
    AchievementCreate,
    Application,
    ApplicationCreate,
    Certification,
    CertificationCreate,
    ApplicationUpdate,
    CareerProfile,
    Company,
    CompanyCreate,
    CompanyUpdate,
    CareerUrlDiscovery,
    CrawlResult,
    CareerDocument,
    EmbeddingChunk,
    ExtractedEntity,
    Credentials,
    DashboardSummary,
    Education,
    EducationCreate,
    ExternalCandidate,
    ExternalCandidateReview,
    ExternalCandidateStatus,
    Experience,
    ExperienceCreate,
    GitHubSourceRequest,
    Job,
    JobRefreshRequest,
    NaukriScrapeRequest,
    SearchRequest,
    SearchResponse,
    JobIntelligence,
    RecommendationFeedback,
    RecommendationFeedbackRecord,
    Notification,
    NotificationUpdate,
    NotificationPreferences,
    ResumeUpdate,
    ResumeVersion,
    LinkedInSourceRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PortfolioSourceRequest,
    ProfileUpdate,
    Project,
    ProjectCreate,
    Skill,
    SkillCreate,
    SkillUpdate,
    SignupRequest,
    User,
    UserAnalytics,
    PrivacySettings,
    PrivacySettingsUpdate,
    RetentionPolicy,
    RetentionPolicyUpdate,
    RetentionPurgeResult,
    UserDataExport,
    ApplicationActivity,
    ResumeTemplate,
    ResumeExport,
    RetrievalEvaluation,
    RetrievalEvaluationRequest,
)
from app.security import generate_token, hash_password
from app.services import service
from app.documents import (
    ALLOWED_DOCUMENTS,
    detect_entities,
    detect_entities_with_engine,
    extract_text,
    read_upload,
)
from app.external_sources import (
    SourceFetchError,
    fetch_github,
    fetch_portfolio,
    parse_linkedin,
)
from app.job_ingestion import CrawlError, discover_career_url, ingestion_store
from app.config import get_settings
from app.job_queue import JobQueue
from app.vector_search import vector_search
from app.intelligence import analyze_job
from app.resumes import (
    TEMPLATES,
    create_version,
    render_latex,
    render_pdf,
    validate_content,
    validate_format,
    validate_template,
)
from app.notifications import (
    create_application_reminders,
    deliver_due_notifications,
    mark_notification,
)
from app.analytics import get_admin_overview, get_user_analytics
from app.admin_store import admin_store

vector_search.jobs_provider = service.list_jobs

router = APIRouter(prefix="/api/v1", tags=["application"])
auth_router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@auth_router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup_route(payload: SignupRequest, response: Response) -> User:
    user = signup(payload)
    _, token = login(Credentials(email=payload.email, password=payload.password))
    _, token = login(Credentials(email=payload.email, password=payload.password))
    set_session_cookie(response, token)
    return user


@auth_router.post("/login", response_model=User)
async def login_route(payload: Credentials, response: Response) -> User:
    user, token = login(payload)
    set_session_cookie(response, token)
    return user


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_route(response: Response, user: User = Depends(require_user)) -> None:
    # The dependency has validated the cookie; revoke every session for a
    # predictable "log out everywhere" security boundary.
    auth_store.revoke_user_sessions(user.id)
    response.delete_cookie(SESSION_COOKIE, path="/")


@auth_router.get("/me", response_model=User)
async def me_route(user: User = Depends(require_user)) -> User:
    return user


@auth_router.post("/password-reset/request")
async def request_password_reset(payload: PasswordResetRequest) -> dict[str, str]:
    user = auth_store.find_by_email(payload.email.strip().lower())
    if user:
        auth_store.reset_tokens[generate_token()] = user.id
    return {"message": "If the account exists, reset instructions have been sent."}


@auth_router.post("/password-reset/confirm")
async def confirm_password_reset(payload: PasswordResetConfirm) -> dict[str, str]:
    user_id = auth_store.reset_tokens.pop(payload.token, None)
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_RESET_TOKEN",
                "message": "Reset token is invalid.",
            },
        )
    auth_store.set_password(user_id, hash_password(payload.password))
    return {"message": "Password updated successfully."}


@auth_router.get("/google/login")
async def google_login_route() -> RedirectResponse:
    return RedirectResponse(google_login_url(), status_code=307)


@auth_router.get("/google/callback")
async def google_callback_route(code: str) -> RedirectResponse:
    _, token = await google_callback(code)
    response = RedirectResponse("/dashboard", status_code=303)
    set_session_cookie(response, token)
    return response


@auth_router.get("/github/login")
async def github_login_route() -> RedirectResponse:
    return RedirectResponse(github_login_url(), status_code=307)


@auth_router.get("/github/callback")
async def github_callback_route(code: str, state: str) -> RedirectResponse:
    _, token = await github_callback(code, state)
    response = RedirectResponse("/dashboard", status_code=303)
    set_session_cookie(response, token)
    return response


@auth_router.delete("/github/token", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_github_token(user: User = Depends(require_user)) -> None:
    token = auth_store.github_tokens.pop(user.id, None)
    settings = get_settings()
    if token and settings.github_client_id and settings.github_client_secret:
        import base64

        credentials = base64.b64encode(
            f"{settings.github_client_id}:{settings.github_client_secret}".encode()
        ).decode()
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            await client.delete(
                f"https://api.github.com/applications/{settings.github_client_id}/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Accept": "application/vnd.github+json",
                },
                json={"access_token": token},
            )


@router.get("/profile", response_model=CareerProfile)
async def get_profile(user: User = Depends(require_user)) -> CareerProfile:
    return auth_store.get_profile(user.id)


@router.patch("/profile", response_model=CareerProfile)
async def update_profile(
    changes: ProfileUpdate, user: User = Depends(require_user)
) -> CareerProfile:
    updated = auth_store.update_profile(user.id, changes)
    if changes.target_companies:
        for comp_name in changes.target_companies:
            name_clean = comp_name.strip()
            if not name_clean:
                continue
            exists = any(
                c.name.lower() == name_clean.lower()
                for c in ingestion_store.companies.values()
            )
            if not exists:
                ingestion_store.add_company(
                    CompanyCreate(name=name_clean),
                    verified=False,
                    requested_by=user.id,
                )
                admin_store.activity("company_whitelist_requested")
                admin_store.audit(
                    user.id,
                    "company_whitelist_requested",
                    "company",
                    name_clean,
                )
    return updated


@router.get("/career/skills", response_model=list[Skill])
async def list_skills(user: User = Depends(require_user)) -> list[Skill]:
    return auth_store.list_entities(user.id, "skills")


@router.post(
    "/career/skills", response_model=Skill, status_code=status.HTTP_201_CREATED
)
async def create_skill(
    payload: SkillCreate, user: User = Depends(require_user)
) -> Skill:
    return auth_store.create_entity(user.id, "skills", payload.model_dump())


def _update_entity(entity_type: str, entity_id: str, payload, user: User):
    entity = auth_store.update_entity(
        user.id, entity_type, entity_id, payload.model_dump(exclude_unset=True)
    )
    if entity is None:
        raise HTTPException(
            status_code=404, detail={"code": f"{entity_type.upper()}_NOT_FOUND"}
        )
    return entity


def _delete_entity(entity_type: str, entity_id: str, user: User) -> None:
    if not auth_store.delete_entity(user.id, entity_type, entity_id):
        raise HTTPException(
            status_code=404, detail={"code": f"{entity_type.upper()}_NOT_FOUND"}
        )


@router.patch("/career/skills/{entity_id}", response_model=Skill)
async def update_skill(
    entity_id: str, payload: SkillUpdate, user: User = Depends(require_user)
) -> Skill:
    entity = auth_store.update_entity(
        user.id, "skills", entity_id, payload.model_dump(exclude_unset=True)
    )
    if entity is None:
        raise HTTPException(status_code=404, detail={"code": "SKILL_NOT_FOUND"})
    return entity


@router.delete("/career/skills/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(entity_id: str, user: User = Depends(require_user)) -> None:
    entity = auth_store.career_entities.get(user.id, {}).get("skills", {}).get(entity_id)
    skill_name = entity.get("name") if entity else None
    _delete_entity("skills", entity_id, user)
    vector_search.index.delete_entity(user.id, "career", entity_id)
    if skill_name:
        prof = auth_store.get_profile(user.id)
        if skill_name in prof.skills:
            new_skills = [s for s in prof.skills if s != skill_name]
            auth_store.profiles[user.id] = prof.model_copy(update={"skills": new_skills})


@router.get("/career/projects", response_model=list[Project])
async def list_projects(user: User = Depends(require_user)) -> list[Project]:
    return auth_store.list_entities(user.id, "projects")


@router.post(
    "/career/projects", response_model=Project, status_code=status.HTTP_201_CREATED
)
async def create_project(
    payload: ProjectCreate, user: User = Depends(require_user)
) -> Project:
    return auth_store.create_entity(user.id, "projects", payload.model_dump())


@router.patch("/career/projects/{entity_id}", response_model=Project)
async def update_project(
    entity_id: str, payload: ProjectCreate, user: User = Depends(require_user)
):
    return _update_entity("projects", entity_id, payload, user)


@router.delete("/career/projects/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(entity_id: str, user: User = Depends(require_user)) -> None:
    _delete_entity("projects", entity_id, user)
    vector_search.index.delete_entity(user.id, "career", entity_id)


@router.get("/career/experience", response_model=list[Experience])
async def list_experience(user: User = Depends(require_user)) -> list[Experience]:
    return auth_store.list_entities(user.id, "experience")


@router.post(
    "/career/experience",
    response_model=Experience,
    status_code=status.HTTP_201_CREATED,
)
async def create_experience(
    payload: ExperienceCreate, user: User = Depends(require_user)
) -> Experience:
    return auth_store.create_entity(user.id, "experience", payload.model_dump())


@router.patch("/career/experience/{entity_id}", response_model=Experience)
async def update_experience(
    entity_id: str, payload: ExperienceCreate, user: User = Depends(require_user)
):
    return _update_entity("experience", entity_id, payload, user)


@router.delete("/career/experience/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(entity_id: str, user: User = Depends(require_user)) -> None:
    _delete_entity("experience", entity_id, user)
    vector_search.index.delete_entity(user.id, "career", entity_id)


@router.get("/career/education", response_model=list[Education])
async def list_education(user: User = Depends(require_user)) -> list[Education]:
    return auth_store.list_entities(user.id, "education")


@router.post(
    "/career/education", response_model=Education, status_code=status.HTTP_201_CREATED
)
async def create_education(
    payload: EducationCreate, user: User = Depends(require_user)
) -> Education:
    return auth_store.create_entity(user.id, "education", payload.model_dump())


@router.patch("/career/education/{entity_id}", response_model=Education)
async def update_education(
    entity_id: str, payload: EducationCreate, user: User = Depends(require_user)
):
    return _update_entity("education", entity_id, payload, user)


@router.delete("/career/education/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(entity_id: str, user: User = Depends(require_user)) -> None:
    _delete_entity("education", entity_id, user)
    vector_search.index.delete_entity(user.id, "career", entity_id)


@router.get("/career/certifications", response_model=list[Certification])
async def list_certifications(
    user: User = Depends(require_user),
) -> list[Certification]:
    return auth_store.list_entities(user.id, "certifications")


@router.post(
    "/career/certifications",
    response_model=Certification,
    status_code=status.HTTP_201_CREATED,
)
async def create_certification(
    payload: CertificationCreate, user: User = Depends(require_user)
) -> Certification:
    return auth_store.create_entity(user.id, "certifications", payload.model_dump())


@router.patch("/career/certifications/{entity_id}", response_model=Certification)
async def update_certification(
    entity_id: str, payload: CertificationCreate, user: User = Depends(require_user)
):
    return _update_entity("certifications", entity_id, payload, user)


@router.delete(
    "/career/certifications/{entity_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_certification(
    entity_id: str, user: User = Depends(require_user)
) -> None:
    _delete_entity("certifications", entity_id, user)
    vector_search.index.delete_entity(user.id, "career", entity_id)


@router.get("/career/achievements", response_model=list[Achievement])
async def list_achievements(user: User = Depends(require_user)) -> list[Achievement]:
    return auth_store.list_entities(user.id, "achievements")


@router.post(
    "/career/achievements",
    response_model=Achievement,
    status_code=status.HTTP_201_CREATED,
)
async def create_achievement(
    payload: AchievementCreate, user: User = Depends(require_user)
) -> Achievement:
    return auth_store.create_entity(user.id, "achievements", payload.model_dump())


@router.patch("/career/achievements/{entity_id}", response_model=Achievement)
async def update_achievement(
    entity_id: str, payload: AchievementCreate, user: User = Depends(require_user)
):
    return _update_entity("achievements", entity_id, payload, user)


@router.delete(
    "/career/achievements/{entity_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_achievement(
    entity_id: str, user: User = Depends(require_user)
) -> None:
    _delete_entity("achievements", entity_id, user)
    vector_search.index.delete_entity(user.id, "career", entity_id)


def _ingest_external_candidates(
    user_id: str, candidates: list[dict], source_type: str
) -> list[dict]:
    created = []
    existing = auth_store.list_external_candidates(user_id)
    existing_ids = {
        (item["source_type"], item["source_id"])
        for item in existing
        if item["status"] != ExternalCandidateStatus.REJECTED
    }
    for candidate in candidates:
        identity = (source_type, candidate["source_id"])
        if identity in existing_ids:
            continue
        created.append(
            auth_store.add_external_candidate(
                user_id, {"source_type": source_type, **candidate}
            )
        )
        existing_ids.add(identity)
    return created


@router.get("/career/sources", response_model=list[ExternalCandidate])
async def list_external_candidates(
    user: User = Depends(require_user),
) -> list[ExternalCandidate]:
    return auth_store.list_external_candidates(user.id)


@router.post("/career/sources/github", response_model=list[ExternalCandidate])
async def ingest_github(
    payload: GitHubSourceRequest, user: User = Depends(require_user)
) -> list[ExternalCandidate]:
    try:
        candidates = fetch_github(payload)
    except SourceFetchError as error:
        raise HTTPException(status_code=422, detail={"code": str(error)}) from error
    return _ingest_external_candidates(user.id, candidates, "github")


@router.post("/career/sources/portfolio", response_model=list[ExternalCandidate])
async def ingest_portfolio(
    payload: PortfolioSourceRequest, user: User = Depends(require_user)
) -> list[ExternalCandidate]:
    try:
        candidates = fetch_portfolio(payload)
    except SourceFetchError as error:
        raise HTTPException(status_code=422, detail={"code": str(error)}) from error
    return _ingest_external_candidates(user.id, candidates, "portfolio")


@router.post("/career/sources/linkedin", response_model=list[ExternalCandidate])
async def ingest_linkedin(
    payload: LinkedInSourceRequest, user: User = Depends(require_user)
) -> list[ExternalCandidate]:
    return _ingest_external_candidates(user.id, parse_linkedin(payload), "linkedin")


@router.post(
    "/career/sources/linkedin/document", response_model=list[ExternalCandidate]
)
async def ingest_linkedin_document(
    file: UploadFile = File(...), user: User = Depends(require_user)
) -> list[ExternalCandidate]:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_DOCUMENTS:
        raise HTTPException(status_code=415, detail={"code": "UNSUPPORTED_DOCUMENT"})
    try:
        content = await read_upload(file)
        text = extract_text(file.filename or "", content_type, content)
    except ValueError as error:
        code = str(error)
        raise HTTPException(
            status_code=413 if code == "DOCUMENT_TOO_LARGE" else 422,
            detail={"code": code},
        ) from error
    candidates = parse_linkedin(LinkedInSourceRequest(profile_text=text))
    candidates[0]["source_id"] = f"document:{file.filename or 'linkedin-profile'}"
    return _ingest_external_candidates(user.id, candidates, "linkedin")


@router.patch("/career/sources/{candidate_id}", response_model=ExternalCandidate)
async def review_external_candidate(
    candidate_id: str,
    payload: ExternalCandidateReview,
    user: User = Depends(require_user),
) -> ExternalCandidate:
    candidate = auth_store.external_candidates[user.id].get(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail={"code": "CANDIDATE_NOT_FOUND"})
    if candidate["status"] == ExternalCandidateStatus.PENDING:
        if payload.status == ExternalCandidateStatus.ACCEPTED:
            values = {
                **candidate["data"],
                "source_type": candidate["source_type"],
                "source_id": candidate["source_id"],
                "confirmed_by_user": True,
                "confidence": 0.8,
            }
            auth_store.create_entity(user.id, candidate["entity_type"], values)
        candidate = auth_store.update_external_candidate(
            user.id, candidate_id, payload.status
        )
    return candidate


def sync_extracted_entity_to_career_knowledge(
    user_id: str, document_id: str, entity: dict[str, Any]
) -> None:
    etype = entity.get("entity_type")
    data = entity.get("data", {})
    raw_text = str(data.get("text", "")).strip()

    if etype == "skills":
        skill_name = data.get("name") or raw_text
        skill_names = (
            [s.strip() for s in skill_name.split(",") if s.strip()]
            if "," in skill_name
            else [skill_name]
        )
        current_profile = auth_store.get_profile(user_id)
        combined_skills = list(current_profile.skills)
        for s in skill_names:
            s_clean = s.strip("•-* \t")[:60]
            if not s_clean:
                continue
            auth_store.create_entity(
                user_id,
                "skills",
                {
                    "name": s_clean,
                    "priority": "HIGH",
                    "source_type": "resume",
                    "source_id": document_id,
                    "confirmed_by_user": True,
                },
            )
            if not any(cs.lower().strip() == s_clean.lower().strip() for cs in combined_skills):
                combined_skills.append(s_clean)
        auth_store.profiles[user_id] = current_profile.model_copy(
            update={"skills": combined_skills}
        )

    elif etype == "experience":
        company = data.get("company") or "Tech Company"
        title = data.get("title") or (
            raw_text.splitlines()[0][:60] if raw_text else "Software Engineer"
        )
        if company == "Experience" and "|" in title:
            parts = [p.strip() for p in title.split("|")]
            company, title = parts[0], parts[1]
        desc = data.get("description") or raw_text[:500]
        dates = data.get("dates") or "Recent"
        auth_store.create_entity(
            user_id,
            "experience",
            {
                "company": company,
                "title": title,
                "dates": dates,
                "description": desc,
                "source_type": "resume",
                "source_id": document_id,
                "confirmed_by_user": True,
            },
        )

    elif etype == "education":
        inst = data.get("institution") or (
            raw_text.splitlines()[0][:80] if raw_text else "University"
        )
        deg = data.get("degree") or (
            raw_text.splitlines()[1][:80]
            if len(raw_text.splitlines()) > 1
            else "Degree"
        )
        auth_store.create_entity(
            user_id,
            "education",
            {
                "institution": inst,
                "degree": deg,
                "year": data.get("year", ""),
                "description": data.get("description") or raw_text[:500],
                "source_type": "resume",
                "source_id": document_id,
                "confirmed_by_user": True,
            },
        )

    elif etype == "projects":
        tech_list = data.get("technologies") or []
        if isinstance(tech_list, str):
            tech_list = [t.strip() for t in tech_list.split(",") if t.strip()]
        auth_store.create_entity(
            user_id,
            "projects",
            {
                "name": data.get("name")
                or (raw_text.splitlines()[0][:60] if raw_text else "Project"),
                "description": data.get("description") or raw_text[:500],
                "technologies": tech_list,
                "url": (data.get("url") or None) if str(data.get("url", "")).strip() else None,
                "source_type": "resume",
                "source_id": document_id,
                "confirmed_by_user": True,
            },
        )

    elif etype == "certifications":
        auth_store.create_entity(
            user_id,
            "certifications",
            {
                "name": data.get("name")
                or (raw_text.splitlines()[0][:80] if raw_text else "Certification"),
                "issuer": data.get("issuer") or "Verified Authority",
                "issued_date": data.get("issued_date") or data.get("year") or "",
                "source_type": "resume",
                "source_id": document_id,
                "confirmed_by_user": True,
            },
        )

    elif etype == "achievements":
        auth_store.create_entity(
            user_id,
            "achievements",
            {
                "title": data.get("title")
                or (raw_text.splitlines()[0][:80] if raw_text else "Achievement"),
                "description": data.get("description") or raw_text[:500],
                "source_type": "resume",
                "source_id": document_id,
                "confirmed_by_user": True,
            },
        )

    elif etype == "headline":
        hl = data.get("name") or data.get("text") or ""
        if hl:
            current_profile = auth_store.get_profile(user_id)
            if not current_profile.headline:
                auth_store.profiles[user_id] = current_profile.model_copy(
                    update={"headline": hl[:80]}
                )


@router.post(
    "/career/documents",
    response_model=CareerDocument,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...), user: User = Depends(require_user)
) -> CareerDocument:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_DOCUMENTS:
        raise HTTPException(status_code=415, detail={"code": "UNSUPPORTED_DOCUMENT"})
    try:
        content = await read_upload(file)
        text = extract_text(file.filename or "", content_type, content)
    except ValueError as error:
        code = str(error)
        raise HTTPException(
            status_code=413 if code == "DOCUMENT_TOO_LARGE" else 422,
            detail={"code": code},
        ) from error

    entities, engine_name = detect_entities_with_engine(text)

    document = auth_store.create_document(
        user.id,
        {
            "filename": file.filename or "resume",
            "content_type": content_type,
            "size": len(content),
            "extracted_text": text,
            "status": "processed",
            "extraction_engine": engine_name,
            "content": content,
        },
    )

    for extracted in entities:
        auth_store.add_extracted_entity(user.id, document["id"], extracted)
        # Automatically populate Career Knowledge Base with extracted findings
        sync_extracted_entity_to_career_knowledge(user.id, document["id"], extracted)

    # Auto-enrich profile skills and headline with extracted findings
    current_profile = auth_store.get_profile(user.id)
    extracted_skills = [
        e["data"]["name"]
        for e in entities
        if e.get("entity_type") == "skills" and "name" in e.get("data", {})
    ]
    extracted_headline = next(
        (e["data"]["text"] for e in entities if e.get("entity_type") == "headline"), ""
    )
    if not extracted_headline:
        first_exp = next(
            (e["data"] for e in entities if e.get("entity_type") == "experience"), None
        )
        if first_exp:
            comp = first_exp.get("company", "")
            titl = first_exp.get("title", "")
            if comp and comp != "Experience" and titl:
                extracted_headline = f"{titl} | {comp}"
            elif titl:
                extracted_headline = titl

    current_skills = list(current_profile.skills or [])
    for s in extracted_skills:
        s_clean = s.strip()
        if s_clean and not any(cs.lower().strip() == s_clean.lower().strip() for cs in current_skills):
            current_skills.append(s_clean)

    profile_updates = {}
    if current_skills != current_profile.skills:
        profile_updates["skills"] = current_skills[:40]
    if (not current_profile.headline) and extracted_headline:
        profile_updates["headline"] = extracted_headline[:80]

    if profile_updates:
        auth_store.update_profile(user.id, ProfileUpdate(**profile_updates))

    return document


@router.get("/career/documents", response_model=list[CareerDocument])
async def list_documents(user: User = Depends(require_user)) -> list[CareerDocument]:
    return list(auth_store.documents[user.id].values())


@router.get(
    "/career/documents/{document_id}/extracted", response_model=list[ExtractedEntity]
)
async def list_extracted(
    document_id: str, user: User = Depends(require_user)
) -> list[ExtractedEntity]:
    if document_id not in auth_store.documents[user.id]:
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND"})
    return auth_store.list_extracted_entities(user.id, document_id)


@router.patch(
    "/career/documents/{document_id}/extracted/{entity_id}",
    response_model=ExtractedEntity,
)
async def review_extracted_entity(
    document_id: str,
    entity_id: str,
    confirmed_by_user: bool,
    user: User = Depends(require_user),
) -> ExtractedEntity:
    if document_id not in auth_store.documents[user.id]:
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND"})
    entity = auth_store.extracted_entities[user.id].get(entity_id)
    if entity is None or entity["document_id"] != document_id:
        raise HTTPException(
            status_code=404, detail={"code": "EXTRACTED_ENTITY_NOT_FOUND"}
        )
    entity["confirmed_by_user"] = confirmed_by_user
    if confirmed_by_user:
        sync_extracted_entity_to_career_knowledge(user.id, document_id, entity)
    return entity


@router.post(
    "/career/documents/{document_id}/accept-all",
    response_model=list[ExtractedEntity],
)
async def accept_all_extracted_entities(
    document_id: str, user: User = Depends(require_user)
) -> list[ExtractedEntity]:
    if document_id not in auth_store.documents[user.id]:
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND"})
    entities = auth_store.list_extracted_entities(user.id, document_id)
    for entity in entities:
        entity["confirmed_by_user"] = True
        sync_extracted_entity_to_career_knowledge(user.id, document_id, entity)
    return entities


@router.delete(
    "/career/documents/{document_id}/extracted/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_extracted_entity(
    document_id: str, entity_id: str, user: User = Depends(require_user)
) -> None:
    if document_id not in auth_store.documents[user.id]:
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND"})
    entity = auth_store.extracted_entities[user.id].get(entity_id)
    if entity is None or entity["document_id"] != document_id:
        raise HTTPException(
            status_code=404, detail={"code": "EXTRACTED_ENTITY_NOT_FOUND"}
        )
    del auth_store.extracted_entities[user.id][entity_id]


@router.post(
    "/career/documents/{document_id}/chunks", response_model=list[EmbeddingChunk]
)
async def prepare_embedding_chunks(
    document_id: str, user: User = Depends(require_user)
) -> list[EmbeddingChunk]:
    if document_id not in auth_store.documents[user.id]:
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND"})
    entities = auth_store.list_extracted_entities(user.id, document_id)
    chunks = [
        EmbeddingChunk(
            id=f"chunk-{entity['id']}",
            entity_type=entity["entity_type"],
            entity_id=entity["id"],
            text=str(entity["data"].get("text", "")),
        )
        for entity in entities
        if entity["confirmed_by_user"]
    ]
    # Sync confirmed extracted entities to career_entities & profile
    for entity in entities:
        if entity.get("confirmed_by_user"):
            sync_extracted_entity_to_career_knowledge(user.id, document_id, entity)
    return chunks


@router.post("/jobs/seed", response_model=list[Job])
async def seed_sample_jobs(_user: User = Depends(require_user)) -> list[Job]:
    now = datetime.now(UTC)
    sample_companies = [
        Company(
            id="company-google",
            name="Google",
            website="https://careers.google.com",
            career_page_url="https://careers.google.com/jobs",
            verification_status="verified",
            created_at=now,
            updated_at=now,
        ),
        Company(
            id="company-stripe",
            name="Stripe",
            website="https://stripe.com",
            career_page_url="https://stripe.com/jobs",
            verification_status="verified",
            created_at=now,
            updated_at=now,
        ),
        Company(
            id="company-meta",
            name="Meta",
            website="https://metacareers.com",
            career_page_url="https://metacareers.com/jobs",
            verification_status="verified",
            created_at=now,
            updated_at=now,
        ),
        Company(
            id="company-nexthire",
            name="NextHire",
            website="https://nexthire.dev",
            career_page_url="https://nexthire.dev/careers",
            verification_status="verified",
            created_at=now,
            updated_at=now,
        ),
    ]
    for company in sample_companies:
        ingestion_store.companies[company.id] = company

    sample_jobs = [
        Job(
            id="job-algo-engineer",
            company_id="company-google",
            title="Algorithms & Competitive Systems Engineer",
            location="Bengaluru / Remote",
            url="https://careers.google.com/jobs/results/101",
            summary="Design, test, and optimize algorithmic core pipelines. High-impact role for competitive programmers, LeetCode problem solvers, and discrete math enthusiasts.",
            description="You will work with high-throughput search and distributed caching infrastructure. Expertise in data structures, algorithmic complexity, graph theory, and dynamic programming required.",
            required_skills=["Algorithms", "Data Structures", "C++", "Python"],
            preferred_skills=["Competitive Programming", "System Design", "Problem Solving"],
            status="open",
            last_seen_at=now,
        ),
        Job(
            id="job-backend-platform",
            company_id="company-stripe",
            title="Senior Backend Platform Engineer",
            location="Remote",
            url="https://stripe.com/jobs/results/202",
            summary="Scale financial ledger microservices and developer APIs handling millions of transactional events per day.",
            description="Work closely with product and infrastructure teams to design resilient Python and Go services with tight latency SLAs and automated rollback safety.",
            required_skills=["Python", "FastAPI", "API Design", "PostgreSQL"],
            preferred_skills=["Docker", "Kubernetes", "Redis", "Cloud"],
            status="open",
            last_seen_at=now,
        ),
        Job(
            id="job-fullstack-dev",
            company_id="company-nexthire",
            title="Full Stack Software Engineer",
            location="Remote / Hybrid",
            url="https://nexthire.dev/careers/results/303",
            summary="Build next-generation intelligent career acceleration tools using React, Vite, and Python backend microservices.",
            description="Collaborate directly with design and AI research teams to deliver fluid, intuitive career management experiences and real-time job matching.",
            required_skills=["Python", "React", "JavaScript", "REST APIs"],
            preferred_skills=["TypeScript", "MongoDB", "Tailwind CSS"],
            status="open",
            last_seen_at=now,
        ),
        Job(
            id="job-systems-core",
            company_id="company-meta",
            title="Core Systems & Distributed Storage Engineer",
            location="Remote",
            url="https://metacareers.com/jobs/results/404",
            summary="Develop low-latency, resilient storage primitives for global-scale social infrastructure and real-time AI workloads.",
            description="Build core platform primitives in C++ and Python with an emphasis on lock-free algorithms, distributed consensus, and Linux kernel tuning.",
            required_skills=["C++", "Algorithms", "Linux", "Concurrency"],
            preferred_skills=["Python", "Networking", "Distributed Systems"],
            status="open",
            last_seen_at=now,
        ),
    ]
    for job in sample_jobs:
        ingestion_store.jobs[job.id] = job

    return sample_jobs


@router.post("/jobs/scrape-naukri", response_model=list[Job])
async def scrape_naukri_jobs_endpoint(
    payload: NaukriScrapeRequest | None = None,
    _user: User = Depends(require_user),
) -> list[Job]:
    req = payload or NaukriScrapeRequest()
    jobs = await asyncio.to_thread(
        ingestion_store.scrape_naukri,
        req.search_term,
        req.location,
        req.results_wanted,
    )
    admin_store.activity("job_ingestion")
    return jobs


@router.get("/jobs", response_model=list[Job])
async def list_jobs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_user),
) -> list[Job]:
    profile = auth_store.get_profile(user.id)
    dismissed = set(getattr(profile, "dismissed_job_ids", []))
    jobs = [job for job in service.list_jobs() if job.status == "open" and job.id not in dismissed]
    return jobs[offset : offset + limit]


@router.post("/jobs/{job_id}/dismiss")
async def dismiss_job(job_id: str, user: User = Depends(require_user)) -> dict[str, Any]:
    profile = auth_store.get_profile(user.id)
    dismissed = list(getattr(profile, "dismissed_job_ids", []))
    if job_id not in dismissed:
        dismissed.append(job_id)
        auth_store.update_profile(user.id, ProfileUpdate(dismissed_job_ids=dismissed))
    return {"status": "dismissed", "job_id": job_id, "dismissed_count": len(dismissed)}


@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str, _user: User = Depends(require_user)) -> Job:
    job = service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    return job


@router.get("/jobs/{job_id}/intelligence", response_model=JobIntelligence)
async def get_job_intelligence(
    job_id: str, user: User = Depends(require_user)
) -> JobIntelligence:
    job = service.get_job(job_id)
    if job is None or job.status != "open":
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    admin_store.activity("job_intelligence")
    return analyze_job(user.id, job)


@router.post(
    "/jobs/{job_id}/resumes",
    response_model=ResumeVersion,
    status_code=status.HTTP_201_CREATED,
)
async def generate_resume_for_job(
    job_id: str, user: User = Depends(require_user)
) -> ResumeVersion:
    job = service.get_job(job_id)
    if job is None or job.status != "open":
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    admin_store.activity("resume_generation")
    return create_version(user.id, job)


@router.get("/resumes", response_model=list[ResumeVersion])
async def list_resumes(user: User = Depends(require_user)) -> list[ResumeVersion]:
    return list(auth_store.resume_versions[user.id].values())


@router.get("/resumes/{resume_id}/exports", response_model=list[ResumeExport])
async def list_resume_exports(
    resume_id: str, user: User = Depends(require_user)
) -> list[ResumeExport]:
    if resume_id not in auth_store.resume_versions[user.id]:
        raise HTTPException(status_code=404, detail={"code": "RESUME_NOT_FOUND"})
    return [
        ResumeExport.model_validate(item)
        for item in auth_store.resume_exports[user.id].values()
        if item["resume_id"] == resume_id
    ]


@router.get("/resumes/{resume_id}", response_model=ResumeVersion)
async def get_resume(
    resume_id: str, user: User = Depends(require_user)
) -> ResumeVersion:
    resume = auth_store.resume_versions[user.id].get(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail={"code": "RESUME_NOT_FOUND"})
    return resume


@router.patch("/resumes/{resume_id}", response_model=ResumeVersion)
async def update_resume(
    resume_id: str, payload: ResumeUpdate, user: User = Depends(require_user)
) -> ResumeVersion:
    resume = auth_store.resume_versions[user.id].get(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail={"code": "RESUME_NOT_FOUND"})
    try:
        validate_content(user.id, payload.content)
        validate_format(payload.content)
    except ValueError as error:
        raise HTTPException(status_code=422, detail={"code": str(error)}) from error
    resume["content"] = payload.content
    if payload.status is not None:
        resume["status"] = payload.status
    if payload.template is not None:
        validate_template(payload.template)
        resume["template"] = payload.template
    resume["updated_at"] = datetime.now(UTC)
    return resume


@router.get("/resume-templates", response_model=list[ResumeTemplate])
async def list_resume_templates(
    _user: User = Depends(require_user),
) -> list[ResumeTemplate]:
    return [
        ResumeTemplate(
            id=template_id, name=template_id.title(), description=description
        )
        for template_id, description in TEMPLATES.items()
    ]


@router.get("/resumes/{resume_id}/latex", response_class=Response)
async def export_resume_latex(
    resume_id: str, user: User = Depends(require_user)
) -> Response:
    resume = auth_store.resume_versions[user.id].get(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail={"code": "RESUME_NOT_FOUND"})
    auth_store.save_resume_export(user.id, resume_id, "latex")
    profile = auth_store.get_profile(user.id)
    return Response(
        content=render_latex(
            resume["content"],
            profile=profile,
            template=resume.get("template", "jack"),
        ),
        media_type="application/x-latex",
        headers={"Content-Disposition": f'attachment; filename="{resume_id}.tex"'},
    )


@router.get("/resumes/{resume_id}/pdf", response_class=Response)
async def export_resume_pdf(
    resume_id: str, user: User = Depends(require_user)
) -> Response:
    resume = auth_store.resume_versions[user.id].get(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail={"code": "RESUME_NOT_FOUND"})
    auth_store.save_resume_export(user.id, resume_id, "pdf")
    profile = auth_store.get_profile(user.id)
    pdf_bytes = render_pdf(
        resume["content"],
        profile=profile,
        template=resume.get("template", "jack"),
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{resume_id}.pdf"'},
    )


@router.post(
    "/jobs/{job_id}/feedback",
    response_model=RecommendationFeedbackRecord,
)
async def save_job_feedback(
    job_id: str,
    payload: RecommendationFeedback,
    user: User = Depends(require_user),
) -> RecommendationFeedbackRecord:
    if service.get_job(job_id) is None:
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    return auth_store.save_recommendation_feedback(user.id, job_id, payload.relevant)


@router.post("/search/reindex", response_model=SearchResponse)
async def reindex_search(
    payload: SearchRequest | None = None, user: User = Depends(require_user)
) -> SearchResponse:
    return vector_search.search(user.id, payload or SearchRequest())


@router.post("/search/jobs", response_model=SearchResponse)
@router.post("/recommendations", response_model=SearchResponse)
async def search_jobs(
    payload: SearchRequest, user: User = Depends(require_user)
) -> SearchResponse:
    admin_store.activity("job_search")
    return vector_search.search(user.id, payload)


@router.post(
    "/admin/search/evaluate",
    response_model=RetrievalEvaluation,
)
async def evaluate_search(
    payload: RetrievalEvaluationRequest,
    admin: User = Depends(require_admin),
) -> RetrievalEvaluation:
    """Evaluate retrieval against an explicit, administrator-owned dataset."""
    evaluation_user = admin.id
    result = vector_search.evaluate(evaluation_user, payload.cases)
    admin_store.audit(admin.id, "search_evaluated", "retrieval")
    return RetrievalEvaluation.model_validate(result)


@router.delete("/search/index/{entity_type}/{entity_id}", status_code=204)
async def delete_search_entity(
    entity_type: str, entity_id: str, user: User = Depends(require_user)
) -> None:
    vector_search.index.delete_entity(user.id, entity_type, entity_id)


@router.get("/companies", response_model=list[Company])
async def list_companies(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    _user: User = Depends(require_user),
) -> list[Company]:
    companies = [
        company for company in ingestion_store.companies.values() if company.active
    ]
    return companies[offset : offset + limit]


@router.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: str, _user: User = Depends(require_user)) -> Company:
    company = ingestion_store.companies.get(company_id)
    if company is None or not company.active:
        raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND"})
    return company


@router.post("/admin/companies", response_model=Company, status_code=201)
async def create_company(
    payload: CompanyCreate, admin: User = Depends(require_admin)
) -> Company:
    company = ingestion_store.add_company(payload, verified=True)
    admin_store.audit(admin.id, "company_created", "company", company.id)
    return company


@router.patch("/admin/companies/{company_id}", response_model=Company)
async def update_company(
    company_id: str,
    payload: CompanyUpdate,
    admin: User = Depends(require_admin),
) -> Company:
    company = ingestion_store.update_company(company_id, payload)
    if company is None:
        raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND"})
    admin_store.audit(admin.id, "company_updated", "company", company_id)
    return company


@router.delete("/admin/companies/{company_id}", status_code=204)
async def delete_company_endpoint(
    company_id: str,
    admin: User = Depends(require_admin),
) -> None:
    deleted = ingestion_store.delete_company(company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND"})
    admin_store.audit(admin.id, "company_deleted", "company", company_id)


@router.post(
    "/admin/companies/{company_id}/discover-career-url",
    response_model=CareerUrlDiscovery,
)
async def discover_company_career_url(
    company_id: str, admin: User = Depends(require_admin)
) -> CareerUrlDiscovery:
    company = ingestion_store.companies.get(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND"})
    if not company.website:
        raise HTTPException(status_code=422, detail={"code": "COMPANY_WEBSITE_MISSING"})
    try:
        career_url = discover_career_url(str(company.website))
    except CrawlError as error:
        raise HTTPException(status_code=422, detail={"code": str(error)}) from error
    if not career_url:
        raise HTTPException(status_code=404, detail={"code": "CAREER_URL_NOT_FOUND"})
    updated = ingestion_store.update_company(
        company_id,
        CompanyUpdate(career_page_url=career_url),
    )
    ingestion_store.companies[company_id] = updated.model_copy(
        update={"career_url_verified_at": datetime.now(UTC)}
    )
    admin_store.audit(admin.id, "career_url_discovered", "company", company_id)
    return CareerUrlDiscovery(career_page_url=career_url)


@router.post("/admin/companies/{company_id}/refresh", response_model=CrawlResult)
async def refresh_company(
    company_id: str, admin: User = Depends(require_admin)
) -> CrawlResult:
    if company_id not in ingestion_store.companies:
        raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND"})
    result = await asyncio.to_thread(ingestion_store.refresh, company_id)
    admin_store.activity("job_ingestion")
    admin_store.audit(
        admin.id,
        "company_refreshed",
        "company",
        company_id,
        {"status": result.status},
    )
    return result


@router.post("/admin/companies/{company_id}/approve", response_model=CrawlResult)
async def approve_company(
    company_id: str, admin: User = Depends(require_admin)
) -> CrawlResult:
    company = ingestion_store.companies.get(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND"})

    updated = company.model_copy(
        update={
            "verification_status": "verified",
            "active": True,
            "career_url_verified_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
    )
    ingestion_store.companies[company_id] = updated
    if ingestion_store._mongo_db is not None:
        try:
            ingestion_store._mongo_db.ingested_companies.update_one(
                {"id": company_id},
                {"$set": updated.model_dump(mode="json")},
                upsert=True,
            )
        except Exception:
            pass

    crawl = await asyncio.to_thread(ingestion_store.refresh, company_id)
    admin_store.activity("company_whitelisted")
    admin_store.audit(
        admin.id,
        "company_whitelisted",
        "company",
        company_id,
        {"name": company.name, "jobs_found": str(crawl.jobs_found)},
    )
    return crawl


@router.post("/admin/companies/{company_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_company(
    company_id: str, admin: User = Depends(require_admin)
) -> Response:
    deleted = ingestion_store.delete_company(company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND"})
    admin_store.audit(admin.id, "company_whitelist_rejected", "company", company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/admin/companies/{company_id}/crawls", response_model=list[CrawlResult])
async def list_company_crawls(
    company_id: str, _admin: User = Depends(require_admin)
) -> list[CrawlResult]:
    if company_id not in ingestion_store.companies:
        raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND"})
    return [crawl for crawl in ingestion_store.crawls if crawl.company_id == company_id]


@router.get("/admin/overview", response_model=AdminOverview)
async def admin_overview(_admin: User = Depends(require_admin)) -> AdminOverview:
    return get_admin_overview()


@router.get("/admin/companies", response_model=list[Company])
async def admin_companies(_admin: User = Depends(require_admin)) -> list[Company]:
    return list(ingestion_store.companies.values())


@router.post("/admin/companies/reset-prototype")
async def reset_prototype_companies_endpoint(admin: User = Depends(require_admin)) -> dict[str, Any]:
    companies = ingestion_store.reset_prototype_companies()
    admin_store.audit(admin.id, "companies_reset_prototype", "company", "bulk", {"count": len(companies)})
    return {"status": "ok", "total": len(companies), "companies": [c.name for c in companies]}


@router.get("/admin/jobs", response_model=list[AdminJobSummary])
async def admin_jobs(_admin: User = Depends(require_admin)) -> list[AdminJobSummary]:
    summaries = []
    for job in service.list_jobs():
        company = ingestion_store.companies.get(job.company_id)
        summaries.append(
            AdminJobSummary(
                job=job, company_name=company.name if company else "Unknown"
            )
        )
    return summaries


@router.get("/admin/crawls", response_model=list[CrawlResult])
async def admin_crawls(_admin: User = Depends(require_admin)) -> list[CrawlResult]:
    return list(reversed(ingestion_store.crawls))


@router.get("/admin/activity", response_model=list[ActivitySummary])
async def admin_activity(
    _admin: User = Depends(require_admin),
) -> list[ActivitySummary]:
    return admin_store.summaries()


@router.get("/admin/audit", response_model=list[AuditEvent])
async def admin_audit(_admin: User = Depends(require_admin)) -> list[AuditEvent]:
    return list(reversed(admin_store.audit_events[-100:]))


@router.get("/admin/retention", response_model=RetentionPolicy)
async def get_retention(_admin: User = Depends(require_admin)) -> RetentionPolicy:
    return admin_store.retention


@router.patch("/admin/retention", response_model=RetentionPolicy)
async def update_retention(
    payload: RetentionPolicyUpdate, admin: User = Depends(require_admin)
) -> RetentionPolicy:
    admin_store.retention = admin_store.retention.model_copy(
        update=payload.model_dump(exclude_unset=True)
    )
    admin_store.audit(admin.id, "retention_policy_updated", "retention")
    return admin_store.retention


@router.post("/admin/retention/purge", response_model=RetentionPurgeResult)
async def purge_retention(admin: User = Depends(require_admin)) -> RetentionPurgeResult:
    result = admin_store.purge()
    admin_store.audit(admin.id, "retention_purged", "retention")
    return result


@router.post("/admin/jobs/refresh", response_model=list[CrawlResult])
async def refresh_companies(
    payload: JobRefreshRequest | None = None,
    admin: User = Depends(require_admin),
) -> list[CrawlResult]:
    del payload
    target_ids = [
        company.id
        for company in ingestion_store.companies.values()
        if company.active and company.verification_status == "verified"
    ]
    results = []
    for cid in target_ids:
        try:
            res = await asyncio.to_thread(ingestion_store.refresh, cid)
            results.append(res)
        except Exception as exc:
            logger.warning("Error refreshing company %s: %s", cid, exc)
    admin_store.activity("job_ingestion")
    admin_store.audit(admin.id, "all_companies_refreshed", "ingestion")
    return results


@router.post("/admin/scrape-naukri", response_model=list[Job])
async def admin_scrape_naukri_endpoint(
    payload: NaukriScrapeRequest | None = None,
    admin: User = Depends(require_admin),
) -> list[Job]:
    req = payload or NaukriScrapeRequest()
    jobs = await asyncio.to_thread(
        ingestion_store.scrape_naukri,
        req.search_term,
        req.location,
        req.results_wanted,
    )
    admin_store.activity("job_ingestion")
    admin_store.audit(
        admin.id,
        "naukri_scraped",
        "jobs",
        req.search_term,
        {"count": len(jobs), "location": req.location},
    )
    return jobs


@router.post("/admin/jobs/schedule", status_code=202)
async def schedule_ingestion(admin: User = Depends(require_admin)) -> dict[str, object]:
    """Queue verified companies for a twice-daily worker invocation."""
    queue = JobQueue(get_settings().job_queue_path)
    queued = [
        queue.enqueue("company_refresh", company.id)
        for company in ingestion_store.companies.values()
        if company.active and company.verification_status == "verified"
    ]
    admin_store.audit(
        admin.id,
        "company_refresh_scheduled",
        "ingestion",
        metadata={"count": str(len(queued))},
    )
    return {"status": "queued", "job_ids": queued}


@router.post("/admin/jobs/purge-career-site-jobs")
async def purge_career_site_jobs_endpoint(
    admin: User = Depends(require_admin),
) -> dict[str, Any]:
    deleted = ingestion_store.purge_non_naukri_jobs()
    admin_store.audit(
        admin.id,
        "career_site_jobs_purged",
        "jobs",
        metadata={"deleted": str(deleted)},
    )
    return {
        "status": "succeeded",
        "deleted_jobs_count": deleted,
        "remaining_naukri_jobs": len(ingestion_store.jobs),
    }


@router.get("/admin/jobs/queue")
async def queue_status(_admin: User = Depends(require_admin)) -> dict[str, int]:
    return JobQueue(get_settings().job_queue_path).counts()


@router.get("/admin/ingestion/alerts")
async def ingestion_alerts(
    _admin: User = Depends(require_admin),
) -> list[dict[str, str]]:
    """Return recent crawl failures for local dashboards or managed alert polling."""
    return list(reversed(ingestion_store.alerts[-100:]))


@router.get("/admin/scheduler/status")
async def get_scheduler_status(_admin: User = Depends(require_admin)) -> dict[str, Any]:
    from app.scheduler import scraper_scheduler
    return scraper_scheduler.get_status()


@router.post("/admin/scheduler/trigger")
async def trigger_scheduler_now(admin: User = Depends(require_admin)) -> dict[str, Any]:
    from app.scheduler import scraper_scheduler
    result = await scraper_scheduler.run_once()
    admin_store.audit(admin.id, "scraper_triggered_manually", "ingestion")
    return result


@router.get("/applications", response_model=list[Application])
async def list_applications(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_user),
) -> list[Application]:
    applications = [
        item for item in service.list_applications() if item.user_id == user.id
    ]
    return applications[offset : offset + limit]


@router.get("/applications/{application_id}", response_model=Application)
async def get_application(
    application_id: str, user: User = Depends(require_user)
) -> Application:
    application = next(
        (
            item
            for item in service.list_applications()
            if item.id == application_id and item.user_id == user.id
        ),
        None,
    )
    if application is None:
        raise HTTPException(status_code=404, detail={"code": "APPLICATION_NOT_FOUND"})
    application.activity = [
        ApplicationActivity.model_validate(item)
        for item in auth_store.application_activity[user.id]
        if item["application_id"] == application_id
    ]
    return application


@router.get(
    "/applications/{application_id}/activity", response_model=list[ApplicationActivity]
)
async def get_application_activity(
    application_id: str, user: User = Depends(require_user)
) -> list[ApplicationActivity]:
    application = next(
        (
            item
            for item in service.list_applications()
            if item.id == application_id and item.user_id == user.id
        ),
        None,
    )
    if application is None:
        raise HTTPException(status_code=404, detail={"code": "APPLICATION_NOT_FOUND"})
    return [
        ApplicationActivity.model_validate(item)
        for item in auth_store.application_activity[user.id]
        if item["application_id"] == application_id
    ]


@router.post(
    "/applications", response_model=Application, status_code=status.HTTP_201_CREATED
)
async def create_application(
    payload: ApplicationCreate, user: User = Depends(require_user)
) -> Application:
    try:
        if payload.resume_version_id is not None:
            resume = auth_store.resume_versions[user.id].get(payload.resume_version_id)
            if (
                resume is None
                or resume["status"] != "approved"
                or resume["job_id"] != payload.job_id
            ):
                raise HTTPException(
                    status_code=422, detail={"code": "APPROVED_RESUME_REQUIRED"}
                )
        application = service.create_application(user.id, payload)
        return application
    except ValueError as error:
        if str(error) == "JOB_NOT_FOUND":
            raise HTTPException(
                status_code=404, detail={"code": "JOB_NOT_FOUND"}
            ) from error
        raise


@router.patch("/applications/{application_id}", response_model=Application)
async def update_application(
    application_id: str,
    payload: ApplicationUpdate,
    user: User = Depends(require_user),
) -> Application:
    if payload.resume_version_id is not None:
        resume = auth_store.resume_versions[user.id].get(payload.resume_version_id)
        application = next(
            (
                item
                for item in service.list_applications()
                if item.id == application_id and item.user_id == user.id
            ),
            None,
        )
        if (
            resume is None
            or resume["status"] != "approved"
            or application is None
            or resume["job_id"] != application.job_id
        ):
            raise HTTPException(
                status_code=422, detail={"code": "APPROVED_RESUME_REQUIRED"}
            )
    application = service.update_application(application_id, user.id, payload)
    if application is None:
        raise HTTPException(status_code=404, detail={"code": "APPLICATION_NOT_FOUND"})
    return application


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: str,
    user: User = Depends(require_user),
) -> Response:
    deleted = service.delete_application(application_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"code": "APPLICATION_NOT_FOUND"})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/notifications", response_model=list[Notification])
async def list_notifications(user: User = Depends(require_user)) -> list[Notification]:
    applications = [
        item for item in service.list_applications() if item.user_id == user.id
    ]
    create_application_reminders(user.id, applications)
    deliver_due_notifications(user.id, user.email)
    return [
        Notification.model_validate(item)
        for item in auth_store.list_notifications(user.id)
    ]


@router.patch("/notifications/{notification_id}", response_model=Notification)
async def update_notification(
    notification_id: str,
    payload: NotificationUpdate,
    user: User = Depends(require_user),
) -> Notification:
    notification = mark_notification(user.id, notification_id, payload.read)
    if notification is None:
        raise HTTPException(status_code=404, detail={"code": "NOTIFICATION_NOT_FOUND"})
    return notification


@router.get("/notification-preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    user: User = Depends(require_user),
) -> NotificationPreferences:
    return NotificationPreferences(**auth_store.notification_preferences[user.id])


@router.patch("/notification-preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    payload: NotificationPreferences, user: User = Depends(require_user)
) -> NotificationPreferences:
    auth_store.notification_preferences[user.id] = payload.model_dump()
    return payload


@router.get("/applications/{application_id}/calendar.ics")
async def export_application_calendar(
    application_id: str, user: User = Depends(require_user)
) -> Response:
    application = next(
        (
            item
            for item in service.list_applications()
            if item.id == application_id and item.user_id == user.id
        ),
        None,
    )
    if application is None or application.interview_at is None:
        raise HTTPException(status_code=404, detail={"code": "INTERVIEW_NOT_FOUND"})
    start = application.interview_at.strftime("%Y%m%dT%H%M%SZ")
    ics = (
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\n"
        f"UID:{application.id}@nexthire\r\nDTSTART:{start}\r\n"
        f"SUMMARY:Interview - {application.job_title}\r\n"
        "END:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{application.id}.ics"'},
    )


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard(user: User = Depends(require_user)) -> DashboardSummary:
    return service.get_dashboard(auth_store.get_profile(user.id), user.id)


@router.get("/analytics", response_model=UserAnalytics)
async def get_analytics(user: User = Depends(require_user)) -> UserAnalytics:
    return get_user_analytics(user.id)


@router.get("/privacy", response_model=PrivacySettings)
async def get_privacy_settings(user: User = Depends(require_user)) -> PrivacySettings:
    return PrivacySettings(**auth_store.privacy_settings[user.id])


@router.patch("/privacy", response_model=PrivacySettings)
async def update_privacy_settings(
    payload: PrivacySettingsUpdate, user: User = Depends(require_user)
) -> PrivacySettings:
    auth_store.privacy_settings[user.id].update(
        payload.model_dump(exclude_unset=True, exclude_none=True)
    )
    admin_store.audit(user.id, "privacy_settings_updated", "privacy", user.id)
    return PrivacySettings(**auth_store.privacy_settings[user.id])


@router.get("/privacy/export", response_model=UserDataExport)
async def export_user_data(user: User = Depends(require_user)) -> UserDataExport:
    admin_store.audit(user.id, "user_data_exported", "user", user.id)
    auth_store._ensure_career_entities(user.id)
    return UserDataExport(
        exported_at=datetime.now(UTC),
        user=user,
        profile=auth_store.get_profile(user.id),
        career_entities={
            entity_type: auth_store.list_entities(user.id, entity_type)
            for entity_type in auth_store.career_entities[user.id]
        },
        documents=list(auth_store.documents[user.id].values()),
        applications=[
            item for item in service.list_applications() if item.user_id == user.id
        ],
        resumes=[
            ResumeVersion.model_validate(item)
            for item in auth_store.resume_versions[user.id].values()
        ],
        notifications=[
            Notification.model_validate(item)
            for item in auth_store.list_notifications(user.id)
        ],
        privacy=PrivacySettings(**auth_store.privacy_settings[user.id]),
    )
