from collections import Counter

from app.auth_store import auth_store
from app.job_ingestion import ingestion_store
from app.models import AdminOverview, ApplicationStatus, SkillGap, UserAnalytics
from app.services import service


def get_user_analytics(user_id: str) -> UserAnalytics:
    if not auth_store.privacy_settings[user_id].get("analytics_enabled", True):
        return UserAnalytics(
            target_companies=auth_store.get_profile(user_id).target_companies
        )
    profile = auth_store.get_profile(user_id)
    jobs = [job for job in service.list_jobs() if job.status == "open"]
    applications = [
        application
        for application in service.list_applications()
        if application.user_id == user_id
    ]
    from app.intelligence import analyze_job, normalize_skill

    # Collect all user skills from profile, preferred skills, and confirmed CKB skills
    ckb_skills = [
        entity["name"]
        for entity in auth_store.career_entities.get(user_id, {})
        .get("skills", {})
        .values()
        if entity.get("confirmed_by_user", True)
    ]
    raw_user_skills = (
        list(profile.skills) + ckb_skills + list(profile.preferred_skills.keys())
    )
    user_skills_set = {normalize_skill(s) for s in raw_user_skills if s.strip()}

    matching_jobs = 0
    gaps: Counter[str] = Counter()
    for job in jobs:
        intel = analyze_job(user_id, job)
        if intel.fit_score >= 50 or bool(intel.matched_required_skills):
            matching_jobs += 1
        for missing_s in intel.missing_required_skills:
            if normalize_skill(missing_s) not in user_skills_set:
                gaps[missing_s] += 1

    return UserAnalytics(
        jobs_discovered=len(jobs),
        matching_jobs=matching_jobs,
        saved_jobs=sum(item.status == ApplicationStatus.SAVED for item in applications),
        applications=len(applications),
        interviews=sum(
            item.status == ApplicationStatus.INTERVIEW for item in applications
        ),
        offers=sum(item.status == ApplicationStatus.OFFER for item in applications),
        rejected_applications=sum(
            item.status == ApplicationStatus.REJECTED for item in applications
        ),
        skill_gaps=[
            SkillGap(skill=skill, jobs=count) for skill, count in gaps.most_common(10)
        ],
        target_companies=profile.target_companies,
    )


def get_admin_overview() -> AdminOverview:
    crawls = ingestion_store.crawls
    jobs = list(service.list_jobs())
    return AdminOverview(
        users=len(auth_store.users),
        companies=len(ingestion_store.companies),
        active_companies=sum(
            company.active for company in ingestion_store.companies.values()
        ),
        pending_companies=sum(
            company.verification_status == "pending"
            for company in ingestion_store.companies.values()
        ),
        jobs=len(jobs),
        open_jobs=sum(job.status == "open" for job in jobs),
        crawls=len(crawls),
        successful_crawls=sum(crawl.status == "succeeded" for crawl in crawls),
        failed_crawls=sum(crawl.status == "failed" for crawl in crawls),
        recent_crawls=list(reversed(crawls[-10:])),
    )
