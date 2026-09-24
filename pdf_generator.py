"""
PDF Resume Generator for JobsFind.
Produces clean, executive-standard, ATS-compliant PDF resumes using ReportLab.
Designed for Sri Lakshmi Sravya Reddy Kovvuri.
"""

import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)

logger = logging.getLogger(__name__)

# Premium Enterprise Color Palette
NAVY_PRIMARY = colors.HexColor("#0f2c59")
BLUE_ACCENT = colors.HexColor("#0284c7")
TEXT_CHARCOAL = colors.HexColor("#1e293b")
TEXT_MUTED = colors.HexColor("#475569")
BORDER_LIGHT = colors.HexColor("#cbd5e1")


class ResumePDFGenerator:
    """Enterprise PDF compiler generating sleek, ATS-parseable resumes."""

    def __init__(self):
        self._init_styles()

    def _init_styles(self):
        """Configure typographic hierarchy with standard Helvetica fonts."""
        styles = getSampleStyleSheet()

        self.name_style = ParagraphStyle(
            "CandidateName",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=NAVY_PRIMARY,
            spaceAfter=3,
        )

        self.headline_style = ParagraphStyle(
            "CandidateHeadline",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=BLUE_ACCENT,
            spaceAfter=3,
        )

        self.contact_style = ParagraphStyle(
            "ContactInfo",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=TEXT_MUTED,
            spaceAfter=8,
        )

        self.section_heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=NAVY_PRIMARY,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        )

        self.body_style = ParagraphStyle(
            "ResumeBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=TEXT_CHARCOAL,
            spaceAfter=4,
        )

        self.job_title_style = ParagraphStyle(
            "JobTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=TEXT_CHARCOAL,
        )

        self.job_meta_style = ParagraphStyle(
            "JobMeta",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            textColor=TEXT_MUTED,
            spaceAfter=3,
        )

        self.bullet_style = ParagraphStyle(
            "BulletText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=TEXT_CHARCOAL,
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=2.5,
        )

        self.skill_category_style = ParagraphStyle(
            "SkillCategory",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12.5,
            textColor=TEXT_CHARCOAL,
            spaceAfter=3,
        )

    def generate_pdf(
        self,
        candidate_name: str,
        headline: str,
        contact_line: str,
        summary: str,
        skills_dict: Dict[str, List[str]],
        certifications: List[Dict[str, str]],
        experiences: List[Dict[str, Any]],
        education: List[Dict[str, str]],
        output: Union[str, Path, io.BytesIO],
    ) -> None:
        """
        Compile resume data into a structured, single/two-page ATS PDF.

        Args:
            candidate_name: Candidate full name.
            headline: Targeted role headline.
            contact_line: Clean contact info string.
            summary: Targeted executive summary text.
            skills_dict: Categorized core skills.
            certifications: List of certifications.
            experiences: List of professional clinical/coding experiences.
            education: List of degrees and institutions.
            output: Destination file path or file-like buffer (io.BytesIO).
        """
        # Document setup with 0.5-inch margins for maximum ATS space
        target = str(output) if isinstance(output, Path) else output
        doc = SimpleDocTemplate(
            target,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        story = []

        # 1. Header (Name, Headline, Contact)
        story.append(Paragraph(candidate_name, self.name_style))
        story.append(Paragraph(headline, self.headline_style))
        story.append(Paragraph(contact_line, self.contact_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=NAVY_PRIMARY, spaceBefore=2, spaceAfter=6))

        # 2. Professional Summary
        story.append(Paragraph("PROFESSIONAL SUMMARY", self.section_heading_style))
        story.append(Paragraph(summary, self.body_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceBefore=4, spaceAfter=4))

        # 3. Core Competencies & Technical Expertise
        story.append(Paragraph("CORE COMPETENCIES & TECHNICAL EXPERTISE", self.section_heading_style))
        for cat_name, skill_list in skills_dict.items():
            formatted_skills = ", ".join(skill_list)
            text = f"<b>{cat_name}:</b> {formatted_skills}"
            story.append(Paragraph(text, self.skill_category_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceBefore=4, spaceAfter=4))

        # 4. Active Certifications & Credentials
        story.append(Paragraph("ACTIVE CERTIFICATIONS & CREDENTIALS", self.section_heading_style))
        for cert in certifications:
            name = cert.get("name", "")
            issuer = cert.get("issuer", "")
            loc = cert.get("location", "")
            date = cert.get("date", "")
            status = cert.get("status", "Active")
            cert_text = f"• <b>{name}</b> — {issuer} ({loc}) | Status: <b>{status}</b> | Date: {date}"
            story.append(Paragraph(cert_text, self.bullet_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceBefore=4, spaceAfter=4))

        # 5. Clinical & Healthcare Experience
        story.append(Paragraph("CLINICAL & HEALTHCARE EXPERIENCE", self.section_heading_style))
        for exp in experiences:
            role = exp.get("role", "")
            company = exp.get("company", "")
            loc = exp.get("location", "")
            dates = exp.get("dates", "")
            highlights = exp.get("highlights", [])

            # Role + Dates on one line
            header_table = Table(
                [[
                    Paragraph(f"<b>{role}</b> — {company}", self.job_title_style),
                    Paragraph(f"<b>{dates}</b>", ParagraphStyle("RightDates", parent=self.job_title_style, alignment=2))
                ]],
                colWidths=[380, 160],
            )
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]))
            story.append(header_table)
            story.append(Paragraph(f"<i>Location: {loc}</i>", self.job_meta_style))

            for h in highlights:
                story.append(Paragraph(f"• {h}", self.bullet_style))

            story.append(Spacer(1, 4))

        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceBefore=2, spaceAfter=4))

        # 6. Education
        story.append(Paragraph("EDUCATION", self.section_heading_style))
        for edu in education:
            deg = edu.get("degree", "Bachelor of Dental Surgery (BDS)")
            inst = edu.get("institution", "")
            loc = edu.get("location", "")
            grad = edu.get("graduation_date", "")
            edu_text = f"• <b>{deg}</b> — {inst}, {loc} (Graduated: {grad})"
            story.append(Paragraph(edu_text, self.bullet_style))

        # Build document
        doc.build(story)
        logger.info("Successfully compiled resume PDF")


def compile_resume_to_pdf(
    candidate_name: str,
    headline: str,
    contact_line: str,
    summary: str,
    skills_dict: Dict[str, List[str]],
    certifications: List[Dict[str, str]],
    experiences: List[Dict[str, Any]],
    education: List[Dict[str, str]],
    output: Union[str, Path, io.BytesIO],
) -> None:
    """Convenience helper function to generate PDF resume."""
    gen = ResumePDFGenerator()
    gen.generate_pdf(
        candidate_name=candidate_name,
        headline=headline,
        contact_line=contact_line,
        summary=summary,
        skills_dict=skills_dict,
        certifications=certifications,
        experiences=experiences,
        education=education,
        output=output,
    )
