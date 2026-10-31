from datetime import UTC, datetime

from app.auth_store import auth_store
from app.intelligence import analyze_job
from app.models import Job, RetrievalEvaluationCase, SearchRequest
from app.vector_search import JsonVectorIndex, PersonalizedSearch


def _job(job_id: str, title: str, skill: str) -> Job:
    return Job(
        id=job_id,
        company_id="company-stage67",
        title=title,
        location="Remote",
        url=f"https://example.com/{job_id}",
        required_skills=[skill],
        last_seen_at=datetime.now(UTC),
    )


def test_json_index_round_trips_records_and_keeps_tenant_deletion(tmp_path):
    path = tmp_path / "vectors.json"
    first = JsonVectorIndex(str(path))
    first.upsert(
        record_id="user:u1:skill-1",
        text="Python",
        user_id="u1",
        entity_type="career",
        entity_id="skill-1",
        source="manual",
    )
    first.upsert(
        record_id="user:u2:skill-1",
        text="Java",
        user_id="u2",
        entity_type="career",
        entity_id="skill-1",
        source="manual",
    )

    second = JsonVectorIndex(str(path))
    assert second.count("u1") == 1
    second.delete_entity("u1", "career", "skill-1")
    assert second.count("u1") == 0
    assert second.count("u2") == 1


def test_hybrid_retrieval_reports_version_and_evaluation_metrics():
    search = PersonalizedSearch(
        lambda: [
            _job("python-job", "Python Platform Engineer", "Python"),
            _job("java-job", "Java Platform Engineer", "Java"),
        ]
    )
    user = auth_store.create_user("stage67-search@example.com", "Stage 67", "hash")
    response = search.search(user.id, SearchRequest(query="Python"))
    assert response.retrieval_version == "hybrid-v1"
    assert response.results[0].job.id == "python-job"

    evaluation = search.evaluate(
        user.id,
        [
            RetrievalEvaluationCase(
                query="Python",
                relevant_job_ids=["python-job"],
            )
        ],
    )
    assert evaluation["precision_at_k"] == 0.5
    assert evaluation["recall_at_k"] == 1.0
    assert evaluation["mean_reciprocal_rank"] == 1.0


def test_intelligence_has_versioned_grounded_output():
    user = auth_store.create_user(
        "stage67-intelligence@example.com", "Stage 67", "hash"
    )
    auth_store.profiles[user.id].skills = ["Python"]
    result = analyze_job(user.id, _job("grounded-job", "Python Engineer", "Python"))
    assert result.model_version == "skills-grounded-v1"
    assert result.fit_score == 100
    assert result.evidence
