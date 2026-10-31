from datetime import UTC, datetime

from app.auth_store import auth_store
from app.intelligence import analyze_job
from app.models import Job, Project


def test_job_intelligence_is_explainable_and_normalizes_aliases():
    user = auth_store.create_user("intelligence@example.com", "Candidate", "hash")
    auth_store.profiles[user.id].skills = ["JavaScript"]
    auth_store.career_entities[user.id]["skills"]["skill-1"] = {
        "id": "skill-1",
        "name": "ReactJS",
        "confirmed_by_user": True,
    }
    project = Project(
        id="project-1",
        user_id=user.id,
        name="Dashboard",
        description="A React frontend",
        technologies=["React"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    auth_store.career_entities[user.id]["projects"][project.id] = project.model_dump()
    job = Job(
        id="job-1",
        company_id="company-1",
        title="Frontend Engineer",
        location="Remote",
        url="https://example.com/job-1",
        required_skills=["JS", "React"],
        preferred_skills=["Kubernetes"],
    )

    result = analyze_job(user.id, job)

    assert result.fit_score == 70
    assert result.recommendation == "recommended"
    assert result.matched_required_skills == ["JS", "React"]
    assert result.missing_preferred_skills == ["Kubernetes"]
    assert [item.name for item in result.relevant_projects] == ["Dashboard"]
    assert result.learning_opportunities[0].skill == "Kubernetes"


def test_low_fit_remains_explorable_without_score_inflation():
    user = auth_store.create_user("low-fit@example.com", "Candidate", "hash")
    job = Job(
        id="job-2",
        company_id="company-1",
        title="Platform Engineer",
        location="Remote",
        url="https://example.com/job-2",
        required_skills=["Python", "Kubernetes"],
    )

    result = analyze_job(user.id, job)

    assert result.fit_score == 0
    assert result.recommendation == "lower_match"
    assert result.missing_required_skills == ["Kubernetes", "Python"]
