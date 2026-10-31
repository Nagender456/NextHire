from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.auth_store import auth_store
from app.job_ingestion import ingestion_store
from app.main import app
from app.models import CompanyCreate


def test_invalid_upload_and_crawler_failure_are_isolated():
    client = TestClient(app)
    email = f"stage12-edge-{datetime.now(UTC).timestamp()}@example.com"
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "display_name": "Edge Candidate",
                "password": "correct horse battery staple",
            },
        ).status_code
        == 201
    )
    invalid_upload = client.post(
        "/api/v1/career/documents",
        files={"file": ("resume.pdf", b"not-a-pdf", "application/pdf")},
    )
    assert invalid_upload.status_code == 422
    assert invalid_upload.json()["detail"]["code"] == "INVALID_PDF"

    company = ingestion_store.add_company(
        CompanyCreate(
            name="Broken Source",
            career_page_url="https://example.invalid/careers",
        ),
        verified=True,
    )
    result = ingestion_store.refresh(company.id)
    assert result.status == "failed"
    assert result.error_code == "CAREER_SOURCE_UNAVAILABLE"

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
        auth_store.notifications,
        auth_store.privacy_settings,
    ):
        collection.pop(user_id, None)
    ingestion_store.companies.pop(company.id, None)
