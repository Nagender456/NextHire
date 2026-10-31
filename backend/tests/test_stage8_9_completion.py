from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.auth_store import auth_store
from app.job_ingestion import ingestion_store
from app.main import app
from app.models import Job
from app.services import service


def test_resume_template_export_history_and_application_activity():
    client = TestClient(app)
    email = "stage89-completion@example.com"
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "display_name": "Stage Eight Nine",
                "password": "correct horse battery staple",
            },
        ).status_code
        == 201
    )
    job = Job(
        id="stage89-job",
        company_id="stage89-company",
        title="Platform Engineer",
        location="Remote",
        url="https://example.com/stage89-job",
    )
    ingestion_store.jobs[job.id] = job

    templates = client.get("/api/v1/resume-templates")
    assert templates.status_code == 200
    assert {item["id"] for item in templates.json()} >= {"default", "technical"}

    resume = client.post(f"/api/v1/jobs/{job.id}/resumes")
    assert resume.status_code == 201
    resume_id = resume.json()["id"]
    assert client.get(f"/api/v1/resumes/{resume_id}/latex").status_code == 200
    exports = client.get(f"/api/v1/resumes/{resume_id}/exports")
    assert exports.status_code == 200
    assert exports.json()[0]["format"] == "latex"

    due = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    application = client.post(
        "/api/v1/applications",
        json={"job_id": job.id, "interview_at": due},
    )
    assert application.status_code == 201
    application_id = application.json()["id"]
    activity = client.get(f"/api/v1/applications/{application_id}/activity")
    assert activity.status_code == 200
    assert activity.json()[0]["action"] == "created"
    calendar = client.get(f"/api/v1/applications/{application_id}/calendar.ics")
    assert calendar.status_code == 200
    assert "BEGIN:VCALENDAR" in calendar.text

    preferences = client.patch(
        "/api/v1/notification-preferences",
        json={"email_enabled": False, "in_app_enabled": True},
    )
    assert preferences.status_code == 200
    assert preferences.json()["email_enabled"] is False

    user_id = auth_store.find_by_email(email).id
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
        auth_store.resume_exports,
        auth_store.notifications,
        auth_store.privacy_settings,
        auth_store.notification_preferences,
    ):
        collection.pop(user_id, None)
    auth_store.application_activity.pop(user_id, None)
    ingestion_store.jobs.pop(job.id, None)
    service.data.applications[:] = [
        item for item in service.data.applications if item.user_id != user_id
    ]
