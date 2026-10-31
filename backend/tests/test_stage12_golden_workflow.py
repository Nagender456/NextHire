from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.auth_store import auth_store
from app.job_ingestion import ingestion_store
from app.main import app
from app.models import Job


def test_golden_workflow_persists_recommendation_resume_application_and_analytics():
    client = TestClient(app)
    email = f"stage12-{datetime.now(UTC).timestamp()}@example.com"
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "display_name": "Stage 12 Candidate",
            "password": "correct horse battery staple",
        },
    )
    assert signup.status_code == 201
    user_id = auth_store.find_by_email(email).id

    assert (
        client.post(
            "/api/v1/career/skills",
            json={"name": "Python", "confirmed_by_user": True},
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/career/projects",
            json={
                "name": "Hiring API",
                "description": "Built a FastAPI service",
                "technologies": ["Python", "FastAPI"],
            },
        ).status_code
        == 201
    )

    job = Job(
        id=f"stage12-job-{user_id}",
        company_id="stage12-company",
        title="Python Platform Engineer",
        location="Remote",
        url="https://example.com/stage12-job",
        required_skills=["Python"],
        preferred_skills=["Kubernetes"],
    )
    ingestion_store.jobs[job.id] = job

    search = client.post("/api/v1/search/jobs", json={"query": "Python"})
    assert search.status_code == 200
    assert search.json()["results"][0]["job"]["id"] == job.id
    intelligence = client.get(f"/api/v1/jobs/{job.id}/intelligence")
    assert intelligence.status_code == 200
    assert intelligence.json()["fit_score"] == 70
    assert intelligence.json()["missing_preferred_skills"] == ["Kubernetes"]

    resume = client.post(f"/api/v1/jobs/{job.id}/resumes")
    assert resume.status_code == 201
    resume_id = resume.json()["id"]
    assert (
        client.patch(
            f"/api/v1/resumes/{resume_id}",
            json={"content": resume.json()["content"], "status": "approved"},
        ).status_code
        == 200
    )

    application = client.post(
        "/api/v1/applications",
        json={
            "job_id": job.id,
            "resume_version_id": resume_id,
            "status": "applied",
        },
    )
    assert application.status_code == 201
    assert (
        client.get(f"/api/v1/applications/{application.json()['id']}").status_code
        == 200
    )
    analytics = client.get("/api/v1/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["applications"] == 1

    ingestion_store.jobs.pop(job.id, None)
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
        collection.pop(user_id, None)
