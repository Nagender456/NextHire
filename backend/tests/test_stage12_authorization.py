from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.auth_store import auth_store
from app.job_ingestion import ingestion_store
from app.main import app
from app.models import Job
from app.services import service


def test_missing_authentication_and_cross_user_application_access_are_denied():
    client = TestClient(app)
    assert client.get("/api/v1/profile").status_code == 401
    suffix = str(datetime.now(UTC).timestamp())
    first_email = f"stage12-first-{suffix}@example.com"
    second_email = f"stage12-second-{suffix}@example.com"
    job = Job(
        id=f"stage12-auth-job-{suffix}",
        company_id="stage12-company",
        title="Backend Engineer",
        location="Remote",
        url="https://example.com/stage12-auth-job",
    )
    ingestion_store.jobs[job.id] = job
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": first_email,
                "display_name": "First Candidate",
                "password": "correct horse battery staple",
            },
        ).status_code
        == 201
    )
    created = client.post("/api/v1/applications", json={"job_id": job.id})
    assert created.status_code == 201
    application_id = created.json()["id"]
    first_user_id = auth_store.find_by_email(first_email).id

    client.post("/api/v1/auth/logout")
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": second_email,
                "display_name": "Second Candidate",
                "password": "correct horse battery staple",
            },
        ).status_code
        == 201
    )
    assert client.get(f"/api/v1/applications/{application_id}").status_code == 404
    assert client.get("/api/v1/applications").json() == []

    second_user_id = auth_store.find_by_email(second_email).id
    ingestion_store.jobs.pop(job.id, None)
    service.data.applications[:] = [
        item
        for item in service.data.applications
        if item.user_id not in {first_user_id, second_user_id}
    ]
    for user_id in (first_user_id, second_user_id):
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
