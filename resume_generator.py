"""
Enterprise Tailored ATS Resume Generator for Sri Lakshmi Sravya Reddy Kovvuri.
Customizes professional summary, core competencies matrix, and experience highlights
to maximize ATS keyword scoring and recruiter alignment for specific Job Descriptions (JDs).
"""

import argparse
import sys
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from config import settings, setup_logging
from models import CandidateProfile, JobPosting, MatchResult
from matcher import ATSMatcher
from job_finder import JobFinderService, CURATED_HEALTHCARE_JOBS
from pdf_generator import compile_resume_to_pdf

logger = logging.getLogger(__name__)


class TailoredResumeGenerator:
    """Enterprise resume customizer generating ATS-compliant resumes tailored to job descriptions."""

    def __init__(self, profile: CandidateProfile, matcher: Optional[ATSMatcher] = None):
        self.profile = profile
        self.matcher = matcher or ATSMatcher(profile)

    def _determine_role_category(self, job: JobPosting, match_result: MatchResult) -> str:
        """Determine the primary role focus to guide narrative specialization."""
        title_lower = (job.title or "").lower()
        desc_lower = (job.description or "").lower()

        if match_result.is_dental_relevant or "dental" in title_lower:
            return "dental"
        elif "cdi" in title_lower or "clinical documentation" in title_lower:
            return "cdi"
        elif "risk adjustment" in title_lower or "hcc" in title_lower or "crc" in title_lower:
            return "risk_adjustment"
        elif "revenue cycle" in title_lower or "denial" in title_lower or "claims" in title_lower:
            return "revenue_cycle"
        elif "inpatient" in title_lower or "surgical" in title_lower:
            return "inpatient_surgical"
        else:
            return "outpatient_medical_coding"

    def _generate_headline(self, job: JobPosting, category: str) -> str:
        """Create an ATS-targeted candidate headline matching the job title."""
        if category == "dental":
            return f"AAPC Certified Professional Coder (CPC) & Former Dentist (BDS) | {job.title}"
        elif category == "cdi":
            return f"AAPC Certified Professional Coder (CPC) & Clinical Documentation Specialist | Former Dentist (BDS)"
        elif category == "revenue_cycle":
            return f"AAPC Certified Professional Coder (CPC) | Revenue Cycle & Claims Denial Specialist"
        elif category == "risk_adjustment":
            return f"AAPC Certified Professional Coder (CPC) | Risk Adjustment & Clinical Diagnostic Coder"
        else:
            return f"AAPC Certified Professional Coder (CPC) & Former Clinician (BDS) | {job.title}"

    def _generate_summary(self, job: JobPosting, match_result: MatchResult, category: str) -> str:
        """Draft a targeted, ATS-keyword-rich professional summary."""
        matched_str = ", ".join(match_result.matched_skills[:5]) if match_result.matched_skills else "ICD-10-CM, CPT, and HCPCS Level II"

        if category == "dental":
            return (
                f"Detail-oriented Certified Professional Coder (CPC) credentialed by the AAPC, offering a rare and powerful "
                f"combination of hands-on diagnostic dentistry (Bachelor of Dental Surgery, BDS) and rigorous procedural coding "
                f"expertise. Uniquely qualified for the {job.title} role at {job.company}, offering deep anatomical fluency in oral "
                f"and maxillofacial procedures, seamless CDT to CPT/ICD-10-CM cross-coding, and pre-authorization precision. "
                f"Proven track record reviewing complex clinical logs, verifying medical necessity, and resolving claim denials."
            )
        elif category == "cdi":
            return (
                f"AAPC Certified Professional Coder (CPC) with direct clinical practitioner experience as a licensed dentist (BDS), "
                f"bridging provider documentation intent with rigorous healthcare compliance guidelines. Tailored for {job.company}'s "
                f"{job.title} position, leveraging clinician-to-clinician communication skills to review electronic health records (EHR), "
                f"identify documentation clarification opportunities, and ensure complete diagnostic capture under CMS guidelines."
            )
        elif category == "risk_adjustment":
            return (
                f"AAPC Certified Professional Coder (CPC) possessing strong foundational clinical pathology and diagnostic knowledge "
                f"from years of direct healthcare delivery. Specially positioned for {job.company}'s {job.title} opening, ensuring strict "
                f"adherence to CMS risk adjustment guidelines, accurate HCC category assignment, and thorough outpatient chart auditing "
                f"to support compliant, data-driven reimbursement."
            )
        elif category == "revenue_cycle":
            return (
                f"Certified Professional Coder (CPC) through AAPC with clinical documentation expertise and dedicated focus on Revenue "
                f"Cycle Management (RCM) integrity. Applying for the {job.title} role at {job.company}, bringing deep experience "
                f"deciphering complex clinical entries, investigating denied claims, auditing modifier usage (e.g., 25, 59), and "
                f"preparing compelling clinical appeals that maximize reimbursement velocity while upholding strict OIG and CMS compliance."
            )
        else:
            return (
                f"AAPC Certified Professional Coder (CPC) in Dayton, Ohio, combining frontline clinical patient care experience as a licensed "
                f"dentist (BDS) with mastery of medical coding standards ({matched_str}). Targeted for the {job.title} position at "
                f"{job.company}. Leverages clinical diagnostic acumen to interpret provider notes with zero ramp-up time, assign precise "
                f"diagnostic and procedural codes, verify medical necessity, and uphold flawless HIPAA and NCCI billing standards."
            )

    def _prioritize_skills(self, match_result: MatchResult) -> Dict[str, List[str]]:
        """Order skills based on job description hits to maximize ATS density."""
        matched_set = set(match_result.matched_skills)

        # Baseline skills from profile
        skills = self.profile.skills

        categorized: Dict[str, List[str]] = {}

        for cat_name, skill_list in skills.items():
            # Sort matched skills to the front of each category
            sorted_list = sorted(
                skill_list,
                key=lambda s: (0 if any(m.lower() in s.lower() or s.lower() in m.lower() for m in matched_set) else 1, s)
            )
            cat_display = cat_name.replace("_", " ").title()
            categorized[cat_display] = sorted_list

        return categorized

    def _generate_experience(self, category: str) -> List[Dict[str, Any]]:
        """Tailor experience bullet points to highlight skills demanded by the target role."""
        experiences = []

        for exp in self.profile.experience:
            role = exp.get("role", "")
            company = exp.get("company", "")
            location = exp.get("location", "")
            dates = exp.get("dates", "")
            base_highlights = list(exp.get("highlights", []))

            # Role-specific tailored bullet points
            tailored_highlights = []

            if category == "dental":
                if "SKY Dental" in company:
                    tailored_highlights.append(
                        "Managed end-to-end clinical charting and electronic procedural documentation for oral surgical, restorative, and periodontal cases, ensuring CDT accuracy."
                    )
                    tailored_highlights.append(
                        "Partnered with practice billing personnel to facilitate cross-coding dental procedures to medical insurance carriers (CPT and ICD-10-CM) to optimize legitimate patient reimbursement."
                    )
                    tailored_highlights.append(
                        "Conducted pre-authorization chart reviews, resolved claims denials through clinical justification letters, and upheld HIPAA healthcare privacy guidelines."
                    )
                else:
                    tailored_highlights.append(
                        "Maintained comprehensive dental clinical logs and diagnostic treatment records for high-volume outpatient patient populations."
                    )
                    tailored_highlights.append(
                        "Cross-referenced patient charts against insurance carrier coverage guidelines, reducing administrative claim submission rejections."
                    )
                    tailored_highlights.append(
                        "Educated clinical and administrative support teams on precise terminology for tooth numbering, quadrant descriptors, and procedural complexity."
                    )
            elif category == "cdi":
                if "SKY Dental" in company:
                    tailored_highlights.append(
                        "Served as Clinical Documentation Lead, evaluating provider treatment records for diagnostic clarity, completeness, and adherence to medical necessity criteria."
                    )
                    tailored_highlights.append(
                        "Facilitated documentation clarification queries directly with practitioners to resolve chart ambiguities prior to administrative billing processing."
                    )
                    tailored_highlights.append(
                        "Instituted structured electronic documentation protocols that enhanced chart integrity, reducing downstream coding queries and audit flags."
                    )
                else:
                    tailored_highlights.append(
                        "Reviewed daily patient records to ensure clinical entries accurately substantiated all rendered diagnoses and therapeutic interventions."
                    )
                    tailored_highlights.append(
                        "Collaborated with healthcare staff to bridge documentation gaps and eliminate conflicting notes in patient health records."
                    )
            elif category == "revenue_cycle":
                if "SKY Dental" in company:
                    tailored_highlights.append(
                        "Directly collaborated with revenue cycle staff to review denied and pended claims, correcting coding errors and drafting clinical appeal justifications."
                    )
                    tailored_highlights.append(
                        "Audited patient encounter forms for accurate modifier usage (e.g. 25, 59) and validated compliance with NCCI edits and payer-specific guidelines."
                    )
                    tailored_highlights.append(
                        "Streamlined charge capture workflows to accelerate reimbursement velocity while maintaining 100% compliance with privacy and OIG regulations."
                    )
                else:
                    tailored_highlights.append(
                        "Audited daily patient accounts and insurance billing inquiries to identify root causes of claim delays and adjudication errors."
                    )
                    tailored_highlights.append(
                        "Verified patient eligibility, pre-authorizations, and coverage determination rules prior to major surgical procedures."
                    )
            else:  # outpatient medical coding / default
                if "SKY Dental" in company:
                    tailored_highlights.append(
                        "Interpreted provider clinical encounter notes, diagnostic findings, and pathology reports to assign accurate procedural and diagnostic designations."
                    )
                    tailored_highlights.append(
                        "Collaborated daily with administrative billing personnel to verify medical necessity and substantiate reimbursement claims under ICD-10 and CPT coding frameworks."
                    )
                    tailored_highlights.append(
                        "Maintained pristine electronic health records (EHR) adhering strictly to CMS guidelines, HIPAA data security, and official coding conventions."
                    )
                else:
                    tailored_highlights.append(
                        "Delivered comprehensive patient care while maintaining detailed diagnostic and operative clinical records."
                    )
                    tailored_highlights.append(
                        "Reviewed health records for completeness, diagnostic specificity, and clinical consistency to reduce administrative processing rejections."
                    )

            experiences.append({
                "role": role,
                "company": company,
                "location": location,
                "dates": dates,
                "highlights": tailored_highlights or base_highlights
            })

        return experiences

    def generate(self, job: JobPosting, match_result: Optional[MatchResult] = None) -> str:
        """
        Generate a complete, ATS-tailored resume in Markdown format.

        Args:
            job: The target JobPosting instance.
            match_result: Optional precomputed MatchResult.

        Returns:
            A clean, ATS-compliant Markdown resume string.
        """
        if match_result is None:
            match_result = self.matcher.match(job)

        category = self._determine_role_category(job, match_result)
        headline = self._generate_headline(job, category)
        summary = self._generate_summary(job, match_result, category)
        skills_dict = self._prioritize_skills(match_result)
        experiences = self._generate_experience(category)

        # Build clean ATS Markdown resume
        lines: List[str] = [
            f"# {self.profile.name}",
            f"**{headline}**",
            f"{self.profile.location} | {self.profile.phone} | {self.profile.email} | AAPC ID: CPC Credentialed",
            "",
            "---",
            "",
            "## PROFESSIONAL SUMMARY",
            summary,
            "",
            "---",
            "",
            "## CORE COMPETENCIES & TECHNICAL EXPERTISE",
        ]

        # Prioritized Skills Matrix
        for cat_name, skill_list in skills_dict.items():
            formatted_skills = ", ".join(skill_list)
            lines.append(f"- **{cat_name}:** {formatted_skills}")

        lines.extend([
            "",
            "---",
            "",
            "## ACTIVE CERTIFICATIONS & LICENSES",
        ])

        for cert in self.profile.certifications:
            issuer = cert.get("issuer", "AAPC")
            loc = cert.get("location", "")
            date = cert.get("date", "")
            status = cert.get("status", "Active")
            lines.append(f"- **{cert['name']}** – {issuer} ({loc}) | Status: **{status}** | Credential Date: {date}")

        lines.extend([
            "",
            "---",
            "",
            "## CLINICAL & HEALTHCARE EXPERIENCE",
        ])

        for exp in experiences:
            lines.append(f"### {exp['role']}")
            lines.append(f"*{exp['company']}* | {exp['location']} | **{exp['dates']}**")
            for h in exp["highlights"]:
                lines.append(f"- {h}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## EDUCATION",
        ])

        for edu in self.profile.education:
            deg = edu.get("degree", "Bachelor of Dental Surgery (BDS)")
            inst = edu.get("institution", "")
            loc = edu.get("location", "")
            grad = edu.get("graduation_date", "")
            lines.append(f"- **{deg}** – {inst}, {loc} (Graduated: {grad})")

        lines.append("")
        resume_md = "\n".join(lines)
        logger.info("Generated tailored resume for '%s' at '%s' (Category: %s)", job.title, job.company, category)
        return resume_md

    def generate_pdf(
        self,
        job: JobPosting,
        output: Union[str, Path, io.BytesIO],
        match_result: Optional[MatchResult] = None,
    ) -> None:
        """
        Generate a complete, ATS-tailored resume compiled to professional PDF format.

        Args:
            job: The target JobPosting instance.
            output: Destination file path or BytesIO buffer.
            match_result: Optional precomputed MatchResult.
        """
        if match_result is None:
            match_result = self.matcher.match(job)

        category = self._determine_role_category(job, match_result)
        headline = self._generate_headline(job, category)
        summary = self._generate_summary(job, match_result, category)
        skills_dict = self._prioritize_skills(match_result)
        experiences = self._generate_experience(category)
        contact_line = f"{self.profile.location} | {self.profile.phone} | {self.profile.email} | AAPC Credentialed CPC"

        compile_resume_to_pdf(
            candidate_name=self.profile.name,
            headline=headline,
            contact_line=contact_line,
            summary=summary,
            skills_dict=skills_dict,
            certifications=self.profile.certifications,
            experiences=experiences,
            education=self.profile.education,
            output=output,
        )
        logger.info("Generated tailored PDF resume for '%s' at '%s'", job.title, job.company)


def build_parser() -> argparse.ArgumentParser:
    """CLI argument parser for resume_generator.py."""
    parser = argparse.ArgumentParser(
        prog="resume_generator",
        description="Tailored ATS Resume Generator for Sri Lakshmi Sravya Reddy Kovvuri"
    )
    parser.add_argument("--id", help="Curated job ID to target (e.g. oh-cc-001, rem-dent-004)")
    parser.add_argument("--all", action="store_true", help="Generate tailored resumes for all curated jobs")
    parser.add_argument("--pdf", action="store_true", help="Compile resume to PDF format")
    parser.add_argument("--output", help="Output file path (e.g. Tailored_Resume.pdf or Tailored_Resume.md)")
    parser.add_argument("--output-dir", default="tailored_resumes", help="Directory for batch outputs (default: tailored_resumes)")
    parser.add_argument("--title", help="Custom job title for ad-hoc posting")
    parser.add_argument("--company", help="Custom company name for ad-hoc posting")
    parser.add_argument("--text", help="Raw job description text for ad-hoc posting")
    parser.add_argument("--file", help="Path to text file with job description")
    return parser


def main() -> None:
    """CLI execution entrypoint."""
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    profile = CandidateProfile.load_from_json(settings.profile_path)
    matcher = ATSMatcher(profile)
    generator = TailoredResumeGenerator(profile, matcher)
    finder = JobFinderService()

    if args.all:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nGenerating tailored ATS resumes (both Markdown & PDF) for all {len(CURATED_HEALTHCARE_JOBS)} curated jobs...\n")

        for job in CURATED_HEALTHCARE_JOBS:
            res = matcher.match(job)
            clean_company = "".join(c for c in job.company if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")

            # 1. Markdown version
            md_file = out_dir / f"Resume_{job.id}_{clean_company}.md"
            resume_content = generator.generate(job, res)
            md_file.write_text(resume_content, encoding="utf-8")

            # 2. PDF version
            pdf_file = out_dir / f"Resume_{job.id}_{clean_company}.pdf"
            generator.generate_pdf(job, pdf_file, res)

            print(f"  ✓ [{res.score}% Fit] Generated: {pdf_file.name} & {md_file.name}")

        print(f"\n🎉 Successfully created all PDF and Markdown resumes in directory: {out_dir.resolve()}\n")
        return

    target_job: Optional[JobPosting] = None

    if args.id:
        for j in finder.cached_jobs:
            if j.id == args.id:
                target_job = j
                break
        if not target_job:
            print(f"Error: Job ID '{args.id}' not found in curated listings.", file=sys.stderr)
            sys.exit(1)
    elif args.file or args.text:
        content = ""
        if args.file:
            fpath = Path(args.file)
            if not fpath.is_file():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)
            content = fpath.read_text(encoding="utf-8")
        else:
            content = args.text or ""

        target_job = JobPosting(
            id="custom-target",
            title=args.title or "Certified Medical Coder",
            company=args.company or "Prospective Healthcare Employer",
            location="Ohio / Remote",
            is_remote=True,
            description=content
        )
    else:
        # Default to Cleveland Clinic curated position if no arguments provided
        print("No job specified. Generating default resume tailored for Cleveland Clinic (oh-cc-001)...")
        target_job = finder.cached_jobs[0]

    match_res = matcher.match(target_job)

    # Determine if PDF output is requested
    is_pdf = args.pdf or (args.output and args.output.lower().endswith(".pdf"))

    if is_pdf:
        out_filename = args.output or f"Resume_{target_job.company.replace(' ', '_')}.pdf"
        out_path = Path(out_filename)
        generator.generate_pdf(target_job, out_path, match_res)
        print(f"\n🎉 Successfully compiled tailored ATS PDF resume to: {out_path.resolve()}\n")
    else:
        resume = generator.generate(target_job, match_res)
        if args.output:
            out_path = Path(args.output)
            out_path.write_text(resume, encoding="utf-8")
            print(f"\nSaved tailored ATS resume to: {out_path.resolve()}\n")
        else:
            print("\n" + "=" * 70)
            print(f"TAILORED ATS RESUME FOR: {target_job.title} at {target_job.company} (Fit: {match_res.score}%)")
            print("=" * 70)
            print(resume)
            print("=" * 70)


if __name__ == "__main__":
    main()
