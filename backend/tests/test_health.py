from fastapi.testclient import TestClient

from app.auth_store import auth_store
from app.external_sources import fetch_github
from app.models import GitHubSourceRequest
from app.models import UserRole
from app.main import app
import app.routes as routes
from app.job_ingestion import ingestion_store


client = TestClient(app)


def authenticated_client() -> TestClient:
    test_client = TestClient(app)
    response = test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "candidate@example.com",
            "display_name": "Candidate",
            "password": "correct horse battery staple",
        },
    )
    if response.status_code == 409:
        test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "candidate@example.com",
                "password": "correct horse battery staple",
            },
        )
    return test_client


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "nexthire-api"}


def test_versioned_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["version"] == "v1"


def test_readiness_endpoint_reports_dependency_state() -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert set(body["dependencies"]) == {"mongodb", "redis"}


def test_foundation_routes_return_initial_shapes() -> None:
    authenticated = authenticated_client()
    profile = authenticated.get("/api/v1/profile")
    jobs = authenticated.get("/api/v1/jobs")
    applications = authenticated.get("/api/v1/applications")

    assert profile.status_code == 200
    assert profile.json()["display_name"] == "Candidate"
    assert jobs.json() == []
    assert applications.json() == []


def test_dashboard_returns_career_search_summary() -> None:
    response = authenticated_client().get("/api/v1/dashboard")

    assert response.status_code == 200
    assert response.json() == {
        "profile": {
            "user_id": "user-1",
            "display_name": "Candidate",
            "email": "candidate@example.com",
            "headline": "",
            "location": "",
            "skills": [],
            "preferred_roles": [],
            "preferred_skills": {},
            "preferred_locations": [],
            "target_companies": [],
            "dismissed_job_ids": [],
        },
        "recommended_jobs": [],
        "applications": [],
        "profile_completeness": 0,
        "jobs_discovered": 0,
        "active_applications": 0,
    }


def test_application_routes_have_foundation_placeholders() -> None:
    for path in ("/login", "/signup", "/admin"):
        response = client.get(path)
        assert response.status_code == 404


def test_authentication_and_profile_lifecycle() -> None:
    authenticated = authenticated_client()

    assert authenticated.get("/api/v1/auth/me").status_code == 200
    updated = authenticated.patch(
        "/api/v1/profile",
        json={
            "location": "Remote",
            "preferred_roles": ["Backend Engineer"],
            "preferred_skills": {"Python": "HIGH"},
            "preferred_locations": ["Remote"],
            "target_companies": ["NextHire"],
        },
    )
    assert updated.status_code == 200
    assert updated.json()["preferred_skills"] == {"Python": "HIGH"}

    logout = authenticated.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert authenticated.get("/api/v1/auth/me").status_code == 401


def test_protected_routes_require_a_session() -> None:
    assert client.get("/api/v1/profile").status_code == 401
    assert client.get("/api/v1/dashboard").status_code == 401


def test_password_reset_changes_password() -> None:
    authenticated_client()
    response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "candidate@example.com"},
    )
    assert response.status_code == 200
    token = next(iter(auth_store.reset_tokens))
    confirm = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "password": "new secure password"},
    )
    assert confirm.status_code == 200
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "candidate@example.com", "password": "new secure password"},
    )
    assert login_response.status_code == 200


def test_career_knowledge_base_manual_entry_lifecycle() -> None:
    authenticated = TestClient(app)
    authenticated.post(
        "/api/v1/auth/signup",
        json={
            "email": "ckb@example.com",
            "display_name": "CKB Candidate",
            "password": "correct horse battery staple",
        },
    )

    created_skill = authenticated.post(
        "/api/v1/career/skills",
        json={
            "name": "Python",
            "priority": "HIGH",
            "description": "Backend development",
        },
    )
    assert created_skill.status_code == 201
    skill = created_skill.json()
    assert skill["confirmed_by_user"] is True
    assert skill["source_type"] == "manual"
    assert authenticated.get("/api/v1/career/skills").json()[0]["name"] == "Python"

    updated_skill = authenticated.patch(
        f"/api/v1/career/skills/{skill['id']}",
        json={"confirmed_by_user": False, "priority": "MEDIUM"},
    )
    assert updated_skill.status_code == 200
    assert updated_skill.json()["confirmed_by_user"] is False

    project = authenticated.post(
        "/api/v1/career/projects",
        json={
            "name": "NextHire",
            "description": "Career platform",
            "technologies": ["FastAPI", "React"],
        },
    )
    assert project.status_code == 201
    assert project.json()["technologies"] == ["FastAPI", "React"]

    assert (
        authenticated.delete(f"/api/v1/career/skills/{skill['id']}").status_code == 204
    )
    assert authenticated.get("/api/v1/career/skills").json() == []


def test_resume_upload_review_and_embedding_preparation() -> None:
    authenticated = TestClient(app)
    authenticated.post(
        "/api/v1/auth/signup",
        json={
            "email": "resume@example.com",
            "display_name": "Resume Candidate",
            "password": "correct horse battery staple",
        },
    )
    pdf = b"%PDF-1.4\n(Experience) Tj\n(Backend Engineer) Tj\n%%EOF"
    uploaded = authenticated.post(
        "/api/v1/career/documents",
        files={"file": ("resume.pdf", pdf, "application/pdf")},
    )
    assert uploaded.status_code == 201
    document = uploaded.json()
    assert document["filename"] == "resume.pdf"
    extracted = authenticated.get(
        f"/api/v1/career/documents/{document['id']}/extracted"
    ).json()
    assert extracted[0]["confirmed_by_user"] is False
    reviewed = authenticated.patch(
        f"/api/v1/career/documents/{document['id']}/extracted/{extracted[0]['id']}",
        params={"confirmed_by_user": True},
    )
    assert reviewed.status_code == 200
    chunks = authenticated.post(f"/api/v1/career/documents/{document['id']}/chunks")
    assert chunks.status_code == 200
    assert len(chunks.json()) == 1


def test_external_sources_require_review_before_enriching_ckb(monkeypatch) -> None:
    authenticated = TestClient(app)
    authenticated.post(
        "/api/v1/auth/signup",
        json={
            "email": "sources@example.com",
            "display_name": "Source Candidate",
            "password": "correct horse battery staple",
        },
    )
    monkeypatch.setattr(
        routes,
        "fetch_github",
        lambda _payload: [
            {
                "source_id": "source-user/demo-project",
                "source_url": "https://github.com/source-user/demo-project",
                "entity_type": "projects",
                "data": {
                    "name": "Demo project",
                    "description": "A project from GitHub",
                    "technologies": ["Python"],
                    "url": "https://github.com/source-user/demo-project",
                },
            }
        ],
    )

    first = authenticated.post(
        "/api/v1/career/sources/github",
        json=GitHubSourceRequest(username="source-user").model_dump(),
    )
    assert first.status_code == 200
    candidate = first.json()[0]
    assert candidate["status"] == "pending"
    assert authenticated.get("/api/v1/career/projects").json() == []

    duplicate = authenticated.post(
        "/api/v1/career/sources/github", json={"username": "source-user"}
    )
    assert duplicate.status_code == 200
    assert duplicate.json() == []

    reviewed = authenticated.patch(
        f"/api/v1/career/sources/{candidate['id']}",
        json={"status": "accepted"},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "accepted"
    projects = authenticated.get("/api/v1/career/projects").json()
    assert projects[0]["source_type"] == "github"
    assert projects[0]["confirmed_by_user"] is True


def test_linkedin_profile_text_is_stored_as_pending_candidate() -> None:
    authenticated = TestClient(app)
    authenticated.post(
        "/api/v1/auth/signup",
        json={
            "email": "linkedin@example.com",
            "display_name": "LinkedIn Candidate",
            "password": "correct horse battery staple",
        },
    )
    response = authenticated.post(
        "/api/v1/career/sources/linkedin",
        json={"profile_text": "Senior engineer building reliable APIs."},
    )
    assert response.status_code == 200
    assert response.json()[0]["source_type"] == "linkedin"
    assert response.json()[0]["status"] == "pending"


def test_github_import_includes_languages_and_readme(monkeypatch) -> None:
    responses = {
        "https://api.github.com/users/source-user/repos?per_page=100": [
            {
                "name": "demo",
                "description": "Demo repository",
                "html_url": "https://github.com/source-user/demo",
                "topics": ["api"],
                "languages_url": "https://api.github.com/repos/source-user/demo/languages",
                "contents_url": "https://api.github.com/repos/source-user/demo/contents",
            }
        ],
        "https://api.github.com/repos/source-user/demo/languages": {"Python": 123},
        "https://api.github.com/repos/source-user/demo/contents/README": {
            "content": "IyBEZW1vIFJlYWRtZQ=="
        },
    }
    monkeypatch.setattr(
        "app.external_sources._fetch",
        lambda url, _accept="text/html": __import__("json")
        .dumps(responses[url])
        .encode(),
    )

    candidates = fetch_github(GitHubSourceRequest(username="source-user"))

    assert candidates[0]["data"]["technologies"] == ["Python", "api"]
    assert "Demo Readme" in candidates[0]["data"]["description"]


def test_portfolio_private_hosts_are_blocked() -> None:
    authenticated = TestClient(app)
    authenticated.post(
        "/api/v1/auth/signup",
        json={
            "email": "portfolio@example.com",
            "display_name": "Portfolio Candidate",
            "password": "correct horse battery staple",
        },
    )

    response = authenticated.post(
        "/api/v1/career/sources/portfolio",
        json={"url": "http://127.0.0.1/profile"},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "SOURCE_URL_BLOCKED"


def test_verified_company_refresh_normalizes_deduplicates_and_closes_jobs(
    monkeypatch,
) -> None:
    authenticated = TestClient(app)
    authenticated.post(
        "/api/v1/auth/signup",
        json={
            "email": "admin@example.com",
            "display_name": "Admin",
            "password": "correct horse battery staple",
        },
    )
    user = auth_store.find_by_email("admin@example.com")
    auth_store.users[user.id]["role"] = UserRole.ADMIN.value
    authenticated.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "correct horse battery staple",
        },
    )
    ingestion_store.companies.clear()
    ingestion_store.jobs.clear()
    ingestion_store.crawls.clear()
    html = """
    <a href="/jobs/backend-engineer">Backend Engineer</a>
    <a href="/jobs/backend-engineer">Backend Engineer duplicate</a>
    """
    monkeypatch.setattr("app.job_ingestion._fetch", lambda _url: html)

    company_response = authenticated.post(
        "/api/v1/admin/companies",
        json={
            "name": "Example",
            "website": "https://example.com",
            "career_page_url": "https://example.com/careers",
        },
    )
    assert company_response.status_code == 201
    company_id = company_response.json()["id"]

    refreshed = authenticated.post(f"/api/v1/admin/companies/{company_id}/refresh")
    assert refreshed.status_code == 200
    assert refreshed.json()["jobs_found"] == 1
    assert len(authenticated.get("/api/v1/jobs").json()) == 1

    monkeypatch.setattr("app.job_ingestion._fetch", lambda _url: "<p>No roles</p>")
    closed = authenticated.post(f"/api/v1/admin/companies/{company_id}/refresh")
    assert closed.json()["jobs_found"] == 0
    assert authenticated.get("/api/v1/jobs").json() == []
    assert list(ingestion_store.jobs.values())[0].status == "closed"
