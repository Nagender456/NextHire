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


def test_manual_application_crud() -> None:
    client = TestClient(app)
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "manual-applicant@example.com",
            "display_name": "Manual Candidate",
            "password": "correct horse battery staple",
        },
    )
    assert signup.status_code == 201
    user_id = auth_store.find_by_email("manual-applicant@example.com").id

    due = (datetime.now(UTC) + timedelta(days=3)).isoformat()
    interview_time = (datetime.now(UTC) + timedelta(days=5)).isoformat()

    # 1. Create manually without job_id
    create_res = client.post(
        "/api/v1/applications",
        json={
            "job_title": "Staff Engineer",
            "company_id": "Vercel",
            "status": "applied",
            "application_url": "https://vercel.com/careers/staff-eng",
            "notes": "Referred by engineering director.",
            "deadline": due,
            "interview_at": interview_time,
            "next_action": "Technical screening call",
            "next_action_at": interview_time,
        },
    )
    assert create_res.status_code == 201
    app_data = create_res.json()
    app_id = app_data["id"]
    assert app_data["job_title"] == "Staff Engineer"
    assert app_data["company_id"] == "Vercel"
    assert app_data["status"] == "applied"
    assert app_data["application_url"] == "https://vercel.com/careers/staff-eng"
    assert app_data["notes"] == "Referred by engineering director."
    assert app_data["next_action"] == "Technical screening call"

    # 2. List applications and verify it appears
    list_res = client.get("/api/v1/applications")
    assert list_res.status_code == 200
    apps = list_res.json()
    assert any(a["id"] == app_id for a in apps)

    # 3. Update application fields
    update_res = client.patch(
        f"/api/v1/applications/{app_id}",
        json={
            "job_title": "Principal Engineer",
            "company_id": "Vercel Inc",
            "status": "interview",
            "notes": "Passed screen, moving to system design.",
        },
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["job_title"] == "Principal Engineer"
    assert updated_data["company_id"] == "Vercel Inc"
    assert updated_data["status"] == "interview"
    assert updated_data["notes"] == "Passed screen, moving to system design."

    # 4. Delete application
    del_res = client.delete(f"/api/v1/applications/{app_id}")
    assert del_res.status_code == 204

    # 5. Verify deletion
    get_res = client.get(f"/api/v1/applications/{app_id}")
    assert get_res.status_code == 404

    # Cleanup
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
