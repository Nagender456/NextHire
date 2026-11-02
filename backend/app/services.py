from datetime import UTC, datetime

from app.models import (
    Application,
    ApplicationCreate,
    ApplicationStatus,
    ApplicationUpdate,
    CareerProfile,
    DashboardSummary,
    Job,
)
from app.repositories import InMemoryRepository, repository
from app.job_ingestion import ingestion_store
from app.auth_store import auth_store


class FoundationService:
    def __init__(self, data: InMemoryRepository) -> None:
        self.data = data

    def get_profile(self) -> CareerProfile:
        return self.data.get_profile()

    def list_jobs(self) -> list[Job]:
        all_jobs = [*ingestion_store.jobs.values(), *self.data.list_jobs()]
        seen_keys: set[str] = set()
        deduped: list[Job] = []
        for job in all_jobs:
            norm_title = " ".join((job.title or "").lower().split())
            norm_company = " ".join((job.company_id or "").lower().split())
            norm_url = str(job.url or "").strip().rstrip("/")
            if norm_url and norm_url in seen_keys:
                continue
            ct_key = f"{norm_company}::{norm_title}"
            if ct_key in seen_keys or job.id in seen_keys:
                continue
            if norm_url:
                seen_keys.add(norm_url)
            seen_keys.add(ct_key)
            seen_keys.add(job.id)
            deduped.append(job)
        return deduped

    def list_applications(self) -> list[Application]:
        return self.data.list_applications()

    def get_job(self, job_id: str) -> Job | None:
        return ingestion_store.jobs.get(job_id) or self.data.get_job(job_id)

    def create_application(
        self, user_id: str, payload: ApplicationCreate
    ) -> Application:
        job = self.get_job(payload.job_id) if payload.job_id else None
        if payload.job_id and not job and not (payload.job_title or payload.company_id):
            raise ValueError("JOB_NOT_FOUND")

        now = datetime.now(UTC)
        if payload.job_id and job:
            existing = next(
                (a for a in self.data.applications if a.user_id == user_id and a.job_id == payload.job_id),
                None,
            )
            if existing:
                existing.status = payload.status
                if payload.status != ApplicationStatus.SAVED and not existing.applied_at:
                    existing.applied_at = now
                if payload.notes:
                    existing.notes = payload.notes
                if payload.deadline is not None:
                    existing.deadline = payload.deadline
                if payload.interview_at is not None:
                    existing.interview_at = payload.interview_at
                if payload.next_action:
                    existing.next_action = payload.next_action
                if payload.next_action_at is not None:
                    existing.next_action_at = payload.next_action_at
                if payload.resume_version_id:
                    existing.resume_version_id = payload.resume_version_id
                if payload.job_title:
                    existing.job_title = payload.job_title
                if payload.company_id:
                    existing.company_id = payload.company_id
                if payload.application_url:
                    existing.application_url = payload.application_url
                existing.updated_at = now
                self.data.add_application(existing)
                from app.auth_store import auth_store

                auth_store.add_application_activity(user_id, existing.id, f"updated_{payload.status}")
                return existing

        from uuid import uuid4
        app_id = f"application-{uuid4().hex[:8]}"
        job_id = payload.job_id or f"manual-{uuid4().hex[:8]}"
        job_title = payload.job_title or (job.title if job else "Custom Role")
        company_id = payload.company_id or (job.company_id if job else "Company")
        app_url = payload.application_url or (job.url if job else None)

        application = Application(
            id=app_id,
            user_id=user_id,
            job_id=job_id,
            status=payload.status,
            applied_at=now if payload.status != ApplicationStatus.SAVED else None,
            company_id=company_id,
            job_title=job_title,
            resume_version_id=payload.resume_version_id,
            application_url=app_url,
            notes=payload.notes,
            deadline=payload.deadline,
            next_action=payload.next_action,
            next_action_at=payload.next_action_at,
            interview_at=payload.interview_at,
            job_snapshot={
                "title": job_title,
                "company_id": str(company_id),
                "url": str(app_url or ""),
            },
            created_at=now,
            updated_at=now,
        )
        from app.auth_store import auth_store

        auth_store.add_application_activity(user_id, application.id, "created")
        return self.data.add_application(application)

    def update_application(
        self, application_id: str, user_id: str, payload: ApplicationUpdate
    ) -> Application | None:
        application = next(
            (item for item in self.list_applications() if item.id == application_id),
            None,
        )
        if application is None or application.user_id != user_id:
            return None
        updated = self.data.update_application(
            application_id, payload.status, payload.resume_version_id
        )
        if updated:
            changes = payload.model_dump(
                exclude_unset=True,
                exclude={"status", "resume_version_id"},
            )
            for field, value in changes.items():
                setattr(updated, field, value)
            updated.updated_at = datetime.now(UTC)
            if (
                payload.status is not None
                and payload.status != ApplicationStatus.SAVED
                and not updated.applied_at
            ):
                updated.applied_at = datetime.now(UTC)
            self.data.add_application(updated)
            from app.auth_store import auth_store

            auth_store.add_application_activity(
                user_id, application_id, "updated", ",".join(changes)
            )
        return updated

    def delete_application(self, application_id: str, user_id: str) -> bool:
        application = next(
            (item for item in self.list_applications() if item.id == application_id),
            None,
        )
        if application is None or application.user_id != user_id:
            return False
        if hasattr(self.data, "delete_application"):
            return self.data.delete_application(application_id)
        self.data.applications[:] = [
            a for a in self.data.applications if a.id != application_id
        ]
        return True

    def get_dashboard(
        self, profile: CareerProfile | None = None, user_id: str | None = None
    ) -> DashboardSummary:
        profile = profile or self.get_profile()
        if user_id and user_id in auth_store.profiles:
            skills_set: list[str] = list(profile.skills or [])
            for s in auth_store.career_entities.get(user_id, {}).get("skills", {}).values():
                name = s.get("name")
                if name and name not in skills_set:
                    skills_set.append(name)
            for ext in auth_store.extracted_entities.get(user_id, {}).values():
                if ext.get("confirmed_by_user") and ext.get("entity_type") == "skills":
                    text = ext.get("data", {}).get("text", "")
                    for p in text.replace("\n", ",").split(","):
                        clean = p.strip().strip("•-* \t")
                        if clean and len(clean) < 60 and clean not in skills_set:
                            skills_set.append(clean)
            for pref_skill in profile.preferred_skills.keys():
                if pref_skill not in skills_set:
                    skills_set.append(pref_skill)
            if len(skills_set) != len(profile.skills or []):
                profile = profile.model_copy(update={"skills": skills_set})
                auth_store.profiles[user_id] = profile

            if not profile.headline:
                for ext in auth_store.extracted_entities.get(user_id, {}).values():
                    if ext.get("confirmed_by_user"):
                        text = str(ext.get("data", {}).get("text", ""))
                        if "LeetCode" in text or "ICPC" in text or "Competitive" in text:
                            profile = profile.model_copy(update={"headline": "Software Engineer | Competitive Programmer"})
                            auth_store.profiles[user_id] = profile
                            break
                        elif ext.get("entity_type") == "experience" and text:
                            first_line = text.splitlines()[0].strip()
                            if first_line and len(first_line) < 60:
                                profile = profile.model_copy(update={"headline": first_line})
                                auth_store.profiles[user_id] = profile
                                break
                if not profile.headline and profile.preferred_roles:
                    profile = profile.model_copy(update={"headline": profile.preferred_roles[0]})
                    auth_store.profiles[user_id] = profile

        applications = [
            application
            for application in self.list_applications()
            if user_id is None or application.user_id == user_id
        ]
        completed_fields = sum(
            bool(value)
            for value in (profile.headline, profile.location, profile.skills)
        )
        all_open_jobs = [j for j in self.list_jobs() if getattr(j, "status", "open") == "open"]
        if user_id:
            try:
                from app.intelligence import analyze_job

                def job_rank(j: Job) -> tuple[int, float]:
                    try:
                        intel = analyze_job(user_id, j)
                        ts = j.last_seen_at.timestamp() if j.last_seen_at else 0.0
                        return (intel.fit_score, ts)
                    except Exception:
                        return (0, 0.0)

                all_open_jobs.sort(key=job_rank, reverse=True)
            except Exception:
                pass
        else:
            all_open_jobs.sort(
                key=lambda j: j.last_seen_at.timestamp() if j.last_seen_at else 0.0,
                reverse=True,
            )

        return DashboardSummary(
            profile=profile,
            recommended_jobs=all_open_jobs[:10],
            applications=applications[:5],
            profile_completeness=round(completed_fields / 3 * 100),
            jobs_discovered=len(self.list_jobs()),
            active_applications=sum(
                application.status.value not in {"rejected", "offer", "withdrawn"}
                for application in applications
            ),
        )


service = FoundationService(repository)
