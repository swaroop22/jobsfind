"""
Unit tests for resume_generator.py TailoredResumeGenerator service.
"""

from pathlib import Path
import pytest
from models import CandidateProfile, JobPosting
from matcher import ATSMatcher
from resume_generator import TailoredResumeGenerator, CURATED_HEALTHCARE_JOBS


@pytest.fixture
def resume_generator(profile: CandidateProfile, matcher: ATSMatcher) -> TailoredResumeGenerator:
    return TailoredResumeGenerator(profile, matcher)


class TestTailoredResumeGenerator:
    def test_dental_resume_tailoring(
        self,
        resume_generator: TailoredResumeGenerator,
        sample_dental_job: JobPosting,
        profile: CandidateProfile
    ):
        resume = resume_generator.generate(sample_dental_job)

        # Basic candidate information
        assert profile.name in resume
        assert profile.email in resume
        assert profile.phone in resume
        assert "AAPC Certified Professional Coder (CPC)" in resume
        assert "Bachelor of Dental Surgery (BDS)" in resume

        # Dental-specific tailoring
        assert "CDT" in resume
        assert "Dental Billing" in resume or "dental" in resume.lower()
        assert "oral" in resume.lower() or "cross-coding" in resume.lower()

    def test_medical_coding_resume_tailoring(
        self,
        resume_generator: TailoredResumeGenerator,
        sample_cpc_job: JobPosting,
        profile: CandidateProfile
    ):
        resume = resume_generator.generate(sample_cpc_job)

        assert profile.name in resume
        assert "Certified Professional Coder (CPC)" in resume
        assert "ICD-10-CM" in resume
        assert "CPT" in resume
        assert sample_cpc_job.company in resume

    def test_cdi_resume_tailoring(
        self,
        resume_generator: TailoredResumeGenerator,
        profile: CandidateProfile
    ):
        cdi_job = JobPosting(
            id="test-cdi-99",
            title="Clinical Documentation Improvement (CDI) Specialist",
            company="OhioHealth",
            location="Columbus, OH",
            is_remote=True,
            description="Review inpatient records, query physicians, improve clinical documentation completeness, CMS guidelines."
        )
        resume = resume_generator.generate(cdi_job)

        assert "Clinical Documentation" in resume
        assert "OhioHealth" in resume
        assert "CMS" in resume
        assert "clarification" in resume.lower() or "queries" in resume.lower()

    def test_custom_ad_hoc_job_resume(
        self,
        resume_generator: TailoredResumeGenerator
    ):
        custom_job = JobPosting(
            id="adhoc-01",
            title="Revenue Cycle Claims Auditor",
            company="MetroHealth",
            location="Cleveland, OH",
            is_remote=False,
            description="Investigate denied claims, modifier 25 review, appeal letters, RCM integrity."
        )
        resume = resume_generator.generate(custom_job)

        assert "MetroHealth" in resume
        assert "Revenue Cycle" in resume
        assert "appeals" in resume.lower() or "denied" in resume.lower()

    def test_batch_curated_generation(
        self,
        resume_generator: TailoredResumeGenerator
    ):
        # Generate resumes for all curated jobs and verify none are empty
        for job in CURATED_HEALTHCARE_JOBS:
            res_md = resume_generator.generate(job)
            assert len(res_md) > 500
            assert job.company in res_md
            assert "AAPC Certified Professional Coder (CPC)" in res_md

    def test_generate_pdf_to_bytesio(
        self,
        resume_generator: TailoredResumeGenerator,
        sample_cpc_job: JobPosting
    ):
        import io
        buf = io.BytesIO()
        resume_generator.generate_pdf(sample_cpc_job, buf)
        pdf_bytes = buf.getvalue()

        # PDF files must start with the standard header %PDF-
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 1000

    def test_generate_pdf_to_file(
        self,
        resume_generator: TailoredResumeGenerator,
        sample_dental_job: JobPosting,
        tmp_path: Path
    ):
        pdf_path = tmp_path / "test_dental_resume.pdf"
        resume_generator.generate_pdf(sample_dental_job, pdf_path)

        assert pdf_path.is_file()
        assert pdf_path.stat().st_size > 1000
        content = pdf_path.read_bytes()
        assert content.startswith(b"%PDF-")
