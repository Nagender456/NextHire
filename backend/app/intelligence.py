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


_JUNK_SKILLS = {"iii", "ii", "iv", "v", "vi", "software", "engineer", "developer", "role", "job", "position", "full-time", "part-time", "intern"}


def is_valid_skill(skill: str) -> bool:
    clean = re.sub(r"[\s\-_]+", " ", str(skill or "").strip().lower())
    return bool(clean) and clean not in _JUNK_SKILLS and len(clean) >= 2


def flatten_candidate_skills(skills: Iterable[str]) -> set[str]:
    result: set[str] = set()
    compound_map = {
        "mern stack": ["mern stack", "react", "node.js", "mongodb", "express", "stack"],
        "mean stack": ["mean stack", "angular", "node.js", "mongodb", "express", "stack"],
        "full stack": ["full stack", "fullstack", "stack"],
        "fullstack": ["full stack", "fullstack", "stack"],
        "c/c++": ["c++", "c"],
        "html/css": ["html", "css"],
        "artificial intelligence": ["ai", "machine learning"],
        "machine learning": ["ml", "machine learning"],
    }
    for raw in skills:
        if not raw or not isinstance(raw, str):
            continue
        clean = raw.strip()
        if not clean:
            continue
        norm = normalize_skill(clean)
        result.add(norm)
        # Category prefix: "Languages: C/C++" -> "C/C++"
        if ":" in clean:
            val = normalize_skill(clean.split(":", 1)[1])
            if val:
                result.add(val)
        # Slash splitting: "C/C++" -> "C", "C++"
        if "/" in clean:
            for part in clean.split("/"):
                p_norm = normalize_skill(part)
                if p_norm:
                    result.add(p_norm)
        # Compound expansion
        lower_raw = clean.lower()
        for key, aliases in compound_map.items():
            if key in lower_raw:
                for alias in aliases:
                    result.add(normalize_skill(alias))
    return result


def _matches_skill(target_skill: str, candidate_skills: set[str]) -> bool:
    if not target_skill:
        return False
    target = normalize_skill(target_skill)
    if not target:
        return False
    if target in candidate_skills:
        return True

    is_short = len(target) <= 3
    for cand in candidate_skills:
        if cand == target:
            return True
        # Direct acronym check
        if (target == "ai" and "artificial intelligence" in cand) or (cand == "ai" and "artificial intelligence" in target):
            return True
        if (target == "ml" and "machine learning" in cand) or (cand == "ml" and "machine learning" in target):
            return True

        if is_short:
            if re.search(r"(^|[^a-z0-9+#])" + re.escape(target) + r"($|[^a-z0-9+#])", cand, re.I):
                return True
        else:
            if re.search(r"\b" + re.escape(target) + r"\b", cand, re.I):
                return True
            if len(cand) >= 4 and re.search(r"\b" + re.escape(cand) + r"\b", target, re.I):
                return True
    return False


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
    
    raw_user_skills = list(profile.skills)
    raw_user_skills.extend(
        entity["name"]
        for entity in entities["skills"].values()
        if entity.get("confirmed_by_user", True)
    )
    candidate_skills = flatten_candidate_skills(raw_user_skills)

    # Filter out junk tokens while preserving original casing
    req_skills = [s for s in job.required_skills if is_valid_skill(s)]
    pref_skills = [s for s in job.preferred_skills if is_valid_skill(s)]

    if not candidate_skills:
        return JobIntelligence(
            job=job,
            fit_score=0,
            recommendation="lower_match",
            recommendation_reason="0% fit: Add your skills in the Career Knowledge Base to see your match score.",
            evidence=["No skills configured on profile"],
            matched_required_skills=[],
            matched_preferred_skills=[],
            missing_required_skills=sorted(req_skills),
            missing_preferred_skills=sorted(pref_skills),
            relevant_projects=[],
            learning_opportunities=[_learning(s, True) for s in sorted(req_skills)[:3]],
        )

    matched_required = [s for s in req_skills if _matches_skill(s, candidate_skills)]
    matched_preferred = [s for s in pref_skills if _matches_skill(s, candidate_skills)]
    missing_required = [s for s in req_skills if s not in matched_required]
    missing_preferred = [s for s in pref_skills if s not in matched_preferred]

    required_score = len(matched_required) / len(req_skills) if req_skills else 0
    preferred_score = len(matched_preferred) / len(pref_skills) if pref_skills else 0

    if req_skills and pref_skills:
        raw_score = (required_score * 0.7 + preferred_score * 0.3) * 100
    elif req_skills:
        raw_score = required_score * 100
    elif pref_skills:
        raw_score = preferred_score * 100
    else:
        raw_score = 0

    job_domain = get_role_domain(job.title or "")
    # Detect candidate domain
    cand_text = " ".join(candidate_skills) + " " + (profile.headline or "").lower()
    cand_is_eng = bool(re.search(r"\b(python|javascript|react|c\+\+|fastapi|docker|sql|engineer|developer|software)\b", cand_text))
    if cand_is_eng and job_domain != "engineering":
        fit_score = min(20, max(8, round(raw_score * 0.15)))
    else:
        fit_score = round(raw_score)

    projects = []
    req_norm_set = {normalize_skill(s) for s in req_skills}
    pref_norm_set = {normalize_skill(s) for s in pref_skills}
    for project in entities.get("projects", {}).values():
        if project.get("confirmed_by_user", True):
            p_dict = dict(project) if isinstance(project, dict) else project.model_dump()
            if not p_dict.get("url"):
                p_dict["url"] = None
            if _project_matches(p_dict, req_norm_set, pref_norm_set):
                try:
                    p_obj = Project.model_validate(p_dict)
                    projects.append(p_obj)
                except Exception:
                    pass
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
        matched_required_skills=matched_required,
        matched_preferred_skills=matched_preferred,
        missing_required_skills=missing_required,
        missing_preferred_skills=missing_preferred,
        relevant_projects=projects,
        learning_opportunities=[
            *[_learning(s, True) for s in missing_required],
            *[_learning(s, False) for s in missing_preferred],
        ],
        evidence=evidence,
        model_version="skills-grounded-v1",
    )
