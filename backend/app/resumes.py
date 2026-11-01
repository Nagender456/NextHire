from __future__ import annotations

import re
from datetime import UTC, datetime

from app.auth_store import auth_store
from app.intelligence import analyze_job
from app.models import Job, ResumeContent, ResumeItem, ResumeVersion

TEMPLATES = {
    "default": "Clean single-column resume",
    "technical": "Technical skills-forward resume",
}


def validate_template(template: str) -> str:
    if template not in TEMPLATES:
        raise ValueError("RESUME_TEMPLATE_NOT_FOUND")
    return template


def validate_format(content: ResumeContent) -> ResumeContent:
    if not content.summary.strip():
        raise ValueError("RESUME_SUMMARY_REQUIRED")
    if len(content.skills) > 40:
        raise ValueError("RESUME_TOO_MANY_SKILLS")
    return content


def _confirmed_entities(user_id: str, entity_type: str) -> list[dict]:
    return [
        entity
        for entity in auth_store.career_entities[user_id][entity_type].values()
        if entity.get("confirmed_by_user", True)
    ]


def generate_resume(user_id: str, job: Job) -> ResumeContent:
    profile = auth_store.get_profile(user_id)
    intelligence = analyze_job(user_id, job)
    confirmed_skills = {
        entity["name"] for entity in _confirmed_entities(user_id, "skills")
    }
    for s in profile.skills:
        if s.strip():
            confirmed_skills.add(s.strip())

    skills = list(
        dict.fromkeys(
            [
                *intelligence.matched_required_skills,
                *intelligence.matched_preferred_skills,
            ]
            + sorted(confirmed_skills)
        )
    )
    if intelligence.relevant_projects:
        projects = []
        for project in intelligence.relevant_projects:
            tech_str = f" [{', '.join(project.technologies)}]" if getattr(project, "technologies", None) else ""
            desc = f": {project.description}" if project.description else ""
            projects.append(
                ResumeItem(
                    text=f"{project.name}{tech_str}{desc}".strip(": "),
                    source_entity_ids=[project.id],
                )
            )
    else:
        # Fall back to user's confirmed projects from Career Knowledge Base
        projects = []
        for item in _confirmed_entities(user_id, "projects"):
            techs = item.get("technologies") or []
            tech_str = f" [{', '.join(techs)}]" if techs else ""
            desc = f": {item.get('description', '')}" if item.get("description") else ""
            projects.append(
                ResumeItem(
                    text=f"{item.get('name', '')}{tech_str}{desc}".strip(": "),
                    source_entity_ids=[item["id"]],
                )
            )
    experience = [
        ResumeItem(
            text=(
                f"{item.get('title', '')} at {item.get('company', '')}"
                + (f" ({item['dates']})" if item.get("dates") else "")
                + (f": {item['description']}" if item.get("description") else "")
            ).strip(" :"),
            source_entity_ids=[item["id"]],
        )
        for item in _confirmed_entities(user_id, "experience")
    ]
    education = [
        ResumeItem(
            text=(
                f"{item.get('degree', '')}"
                + (f" - {item['field_of_study']}" if item.get("field_of_study") else "")
                + (f" at {item['institution']}" if item.get("institution") else "")
            ).strip(" - at:"),
            source_entity_ids=[item["id"]],
        )
        for item in _confirmed_entities(user_id, "education")
    ]
    certifications = [
        ResumeItem(
            text=(
                f"{item.get('name', '')}"
                + (f" - {item['issuer']}" if item.get("issuer") else "")
                + (f" ({item['issued_date']})" if item.get("issued_date") else "")
            ).strip(" -()"),
            source_entity_ids=[item["id"]],
        )
        for item in _confirmed_entities(user_id, "certifications")
    ]
    summary = profile.headline or f"{profile.display_name} - {job.title}"
    return ResumeContent(
        summary=summary,
        skills=skills,
        experience=experience,
        projects=projects,
        education=education,
        certifications=certifications,
        section_order=[
            "summary",
            "skills",
            "experience",
            "projects",
            "education",
            "certifications",
        ],
    )


def validate_content(user_id: str, content: ResumeContent) -> ResumeContent:
    known_ids = {
        entity["id"]
        for entities in auth_store.career_entities[user_id].values()
        for entity in entities.values()
        if entity.get("confirmed_by_user", True)
    }
    for section in (
        content.experience,
        content.projects,
        content.education,
        content.certifications,
    ):
        for item in section:
            if (
                not item.source_entity_ids
                or not set(item.source_entity_ids) <= known_ids
            ):
                raise ValueError("RESUME_ITEM_REQUIRES_CONFIRMED_SOURCE")
    return content


def render_latex(content: ResumeContent) -> str:
    def escape(value: str) -> str:
        return re.sub(r"([\\{}%&#_$])", r"\\\1", value)

    lines = [
        r"\documentclass[11pt]{article}",
        r"\begin{document}",
    ]
    if content.summary:
        lines.append(f"\\section*{{{escape(content.summary)}}}")

    section_map = {
        "skills": ("Skills", [ResumeItem(text=skill) for skill in content.skills]),
        "experience": ("Experience", content.experience),
        "projects": ("Projects", content.projects),
        "education": ("Education", content.education),
        "certifications": ("Certifications", content.certifications),
    }

    order = [
        s.lower()
        for s in (content.section_order or [])
        if s.lower() in section_map
    ]
    for key in ("skills", "experience", "projects", "education", "certifications"):
        if key not in order:
            order.append(key)

    for key in order:
        title, items = section_map[key]
        if not items:
            continue
        lines.extend([f"\\section*{{{title}}}", r"\begin{itemize}"])
        lines.extend(f"\\item {escape(item.text)}" for item in items)
        lines.append(r"\end{itemize}")
    lines.extend([r"\end{document}", ""])
    return "\n".join(lines)


def create_version(user_id: str, job: Job) -> ResumeVersion:
    content = validate_format(generate_resume(user_id, job))
    now = datetime.now(UTC)
    return ResumeVersion.model_validate(
        auth_store.create_resume_version(
            user_id,
            {
                "job_id": job.id,
                "version": auth_store.next_resume_version(user_id, job.id),
                "status": "draft",
                "template": "default",
                "content": content,
                "created_at": now,
                "updated_at": now,
            },
        )
    )
