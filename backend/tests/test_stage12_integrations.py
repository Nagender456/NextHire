from datetime import UTC, datetime, timedelta
import json

from fastapi.testclient import TestClient

from app.auth_store import auth_store
from app.external_sources import fetch_github, fetch_portfolio
from app.job_ingestion import ingestion_store
from app.main import app
from app.models import GitHubSourceRequest, Job
from app.notifications import InMemoryEmailProvider, email_provider
from app.services import service


def _remove_user(user_id: str) -> None:
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


def test_external_source_review_and_resume_latex_export(monkeypatch) -> None:
    responses = {
        "https://api.github.com/users/stage12/repos?per_page=100": [
            {
                "name": "hiring-api",
                "description": "Career API",
                "html_url": "https://github.com/stage12/hiring-api",
                "topics": ["api"],
                "languages_url": "https://api.github.com/repos/stage12/hiring-api/languages",
                "contents_url": "https://api.github.com/repos/stage12/hiring-api/contents",
            }
        ],
        "https://api.github.com/repos/stage12/hiring-api/languages": {"Python": 10},
        "https://api.github.com/repos/stage12/hiring-api/contents/README": {
            "content": "IyBIZWxsbw=="
        },
    }

    monkeypatch.setattr(
        "app.external_sources._fetch",
        lambda url, _accept="text/html": json.dumps(responses[url]).encode(),
    )
    assert fetch_github(GitHubSourceRequest(username="stage12"))[0]["data"][
        "technologies"
    ] == ["Python", "api"]

    monkeypatch.setattr(
        "app.external_sources._fetch",
        lambda _url, _accept="text/html": b"<html><body>Python portfolio</body></html>",
    )
    portfolio = fetch_portfolio(
        type("PortfolioRequest", (), {"url": "https://portfolio.example"})()
    )
    assert "Python portfolio" in portfolio[0]["data"]["description"]
    monkeypatch.setattr(
        "app.external_sources._fetch",
        lambda url, _accept="text/html": json.dumps(responses[url]).encode(),
    )

    client = TestClient(app)
    email = "stage12-integrations@example.com"
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "display_name": "Integration Candidate",
                "password": "correct horse battery staple",
            },
        ).status_code
        == 201
    )
    candidate = client.post(
        "/api/v1/career/sources/github",
        json={"username": "stage12"},
    )
    assert candidate.status_code == 200
    candidate_id = candidate.json()[0]["id"]
    assert (
        client.patch(
            f"/api/v1/career/sources/{candidate_id}",
            json={"status": "accepted"},
        ).status_code
        == 200
    )

    user_id = auth_store.find_by_email(email).id
    job = Job(
        id="stage12-latex-job",
        company_id="stage12-company",
        title="Python Engineer",
        location="Remote",
        url="https://example.com/stage12-latex-job",
        required_skills=["Python"],
    )
    ingestion_store.jobs[job.id] = job
    resume = client.post(f"/api/v1/jobs/{job.id}/resumes")
    assert resume.status_code == 201
    latex = client.get(f"/api/v1/resumes/{resume.json()['id']}/latex")
    assert latex.status_code == 200
    assert latex.headers["content-type"].startswith("application/x-latex")
    assert "\\documentclass" in latex.text

    ingestion_store.jobs.pop(job.id, None)
    _remove_user(user_id)


def test_due_notification_is_delivered_once() -> None:
    provider = email_provider
    assert isinstance(provider, InMemoryEmailProvider)
    provider.sent.clear()
    client = TestClient(app)
    email = "stage12-notification@example.com"
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "display_name": "Notification Candidate",
                "password": "correct horse battery staple",
            },
        ).status_code
        == 201
    )
    job = Job(
        id="stage12-notification-job",
        company_id="stage12-company",
        title="Platform Engineer",
        location="Remote",
        url="https://example.com/stage12-notification-job",
    )
    ingestion_store.jobs[job.id] = job
    due = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    application = client.post(
        "/api/v1/applications",
        json={"job_id": job.id, "next_action": "Follow up", "next_action_at": due},
    )
    assert application.status_code == 201
    first = client.get("/api/v1/notifications")
    second = client.get("/api/v1/notifications")
    assert first.status_code == second.status_code == 200
    assert len(provider.sent) == 1

    user_id = auth_store.find_by_email(email).id
    ingestion_store.jobs.pop(job.id, None)
    service.data.applications[:] = [
        item for item in service.data.applications if item.user_id != user_id
    ]
    _remove_user(user_id)
