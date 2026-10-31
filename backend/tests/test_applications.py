from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.job_ingestion import ingestion_store
from app.main import app
from app.models import Job
from app.auth_store import auth_store
from app.services import service


def test_application_details_and_reminders_are_idempotent() -> None:
    client = TestClient(app)
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "application-stage@example.com",
            "display_name": "Applicant",
            "password": "correct horse battery staple",
        },
    )
    assert signup.status_code == 201
    ingestion_store.jobs["stage9-job"] = Job(
        id="stage9-job",
        company_id="company-1",
        title="Platform Engineer",
        location="Remote",
        url="https://example.com/stage9-job",
    )
    due = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    created = client.post(
        "/api/v1/applications",
        json={
            "job_id": "stage9-job",
            "status": "applied",
            "notes": "Submitted through the company portal.",
            "deadline": due,
            "next_action": "Follow up",
            "next_action_at": due,
        },
    )
    assert created.status_code == 201
    application = created.json()
    assert application["job_title"] == "Platform Engineer"
    assert application["notes"] == "Submitted through the company portal."

    notifications = client.get("/api/v1/notifications")
    assert notifications.status_code == 200
    assert len(notifications.json()) == 2
    assert len(client.get("/api/v1/notifications").json()) == 2

    updated = client.patch(
        f"/api/v1/applications/{application['id']}",
        json={"status": "interview", "interview_at": due},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "interview"

    marked = client.patch(
        f"/api/v1/notifications/{notifications.json()[0]['id']}",
        json={"read": True},
    )
    assert marked.status_code == 200
    assert marked.json()["read_at"] is not None
    user_id = auth_store.find_by_email("application-stage@example.com").id
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
    ingestion_store.jobs.pop("stage9-job", None)
    service.data.applications[:] = [
        item for item in service.data.applications if item.user_id != user_id
    ]
