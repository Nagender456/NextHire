from datetime import UTC, datetime
from fastapi.testclient import TestClient

from app.auth_store import auth_store
from app.job_ingestion import ingestion_store
from app.main import app
from app.models import CrawlResult, UserRole


def test_candidate_target_company_whitelist_workflow(monkeypatch):
    suffix = str(int(datetime.now(UTC).timestamp() * 1000))
    candidate_email = f"candidate-{suffix}@example.com"
    admin_email = f"admin-{suffix}@example.com"

    # 1. Candidate signs up and logs in
    cand_client = TestClient(app)
    signup_resp = cand_client.post(
        "/api/v1/auth/signup",
        json={
            "email": candidate_email,
            "display_name": "Target Company Candidate",
            "password": "correct horse battery staple",
        },
    )
    assert signup_resp.status_code == 201

    # 2. Candidate updates profile with new target company
    target_name = f"Unicorn Corp {suffix}"
    profile_resp = cand_client.patch(
        "/api/v1/profile",
        json={"target_companies": [target_name]},
    )
    assert profile_resp.status_code == 200

    # 3. Verify company was added with verification_status='pending'
    pending_company = next(
        (c for c in ingestion_store.companies.values() if c.name == target_name),
        None,
    )
    assert pending_company is not None
    assert pending_company.verification_status == "pending"

    # 4. Candidate cannot approve or reject (403 Forbidden)
    assert (
        cand_client.post(
            f"/api/v1/admin/companies/{pending_company.id}/approve"
        ).status_code
        == 403
    )
    assert (
        cand_client.post(
            f"/api/v1/admin/companies/{pending_company.id}/reject"
        ).status_code
        == 403
    )

    # 5. Admin logs in
    admin_client = TestClient(app)
    admin_client.post(
        "/api/v1/auth/signup",
        json={
            "email": admin_email,
            "display_name": "Whitelist Admin",
            "password": "correct horse battery staple",
        },
    )
    admin_user = auth_store.find_by_email(admin_email)
    auth_store.users[admin_user.id]["role"] = UserRole.ADMIN.value
    admin_client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_email,
            "password": "correct horse battery staple",
        },
    )

    # 6. Admin overview shows pending company count
    overview_resp = admin_client.get("/api/v1/admin/overview")
    assert overview_resp.status_code == 200
    assert overview_resp.json()["pending_companies"] >= 1

    # Mock ingestion_store.refresh for approve to avoid hitting external scrapers
    now = datetime.now(UTC)
    monkeypatch.setattr(
        ingestion_store,
        "refresh",
        lambda comp_id: CrawlResult(
            id=f"crawl-{comp_id}",
            company_id=comp_id,
            status="succeeded",
            jobs_found=5,
            jobs_added=5,
            jobs_updated=0,
            started_at=now,
            completed_at=now,
        ),
    )

    # 7. Admin approves the company
    approve_resp = admin_client.post(
        f"/api/v1/admin/companies/{pending_company.id}/approve"
    )
    assert approve_resp.status_code == 200
    assert (
        ingestion_store.companies[pending_company.id].verification_status == "verified"
    )

    # 8. Another company added by candidate to test rejection
    rej_target = f"Rejected Corp {suffix}"
    cand_client.patch(
        "/api/v1/profile",
        json={"target_companies": [target_name, rej_target]},
    )
    rej_company = next(
        (c for c in ingestion_store.companies.values() if c.name == rej_target),
        None,
    )
    assert rej_company is not None
    assert rej_company.verification_status == "pending"

    # 9. Admin rejects company
    reject_resp = admin_client.post(f"/api/v1/admin/companies/{rej_company.id}/reject")
    assert reject_resp.status_code == 204
    assert rej_company.id not in ingestion_store.companies
