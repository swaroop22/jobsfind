"""
Unit tests for tracker.py SQLite application persistence.
"""

from pathlib import Path
import pytest
from tracker import ApplicationTracker
from models import ApplicationStatus
from exceptions import DatabaseError


class TestApplicationTracker:
    def test_add_and_get_application(self, tracker: ApplicationTracker):
        app_id = tracker.add_application(
            job_title="Certified Medical Coder",
            company="Cleveland Clinic",
            location="Cleveland, OH",
            status=ApplicationStatus.APPLIED.value,
            match_score=88.5,
            notes="Submitted online",
            job_url="https://jobs.clevelandclinic.org"
        )
        assert app_id > 0

        records = tracker.get_all()
        assert len(records) == 1
        rec = records[0]
        assert rec.id == app_id
        assert rec.job_title == "Certified Medical Coder"
        assert rec.company == "Cleveland Clinic"
        assert rec.status == "Applied"
        assert rec.match_score == 88.5

    def test_update_status_and_notes(self, tracker: ApplicationTracker):
        app_id = tracker.add_application(
            job_title="CDI Specialist",
            company="OhioHealth",
            location="Columbus, OH"
        )

        success = tracker.update_status(app_id, ApplicationStatus.INTERVIEWING.value, notes="First interview scheduled")
        assert success is True

        records = tracker.get_all()
        assert records[0].status == "Interviewing"
        assert records[0].notes == "First interview scheduled"

    def test_delete_application(self, tracker: ApplicationTracker):
        app_id = tracker.add_application(
            job_title="Coding Specialist",
            company="Premier Health",
            location="Dayton, OH"
        )
        assert len(tracker.get_all()) == 1

        deleted = tracker.delete_application(app_id)
        assert deleted is True
        assert len(tracker.get_all()) == 0

    def test_get_statistics(self, tracker: ApplicationTracker):
        tracker.add_application("Job 1", "Company A", "Ohio", status="Saved", match_score=70.0)
        tracker.add_application("Job 2", "Company B", "Remote", status="Applied", match_score=90.0)
        tracker.add_application("Job 3", "Company C", "Ohio", status="Interviewing", match_score=80.0)

        stats = tracker.get_statistics()
        assert stats["total"] == 3
        assert stats["saved"] == 1
        assert stats["applied"] == 1
        assert stats["interviewing"] == 1
        assert stats["offers"] == 0
        assert stats["avg_match_score"] == 80.0

    def test_to_dataframe(self, tracker: ApplicationTracker):
        # Empty tracker
        df_empty = tracker.to_dataframe()
        assert df_empty.empty
        assert "Job Title" in df_empty.columns

        # Non-empty tracker
        tracker.add_application("Job 1", "Company A", "Ohio", match_score=85.0)
        df = tracker.to_dataframe()
        assert len(df) == 1
        assert df.iloc[0]["Company"] == "Company A"
        assert df.iloc[0]["Match Score %"] == "85.0%"

    def test_validation_missing_fields_raises_error(self, tracker: ApplicationTracker):
        with pytest.raises(ValueError):
            tracker.add_application(job_title="", company="Test")

        with pytest.raises(ValueError):
            tracker.add_application(job_title="Test", company="")
