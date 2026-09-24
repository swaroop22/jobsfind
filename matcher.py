"""
Intelligent ATS Job Matcher and Analyzer tailored to Sri Lakshmi Sravya Reddy Kovvuri's profile.
Evaluates job postings against clinical credentials, coding standards, and medical terminology.
"""

import re
import logging
from typing import List, Dict, Tuple, Set, Optional
from models import CandidateProfile, JobPosting, MatchResult

logger = logging.getLogger(__name__)


class ATSMatcher:
    """Enterprise ATS Matcher and scoring engine."""

    def __init__(self, profile: CandidateProfile):
        """
        Initialize the matcher with a CandidateProfile.

        Args:
            profile: Loaded and validated CandidateProfile.
        """
        self.profile = profile

        # Skill categories and their importance weights (0.0 to 1.0)
        self.taxonomy = {
            "certifications": {
                "weight": 0.30,
                "keywords": {
                    "cpc": "Certified Professional Coder (CPC)",
                    "certified professional coder": "Certified Professional Coder (CPC)",
                    "aapc": "American Academy of Professional Coders (AAPC)",
                    "ahima": "AHIMA Certification",
                    "ccs": "Certified Coding Specialist (CCS)",
                    "rhit": "RHIT",
                    "rhia": "RHIA",
                },
                "profile_has": ["cpc", "certified professional coder", "aapc"]
            },
            "coding_standards": {
                "weight": 0.25,
                "keywords": {
                    "icd-10": "ICD-10-CM",
                    "icd-10-cm": "ICD-10-CM",
                    "icd-10-pcs": "ICD-10-PCS",
                    "cpt": "CPT Coding",
                    "hcpcs": "HCPCS Level II",
                    "e/m": "E/M (Evaluation and Management)",
                    "evaluation and management": "E/M (Evaluation and Management)",
                    "cdt": "CDT (Dental Coding)",
                    "modifiers": "Modifiers (25, 59, etc.)"
                },
                "profile_has": ["icd-10", "icd-10-cm", "cpt", "hcpcs", "e/m", "evaluation and management", "cdt", "modifiers"]
            },
            "compliance_and_regulations": {
                "weight": 0.15,
                "keywords": {
                    "hipaa": "HIPAA Compliance",
                    "cms": "CMS Guidelines",
                    "ncci": "NCCI Edits",
                    "oig": "OIG Compliance",
                    "medical necessity": "Medical Necessity Verification",
                    "payer policies": "Payer Policies"
                },
                "profile_has": ["hipaa", "cms", "ncci", "oig", "medical necessity", "payer policies"]
            },
            "clinical_documentation_and_rcm": {
                "weight": 0.15,
                "keywords": {
                    "cdi": "Clinical Documentation Improvement (CDI)",
                    "clinical documentation": "Clinical Documentation",
                    "revenue cycle": "Revenue Cycle Management (RCM)",
                    "rcm": "Revenue Cycle Management (RCM)",
                    "denials": "Denials & Appeals Management",
                    "appeals": "Insurance Appeals",
                    "chart review": "Chart Auditing & Review",
                    "auditing": "Coding Auditing",
                    "ehr": "Electronic Health Records (EHR)",
                    "epic": "Epic EHR",
                    "cerner": "Cerner EHR",
                    "prior authorization": "Prior Authorization"
                },
                "profile_has": ["cdi", "clinical documentation", "revenue cycle", "rcm", "denials", "appeals", "chart review", "auditing", "ehr"]
            },
            "dental_and_clinical_expertise": {
                "weight": 0.15,
                "keywords": {
                    "dental": "Dental Clinical Expertise",
                    "dentist": "Dental Practice Knowledge",
                    "oral health": "Oral Health Terminology",
                    "anatomy": "Anatomic & Pathologic Terminology",
                    "pathology": "Pathology Understanding",
                    "medical terminology": "Medical Terminology"
                },
                "profile_has": ["dental", "dentist", "oral health", "anatomy", "pathology", "medical terminology"]
            }
        }

    def _clean_text(self, text: Optional[str]) -> str:
        """Sanitize text by replacing special characters and lowercasing."""
        if not text:
            return ""
        return re.sub(r"[^\w\s\-/]", " ", text.lower())

    def match(self, job: JobPosting) -> MatchResult:
        """
        Evaluate a job posting against candidate's profile.

        Args:
            job: JobPosting instance.

        Returns:
            MatchResult containing score, matched skills, gaps, strengths, and pitch.
        """
        job_title = job.title or ""
        job_desc = job.description or ""
        full_text = f"{job_title} {job_desc}".lower()
        cleaned_text = self._clean_text(full_text)

        matched_skills: Set[str] = set()
        missing_skills: Set[str] = set()
        strengths: List[str] = []
        improvement_tips: List[str] = []

        is_cpc_required = bool(re.search(r"\b(cpc|certified professional coder)\b", cleaned_text))
        is_dental_relevant = bool(re.search(r"\b(dental|dentistry|oral|bds|cdt)\b", cleaned_text))
        is_cdi_relevant = bool(re.search(r"\b(cdi|clinical documentation improvement)\b", cleaned_text))

        # Find total domain keyword hits in the job
        domain_hits = 0
        cat_scores: List[float] = []
        cat_weights: List[float] = []

        for cat_name, cat_data in self.taxonomy.items():
            cat_weight = float(cat_data["weight"])
            keywords_dict = cat_data["keywords"]
            candidate_keywords = set(cat_data["profile_has"])

            found_in_job: List[Tuple[str, str]] = []
            for kw_key, kw_label in keywords_dict.items():
                pattern = r"\b" + re.escape(kw_key) + r"\b"
                if re.search(pattern, cleaned_text):
                    found_in_job.append((kw_key, kw_label))

            if found_in_job:
                domain_hits += len(found_in_job)
                matched_count = 0
                for kw_key, kw_label in found_in_job:
                    if kw_key in candidate_keywords:
                        matched_skills.add(kw_label)
                        matched_count += 1
                    else:
                        missing_skills.add(kw_label)

                cat_ratio = matched_count / len(found_in_job)
                cat_scores.append(cat_ratio * cat_weight)
                cat_weights.append(cat_weight)

        if domain_hits == 0:
            # Irrelevant or completely unrelated job posting
            raw_score = 15.0
        else:
            # Score based on candidate's coverage of the job's stated requirements
            sum_weights = sum(cat_weights)
            coverage_score = (sum(cat_scores) / sum_weights) * 100.0 if sum_weights > 0 else 20.0
            density_factor = min(1.0, domain_hits / 3.0)
            raw_score = coverage_score * (0.6 + 0.4 * density_factor)

        # High-impact bonuses:
        # 1. CPC match bonus
        if is_cpc_required:
            raw_score = min(100.0, raw_score + 15.0)
            strengths.append("Direct match on primary certification: Certified Professional Coder (CPC) credentialed by AAPC.")

        # 2. Dental synergy bonus
        if is_dental_relevant:
            raw_score = min(100.0, raw_score + 20.0)
            strengths.append("Exceptional Advantage: Former licensed Dentist (BDS) applying for dental coding/claims with deep clinical anatomy understanding.")

        # 3. Location bonus
        job_loc_lower = (job.location or "").lower()
        if job.is_remote or "remote" in job_loc_lower:
            strengths.append("Remote Flexibility: Role is Remote/Hybrid, ideal for home-based coding workflows.")
        elif "oh" in job_loc_lower or "ohio" in job_loc_lower:
            strengths.append("Local Advantage: Position is located in candidate's home state of Ohio.")

        # Title alignment check
        title_lower = job_title.lower()
        for target in self.profile.target_roles:
            if target.lower() in title_lower or any(word in title_lower for word in ["coder", "coding", "cdi", "claims", "billing"]):
                strengths.append(f"Target Role Match: Job title aligns directly with '{target}'.")
                break

        # If zero domain hits and no relevant title, cap score low
        if domain_hits == 0 and not any(w in title_lower for w in ["coder", "coding", "claims", "billing", "cdi", "dental"]):
            raw_score = min(raw_score, 25.0)

        # Generate actionable improvement tips
        if "Epic EHR" in missing_skills or "Cerner EHR" in missing_skills:
            improvement_tips.append("Role mentions specific EHR (e.g. Epic/Cerner). Highlight your EHR fluency and fast adaptability to clinical health software.")
        if "ICD-10-PCS" in missing_skills:
            improvement_tips.append("Inpatient coding role: Emphasize your deep surgical/procedural anatomy knowledge to position yourself for ICD-10-PCS workflows.")
        if not improvement_tips:
            improvement_tips.append("Your background aligns strongly. Emphasize your clinician-to-coder translation skills in the application.")

        # Recommended custom pitch
        if is_dental_relevant:
            pitch = (
                "Highlight your rare dual qualification: a clinically trained Dentist (BDS) paired with AAPC Certified "
                "Professional Coder (CPC) credentialing. Emphasize zero-ramp clinical comprehension of complex dental "
                "procedures, CDT/CPT mapping, and preventing documentation denials."
            )
        elif is_cdi_relevant:
            pitch = (
                "Pitch your clinical practitioner background to bridge communication between physicians and billing teams. "
                "Highlight how your firsthand experience documenting patient treatments allows you to spot chart ambiguities and ensure medical necessity."
            )
        else:
            pitch = (
                "Position yourself as a CPC-certified coder with a clinical advantage: you understand provider intent from "
                "the practitioner side, ensuring superior ICD-10-CM and CPT accuracy, lower denial rates, and compliant revenue cycle alignment."
            )

        final_score = round(min(100.0, max(20.0, raw_score)), 1)
        logger.debug("Matched job '%s' (ID: %s) -> Score: %.1f", job.title, job.id, final_score)

        return MatchResult(
            job=job,
            score=final_score,
            matched_skills=sorted(list(matched_skills)),
            missing_skills=sorted(list(missing_skills)),
            is_cpc_required=is_cpc_required,
            is_dental_relevant=is_dental_relevant,
            strengths=strengths,
            improvement_tips=improvement_tips,
            recommended_pitch=pitch
        )
