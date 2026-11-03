from datetime import UTC, datetime

import pytest

from app.auth_store import auth_store
from app.models import Job, ResumeContent, ResumeItem
from app.resumes import create_version, render_latex, validate_content


def test_resume_generation_uses_confirmed_facts_and_versions_per_job() -> None:
    user = auth_store.create_user("resume@example.com", "Candidate", "hash")
    auth_store.profiles[user.id].headline = "Backend engineer"
    project = {
        "id": "project-1",
        "user_id": user.id,
        "name": "Hiring API",
        "description": "Built a Python API",
        "technologies": ["Python"],
        "confirmed_by_user": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    auth_store.career_entities[user.id]["projects"][project["id"]] = project
    job = Job(
        id="resume-job",
        company_id="company-1",
        title="Python Engineer",
        location="Remote",
        url="https://example.com/resume-job",
        required_skills=["Python"],
    )

    first = create_version(user.id, job)
    second = create_version(user.id, job)

    assert first.version == 1
    assert second.version == 2
    assert first.content.summary == "Backend engineer"
    assert first.content.projects[0].source_entity_ids == ["project-1"]


def test_resume_edits_require_confirmed_sources_and_escape_latex() -> None:
    user = auth_store.create_user("resume-edit@example.com", "Candidate", "hash")
    content = ResumeContent(
        summary="Candidate & engineer",
        experience=[ResumeItem(text="Unverified claim", source_entity_ids=["missing"])],
    )

    with pytest.raises(ValueError, match="CONFIRMED_SOURCE"):
        validate_content(user.id, content)

    latex = render_latex(
        ResumeContent(summary="Candidate & engineer", skills=["C++", "Python"])
    )
    assert r"Candidate \& engineer" in latex
    assert r"C++" in latex


def test_jack_resume_template_and_pdf_export() -> None:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.resumes import render_pdf, TEMPLATES

    assert "jack" in TEMPLATES

    # Test PDF download endpoint with authenticated client
    client = TestClient(app)
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "pdf-resume@example.com",
            "display_name": "Jane Doe",
            "password": "correct horse battery staple",
        },
    )
    assert signup.status_code == 201
    user_id = auth_store.find_by_email("pdf-resume@example.com").id

    job = Job(
        id="pdf-job-1",
        company_id="company-pdf",
        title="Software Engineer",
        location="San Francisco, CA",
        url="https://example.com/pdf-job",
        required_skills=["Python", "FastAPI"],
    )

    version = create_version(user_id, job)
    assert version.template == "jack"

    # Test direct PDF rendering
    pdf_bytes = render_pdf(version.content, profile=auth_store.get_profile(user_id))
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")

    resp = client.get(f"/api/v1/resumes/{version.id}/pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert f'attachment; filename="{version.id}.pdf"' in resp.headers["content-disposition"]
    assert resp.content.startswith(b"%PDF-")
