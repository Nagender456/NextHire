from __future__ import annotations

import html
import io
import re
from datetime import UTC, datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Table, TableStyle

from app.auth_store import auth_store
from app.intelligence import analyze_job
from app.models import CareerProfile, Job, ResumeContent, ResumeItem, ResumeVersion

TEMPLATES = {
    "jack": "Jack Resume - Industry standard ATS single-column template",
    "default": "Clean single-column resume (Jack Resume style)",
    "technical": "Technical skills-forward resume",
}


def validate_template(template: str) -> str:
    if template in ("jake", "jack"):
        return "jack"
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
    auth_store._ensure_career_entities(user_id)
    return [
        entity
        for entity in auth_store.career_entities[user_id][entity_type].values()
        if entity.get("confirmed_by_user", True)
    ]


def _parse_experience_text(text: str) -> dict[str, str]:
    m = re.match(
        r"^(.*?)\s+at\s+([^(:]+?)(?:\s*\(([^)]+)\))?(?:\s*:\s*(.*))?$", text.strip()
    )
    if m:
        return {
            "title": m.group(1).strip(),
            "company": m.group(2).strip(),
            "dates": (m.group(3) or "").strip(),
            "description": (m.group(4) or "").strip(),
        }
    return {"title": text.strip(), "company": "", "dates": "", "description": ""}


def _parse_education_text(text: str) -> dict[str, str]:
    m = re.match(
        r"^(.*?)\s+at\s+([^(:]+?)(?:\s*\(([^)]+)\))?(?:\s*:\s*(.*))?$", text.strip()
    )
    if m:
        return {
            "degree": m.group(1).strip(),
            "institution": m.group(2).strip(),
            "dates": (m.group(3) or "").strip(),
            "description": (m.group(4) or "").strip(),
        }
    return {"degree": text.strip(), "institution": "", "dates": "", "description": ""}


def _parse_project_text(text: str) -> dict[str, str]:
    m = re.match(r"^(.*?)(?:\s*\[(.*?)\])?(?:\s*:\s*(.*))?$", text.strip())
    if m:
        return {
            "name": m.group(1).strip(),
            "tech": (m.group(2) or "").strip(),
            "dates": "",
            "description": (m.group(3) or "").strip(),
        }
    return {"name": text.strip(), "tech": "", "dates": "", "description": ""}


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
            tech_str = (
                f" [{', '.join(project.technologies)}]"
                if getattr(project, "technologies", None)
                else ""
            )
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
            desc = (
                f": {item.get('description', '')}" if item.get("description") else ""
            )
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
    auth_store._ensure_career_entities(user_id)
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


def render_latex(
    content: ResumeContent,
    profile: CareerProfile | None = None,
    template: str = "jack",
) -> str:
    def escape(value: str) -> str:
        return re.sub(r"([\\{}%&#_$])", r"\\\1", str(value or ""))

    lines = [
        r"\documentclass[letterpaper,11pt]{article}",
        "",
        r"\usepackage{latexsym}",
        r"\usepackage[empty]{fullpage}",
        r"\usepackage{titlesec}",
        r"\usepackage{marvosym}",
        r"\usepackage[usenames,dvipsnames]{color}",
        r"\usepackage{verbatim}",
        r"\usepackage{enumitem}",
        r"\usepackage[hidelinks]{hyperref}",
        r"\usepackage{fancyhdr}",
        r"\usepackage[english]{babel}",
        r"\usepackage{tabularx}",
        "",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        r"\fancyfoot{}",
        r"\renewcommand{\headrulewidth}{0pt}",
        r"\renewcommand{\footrulewidth}{0pt}",
        "",
        r"\addtolength{\oddsidemargin}{-0.5in}",
        r"\addtolength{\evensidemargin}{-0.5in}",
        r"\addtolength{\textwidth}{1in}",
        r"\addtolength{\topmargin}{-.5in}",
        r"\addtolength{\textheight}{1.0in}",
        "",
        r"\urlstyle{same}",
        r"\raggedbottom",
        r"\raggedright",
        r"\setlength{\tabcolsep}{0in}",
        "",
        r"\titleformat{\section}{",
        r"  \vspace{-4pt}\scshape\raggedright\large",
        r"}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]",
        "",
        r"\newcommand{\resumeItem}[1]{",
        r"  \item\small{",
        r"    {#1 \vspace{-2pt}}",
        r"  }",
        r"}",
        "",
        r"\newcommand{\resumeSubheading}[4]{",
        r"  \vspace{-2pt}\item",
        r"    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}",
        r"      \textbf{#1} & #2 \\",
        r"      \textit{\small#3} & \textit{\small #4} \\",
        r"    \end{tabular*}\vspace{-7pt}",
        r"}",
        "",
        r"\newcommand{\resumeProjectHeading}[2]{",
        r"    \item",
        r"    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}",
        r"      \small#1 & #2 \\",
        r"    \end{tabular*}\vspace{-7pt}",
        r"}",
        "",
        r"\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}",
        r"\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}",
        r"\newcommand{\resumeItemListStart}{\begin{itemize}}",
        r"\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}",
        "",
        r"\begin{document}",
    ]

    candidate_name = ""
    if profile and profile.display_name:
        candidate_name = profile.display_name
    elif content.summary and len(content.summary.split()) <= 4:
        candidate_name = content.summary
    else:
        candidate_name = "Candidate Resume"

    contact_parts = []
    if profile:
        if profile.location:
            contact_parts.append(escape(profile.location))
        if profile.email:
            contact_parts.append(
                r"\href{mailto:"
                + escape(profile.email)
                + r"}{\underline{"
                + escape(profile.email)
                + r"}}"
            )
    if not contact_parts:
        contact_parts.append(escape("Remote"))

    contact_line = " $|$ ".join(contact_parts)
    lines.extend([
        r"\begin{center}",
        f"    \\textbf{{\\Huge \\scshape {escape(candidate_name)}}} \\\\ \\vspace{{1pt}}",
        f"    \\small {contact_line}",
        r"\end{center}",
    ])

    if content.summary:
        lines.extend([
            r"\section{Summary}",
            r"\small{",
            f"  {escape(content.summary)}",
            r"}",
        ])

    section_map = {
        "education": "Education",
        "experience": "Experience",
        "projects": "Projects",
        "skills": "Technical Skills",
        "certifications": "Certifications",
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
        if key == "skills":
            if not content.skills:
                continue
            lines.extend([
                r"\section{Technical Skills}",
                r"\begin{itemize}[leftmargin=0.15in, label={}]",
                r"  \small{\item{",
                f"    \\textbf{{Skills}}{{: {escape(', '.join(content.skills))}}}",
                r"  }}",
                r"\end{itemize}",
            ])
        elif key == "experience":
            if not content.experience:
                continue
            lines.extend([
                r"\section{Experience}",
                r"\resumeSubHeadingListStart",
            ])
            for item in content.experience:
                p = _parse_experience_text(item.text)
                if p["company"]:
                    lines.extend([
                        r"  \resumeSubheading",
                        f"    {{{escape(p['title'])}}}{{{escape(p['dates'])}}}",
                        f"    {{{escape(p['company'])}}}{{}}",
                    ])
                    if p["description"]:
                        lines.extend([
                            r"    \resumeItemListStart",
                            f"      \\resumeItem{{{escape(p['description'])}}}",
                            r"    \resumeItemListEnd",
                        ])
                else:
                    lines.extend([
                        r"  \resumeItemListStart",
                        f"    \\resumeItem{{{escape(item.text)}}}",
                        r"  \resumeItemListEnd",
                    ])
            lines.append(r"\resumeSubHeadingListEnd")
        elif key == "projects":
            if not content.projects:
                continue
            lines.extend([
                r"\section{Projects}",
                r"\resumeSubHeadingListStart",
            ])
            for item in content.projects:
                p = _parse_project_text(item.text)
                tech_str = f" $|$ \\emph{{{escape(p['tech'])}}}" if p["tech"] else ""
                lines.extend([
                    r"  \resumeProjectHeading",
                    f"    {{\\textbf{{{escape(p['name'])}}}{tech_str}}}{{{escape(p['dates'])}}}",
                ])
                if p["description"]:
                    lines.extend([
                        r"    \resumeItemListStart",
                        f"      \\resumeItem{{{escape(p['description'])}}}",
                        r"    \resumeItemListEnd",
                    ])
            lines.append(r"\resumeSubHeadingListEnd")
        elif key == "education":
            if not content.education:
                continue
            lines.extend([
                r"\section{Education}",
                r"\resumeSubHeadingListStart",
            ])
            for item in content.education:
                p = _parse_education_text(item.text)
                if p["institution"]:
                    lines.extend([
                        r"  \resumeSubheading",
                        f"    {{{escape(p['institution'])}}}{{{escape(p['dates'])}}}",
                        f"    {{{escape(p['degree'])}}}{{}}",
                    ])
                    if p["description"]:
                        lines.extend([
                            r"    \resumeItemListStart",
                            f"      \\resumeItem{{{escape(p['description'])}}}",
                            r"    \resumeItemListEnd",
                        ])
                else:
                    lines.extend([
                        r"  \resumeItemListStart",
                        f"    \\resumeItem{{{escape(item.text)}}}",
                        r"  \resumeItemListEnd",
                    ])
            lines.append(r"\resumeSubHeadingListEnd")
        elif key == "certifications":
            if not content.certifications:
                continue
            lines.extend([
                r"\section{Certifications}",
                r"\resumeSubHeadingListStart",
            ])
            for item in content.certifications:
                lines.extend([
                    r"  \resumeItemListStart",
                    f"    \\resumeItem{{{escape(item.text)}}}",
                    r"  \resumeItemListEnd",
                ])
            lines.append(r"\resumeSubHeadingListEnd")

    lines.extend([r"\end{document}", ""])
    return "\n".join(lines)


def render_pdf(
    content: ResumeContent,
    profile: CareerProfile | None = None,
    template: str = "jack",
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "JackPdfName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
        spaceAfter=2,
    )
    contact_style = ParagraphStyle(
        "JackPdfContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=8,
    )
    section_title_style = ParagraphStyle(
        "JackPdfSectionTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#111827"),
        spaceBefore=6,
        spaceAfter=1,
    )
    sub_left_style = ParagraphStyle(
        "JackPdfSubLeft",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#111827"),
    )
    sub_right_style = ParagraphStyle(
        "JackPdfSubRight",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#4b5563"),
    )
    bullet_style = ParagraphStyle(
        "JackPdfBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        leftIndent=12,
        firstLineIndent=-8,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "JackPdfBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=2,
    )

    def esc(text: str) -> str:
        return html.escape(str(text or ""))

    story = []

    candidate_name = ""
    if profile and profile.display_name:
        candidate_name = profile.display_name
    elif content.summary and len(content.summary.split()) <= 4:
        candidate_name = content.summary
    else:
        candidate_name = "Candidate Resume"

    story.append(Paragraph(f"<b>{esc(candidate_name)}</b>", name_style))

    contact_parts = []
    if profile:
        if profile.location:
            contact_parts.append(profile.location)
        if profile.email:
            contact_parts.append(profile.email)
    if not contact_parts:
        contact_parts.append("Remote")

    contact_html = " &nbsp;|&nbsp; ".join(esc(p) for p in contact_parts)
    story.append(Paragraph(contact_html, contact_style))

    if content.summary:
        story.append(Paragraph("SUMMARY", section_title_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.8,
                color=colors.HexColor("#374151"),
                spaceBefore=1,
                spaceAfter=4,
            )
        )
        story.append(Paragraph(esc(content.summary), body_style))

    order = [
        s.lower()
        for s in (content.section_order or [])
        if s.lower()
        in ("skills", "experience", "projects", "education", "certifications")
    ]
    for key in ("skills", "experience", "projects", "education", "certifications"):
        if key not in order:
            order.append(key)

    col1 = 410
    col2 = 130

    for key in order:
        if key == "skills":
            if not content.skills:
                continue
            story.append(Paragraph("TECHNICAL SKILLS", section_title_style))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.8,
                    color=colors.HexColor("#374151"),
                    spaceBefore=1,
                    spaceAfter=4,
                )
            )
            skills_text = f"<b>Skills:</b> {esc(', '.join(content.skills))}"
            story.append(Paragraph(skills_text, body_style))

        elif key == "experience":
            if not content.experience:
                continue
            story.append(Paragraph("EXPERIENCE", section_title_style))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.8,
                    color=colors.HexColor("#374151"),
                    spaceBefore=1,
                    spaceAfter=4,
                )
            )
            for item in content.experience:
                p = _parse_experience_text(item.text)
                if p["company"]:
                    left_html = f"<b>{esc(p['title'])}</b> — {esc(p['company'])}"
                    right_html = esc(p["dates"])
                    t = Table(
                        [[
                            Paragraph(left_html, sub_left_style),
                            Paragraph(right_html, sub_right_style),
                        ]],
                        colWidths=[col1, col2],
                    )
                    t.setStyle(
                        TableStyle([
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                            ("TOPPADDING", (0, 0), (-1, -1), 1),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ])
                    )
                    story.append(t)
                    if p["description"]:
                        story.append(
                            Paragraph(
                                f"&bull;&nbsp;&nbsp;{esc(p['description'])}",
                                bullet_style,
                            )
                        )
                else:
                    story.append(
                        Paragraph(f"&bull;&nbsp;&nbsp;{esc(item.text)}", bullet_style)
                    )

        elif key == "projects":
            if not content.projects:
                continue
            story.append(Paragraph("PROJECTS", section_title_style))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.8,
                    color=colors.HexColor("#374151"),
                    spaceBefore=1,
                    spaceAfter=4,
                )
            )
            for item in content.projects:
                p = _parse_project_text(item.text)
                tech_span = f" | <i>{esc(p['tech'])}</i>" if p["tech"] else ""
                left_html = f"<b>{esc(p['name'])}</b>{tech_span}"
                right_html = esc(p["dates"])
                t = Table(
                    [[
                        Paragraph(left_html, sub_left_style),
                        Paragraph(right_html, sub_right_style),
                    ]],
                    colWidths=[col1, col2],
                )
                t.setStyle(
                    TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                        ("TOPPADDING", (0, 0), (-1, -1), 1),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ])
                )
                story.append(t)
                if p["description"]:
                    story.append(
                        Paragraph(
                            f"&bull;&nbsp;&nbsp;{esc(p['description'])}",
                            bullet_style,
                        )
                    )

        elif key == "education":
            if not content.education:
                continue
            story.append(Paragraph("EDUCATION", section_title_style))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.8,
                    color=colors.HexColor("#374151"),
                    spaceBefore=1,
                    spaceAfter=4,
                )
            )
            for item in content.education:
                p = _parse_education_text(item.text)
                if p["institution"]:
                    left_html = f"<b>{esc(p['institution'])}</b> — {esc(p['degree'])}"
                    right_html = esc(p["dates"])
                    t = Table(
                        [[
                            Paragraph(left_html, sub_left_style),
                            Paragraph(right_html, sub_right_style),
                        ]],
                        colWidths=[col1, col2],
                    )
                    t.setStyle(
                        TableStyle([
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                            ("TOPPADDING", (0, 0), (-1, -1), 1),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ])
                    )
                    story.append(t)
                    if p["description"]:
                        story.append(
                            Paragraph(
                                f"&bull;&nbsp;&nbsp;{esc(p['description'])}",
                                bullet_style,
                            )
                        )
                else:
                    story.append(
                        Paragraph(f"&bull;&nbsp;&nbsp;{esc(item.text)}", bullet_style)
                    )

        elif key == "certifications":
            if not content.certifications:
                continue
            story.append(Paragraph("CERTIFICATIONS", section_title_style))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.8,
                    color=colors.HexColor("#374151"),
                    spaceBefore=1,
                    spaceAfter=4,
                )
            )
            for item in content.certifications:
                story.append(
                    Paragraph(f"&bull;&nbsp;&nbsp;{esc(item.text)}", bullet_style)
                )

    doc.build(story)
    return buffer.getvalue()


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
                "template": "jack",
                "content": content,
                "created_at": now,
                "updated_at": now,
            },
        )
    )
