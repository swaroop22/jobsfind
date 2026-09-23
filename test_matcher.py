"""
Unit tests for the jobsfind ATS Matcher, Profile parser, Cover Letter generator, and Application Tracker.
"""

import unittest
from pathlib import Path
from models import CandidateProfile, JobPosting
from matcher import ATSMatcher
from cover_letter import CoverLetterGenerator
from tracker import ApplicationTracker


class TestJobsFind(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        profile_path = Path(__file__).parent / "resume_profile.json"
        cls.profile = CandidateProfile.load_from_json(profile_path)
        cls.matcher = ATSMatcher(cls.profile)
        cls.generator = CoverLetterGenerator(cls.profile)

    def test_profile_loading(self):
        self.assertEqual(self.profile.name, "Sri Lakshmi Sravya Reddy Kovvuri")
        self.assertIn("Certified Professional Coder (CPC)", [c["name"] for c in self.profile.certifications])
        self.assertIn("ICD-10-CM", self.profile.skills["coding_systems"])
        self.assertIn("HIPAA", self.profile.skills["compliance_and_regulations"])

    def test_medical_coding_job_match(self):
        job = JobPosting(
            id="test-cpc-01",
            title="Certified Medical Coder (CPC)",
            company="MetroHealth Ohio",
            location="Cleveland, OH",
            is_remote=False,
            description="Seeking CPC certified medical coder. Requires ICD-10-CM, CPT, HCPCS, E/M coding, HIPAA compliance, and chart review."
        )
        res = self.matcher.match(job)
        self.assertTrue(res.is_cpc_required)
        self.assertGreaterEqual(res.score, 75.0)
        self.assertTrue(any("CPC" in s for s in res.matched_skills))
        self.assertTrue(any("ICD-10" in s for s in res.matched_skills))

    def test_dental_job_bonus(self):
        job = JobPosting(
            id="test-dent-01",
            title="Dental Billing and Coding Specialist",
            company="Dental Network",
            location="Remote",
            is_remote=True,
            description="Requires dental clinic understanding, CDT and CPT cross coding, and dental anatomy."
        )
        res = self.matcher.match(job)
        self.assertTrue(res.is_dental_relevant)
        self.assertGreaterEqual(res.score, 75.0)
        self.assertTrue(any("Dentist" in s or "Dental" in s for s in res.strengths))

    def test_unrelated_job_low_match(self):
        job = JobPosting(
            id="test-unrelated",
            title="Senior Java Backend Engineer",
            company="FinTech Corp",
            location="New York, NY",
            is_remote=True,
            description="Must know Kubernetes, Spring Boot, Microservices, and Kafka."
        )
        res = self.matcher.match(job)
        self.assertFalse(res.is_cpc_required)
        self.assertFalse(res.is_dental_relevant)
        self.assertLess(res.score, 60.0)

    def test_cover_letter_generation(self):
        job = JobPosting(
            id="test-cl-01",
            title="Certified Medical Coder",
            company="OhioHealth",
            location="Columbus, OH",
            is_remote=True,
            description="Certified coder with CPC and EHR experience."
        )
        res = self.matcher.match(job)
        letter = self.generator.generate(job, res)
        self.assertIn("Sri Lakshmi Sravya Reddy Kovvuri", letter)
        self.assertIn("OhioHealth", letter)
        self.assertIn("Certified Professional Coder (CPC)", letter)
        self.assertIn("Bachelor of Dental Surgery (BDS)", letter)

    def test_tracker_db(self):
        test_db = Path(__file__).parent / "test_applications.db"
        if test_db.exists():
            test_db.unlink()

        tracker = ApplicationTracker(db_path=test_db)
        app_id = tracker.add_application(
            job_title="Medical Coder",
            company="Test Hospital",
            location="Dayton, OH",
            status="Applied",
            match_score=88.5
        )
        self.assertIsNotNone(app_id)
        records = tracker.get_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].company, "Test Hospital")

        tracker.update_status(app_id, "Interviewing", notes="First round phone screen scheduled")
        updated = tracker.get_all()[0]
        self.assertEqual(updated.status, "Interviewing")
        self.assertEqual(updated.notes, "First round phone screen scheduled")

        if test_db.exists():
            test_db.unlink()


if __name__ == "__main__":
    unittest.main()
