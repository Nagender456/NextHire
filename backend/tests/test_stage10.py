from fastapi.testclient import TestClient

from app.auth_store import auth_store
from app.job_ingestion import ingestion_store
from app.main import app
from app.models import Job, UserRole
from app.services import service


def test_user_analytics_is_scoped_and_reports_skill_gaps() -> None:
    client = TestClient(app)
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "analytics-stage@example.com",
            "display_name": "Analytics Candidate",
            "password": "correct horse battery staple",
        },
    )
    assert signup.status_code == 201
    user_id = auth_store.find_by_email("analytics-stage@example.com").id
    ingestion_store.jobs["analytics-job"] = Job(
        id="analytics-job",
        company_id="company-analytics",
        title="Platform Engineer",
        location="Remote",
        url="https://example.com/analytics-job",
        required_skills=["Python", "Kubernetes"],
    )
    auth_store.profiles[user_id].skills = ["Python"]

    response = client.get("/api/v1/analytics")

    assert response.status_code == 200
    assert response.json()["jobs_discovered"] >= 1
    assert response.json()["matching_jobs"] == 1
    assert response.json()["skill_gaps"] == [{"skill": "Kubernetes", "jobs": 1}]

    ingestion_store.jobs.pop("analytics-job")
    for collection in (
        auth_store.users,
        auth_store.profiles,
        auth_store.career_entities,
        auth_store.documents,
        auth_store.document_contents,
        auth_store.extracted_entities,
        auth_store.external_candidates,
        auth_store.recommendation_feedback,
        auth_store.resume_versions,
        auth_store.notifications,
    ):
        collection.pop(user_id, None)
    service.data.applications[:] = [
        item for item in service.data.applications if item.user_id != user_id
    ]


def test_admin_overview_requires_admin_and_reports_crawls() -> None:
    client = TestClient(app)
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "admin-stage@example.com",
            "display_name": "Stage Admin",
            "password": "correct horse battery staple",
        },
    )
    assert signup.status_code == 201
    assert client.get("/api/v1/admin/overview").status_code == 403

    user = auth_store.find_by_email("admin-stage@example.com")
    auth_store.users[user.id]["role"] = UserRole.ADMIN.value
    client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin-stage@example.com",
            "password": "correct horse battery staple",
        },
    )
    response = client.get("/api/v1/admin/overview")

    assert response.status_code == 200
    assert response.json()["users"] >= 1

    for collection in (
        auth_store.users,
        auth_store.profiles,
        auth_store.career_entities,
        auth_store.documents,
        auth_store.document_contents,
        auth_store.extracted_entities,
        auth_store.external_candidates,
        auth_store.recommendation_feedback,
        auth_store.resume_versions,
        auth_store.notifications,
    ):
        collection.pop(user.id, None)


def test_privacy_controls_and_data_export() -> None:
    client = TestClient(app)
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "privacy-stage@example.com",
            "display_name": "Privacy Candidate",
            "password": "correct horse battery staple",
        },
    )
    assert signup.status_code == 201

    updated = client.patch("/api/v1/privacy", json={"analytics_enabled": False})
    assert updated.status_code == 200
    assert updated.json()["analytics_enabled"] is False
    analytics = client.get("/api/v1/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["applications"] == 0

    exported = client.get("/api/v1/privacy/export")
    assert exported.status_code == 200
    assert exported.json()["user"]["email"] == "privacy-stage@example.com"
    assert exported.json()["privacy"]["analytics_enabled"] is False

    user = auth_store.find_by_email("privacy-stage@example.com")
    for collection in (
        auth_store.users,
        auth_store.profiles,
        auth_store.career_entities,
        auth_store.documents,
        auth_store.document_contents,
        auth_store.extracted_entities,
        auth_store.external_candidates,
        auth_store.recommendation_feedback,
        auth_store.resume_versions,
        auth_store.notifications,
        auth_store.privacy_settings,
    ):
        collection.pop(user.id, None)
