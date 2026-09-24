"""
Targeted cover letter and application narrative generator for Sri Lakshmi Sravya Reddy Kovvuri.
Customized for Medical Coding, Dental Coding, CDI, and Revenue Cycle roles.
Generates dynamic, professional letters tailored to employer requirements and match results.
"""

import logging
from datetime import datetime
from models import CandidateProfile, JobPosting, MatchResult

logger = logging.getLogger(__name__)


class CoverLetterGenerator:
    """Enterprise narrative generator creating tailored cover letters."""

    def __init__(self, profile: CandidateProfile):
        self.profile = profile

    def generate(self, job: JobPosting, match_result: MatchResult) -> str:
        """
        Generate a compelling, personalized cover letter addressing the employer's specific job description.

        Args:
            job: The target JobPosting.
            match_result: The ATS MatchResult containing matched skills and domain signals.

        Returns:
            Formatted, ready-to-submit cover letter string.
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        is_dental = match_result.is_dental_relevant

        # Dynamic introductory hook
        if is_dental:
            hook_paragraph = (
                f"I am writing to express my strong enthusiasm for the {job.title} position at {job.company}. "
                f"As an AAPC Certified Professional Coder (CPC) and a licensed clinician holding a Bachelor of Dental Surgery (BDS), "
                f"I offer a rare dual qualification: deep, firsthand clinical mastery of dental procedures and oral anatomy paired "
                f"with rigorous expertise in CDT, CPT, ICD-10-CM, and HCPCS coding systems."
            )
        else:
            hook_paragraph = (
                f"I am writing to submit my application for the {job.title} position at {job.company}. "
                f"Holding active Certified Professional Coder (CPC) credentialing from the AAPC in Dayton, Ohio, "
                f"combined with hands-on clinical experience as a licensed dentist (BDS), I bring a distinctive clinician's perspective "
                f"to medical coding, clinical documentation integrity, and revenue cycle compliance."
            )

        # Dynamic body paragraph 1: Clinical + Coding synthesis
        body_clinical = (
            "Throughout my clinical career at SKY Dental Clinic and Dentalign Multispeciality Clinic, I worked at the frontline "
            "of patient care, treatment planning, and detailed electronic clinical documentation. I routinely partnered with "
            "billing and revenue cycle staff to decipher complex clinical chart entries, verify medical necessity, and ensure "
            "accurate diagnostic and procedural alignment before claim submission. This firsthand clinical background gives me "
            "an intuitive understanding of provider documentation rationale, allowing me to bridge the gap between provider intent "
            "and compliant coding without costly back-and-forth delays."
        )

        # Dynamic body paragraph 2: Technical coding standards and compliance
        matched_str = (
            ", ".join(match_result.matched_skills[:5])
            if match_result.matched_skills
            else "ICD-10-CM, CPT, and HCPCS Level II"
        )
        body_technical = (
            f"My technical expertise aligns directly with the requirements at {job.company}, including proficiency in {matched_str}. "
            f"I strictly adhere to CMS guidelines, NCCI edits, HIPAA privacy protocols, and payer coverage determinations to "
            f"minimize claim denials, accelerate reimbursement velocity, and protect organizational compliance. Furthermore, "
            f"my rapid fluency across EHR and practice management systems ensures seamless integration into your team's workflow."
        )

        # Dynamic closing paragraph
        closing_paragraph = (
            f"I am excited about the opportunity to contribute to {job.company}'s mission of delivering clinical and operational excellence. "
            f"I welcome the opportunity to discuss how my clinical diagnostic precision, CPC-certified coding accuracy, and dedication "
            f"to revenue cycle integrity will make an immediate impact on your team."
        )

        cover_letter = f"""{self.profile.name}
{self.profile.title}
{self.profile.location} | {self.profile.phone} | {self.profile.email}

{date_str}

Hiring Committee / Talent Acquisition Team
{job.company}
{job.location}

Subject: Application for {job.title} (Requisition / Posting: {job.id})

Dear Hiring Team at {job.company},

{hook_paragraph}

{body_clinical}

{body_technical}

{closing_paragraph}

Thank you for your time, consideration, and review of my qualifications.

Sincerely,

{self.profile.name}
AAPC Certified Professional Coder (CPC)
Bachelor of Dental Surgery (BDS)
{self.profile.email} | {self.profile.phone}
"""
        logger.debug("Generated cover letter for job %s at %s", job.id, job.company)
        return cover_letter.strip()
