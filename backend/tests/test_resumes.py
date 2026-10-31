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
