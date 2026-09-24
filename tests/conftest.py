"""
Pytest configuration and shared fixtures for JobsFind test suite.
"""

import sys
from pathlib import Path
import pytest

# Ensure root directory is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models import CandidateProfile, JobPosting
from matcher import ATSMatcher
from cover_letter import CoverLetterGenerator
from tracker import ApplicationTracker


@pytest.fixture
def profile_path() -> Path:
    """Fixture providing path to valid candidate profile JSON."""
    return ROOT_DIR / "resume_profile.json"


@pytest.fixture
def profile(profile_path: Path) -> CandidateProfile:
    """Fixture providing loaded CandidateProfile instance."""
    return CandidateProfile.load_from_json(profile_path)


@pytest.fixture
def matcher(profile: CandidateProfile) -> ATSMatcher:
    """Fixture providing ATSMatcher instance."""
    return ATSMatcher(profile)


@pytest.fixture
def cover_letter_gen(profile: CandidateProfile) -> CoverLetterGenerator:
    """Fixture providing CoverLetterGenerator instance."""
    return CoverLetterGenerator(profile)


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Fixture providing an isolated SQLite database path cleaned up after each test."""
    db_file = tmp_path / "test_applications.db"
    yield db_file
    if db_file.exists():
        try:
            db_file.unlink()
        except Exception:
            pass


@pytest.fixture
def tracker(temp_db: Path) -> ApplicationTracker:
    """Fixture providing ApplicationTracker bound to isolated temporary database."""
    return ApplicationTracker(db_path=temp_db)


@pytest.fixture
def sample_cpc_job() -> JobPosting:
    """Sample outpatient medical coding job requiring CPC and ICD-10."""
    return JobPosting(
        id="fixture-cpc-01",
        title="Certified Outpatient Medical Coder (CPC)",
        company="MetroHealth System",
        location="Cleveland, OH",
        is_remote=False,
        description="Seeking Certified Professional Coder (CPC). Requires ICD-10-CM, CPT, HCPCS, E/M coding, HIPAA compliance, and chart review."
    )


@pytest.fixture
def sample_dental_job() -> JobPosting:
    """Sample dental billing & cross-coding job."""
    return JobPosting(
        id="fixture-dent-02",
        title="Dental Billing and Coding Specialist",
        company="Apex Dental Partners",
        location="Remote",
        is_remote=True,
        description="Requires dental clinic understanding, CDT and CPT cross coding, and dental anatomy."
    )
