"""
Enterprise Tailored ATS Resume Generator for Sri Lakshmi Sravya Reddy Kovvuri.
Customizes professional summary, core competencies matrix, and experience highlights
to maximize ATS keyword scoring and recruiter alignment for specific Job Descriptions (JDs).
"""

import argparse
import sys
import io
import re
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

    def _clean_job_title(self, title: str) -> str:
        """Sanitize raw job posting titles to produce clean, professional resume headlines."""
        cleaned = title or ""
        patterns_to_strip = [
            r"\s*\(\s*CPC\s+Required\s*\)",
            r"\s*\(\s*Remote\b[^\)]*\)",
            r"\s*\(\s*Hybrid\b[^\)]*\)",
            r"\s*\(\s*On-site\b[^\)]*\)",
            r"\s*\(\s*Nationwide\b[^\)]*\)",
            r"\s*\(\s*USA\b[^\)]*\)",
            r"\s*\(\s*Full[- ]?time\b[^\)]*\)",
            r"\s*\(\s*Part[- ]?time\b[^\)]*\)",
        ]
        for pat in patterns_to_strip:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip(" -|/,")
        return cleaned or title

    def _generate_headline(self, job: JobPosting, category: str) -> str:
        """Create a polished, human-written professional headline tailored to the role."""
        clean_title = self._clean_job_title(job.title)

        if category == "dental":
            return f"AAPC Certified Professional Coder (CPC) & Former Dentist (BDS) | {clean_title}"
        elif category == "cdi":
            return "AAPC Certified Professional Coder (CPC) & Clinical Documentation Specialist | Former Clinician (BDS)"
        elif category == "revenue_cycle":
            return "AAPC Certified Professional Coder (CPC) | Revenue Cycle & Claims Denial Specialist"
        elif category == "risk_adjustment":
            return "AAPC Certified Professional Coder (CPC) | Risk Adjustment & HCC Diagnostic Coding Specialist"
        elif category == "inpatient_surgical":
            return "AAPC Certified Professional Coder (CPC) & Former Clinician (BDS) | Surgical & Specialty Medical Coder"
        else:
            return f"AAPC Certified Professional Coder (CPC) & Former Clinician (BDS) | {clean_title}"

    def _generate_summary(self, job: JobPosting, match_result: MatchResult, category: str) -> str:
        """Draft an authentic, human-written professional summary free from AI tells and keyword stuffing."""
        company = job.company.strip() if job.company else "the organization"

        if category == "dental":
            return (
                f"AAPC Certified Professional Coder (CPC) and former clinical dentist holding a Bachelor of Dental "
                f"Surgery (BDS), offering comprehensive diagnostic knowledge of oral and maxillofacial anatomy, restorative "
                f"dentistry, and surgical procedures. Highly proficient in CDT procedure coding, medical cross-coding to "
                f"CPT and ICD-10-CM, and pre-authorization documentation. Experienced in reviewing operative records, "
                f"verifying medical necessity, and formulating clinical appeal letters to resolve denied claims. Dedicated "
                f"to supporting {company} with coding precision, documentation compliance, and efficient revenue turnaround."
            )
        elif category == "cdi":
            return (
                f"AAPC Certified Professional Coder (CPC) and former clinical dentist (BDS) with an extensive foundation in clinical "
                f"pathology, treatment protocols, and medical record review. Skilled at bridging provider clinical documentation "
                f"with official CMS guidelines, ICD-10-CM coding conventions, and healthcare compliance standards. Experienced in "
                f"evaluating electronic health records (EHR), identifying clarification opportunities, and crafting compliant "
                f"physician queries to ensure complete diagnostic specificity and minimize coding delays. Dedicated to advancing "
                f"clinical documentation integrity and chart quality for {company}."
            )
        elif category == "risk_adjustment":
            return (
                f"AAPC Certified Professional Coder (CPC) with direct clinical healthcare training (BDS), bringing strong "
                f"pathology knowledge to risk adjustment coding and chart auditing. Proficient in ICD-10-CM official coding "
                f"guidelines, CMS risk adjustment models, and hierarchical condition category (HCC) capture. Experienced in "
                f"abstracting chronic conditions from outpatient clinical notes, validating that documentation satisfies MEAT "
                f"criteria (Monitor, Evaluate, Assess, Treat), and upholding data integrity. Prepared to support {company} with "
                f"meticulous diagnostic review and compliant risk adjustment reporting."
            )
        elif category == "revenue_cycle":
            return (
                f"AAPC Certified Professional Coder (CPC) with a clinical documentation background, specializing in revenue "
                f"cycle integrity and claims denial management. Experienced in evaluating explanation of benefits (EOBs), "
                f"identifying root causes of claim rejections, and auditing modifier utilization (e.g., 25, 59) in accordance "
                f"with NCCI edits and payer-specific policies. Skilled in authoring evidence-based clinical appeal letters "
                f"and collaborating with billing specialists to optimize claim turnaround. Dedicated to supporting {company} "
                f"in recovering legitimate reimbursement while upholding strict compliance standards."
            )
        elif category == "inpatient_surgical":
            return (
                f"AAPC Certified Professional Coder (CPC) with a clinical dentistry foundation (BDS), providing deep anatomical "
                f"knowledge of head and neck structures, surgical procedures, and clinical charting. Proficient in assigning "
                f"accurate ICD-10-CM, CPT, and HCPCS Level II codes for complex specialty and surgical encounters while validating "
                f"medical necessity and NCCI edits. Experienced in auditing operative notes and collaborating with clinical teams "
                f"to uphold documentation accuracy and compliant billing workflows for {company}."
            )
        else:  # outpatient medical coding / default
            return (
                f"AAPC Certified Professional Coder (CPC) with a clinical background as a Bachelor of Dental Surgery (BDS) "
                f"clinician, bringing hands-on diagnostic knowledge to outpatient medical coding, chart abstraction, and clinical "
                f"documentation review. Thoroughly versed in ICD-10-CM, CPT, and HCPCS Level II coding conventions, Evaluation and "
                f"Management (E/M) guidelines, NCCI edits, and CMS billing regulations. Experienced in interpreting provider "
                f"encounter notes, verifying medical necessity, and collaborating across clinical and billing teams to ensure coding "
                f"completeness and prevent claims rejections. Dedicated to supporting {company} with thorough documentation "
                f"analysis, accurate code assignment, and compliant revenue cycle practices."
            )

    def _prioritize_skills(
        self, match_result: MatchResult, category: str = "outpatient_medical_coding"
    ) -> Dict[str, List[str]]:
        """
        Organize skills into clean, human professional categories with JD-matched competencies prioritized naturally.
        Avoids mechanical keyword dumps and presents competencies like an experienced human coder.
        """
        matched_set = {m.lower() for m in match_result.matched_skills}

        def sort_skills(skill_list: List[str]) -> List[str]:
            return sorted(
                skill_list,
                key=lambda s: (0 if any(m in s.lower() or s.lower() in m for m in matched_set) else 1, s)
            )

        coding_skills = [
            "ICD-10-CM",
            "CPT",
            "HCPCS Level II",
            "Evaluation & Management (E/M)",
            "Modifiers (25, 59)"
        ]
        if category in ("dental", "inpatient_surgical") or match_result.is_dental_relevant:
            coding_skills.insert(3, "CDT Dental Coding")

        compliance_skills = [
            "CMS Guidelines",
            "NCCI Edits",
            "HIPAA Privacy Standards",
            "Medical Necessity Guidelines",
            "OIG Compliance",
            "Payer Coverage Policies"
        ]

        health_it_skills = [
            "Electronic Health Records (EHR / Epic)",
            "Practice Management Systems",
            "Revenue Cycle Management (RCM)",
            "Claims Scrubbers",
            "Prior Authorization Workflows"
        ]

        clinical_skills = [
            "Clinical Documentation Improvement (CDI)",
            "Chart Auditing & Review",
            "Anatomic & Pathologic Terminology",
            "Claim Denial Resolution & Appeals"
        ]

        categorized: Dict[str, List[str]] = {
            "Medical & Procedural Coding": sort_skills(coding_skills),
            "Regulatory & Healthcare Compliance": sort_skills(compliance_skills),
            "Health Information Systems & RCM": sort_skills(health_it_skills),
            "Clinical Documentation & Review": sort_skills(clinical_skills),
        }

        if category in ("dental", "inpatient_surgical") or match_result.is_dental_relevant:
            dental_skills = [
                "Oral Healthcare & Diagnosis",
                "Maxillofacial Anatomy",
                "Dental Procedures & Treatment Planning",
                "Dental Charting & Clinical Records"
            ]
            categorized["Clinical Dental Specialties"] = sort_skills(dental_skills)

        return categorized

    def _generate_experience(self, category: str) -> List[Dict[str, Any]]:
        """Tailor experience bullet points with authentic, active clinical and coding achievements."""
        experiences = []

        for exp in self.profile.experience:
            role = exp.get("role", "")
            company = exp.get("company", "")
            location = exp.get("location", "")
            dates = exp.get("dates", "")
            base_highlights = list(exp.get("highlights", []))

            tailored_highlights: List[str] = []

            if category == "dental":
                if "SKY Dental" in company:
                    tailored_highlights = [
                        "Directed clinical charting and electronic procedure documentation for complex surgical, restorative, and periodontal cases, ensuring CDT code accuracy.",
                        "Collaborated closely with practice billing personnel to cross-code oral surgical procedures to medical carriers using CPT, ICD-10-CM, and HCPCS Level II codes.",
                        "Conducted pre-authorization chart reviews, prepared clinical necessity appeal narratives for denied claims, and maintained compliance with HIPAA privacy standards.",
                        "Standardized electronic clinical note templates across care teams to ensure documentation completeness and expedite insurance reimbursement turnaround."
                    ]
                else:
                    tailored_highlights = [
                        "Conducted comprehensive patient diagnostic examinations and surgical treatments while authoring detailed operative logs and treatment plans.",
                        "Reviewed patient charts against insurance carrier coverage criteria to eliminate documentation discrepancies and prevent claim rejections.",
                        "Educated administrative staff on anatomical descriptors, tooth numbering conventions, and procedural complexity to improve billing accuracy."
                    ]
            elif category == "cdi":
                if "SKY Dental" in company:
                    tailored_highlights = [
                        "Led clinical documentation review initiatives, evaluating provider encounter notes for diagnostic clarity, completeness, and adherence to medical necessity criteria.",
                        "Initiated compliant clinician documentation queries to resolve record ambiguities, conflicting entries, and unstated secondary conditions prior to billing submission.",
                        "Implemented standardized electronic documentation protocols that enhanced chart integrity and reduced downstream coding queries.",
                        "Maintained patient health records in full compliance with CMS documentation principles and official coding conventions."
                    ]
                else:
                    tailored_highlights = [
                        "Audited daily patient records to ensure clinical documentation fully substantiated all diagnosed conditions and rendered therapeutic treatments.",
                        "Collaborated with clinical and administrative colleagues to resolve chart documentation gaps and promote consistent medical record keeping.",
                        "Assisted in reviewing pre-treatment plans and clinical notes to verify alignment with payer documentation standards."
                    ]
            elif category == "revenue_cycle":
                if "SKY Dental" in company:
                    tailored_highlights = [
                        "Collaborated directly with revenue cycle personnel to review denied and pended claims, identify root-cause coding issues, and draft clinical appeal justifications.",
                        "Audited encounter records for correct modifier usage (e.g., 25, 59) and validated billing compliance with NCCI edits and payer coverage guidelines.",
                        "Streamlined charge capture workflows to accelerate reimbursement turnaround while maintaining 100% adherence to compliance guidelines.",
                        "Analyzed recurring billing discrepancies and provided clinical feedback to reduce initial claim rejection rates."
                    ]
                else:
                    tailored_highlights = [
                        "Audited patient encounter accounts and insurance explanation of benefits (EOBs) to identify adjudication errors and billing delays.",
                        "Verified patient eligibility, prior authorizations, and coverage determinations prior to extensive surgical treatments.",
                        "Assisted billing teams in clarifying procedure descriptions and clinical justifications to resolve payer inquiries."
                    ]
            elif category == "risk_adjustment":
                if "SKY Dental" in company:
                    tailored_highlights = [
                        "Reviewed comprehensive patient encounter records to abstract documented chronic conditions and comorbidities, ensuring accurate ICD-10-CM code assignment.",
                        "Verified that clinical notes satisfied MEAT criteria (Monitor, Evaluate, Assess, Treat) to support compliant HCC category assignment and audit readiness.",
                        "Audited charts for diagnostic specificity and documentation completeness, identifying uncaptured manifestations and secondary diagnoses.",
                        "Maintained data privacy and strict adherence to CMS official coding and reporting guidelines for risk-adjusted reimbursement."
                    ]
                else:
                    tailored_highlights = [
                        "Conducted clinical examinations and documented complete patient histories, physical assessments, and therapeutic interventions in electronic charts.",
                        "Reviewed outpatient records for diagnostic completeness and clinical consistency to ensure documentation integrity.",
                        "Maintained detailed clinical encounter logs upholding healthcare compliance and patient confidentiality standards."
                    ]
            elif category == "inpatient_surgical":
                if "SKY Dental" in company:
                    tailored_highlights = [
                        "Reviewed and abstracted operative reports, pathology findings, and surgical notes for head and neck procedures, ensuring precise CPT and ICD-10-CM code assignment.",
                        "Audited procedural records for medical necessity substantiation, correct surgical modifier application, and NCCI unbundling edit compliance.",
                        "Collaborated with surgical and billing teams to clarify complex operative techniques and resolve pre-bill coding inquiries.",
                        "Maintained electronic health records (EHR) adhering strictly to CMS documentation guidelines and HIPAA privacy regulations."
                    ]
                else:
                    tailored_highlights = [
                        "Delivered clinical patient care and performed minor oral surgical procedures while authoring thorough diagnostic and operative progress notes.",
                        "Audited clinical encounter records for completeness, diagnostic specificity, and adherence to surgical treatment protocols.",
                        "Coordinated with insurance specialists to confirm pre-authorizations and resolve procedural coverage inquiries."
                    ]
            else:  # outpatient medical coding / default
                if "SKY Dental" in company:
                    tailored_highlights = [
                        "Reviewed and abstracted outpatient clinical encounter notes, diagnostic findings, and treatment plans to assign accurate ICD-10-CM, CPT, and HCPCS Level II codes.",
                        "Collaborated daily with administrative billing personnel to verify medical necessity, resolve coding discrepancies, and align charting with NCCI edits.",
                        "Audited patient records for documentation completeness and appropriate modifier application prior to claims submission, reducing preventable rejections.",
                        "Maintained electronic health records (EHR) in strict compliance with CMS documentation standards, HIPAA privacy rules, and official coding conventions.",
                        "Prepared clinical justification summaries to assist billing staff in resolving payer documentation requests and pended claims."
                    ]
                else:
                    tailored_highlights = [
                        "Delivered patient care while authoring detailed clinical progress notes, diagnostic evaluations, and procedure records.",
                        "Reviewed outpatient health records for completeness, diagnostic specificity, and clinical consistency to minimize administrative processing delays.",
                        "Interfaced with administrative staff to clarify procedure descriptions and verify insurance coverage requirements."
                    ]

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
        skills_dict = self._prioritize_skills(match_result, category)
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
        skills_dict = self._prioritize_skills(match_result, category)
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
            md_file = out_dir / f"Sri_Kovvuri_Resume_{job.id}_{clean_company}.md"
            resume_content = generator.generate(job, res)
            md_file.write_text(resume_content, encoding="utf-8")

            # 2. PDF version
            pdf_file = out_dir / f"Sri_Kovvuri_Resume_{job.id}_{clean_company}.pdf"
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
        out_filename = args.output or f"Sri_Kovvuri_Resume_{target_job.company.replace(' ', '_')}.pdf"
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
