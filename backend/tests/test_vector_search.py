from datetime import UTC, datetime

from app.auth_store import auth_store
from app.models import Job, SearchRequest
from app.vector_search import PersonalizedSearch


def _job(job_id: str, company_id: str, title: str, location: str) -> Job:
    return Job(
        id=job_id,
        company_id=company_id,
        title=title,
        location=location,
        url=f"https://example.com/{job_id}",
        description=f"Build {title} applications",
        required_skills=["python"],
        last_seen_at=datetime.now(UTC),
    )


def _user_id(label: str) -> str:
    return auth_store.create_user(
        f"{label}@example.com", label, "test-password-hash"
    ).id


def test_search_ranks_semantically_related_jobs_and_applies_filters():
    search = PersonalizedSearch(
        lambda: [
            _job("job-python", "company-a", "Python backend engineer", "Remote"),
            _job("job-design", "company-b", "Product designer", "New York"),
        ]
    )

    user_id = _user_id("vector-ranking")
    response = search.search(user_id, SearchRequest(query="python", limit=10))

    assert response.results[0].job.id == "job-python"
    assert "python" in response.results[0].matched_terms
    assert response.embedding_model == "local-hash-64"
    assert (
        search.search(
            user_id,
            SearchRequest(query="", company_id="company-b"),
        )
        .results[0]
        .job.id
        == "job-design"
    )


def test_user_index_records_are_tenant_scoped():
    search = PersonalizedSearch(
        lambda: [_job("job-1", "company-a", "Engineer", "Remote")]
    )

    user_one = _user_id("vector-one")
    user_two = _user_id("vector-two")
    search.search(user_one, SearchRequest())
    search.search(user_two, SearchRequest())

    assert search.index.count(user_one) >= 1
    assert search.index.count(user_two) >= 1
    assert all(
        record.metadata.user_id in {None, user_one, user_two}
        for record in search.index.records.values()
    )


def test_deleted_entity_is_removed_from_index():
    search = PersonalizedSearch(lambda: [])
    search.index.upsert(
        record_id="user:user-1:skill-1",
        text="python",
        user_id="user-1",
        entity_type="career",
        entity_id="skill-1",
        source="manual",
    )

    search.index.delete_entity("user-1", "career", "skill-1")

    assert "user:user-1:skill-1" not in search.index.records
