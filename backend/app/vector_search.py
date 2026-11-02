from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from app.auth_store import auth_store
from app.models import (
    CareerProfile,
    Job,
    SearchRequest,
    SearchResponse,
    SearchResult,
    VectorMetadata,
    VectorRecord,
)

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.-]{1,}")


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, text: str) -> list[float]: ...


class HashEmbeddingProvider:
    """Deterministic local provider used until a hosted provider is configured."""

    name = "local-hash-64"
    dimensions = 64

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in _TOKEN_RE.findall(text.lower()):
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            vector[index] += 1 if digest[2] % 2 else -1
        magnitude = math.sqrt(sum(value * value for value in vector))
        return [value / magnitude for value in vector] if magnitude else vector


class VectorIndex:
    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        self.provider = provider or HashEmbeddingProvider()
        self.records: dict[str, VectorRecord] = {}

    def upsert(
        self,
        *,
        record_id: str,
        text: str,
        user_id: str | None,
        entity_type: str,
        entity_id: str,
        source: str,
        company_id: str | None = None,
        job_id: str | None = None,
    ) -> VectorRecord:
        record = VectorRecord(
            id=record_id,
            text=text,
            embedding=self.provider.embed(text),
            metadata=VectorMetadata(
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                company_id=company_id,
                job_id=job_id,
                source=source,
                updated_at=datetime.now(UTC),
            ),
        )
        self.records[record_id] = record
        return record

    def delete(self, record_id: str) -> None:
        self.records.pop(record_id, None)

    def delete_entity(self, user_id: str, entity_type: str, entity_id: str) -> None:
        self.records = {
            key: record
            for key, record in self.records.items()
            if not (
                record.metadata.user_id == user_id
                and record.metadata.entity_type == entity_type
                and record.metadata.entity_id == entity_id
            )
        }

    def delete_user(self, user_id: str) -> None:
        self.records = {
            key: record
            for key, record in self.records.items()
            if record.metadata.user_id != user_id
        }

    def count(self, user_id: str | None = None) -> int:
        return sum(
            user_id is None or record.metadata.user_id == user_id
            for record in self.records.values()
        )


class JsonVectorIndex(VectorIndex):
    """Durable local index with the same boundary as hosted vector stores."""

    def __init__(self, path: str, provider: EmbeddingProvider | None = None) -> None:
        self.path = path
        super().__init__(provider)
        self._load()

    def _load(self) -> None:
        source = Path(self.path)
        if not source.exists():
            return
        try:
            payload = json.loads(source.read_text())
            self.records = {
                item["id"]: VectorRecord.model_validate(item) for item in payload
            }
        except (OSError, ValueError, TypeError):
            self.records = {}

    def _save(self) -> None:
        source = Path(self.path)
        source.parent.mkdir(parents=True, exist_ok=True)
        temporary = source.with_suffix(f"{source.suffix}.tmp")
        temporary.write_text(
            json.dumps(
                [record.model_dump(mode="json") for record in self.records.values()]
            )
        )
        temporary.replace(source)

    def upsert(self, **kwargs) -> VectorRecord:
        record = super().upsert(**kwargs)
        self._save()
        return record

    def delete(self, record_id: str) -> None:
        super().delete(record_id)
        self._save()

    def delete_entity(self, user_id: str, entity_type: str, entity_id: str) -> None:
        super().delete_entity(user_id, entity_type, entity_id)
        self._save()

    def delete_user(self, user_id: str) -> None:
        super().delete_user(user_id)
        self._save()


def _profile_text(profile: CareerProfile, entities: list[dict]) -> str:
    values = [
        profile.headline,
        profile.location,
        " ".join(profile.skills),
        " ".join(profile.preferred_roles),
        " ".join(profile.preferred_skills),
        " ".join(profile.preferred_locations),
        " ".join(profile.target_companies),
    ]
    for entity in entities:
        values.extend(str(value) for value in entity.values() if value is not None)
    return " ".join(values)


def _job_text(job: Job) -> str:
    return " ".join(
        [
            job.title,
            job.location,
            job.summary,
            job.description,
            " ".join(job.required_skills),
            " ".join(job.preferred_skills),
            job.experience or "",
            job.employment_type or "",
        ]
    )


class PersonalizedSearch:
    retrieval_version = "hybrid-v1"

    def __init__(self, jobs_provider, index: VectorIndex | None = None) -> None:
        self.jobs_provider = jobs_provider
        self.index = index or VectorIndex()

    def index_jobs(self) -> int:
        jobs = self.jobs_provider()
        for job in jobs:
            if job.status == "open":
                self.index.upsert(
                    record_id=f"job:{job.id}",
                    text=_job_text(job),
                    user_id=None,
                    entity_type="job",
                    entity_id=job.id,
                    source="job",
                    company_id=job.company_id,
                    job_id=job.id,
                )
            else:
                self.index.delete(f"job:{job.id}")
        return sum(job.status == "open" for job in jobs)

    def index_user(self, user_id: str) -> int:
        self.index.delete_user(user_id)
        profile = auth_store.get_profile(user_id)
        entities = [
            entity
            for entity_group in auth_store.career_entities[user_id].values()
            for entity in entity_group.values()
            if entity.get("confirmed_by_user", True)
        ]
        self.index.upsert(
            record_id=f"user:{user_id}:profile",
            text=_profile_text(profile, entities),
            user_id=user_id,
            entity_type="profile",
            entity_id=user_id,
            source="career-profile",
        )
        for entity in entities:
            text = " ".join(
                str(value) for value in entity.values() if value is not None
            )
            self.index.upsert(
                record_id=f"user:{user_id}:{entity['id']}",
                text=text,
                user_id=user_id,
                entity_type="career",
                entity_id=entity["id"],
                source=entity.get("source_type", "manual"),
            )
        return len(entities) + 1

    def reindex(self, user_id: str) -> None:
        self.index_jobs()
        self.index_user(user_id)

    def search(self, user_id: str, request: SearchRequest) -> SearchResponse:
        self.reindex(user_id)
        profile = auth_store.get_profile(user_id)
        dismissed = set(getattr(profile, "dismissed_job_ids", []))
        profile_record = self.index.records.get(f"user:{user_id}:profile")
        profile_text = profile_record.text if profile_record else ""
        query_text = f"{profile_text} {request.query}".strip()
        query_vector = (
            self.index.provider.embed(query_text)
            if query_text
            else [0.0] * self.index.provider.dimensions
        )
        requested_terms = set(_TOKEN_RE.findall(request.query.lower()))
        jobs = {job.id: job for job in self.jobs_provider() if job.status == "open"}
        user_skills = [s for s in getattr(profile, "skills", []) if s.strip()]
        has_user_context = bool(
            user_skills or (profile.headline and profile.headline.strip())
        )
        has_query = bool(request.query.strip())
        results: list[SearchResult] = []
        for record in self.index.records.values():
            metadata = record.metadata
            if metadata.user_id is not None or metadata.job_id not in jobs:
                continue
            if metadata.job_id in dismissed:
                continue
            job = jobs[metadata.job_id]
            if request.company_id and job.company_id != request.company_id:
                continue
            if (
                request.location
                and request.location.lower() not in job.location.lower()
            ):
                continue
            job_terms = set(_TOKEN_RE.findall(_job_text(job).lower()))
            terms = requested_terms.intersection(job_terms)
            lexical_score = (
                len(terms) / len(requested_terms) if requested_terms else 0.0
            )

            if not has_user_context and not has_query:
                score = 0.0
            else:
                semantic_score = max(
                    0.0,
                    min(
                        1.0, sum(a * b for a, b in zip(query_vector, record.embedding))
                    ),
                )
                score = (
                    semantic_score * 0.7 + lexical_score * 0.3
                    if requested_terms
                    else semantic_score
                )

            results.append(
                SearchResult(
                    job=job,
                    score=round(score, 6),
                    matched_terms=sorted(terms),
                    source=metadata.source,
                )
            )
        results.sort(key=lambda result: (-result.score, result.job.id))
        return SearchResponse(
            results=results[: request.limit],
            indexed_jobs=sum(
                record.metadata.entity_type == "job"
                for record in self.index.records.values()
            ),
            indexed_profile_chunks=self.index.count(user_id),
            embedding_model=self.index.provider.name,
            retrieval_version=self.retrieval_version,
        )

    def evaluate(
        self,
        user_id: str,
        cases: list,
    ) -> dict[str, float | int | str]:
        from app.models import SearchRequest

        precision = recall = reciprocal_rank = 0.0
        for case in cases:
            response = self.search(
                user_id,
                SearchRequest(
                    query=case.query,
                    company_id=case.company_id,
                    location=case.location,
                    limit=case.limit,
                ),
            )
            returned = [result.job.id for result in response.results]
            relevant = set(case.relevant_job_ids)
            hits = sum(job_id in relevant for job_id in returned)
            precision += hits / len(returned) if returned else 0
            recall += hits / len(relevant) if relevant else 1
            reciprocal_rank += next(
                (
                    1 / (index + 1)
                    for index, job_id in enumerate(returned)
                    if job_id in relevant
                ),
                0,
            )
        count = len(cases)
        return {
            "cases": count,
            "precision_at_k": round(precision / count, 6),
            "recall_at_k": round(recall / count, 6),
            "mean_reciprocal_rank": round(reciprocal_rank / count, 6),
            "retrieval_version": self.retrieval_version,
            "embedding_model": self.index.provider.name,
        }


def _create_index() -> VectorIndex:
    from app.config import get_settings

    path = get_settings().vector_index_path
    return JsonVectorIndex(path) if path else VectorIndex()


vector_search = PersonalizedSearch(lambda: [], _create_index())
