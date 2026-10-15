"""
Resume Builder PDF Generation Service for GOAT AI.
Uses ReportLab to dynamically construct clean, ATS-friendly resumes
in multiple professional styles (Modern Minimalist and Classic ATS).
"""

import io
from typing import Dict, Any, List, Union
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def safe_text(val: Any) -> str:
    """
    Safely escape XML characters (&, <, >) to avoid ReportLab parsing crashes
    while preserving non-empty clean string representations.
    """
    if val is None:
        return ""
    text = str(val).strip()
    return escape(text)


def _parse_bullet_list(bullets: Union[List[str], str, None]) -> List[str]:
    """Parse list or newline/bullet-delimited string into clean list of strings."""
    if not bullets:
        return []
    if isinstance(bullets, list):
        return [str(b).strip() for b in bullets if str(b).strip()]
    if isinstance(bullets, str):
        lines = []
        for line in bullets.split("\n"):
            line = line.strip()
            # Strip leading bullet symbols if present in raw text
            if line.startswith(("-", "*", "•", "–")):
                line = line[1:].strip()
            if line:
                lines.append(line)
        return lines
    return []


def generate_resume_pdf(resume_data: Dict[str, Any], template_style: str = "modern") -> io.BytesIO:
    """
    Generate an in-memory PDF resume from structured resume data.
    
    Supported template styles:
      - 'modern': Modern Minimalist layout with contemporary typography and subtle indigo accents.
      - 'classic': Classic ATS layout with traditional monochrome styling and clear single-column flow.
    """
    buffer = io.BytesIO()
    
    # 0.5-inch margins (36 pt) for optimal ATS page utilization
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    style_name = str(template_style).lower().strip()
    if "classic" in style_name:
        story = _build_classic_ats_story(resume_data)
    else:
        story = _build_modern_minimalist_story(resume_data)

    doc.build(story)
    buffer.seek(0)
    return buffer


def _build_modern_minimalist_story(data: Dict[str, Any]) -> List[Any]:
    """Modern Minimalist ATS-optimized resume layout."""
    styles = getSampleStyleSheet()
    story: List[Any] = []

    # Typography & Colors
    primary_color = colors.HexColor("#0f172a")  # Deep Slate / Black
    accent_color = colors.HexColor("#4f46e5")   # Indigo Accent
    subtext_color = colors.HexColor("#475569")  # Slate Gray
    border_color = colors.HexColor("#e2e8f0")   # Light Divider

    name_style = ParagraphStyle(
        'ModName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=0  # Left aligned
    )
    title_style = ParagraphStyle(
        'ModTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=accent_color,
        spaceBefore=2,
        spaceAfter=4
    )
    contact_style = ParagraphStyle(
        'ModContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=subtext_color
    )
    section_h_style = ParagraphStyle(
        'ModSecHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=3,
        keepWithNext=True
    )
    item_title_style = ParagraphStyle(
        'ModItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=primary_color
    )
    item_sub_style = ParagraphStyle(
        'ModItemSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=subtext_color
    )
    item_date_style = ParagraphStyle(
        'ModItemDate',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=subtext_color,
        alignment=2  # Right-aligned
    )
    body_style = ParagraphStyle(
        'ModBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1e293b")
    )
    bullet_style = ParagraphStyle(
        'ModBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=12,
        firstLineIndent=-12,
        spaceAfter=2
    )

    # 1. Header (Name & Contact)
    full_name = safe_text(data.get("full_name") or "Your Name")
    headline = safe_text(data.get("headline") or "")
    story.append(Paragraph(full_name, name_style))
    if headline:
        story.append(Paragraph(headline, title_style))

    contact = data.get("contact", {})
    contact_parts = []
    if contact.get("email"):
        contact_parts.append(safe_text(contact["email"]))
    if contact.get("phone"):
        contact_parts.append(safe_text(contact["phone"]))
    if contact.get("location"):
        contact_parts.append(safe_text(contact["location"]))
    if contact.get("linkedin"):
        contact_parts.append(safe_text(contact["linkedin"]))
    if contact.get("github"):
        contact_parts.append(safe_text(contact["github"]))
    if contact.get("portfolio"):
        contact_parts.append(safe_text(contact["portfolio"]))

    if contact_parts:
        story.append(Paragraph(" &bull; ".join(contact_parts), contact_style))

    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.2, color=accent_color, spaceAfter=6, spaceBefore=4))

    # 2. Professional Summary
    summary = safe_text(data.get("summary") or "")
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4, spaceBefore=1))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 4))

    # 3. Technical Skills
    skills = data.get("skills")
    if skills:
        story.append(Paragraph("TECHNICAL SKILLS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4, spaceBefore=1))
        
        if isinstance(skills, dict):
            for cat_name, cat_val in skills.items():
                if cat_val:
                    c_title = safe_text(cat_name).replace("_", " ").title()
                    c_skills = safe_text(cat_val)
                    story.append(Paragraph(f"<b>{c_title}:</b> {c_skills}", body_style))
                    story.append(Spacer(1, 1.5))
        elif isinstance(skills, list):
            skill_text = ", ".join(safe_text(s) for s in skills if s)
            if skill_text:
                story.append(Paragraph(skill_text, body_style))
        elif isinstance(skills, str) and skills.strip():
            story.append(Paragraph(safe_text(skills), body_style))
        story.append(Spacer(1, 4))

    # 4. Work Experience & Internships
    experience = data.get("experience", [])
    if experience:
        story.append(Paragraph("EXPERIENCE & INTERNSHIPS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4, spaceBefore=1))

        for exp in experience:
            role = safe_text(exp.get("role") or "")
            company = safe_text(exp.get("company") or "")
            location = safe_text(exp.get("location") or "")
            start_date = safe_text(exp.get("start_date") or "")
            end_date = safe_text(exp.get("end_date") or ("Present" if exp.get("current") else ""))
            
            date_range = ""
            if start_date and end_date:
                date_range = f"{start_date} – {end_date}"
            elif start_date:
                date_range = start_date

            # Top line: Role + Company on left, Date on right
            left_p = Paragraph(f"<b>{role}</b>{f' &mdash; {company}' if company else ''}", item_title_style)
            right_p = Paragraph(date_range, item_date_style)
            tbl = Table([[left_p, right_p]], colWidths=[380, 160])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(tbl)

            if location:
                story.append(Paragraph(location, item_sub_style))

            story.append(Spacer(1, 2))

            bullets = _parse_bullet_list(exp.get("bullets"))
            for b in bullets:
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_text(b)}", bullet_style))
            story.append(Spacer(1, 4))

    # 5. Projects
    projects = data.get("projects", [])
    if projects:
        story.append(Paragraph("KEY PROJECTS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4, spaceBefore=1))

        for proj in projects:
            title = safe_text(proj.get("title") or "")
            tech = safe_text(proj.get("technologies") or "")
            link = safe_text(proj.get("link") or "")
            
            title_text = f"<b>{title}</b>"
            if tech:
                title_text += f" <font color='#64748b'>| {tech}</font>"

            left_p = Paragraph(title_text, item_title_style)
            right_p = Paragraph(link, item_date_style) if link else Paragraph("", item_date_style)
            tbl = Table([[left_p, right_p]], colWidths=[380, 160])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(tbl)

            story.append(Spacer(1, 2))
            bullets = _parse_bullet_list(proj.get("bullets"))
            for b in bullets:
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_text(b)}", bullet_style))
            story.append(Spacer(1, 4))

    # 6. Education
    education = data.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4, spaceBefore=1))

        for edu in education:
            degree = safe_text(edu.get("degree") or "")
            school = safe_text(edu.get("school") or "")
            grad_year = safe_text(edu.get("graduation_year") or edu.get("dates") or "")
            location = safe_text(edu.get("location") or "")
            gpa = safe_text(edu.get("gpa") or "")
            honors = safe_text(edu.get("honors") or "")

            left_content = f"<b>{degree}</b>"
            if school:
                left_content += f" &mdash; {school}"
            if location:
                left_content += f" <font color='#64748b'>({location})</font>"

            left_p = Paragraph(left_content, item_title_style)
            right_p = Paragraph(grad_year, item_date_style)
            tbl = Table([[left_p, right_p]], colWidths=[420, 120])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(tbl)

            notes = []
            if gpa:
                notes.append(f"GPA: {gpa}")
            if honors:
                notes.append(honors)
            if notes:
                story.append(Paragraph(", ".join(notes), item_sub_style))

            story.append(Spacer(1, 4))

    # 7. Certifications
    certifications = data.get("certifications", [])
    if certifications:
        story.append(Paragraph("CERTIFICATIONS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4, spaceBefore=1))

        for cert in certifications:
            if isinstance(cert, str):
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_text(cert)}", bullet_style))
            elif isinstance(cert, dict):
                c_name = safe_text(cert.get("name") or "")
                c_issuer = safe_text(cert.get("issuer") or "")
                c_date = safe_text(cert.get("date") or "")
                c_id = safe_text(cert.get("credential_id") or "")

                line = f"<b>{c_name}</b>"
                if c_issuer:
                    line += f" &mdash; {c_issuer}"
                if c_id:
                    line += f" <font color='#64748b'>(ID: {c_id})</font>"
                
                left_p = Paragraph(f"&bull;&nbsp;&nbsp;{line}", bullet_style)
                right_p = Paragraph(c_date, item_date_style)
                tbl = Table([[left_p, right_p]], colWidths=[420, 120])
                tbl.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0.5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
                ]))
                story.append(tbl)
        story.append(Spacer(1, 4))

    # 8. Achievements
    achievements = _parse_bullet_list(data.get("achievements"))
    if achievements:
        story.append(Paragraph("HONORS & ACHIEVEMENTS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4, spaceBefore=1))
        for ach in achievements:
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_text(ach)}", bullet_style))
        story.append(Spacer(1, 4))

    # 9. Languages
    languages = data.get("languages", [])
    if languages:
        story.append(Paragraph("LANGUAGES", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4, spaceBefore=1))
        
        lang_strs = []
        for l in languages:
            if isinstance(l, dict):
                n = safe_text(l.get("name") or "")
                p = safe_text(l.get("proficiency") or "")
                if n and p:
                    lang_strs.append(f"{n} ({p})")
                elif n:
                    lang_strs.append(n)
            elif isinstance(l, str) and l.strip():
                lang_strs.append(safe_text(l))
        if lang_strs:
            story.append(Paragraph(", ".join(lang_strs), body_style))

    return story


def _build_classic_ats_story(data: Dict[str, Any]) -> List[Any]:
    """Classic ATS layout with serif typography and clean traditional sections."""
    styles = getSampleStyleSheet()
    story: List[Any] = []

    # Typography & Colors (Monochrome / Times-Roman)
    black_color = colors.HexColor("#000000")
    dark_gray = colors.HexColor("#222222")

    name_style = ParagraphStyle(
        'ClassicName',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=20,
        leading=24,
        textColor=black_color,
        alignment=1  # Centered
    )
    contact_style = ParagraphStyle(
        'ClassicContact',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13,
        textColor=dark_gray,
        alignment=1,  # Centered
        spaceBefore=3,
        spaceAfter=4
    )
    section_h_style = ParagraphStyle(
        'ClassicSecHead',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=11,
        leading=14,
        textColor=black_color,
        spaceBefore=9,
        spaceAfter=2,
        keepWithNext=True
    )
    item_title_style = ParagraphStyle(
        'ClassicItemTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10,
        leading=13,
        textColor=black_color
    )
    item_sub_style = ParagraphStyle(
        'ClassicItemSub',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=9.5,
        leading=13,
        textColor=dark_gray
    )
    item_date_style = ParagraphStyle(
        'ClassicItemDate',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13,
        textColor=black_color,
        alignment=2  # Right aligned
    )
    body_style = ParagraphStyle(
        'ClassicBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13.5,
        textColor=black_color
    )
    bullet_style = ParagraphStyle(
        'ClassicBullet',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13,
        textColor=black_color,
        leftIndent=14,
        firstLineIndent=-14,
        spaceAfter=2
    )

    # 1. Header (Centered Name & Contact)
    full_name = safe_text(data.get("full_name") or "Your Name").upper()
    story.append(Paragraph(full_name, name_style))

    contact = data.get("contact", {})
    contact_parts = []
    if contact.get("email"):
        contact_parts.append(safe_text(contact["email"]))
    if contact.get("phone"):
        contact_parts.append(safe_text(contact["phone"]))
    if contact.get("location"):
        contact_parts.append(safe_text(contact["location"]))
    if contact.get("linkedin"):
        contact_parts.append(safe_text(contact["linkedin"]))
    if contact.get("github"):
        contact_parts.append(safe_text(contact["github"]))
    if contact.get("portfolio"):
        contact_parts.append(safe_text(contact["portfolio"]))

    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), contact_style))

    story.append(HRFlowable(width="100%", thickness=1, color=black_color, spaceAfter=6, spaceBefore=4))

    # 2. Professional Summary
    summary = safe_text(data.get("summary") or "")
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#666666"), spaceAfter=4, spaceBefore=1))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 3))

    # 3. Technical Skills
    skills = data.get("skills")
    if skills:
        story.append(Paragraph("TECHNICAL SKILLS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#666666"), spaceAfter=4, spaceBefore=1))
        
        if isinstance(skills, dict):
            for cat_name, cat_val in skills.items():
                if cat_val:
                    c_title = safe_text(cat_name).replace("_", " ").title()
                    c_skills = safe_text(cat_val)
                    story.append(Paragraph(f"<b>{c_title}:</b> {c_skills}", body_style))
                    story.append(Spacer(1, 1))
        elif isinstance(skills, list):
            skill_text = ", ".join(safe_text(s) for s in skills if s)
            if skill_text:
                story.append(Paragraph(skill_text, body_style))
        elif isinstance(skills, str) and skills.strip():
            story.append(Paragraph(safe_text(skills), body_style))
        story.append(Spacer(1, 3))

    # 4. Work Experience & Internships
    experience = data.get("experience", [])
    if experience:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#666666"), spaceAfter=4, spaceBefore=1))

        for exp in experience:
            role = safe_text(exp.get("role") or "")
            company = safe_text(exp.get("company") or "")
            location = safe_text(exp.get("location") or "")
            start_date = safe_text(exp.get("start_date") or "")
            end_date = safe_text(exp.get("end_date") or ("Present" if exp.get("current") else ""))
            
            date_range = ""
            if start_date and end_date:
                date_range = f"{start_date} &ndash; {end_date}"
            elif start_date:
                date_range = start_date

            left_p = Paragraph(f"<b>{company}</b>{f' &mdash; {location}' if location else ''}", item_title_style)
            right_p = Paragraph(date_range, item_date_style)
            tbl = Table([[left_p, right_p]], colWidths=[380, 160])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(tbl)

            if role:
                story.append(Paragraph(f"<i>{role}</i>", item_sub_style))

            story.append(Spacer(1, 2))
            bullets = _parse_bullet_list(exp.get("bullets"))
            for b in bullets:
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_text(b)}", bullet_style))
            story.append(Spacer(1, 4))

    # 5. Projects
    projects = data.get("projects", [])
    if projects:
        story.append(Paragraph("PROJECTS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#666666"), spaceAfter=4, spaceBefore=1))

        for proj in projects:
            title = safe_text(proj.get("title") or "")
            tech = safe_text(proj.get("technologies") or "")
            link = safe_text(proj.get("link") or "")

            title_text = f"<b>{title}</b>"
            if tech:
                title_text += f" (<i>{tech}</i>)"

            left_p = Paragraph(title_text, item_title_style)
            right_p = Paragraph(link, item_date_style) if link else Paragraph("", item_date_style)
            tbl = Table([[left_p, right_p]], colWidths=[380, 160])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(tbl)

            story.append(Spacer(1, 2))
            bullets = _parse_bullet_list(proj.get("bullets"))
            for b in bullets:
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_text(b)}", bullet_style))
            story.append(Spacer(1, 4))

    # 6. Education
    education = data.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#666666"), spaceAfter=4, spaceBefore=1))

        for edu in education:
            degree = safe_text(edu.get("degree") or "")
            school = safe_text(edu.get("school") or "")
            grad_year = safe_text(edu.get("graduation_year") or edu.get("dates") or "")
            location = safe_text(edu.get("location") or "")
            gpa = safe_text(edu.get("gpa") or "")
            honors = safe_text(edu.get("honors") or "")

            left_content = f"<b>{school}</b>"
            if location:
                left_content += f", {location}"

            left_p = Paragraph(left_content, item_title_style)
            right_p = Paragraph(grad_year, item_date_style)
            tbl = Table([[left_p, right_p]], colWidths=[420, 120])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(tbl)

            if degree:
                degree_line = f"<i>{degree}</i>"
                if gpa:
                    degree_line += f" &mdash; GPA: {gpa}"
                if honors:
                    degree_line += f" &mdash; {honors}"
                story.append(Paragraph(degree_line, item_sub_style))

            story.append(Spacer(1, 4))

    # 7. Certifications
    certifications = data.get("certifications", [])
    if certifications:
        story.append(Paragraph("CERTIFICATIONS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#666666"), spaceAfter=4, spaceBefore=1))

        for cert in certifications:
            if isinstance(cert, str):
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_text(cert)}", bullet_style))
            elif isinstance(cert, dict):
                c_name = safe_text(cert.get("name") or "")
                c_issuer = safe_text(cert.get("issuer") or "")
                c_date = safe_text(cert.get("date") or "")
                c_id = safe_text(cert.get("credential_id") or "")

                line = f"<b>{c_name}</b>"
                if c_issuer:
                    line += f" &mdash; {c_issuer}"
                if c_id:
                    line += f" (ID: {c_id})"

                left_p = Paragraph(f"&bull;&nbsp;&nbsp;{line}", bullet_style)
                right_p = Paragraph(c_date, item_date_style)
                tbl = Table([[left_p, right_p]], colWidths=[420, 120])
                tbl.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0.5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
                ]))
                story.append(tbl)
        story.append(Spacer(1, 4))

    # 8. Achievements
    achievements = _parse_bullet_list(data.get("achievements"))
    if achievements:
        story.append(Paragraph("ACHIEVEMENTS", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#666666"), spaceAfter=4, spaceBefore=1))
        for ach in achievements:
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{safe_text(ach)}", bullet_style))
        story.append(Spacer(1, 4))

    # 9. Languages
    languages = data.get("languages", [])
    if languages:
        story.append(Paragraph("LANGUAGES", section_h_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#666666"), spaceAfter=4, spaceBefore=1))
        
        lang_strs = []
        for l in languages:
            if isinstance(l, dict):
                n = safe_text(l.get("name") or "")
                p = safe_text(l.get("proficiency") or "")
                if n and p:
                    lang_strs.append(f"{n} ({p})")
                elif n:
                    lang_strs.append(n)
            elif isinstance(l, str) and l.strip():
                lang_strs.append(safe_text(l))
        if lang_strs:
            story.append(Paragraph(", ".join(lang_strs), body_style))

    return story
