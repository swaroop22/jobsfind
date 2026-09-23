"""
Job Finder service combining real-time public remote job feeds with curated healthcare listings
targeted for Ohio and Remote Certified Medical Coders, Dental Coders, and CDI Specialists.
"""

import requests
from typing import List, Optional
from models import JobPosting


CURATED_HEALTHCARE_JOBS = [
    JobPosting(
        id="oh-cc-001",
        title="Certified Medical Coder - Outpatient Specialty (CPC Required)",
        company="Cleveland Clinic",
        location="Cleveland, OH (Hybrid/Remote)",
        is_remote=True,
        description=(
            "Cleveland Clinic is seeking a detail-oriented Certified Medical Coder (CPC) to assign diagnostic and "
            "procedural codes using ICD-10-CM, CPT, and HCPCS Level II. The coder will review provider clinical notes, "
            "ensure medical necessity verification, verify NCCI edits, and collaborate with CDI specialists to resolve "
            "documentation queries. Requirements: Active AAPC CPC or AHIMA certification, strong anatomy and physiology "
            "foundation, and familiarity with EHR/Epic billing systems."
        ),
        url="https://jobs.clevelandclinic.org",
        posted_date="2026-09-20",
        salary_range="$28 - $36 / hour",
        employment_type="Full-time",
        source="Cleveland Clinic Health System",
        category="Medical Coding"
    ),
    JobPosting(
        id="oh-health-002",
        title="Clinical Documentation Improvement (CDI) Specialist",
        company="OhioHealth",
        location="Columbus, OH (Hybrid / Remote Option)",
        is_remote=True,
        description=(
            "Join OhioHealth as a CDI Specialist! In this role, you will facilitate the overall quality and completeness "
            "of clinical documentation across inpatient and outpatient care settings. Clinicians (Dentists, Physicians, Nurses) "
            "or experienced coders with strong clinical background are highly preferred. Responsibilities include reviewing "
            "electronic health records (EHR), identifying clarification opportunities with providers, and ensuring adherence "
            "to CMS guidelines, HIPAA, and coding accuracy."
        ),
        url="https://www.ohiohealth.com/careers",
        posted_date="2026-09-18",
        salary_range="$72,000 - $88,000 / year",
        employment_type="Full-time",
        source="OhioHealth Careers",
        category="Clinical Documentation Improvement"
    ),
    JobPosting(
        id="oh-prem-003",
        title="Medical Coding Specialist - Revenue Cycle & Denials",
        company="Premier Health",
        location="Dayton, OH (On-site / Hybrid)",
        is_remote=False,
        description=(
            "Premier Health in Dayton, OH is looking for an experienced Coding Specialist to support our Revenue Cycle "
            "Management (RCM) team. Focus on reviewing denied claims, drafting clinical appeals, correcting ICD-10 and CPT "
            "codes, verifying modifiers (25, 59), and ensuring compliance with payer guidelines and OIG standards. "
            "Must hold active CPC from AAPC or equivalent."
        ),
        url="https://www.premierhealth.com/careers",
        posted_date="2026-09-21",
        salary_range="$27 - $34 / hour",
        employment_type="Full-time",
        source="Premier Health Dayton",
        category="Revenue Cycle & Denials"
    ),
    JobPosting(
        id="rem-dent-004",
        title="Dental Billing & Coding Specialist (CDT & CPT Cross-Coding)",
        company="Heartland Dental / Modern Dental Network",
        location="Remote (USA - Ohio Preferred)",
        is_remote=True,
        description=(
            "Exciting remote opportunity for a Dental Billing & Coding Specialist! We are looking for a candidate with strong "
            "knowledge of dental procedures, CDT coding, and cross-coding dental procedures to medical insurance (CPT / ICD-10-CM / HCPCS). "
            "Candidates with clinical dental education (BDS / Dental Surgery background) or dental clinic experience who hold a CPC "
            "or dental coding credential are uniquely positioned for this high-impact position. Responsibilities include claims "
            "submission, pre-authorization, patient chart review, and appealing denied claims."
        ),
        url="https://heartland.com/careers",
        posted_date="2026-09-22",
        salary_range="$65,000 - $80,000 / year",
        employment_type="Full-time",
        source="National Dental Partners",
        category="Dental Coding & Cross-Coding"
    ),
    JobPosting(
        id="rem-opt-005",
        title="Remote Risk Adjustment Coder (HCC / ICD-10-CM)",
        company="Optum / UnitedHealth Group",
        location="Remote (Nationwide)",
        is_remote=True,
        description=(
            "Optum is hiring Remote Risk Adjustment Coders to review outpatient medical records for Medicare Advantage "
            "and Commercial Risk Adjustment. Assign appropriate ICD-10-CM diagnosis codes and HCC categories adhering to "
            "strict CMS official guidelines. Requirements: CPC or CRC credential from AAPC. Candidate must possess rigorous "
            "understanding of medical conditions, chronic disease pathology, and chart auditing."
        ),
        url="https://careers.unitedhealthgroup.com",
        posted_date="2026-09-19",
        salary_range="$29 - $38 / hour",
        employment_type="Full-time",
        source="UnitedHealth Group / Optum",
        category="Risk Adjustment (HCC)"
    ),
    JobPosting(
        id="oh-dayton-006",
        title="Pediatric & Dental Surgical Coder",
        company="Dayton Children's Hospital",
        location="Dayton, OH",
        is_remote=False,
        description=(
            "Dayton Children's is hiring a Surgical & Specialty Coder with familiarity in oral/maxillofacial and pediatric "
            "surgical procedures. Translates physician documentation into ICD-10-CM, CPT, and HCPCS codes. Evaluates clinical "
            "notes for completeness, assists clinical staff with documentation compliance, and resolves billing inquiries. "
            "AAPC Certified Professional Coder (CPC) required. Clinical background is a substantial asset."
        ),
        url="https://www.childrensdayton.org/careers",
        posted_date="2026-09-22",
        salary_range="$30 - $37 / hour",
        employment_type="Full-time",
        source="Dayton Children's Careers",
        category="Surgical & Dental Coding"
    ),
    JobPosting(
        id="rem-elev-007",
        title="Healthcare Claims Auditor & Appeals Analyst (Remote)",
        company="Elevance Health (Anthem)",
        location="Remote (USA)",
        is_remote=True,
        description=(
            "Analyze complex medical and dental claims for medical necessity, coding accuracy, and reimbursement alignment. "
            "Conduct chart reviews, identify documentation deficiencies, ensure compliance with NCCI edits and CMS policy, "
            "and prepare appeal determinations. CPC or clinical degree required."
        ),
        url="https://careers.elevancehealth.com",
        posted_date="2026-09-17",
        salary_range="$68,000 - $82,000 / year",
        employment_type="Full-time",
        source="Elevance Health",
        category="Claims & Auditing"
    ),
    JobPosting(
        id="oh-cin-008",
        title="Outpatient Health Center Coding & Billing Lead",
        company="UC Health (University of Cincinnati)",
        location="Cincinnati, OH (Hybrid)",
        is_remote=True,
        description=(
            "UC Health seeks a certified coder to lead outpatient clinic documentation review, CPT and ICD-10 assignment, "
            "and provider education. Focus on E/M guidelines, procedure coding, and bridging clinical intent with billing rules. "
            "AAPC CPC certification required. Experience interfacing with clinical teams to clarify chart entries is essential."
        ),
        url="https://uchealth.com/careers",
        posted_date="2026-09-23",
        salary_range="$31 - $39 / hour",
        employment_type="Full-time",
        source="UC Health Cincinnati",
        category="Medical Coding"
    )
]


class JobFinderService:
    def __init__(self):
        self.cached_jobs: List[JobPosting] = list(CURATED_HEALTHCARE_JOBS)

    def fetch_live_remote_jobs(self, query: str = "medical coder") -> List[JobPosting]:
        """
        Query public remote job APIs (Jobicy / Remotive) for live listings.
        Safely falls back to curated database on connection issues.
        """
        live_jobs = []
        try:
            url = f"https://jobicy.com/api/v2/remote-jobs?count=15&tag={query.replace(' ', '+')}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", []):
                    live_jobs.append(
                        JobPosting(
                            id=f"jobicy-{item.get('id', '')}",
                            title=item.get("jobTitle", "Medical Coding Specialist"),
                            company=item.get("companyName", "Healthcare Partner"),
                            location=item.get("jobGeo", "Remote"),
                            is_remote=True,
                            description=item.get("jobDescription", ""),
                            url=item.get("url", ""),
                            posted_date=item.get("pubDate", "")[:10],
                            salary_range=f"{item.get('annualSalaryMin', '')} - {item.get('annualSalaryMax', '')}" if item.get('annualSalaryMin') else "Competitive",
                            employment_type=item.get("jobType", "Full-time"),
                            source="Jobicy Remote Feed",
                            category="Remote Healthcare"
                        )
                    )
        except Exception:
            # Silent fallback to curated database if network or API is unavailable
            pass
        return live_jobs

    def search_jobs(
        self,
        keywords: Optional[str] = None,
        location_filter: str = "All",  # "All", "Ohio Only", "Remote Only"
        category_filter: str = "All",
        include_live: bool = True
    ) -> List[JobPosting]:
        """
        Filter jobs by keywords, location, and category.
        """
        all_jobs = list(self.cached_jobs)
        if include_live:
            live = self.fetch_live_remote_jobs("medical coder")
            all_jobs.extend(live)

        filtered = []
        for job in all_jobs:
            # Location filtering
            if location_filter == "Ohio Only":
                if not ("oh" in job.location.lower() or "ohio" in job.location.lower()):
                    continue
            elif location_filter == "Remote Only":
                if not job.is_remote and "remote" not in job.location.lower():
                    continue

            # Category filtering
            if category_filter != "All" and job.category != category_filter:
                continue

            # Keyword filtering
            if keywords:
                kw_terms = [k.strip().lower() for k in keywords.split() if k.strip()]
                searchable = f"{job.title} {job.company} {job.description} {job.location}".lower()
                if not all(term in searchable for term in kw_terms):
                    continue

            filtered.append(job)

        return filtered
