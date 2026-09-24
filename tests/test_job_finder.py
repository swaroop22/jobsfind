"""
Unit tests for JobFinderService search filtering and live feed fallback.
"""

from unittest.mock import MagicMock
import pytest
from job_finder import JobFinderService
from models import JobPosting


class TestJobFinderService:
    def test_search_curated_all(self):
        finder = JobFinderService()
        jobs = finder.search_jobs(include_live=False)
        assert len(jobs) >= 8
        assert any(j.company == "Cleveland Clinic" for j in jobs)

    def test_filter_ohio_only(self):
        finder = JobFinderService()
        ohio_jobs = finder.search_jobs(location_filter="Ohio Only", include_live=False)
        for job in ohio_jobs:
            loc = job.location.lower()
            assert "oh" in loc or "ohio" in loc

    def test_filter_remote_only(self):
        finder = JobFinderService()
        remote_jobs = finder.search_jobs(location_filter="Remote Only", include_live=False)
        for job in remote_jobs:
            assert job.is_remote or "remote" in job.location.lower()

    def test_filter_by_keyword(self):
        finder = JobFinderService()
        dental_jobs = finder.search_jobs(keywords="dental", include_live=False)
        assert len(dental_jobs) > 0
        for job in dental_jobs:
            searchable = f"{job.title} {job.company} {job.description} {job.location}".lower()
            assert "dental" in searchable

    def test_mock_live_remote_jobs_success(self):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jobs": [
                {
                    "id": 99999,
                    "jobTitle": "Lead Remote Medical Coder",
                    "companyName": "HealthCorp USA",
                    "jobGeo": "Remote",
                    "jobDescription": "Need CPC coder for telehealth.",
                    "url": "https://example.com/job/99999",
                    "pubDate": "2026-09-22 10:00:00",
                    "annualSalaryMin": "70000",
                    "annualSalaryMax": "85000",
                    "jobType": "Full-time"
                }
            ]
        }
        mock_session.get.return_value = mock_response

        finder = JobFinderService(session=mock_session)
        live_jobs = finder.fetch_live_remote_jobs("medical coder")
        assert len(live_jobs) == 1
        assert live_jobs[0].id == "jobicy-99999"
        assert live_jobs[0].company == "HealthCorp USA"
        assert live_jobs[0].is_remote is True

    def test_mock_live_remote_jobs_network_failure_fallback(self):
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Connection timeout")

        finder = JobFinderService(session=mock_session)
        live_jobs = finder.fetch_live_remote_jobs("medical coder")
        assert live_jobs == []
        # Fallback to curated jobs still works
        all_jobs = finder.search_jobs(include_live=True)
        assert len(all_jobs) >= 8
