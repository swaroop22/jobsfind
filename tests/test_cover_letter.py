"""
Unit tests for CoverLetterGenerator dynamic letter creation and profile consistency.
"""

from models import CandidateProfile, JobPosting
from matcher import ATSMatcher
from cover_letter import CoverLetterGenerator


class TestCoverLetterGenerator:
    def test_dental_tailored_cover_letter(
        self,
        cover_letter_gen: CoverLetterGenerator,
        matcher: ATSMatcher,
        sample_dental_job: JobPosting,
        profile: CandidateProfile
    ):
        match_res = matcher.match(sample_dental_job)
        letter = cover_letter_gen.generate(sample_dental_job, match_res)

        # Dynamic profile information checks
        assert profile.name in letter
        assert profile.email in letter
        assert profile.phone in letter
        assert sample_dental_job.company in letter
        assert sample_dental_job.title in letter

        # Clinical dental hooks
        assert "Bachelor of Dental Surgery (BDS)" in letter
        assert "AAPC Certified Professional Coder (CPC)" in letter
        assert "CDT" in letter

    def test_medical_coding_tailored_cover_letter(
        self,
        cover_letter_gen: CoverLetterGenerator,
        matcher: ATSMatcher,
        sample_cpc_job: JobPosting,
        profile: CandidateProfile
    ):
        match_res = matcher.match(sample_cpc_job)
        letter = cover_letter_gen.generate(sample_cpc_job, match_res)

        assert profile.name in letter
        assert profile.email in letter
        assert profile.phone in letter
        assert sample_cpc_job.company in letter
        assert sample_cpc_job.title in letter
        assert "Certified Professional Coder (CPC)" in letter
