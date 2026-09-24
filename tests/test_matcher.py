"""
Unit tests for ATSMatcher algorithm and scoring behavior.
"""

import pytest
from models import JobPosting
from matcher import ATSMatcher


class TestATSMatcher:
    def test_cpc_medical_coding_job_match(self, matcher: ATSMatcher, sample_cpc_job: JobPosting):
        result = matcher.match(sample_cpc_job)
        assert result.is_cpc_required is True
        assert result.score >= 75.0
        assert any("CPC" in s for s in result.matched_skills)
        assert any("ICD-10" in s for s in result.matched_skills)
        assert len(result.strengths) > 0
        assert "CPC" in result.recommended_pitch or "coder" in result.recommended_pitch

    def test_dental_job_clinician_bonus(self, matcher: ATSMatcher, sample_dental_job: JobPosting):
        result = matcher.match(sample_dental_job)
        assert result.is_dental_relevant is True
        assert result.score >= 75.0
        assert any("Dentist" in s or "Dental" in s for s in result.strengths)
        assert "Dentist" in result.recommended_pitch or "dental" in result.recommended_pitch

    def test_unrelated_job_low_match(self, matcher: ATSMatcher):
        unrelated = JobPosting(
            id="test-swe-99",
            title="Senior Java Backend Engineer",
            company="FinTech Payments Corp",
            location="New York, NY",
            is_remote=True,
            description="Seeking Kubernetes, Kafka, AWS, Docker, Spring Boot developer."
        )
        result = matcher.match(unrelated)
        assert result.is_cpc_required is False
        assert result.is_dental_relevant is False
        assert result.score <= 50.0

    def test_empty_or_minimal_job_posting(self, matcher: ATSMatcher):
        minimal = JobPosting(
            id="empty-01",
            title="",
            company="",
            location="",
            is_remote=False,
            description=""
        )
        result = matcher.match(minimal)
        assert 20.0 <= result.score <= 30.0
        assert len(result.matched_skills) == 0

    def test_score_boundary_limits(self, matcher: ATSMatcher):
        # Even with extensive matches, score should not exceed 100.0
        perfect_job = JobPosting(
            id="perfect-01",
            title="Certified Professional Coder (CPC) Dental & Outpatient CDI Specialist",
            company="Ohio Health System",
            location="Dayton, OH",
            is_remote=True,
            description=(
                "AAPC CPC required. CDT dental coding, CPT, ICD-10-CM, HCPCS, E/M, HIPAA, CMS, "
                "NCCI edits, OIG, CDI, RCM, chart review, medical terminology, dental anatomy."
            )
        )
        result = matcher.match(perfect_job)
        assert result.score <= 100.0
        assert result.score >= 90.0
