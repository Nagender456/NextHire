from __future__ import annotations

import re
from collections.abc import Iterable

from app.auth_store import auth_store
from app.models import (
    Job,
    JobIntelligence,
    LearningOpportunity,
    Project,
)

_ALIASES = {
    "js": "javascript",
    "javascript": "javascript",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "react": "react",
    "py": "python",
    "k8s": "kubernetes",
}
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.-]{1,}", re.I)
_RESOURCES = {
    "kubernetes": ["Kubernetes Basics", "Kubernetes Documentation"],
    "redis": ["Redis University", "Redis Documentation"],
    "python": ["Python Documentation", "Real Python"],
    "javascript": ["MDN JavaScript Guide"],
    "node.js": ["Node.js Learn"],
    "react": ["React Learn"],
}


def normalize_skill(skill: str) -> str:
    cleaned = re.sub(r"\s+", " ", skill.strip().lower())
    return _ALIASES.get(cleaned, cleaned)


def _skills(values: Iterable[str]) -> dict[str, str]:
    return {normalize_skill(value): value for value in values if value.strip()}


def _project_matches(project: dict, required: set[str], preferred: set[str]) -> bool:
    project_terms = {
        normalize_skill(value)
        for key in ("name", "description", "technologies")
        for value in (
            project.get(key, [])
            if isinstance(project.get(key), list)
            else [str(project.get(key, ""))]
        )
        for value in _TOKEN_RE.findall(str(value))
    }
    return bool(project_terms & (required | preferred))


def _learning(skill: str, required: bool) -> LearningOpportunity:
    normalized = normalize_skill(skill)
    return LearningOpportunity(
        skill=skill,
        reason=(
            "This required skill is part of the core job requirements."
            if required
            else "This preferred skill can strengthen your match for the role."
        ),
        resources=_RESOURCES.get(
            normalized, [f"{skill.title()} official documentation"]
        ),
        progression=[
            f"Review {skill} fundamentals",
            f"Build a small {skill} project",
            f"Apply {skill} in a production-style workflow",
        ],
    )


def get_role_domain(title: str) -> str:
    tl = (title or "").lower()
    if re.search(r"\b(marketing|seo|aeo|geo|growth|brand|campaign|content|communications)\b", tl):
        return "marketing"
    if re.search(r"\b(finance|accounting|ar analyst|ap analyst|tax|audit|treasury)\b", tl):
        return "finance"
    if re.search(r"\b(sales|account executive|business development|bdr|sdr|account manager)\b", tl):
        return "sales"
    if re.search(r"\b(recruiter|talent|hr|investigator|abuse investigator|compliance|legal)\b", tl):
        return "operations"
    if re.search(r"\b(software engineer|backend|frontend|full stack|developer|ai engineer|machine learning|data scientist|systems engineer|devops|looker|platform)\b", tl):
        return "engineering"
    return "engineering"


def analyze_job(user_id: str, job: Job) -> JobIntelligence:
    profile = auth_store.get_profile(user_id)
    entities = auth_store.career_entities[user_id]
    user_skills = _skills(profile.skills)
    user_skills.update(
        _skills(
            entity["name"]
            for entity in entities["skills"].values()
            if entity.get("confirmed_by_user", True)
        )
    )
    required = _skills(job.required_skills)
    preferred = _skills(job.preferred_skills)
    matched_required = sorted(set(required) & set(user_skills))
    matched_preferred = sorted(set(preferred) & set(user_skills))
    missing_required = sorted(set(required) - set(user_skills))
    missing_preferred = sorted(set(preferred) - set(user_skills))
    required_score = len(matched_required) / len(required) if required else 1
    preferred_score = len(matched_preferred) / len(preferred) if preferred else 1
    if required and preferred:
        raw_score = (required_score * 0.7 + preferred_score * 0.3) * 100
    elif required:
        raw_score = required_score * 100
    elif preferred:
        raw_score = preferred_score * 100
    else:
        raw_score = 0

    job_domain = get_role_domain(job.title or "")
    # Detect candidate domain
    cand_text = " ".join(user_skills.keys()) + " " + (profile.headline or "").lower()
    cand_is_eng = bool(re.search(r"\b(python|javascript|react|c\+\+|fastapi|docker|sql|engineer|developer|software)\b", cand_text))
    if cand_is_eng and job_domain != "engineering":
        fit_score = min(20, max(8, round(raw_score * 0.15)))
    else:
        fit_score = round(raw_score)

    projects = [
        Project.model_validate(project)
        for project in entities["projects"].values()
        if project.get("confirmed_by_user", True)
        and _project_matches(project, set(required), set(preferred))
    ]
    recommendation = "recommended" if fit_score >= 60 else "lower_match"
    if cand_is_eng and job_domain != "engineering":
        reason = f"{fit_score}% fit: This role is in {job_domain.title()}, which diverges from your engineering background."
    elif missing_required:
        reason = (
            f"{fit_score}% fit with {len(missing_required)} required skill gap"
            f"{'s' if len(missing_required) != 1 else ''}."
        )
    else:
        reason = f"{fit_score}% fit based on required and preferred skill matches."
    evidence = [
        f"Matched required skills: {', '.join(matched_required) or 'none'}",
        f"Matched preferred skills: {', '.join(matched_preferred) or 'none'}",
    ]
    if projects:
        evidence.append(
            f"Relevant projects: {', '.join(project.name for project in projects)}"
        )
    return JobIntelligence(
        job=job,
        fit_score=fit_score,
        recommendation=recommendation,
        recommendation_reason=reason,
        matched_required_skills=[required[skill] for skill in matched_required],
        matched_preferred_skills=[preferred[skill] for skill in matched_preferred],
        missing_required_skills=[required[skill] for skill in missing_required],
        missing_preferred_skills=[preferred[skill] for skill in missing_preferred],
        relevant_projects=projects,
        learning_opportunities=[
            *[_learning(required[skill], True) for skill in missing_required],
            *[_learning(preferred[skill], False) for skill in missing_preferred],
        ],
        evidence=evidence,
        model_version="skills-grounded-v1",
    )
