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
    "ts": "typescript",
    "typescript": "typescript",
    "py": "python",
    "python": "python",
    "python3": "python",
    "golang": "go",
    "go": "go",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "react native": "react native",
    "next": "next.js",
    "nextjs": "next.js",
    "next.js": "next.js",
    "vue": "vue",
    "vuejs": "vue",
    "vue.js": "vue",
    "angular": "angular",
    "angularjs": "angular",
    "express": "express",
    "expressjs": "express",
    "express.js": "express",
    "fastapi": "fastapi",
    "django": "django",
    "flask": "flask",
    "spring": "spring boot",
    "springboot": "spring boot",
    "spring boot": "spring boot",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "psql": "postgresql",
    "mysql": "mysql",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "redis": "redis",
    "sqlite": "sqlite",
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "google cloud",
    "google cloud": "google cloud",
    "azure": "azure",
    "microsoft azure": "azure",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "docker": "docker",
    "containerization": "docker",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    "github actions": "github actions",
    "gitlab ci": "gitlab ci",
    "rest": "rest apis",
    "restful": "rest apis",
    "rest api": "rest apis",
    "rest apis": "rest apis",
    "graphql": "graphql",
    "tailwind": "tailwind css",
    "tailwindcss": "tailwind css",
    "tailwind css": "tailwind css",
    "css": "css",
    "css3": "css",
    "html": "html",
    "html5": "html",
    "ml": "machine learning",
    "machine learning": "machine learning",
    "deep learning": "deep learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "llm": "large language models",
    "llms": "large language models",
    "large language models": "large language models",
    "c++": "c++",
    "cpp": "c++",
    "c#": "c#",
    "csharp": "c#",
    ".net": ".net",
    "dotnet": ".net",
    "microservices": "microservices",
    "system design": "system design",
    "data structures": "data structures",
    "algorithms": "algorithms",
    "sql": "sql",
}
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.-]{1,}", re.I)
_RESOURCES = {
    "kubernetes": ["Kubernetes Basics", "Kubernetes Documentation"],
    "redis": ["Redis University", "Redis Documentation"],
    "python": ["Python Documentation", "Real Python"],
    "javascript": ["MDN JavaScript Guide"],
    "node.js": ["Node.js Learn"],
    "react": ["React Learn"],
    "docker": ["Docker Official Docs"],
    "aws": ["AWS Skill Builder"],
    "postgresql": ["PostgreSQL Tutorial"],
    "fastapi": ["FastAPI Tutorial - User Guide"],
    "go": ["A Tour of Go"],
}


def normalize_skill(skill: str) -> str:
    cleaned = re.sub(r"[\s\-_]+", " ", skill.strip().lower()).strip(".#*•- ")
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
    auth_store._ensure_career_entities(user_id)
    entities = auth_store.career_entities[user_id]
    user_skills = _skills(profile.skills)
    user_skills.update(
        _skills(
            entity["name"]
            for entity in entities["skills"].values()
            if entity.get("confirmed_by_user", True)
        )
    )
    if not user_skills:
        required = _skills(job.required_skills)
        preferred = _skills(job.preferred_skills)
        return JobIntelligence(
            job=job,
            fit_score=0,
            recommendation="lower_match",
            recommendation_reason="0% fit: Add your skills in the Career Knowledge Base to see your match score.",
            evidence=["No skills configured on profile"],
            matched_required_skills=[],
            matched_preferred_skills=[],
            missing_required_skills=sorted(required.values()),
            missing_preferred_skills=sorted(preferred.values()),
            relevant_projects=[],
            learning_opportunities=[_learning(s, True) for s in sorted(required.values())[:3]],
        )
    required = _skills(job.required_skills)
    preferred = _skills(job.preferred_skills)
    matched_required = sorted(set(required) & set(user_skills))
    matched_preferred = sorted(set(preferred) & set(user_skills))
    missing_required = sorted(set(required) - set(user_skills))
    missing_preferred = sorted(set(preferred) - set(user_skills))
    required_score = len(matched_required) / len(required) if required else 0
    preferred_score = len(matched_preferred) / len(preferred) if preferred else 0
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
