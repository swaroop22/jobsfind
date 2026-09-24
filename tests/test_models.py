"""
Unit tests for models.py data structures, validation, and serialization.
"""

import json
from pathlib import Path
import pytest

from models import CandidateProfile, JobPosting, MatchResult, ApplicationRecord, ApplicationStatus
from exceptions import ProfileNotFoundError, ProfileValidationError


class TestCandidateProfile:
    def test_load_valid_profile(self, profile_path: Path):
        profile = CandidateProfile.load_from_json(profile_path)
        assert profile.name == "Sri Lakshmi Sravya Reddy Kovvuri"
        assert "Certified Professional Coder (CPC)" in [c["name"] for c in profile.certifications]
        assert "ICD-10-CM" in profile.skills["coding_systems"]
        assert "HIPAA" in profile.skills["compliance_and_regulations"]
        assert "BDS" in profile.education[0]["degree"]

    def test_load_nonexistent_profile_raises_error(self, tmp_path: Path):
        fake_path = tmp_path / "nonexistent_profile.json"
        with pytest.raises(ProfileNotFoundError):
            CandidateProfile.load_from_json(fake_path)

    def test_load_malformed_json_raises_error(self, tmp_path: Path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("NOT A VALID JSON {", encoding="utf-8")
        with pytest.raises(ProfileValidationError):
            CandidateProfile.load_from_json(bad_json)

    def test_load_missing_required_candidate_fields_raises_error(self, tmp_path: Path):
        incomplete_json = tmp_path / "incomplete.json"
        incomplete_json.write_text(json.dumps({"candidate": {"name": "Only Name"}}), encoding="utf-8")
        with pytest.raises(ProfileValidationError) as excinfo:
            CandidateProfile.load_from_json(incomplete_json)
        assert "missing required fields" in str(excinfo.value)

    def test_all_keywords(self, profile: CandidateProfile):
        keywords = profile.all_keywords()
        assert "ICD-10-CM" in keywords
        assert "CPT" in keywords
        assert "Certified Professional Coder (CPC)" in keywords

    def test_to_dict_serialization(self, profile: CandidateProfile):
        d = profile.to_dict()
        assert isinstance(d, dict)
        assert d["name"] == profile.name
        assert "skills" in d


class TestJobPostingAndApplicationModels:
    def test_job_posting_to_dict_and_from_dict(self, sample_cpc_job: JobPosting):
        job_dict = sample_cpc_job.to_dict()
        assert job_dict["id"] == "fixture-cpc-01"
        assert job_dict["company"] == "MetroHealth System"

        reconstructed = JobPosting.from_dict(job_dict)
        assert reconstructed.id == sample_cpc_job.id
        assert reconstructed.title == sample_cpc_job.title
        assert reconstructed.company == sample_cpc_job.company

    def test_application_status_values(self):
        statuses = ApplicationStatus.values()
        assert "Saved" in statuses
        assert "Applied" in statuses
        assert "Interviewing" in statuses
        assert "Offer" in statuses
        assert "Rejected" in statuses

    def test_application_record_to_dict(self):
        rec = ApplicationRecord(
            id=1,
            job_title="Medical Coder",
            company="Cleveland Clinic",
            location="Remote",
            status=ApplicationStatus.APPLIED.value,
            applied_date="2026-09-23",
            match_score=92.5,
            notes="Submitted",
            job_url="https://example.com"
        )
        d = rec.to_dict()
        assert d["id"] == 1
        assert d["status"] == "Applied"
        assert d["match_score"] == 92.5
