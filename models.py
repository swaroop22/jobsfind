"""
Data models for candidate profile, job listings, match results, and application tracking.
Enterprise-grade data structures with type safety, schema validation, and serialization.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
import json
import logging

from exceptions import ProfileNotFoundError, ProfileValidationError

logger = logging.getLogger(__name__)


class ApplicationStatus(str, Enum):
    """Permitted application lifecycle stages."""
    SAVED = "Saved"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"

    @classmethod
    def values(cls) -> List[str]:
        return [item.value for item in cls]


@dataclass
class CandidateProfile:
    """Represents a candidate's credentials, skills, experience, and target roles."""

    name: str
    title: str
    email: str
    phone: str
    location: str
    preferred_locations: List[str]
    summary: str
    certifications: List[Dict[str, str]] = field(default_factory=list)
    education: List[Dict[str, str]] = field(default_factory=list)
    skills: Dict[str, List[str]] = field(default_factory=dict)
    experience: List[Dict[str, Any]] = field(default_factory=list)
    target_roles: List[str] = field(default_factory=list)

    @classmethod
    def load_from_json(cls, file_path: Union[str, Path]) -> "CandidateProfile":
        """
        Load and validate a candidate profile from a JSON file.

        Args:
            file_path: Path to the JSON profile file.

        Returns:
            CandidateProfile instance.

        Raises:
            ProfileNotFoundError: If the file does not exist.
            ProfileValidationError: If JSON is invalid or missing required fields.
        """
        path = Path(file_path)
        if not path.is_file():
            raise ProfileNotFoundError(f"Profile file not found at: {path.resolve()}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ProfileValidationError(f"Invalid JSON in profile file: {exc}") from exc
        except Exception as exc:
            raise ProfileValidationError(f"Error reading profile file: {exc}") from exc

        if not isinstance(data, dict) or "candidate" not in data:
            raise ProfileValidationError("Profile JSON must contain a top-level 'candidate' object.")

        c = data["candidate"]
        required_fields = ["name", "title", "email", "phone", "location", "summary"]
        missing = [rf for rf in required_fields if not c.get(rf)]
        if missing:
            raise ProfileValidationError(f"Candidate profile missing required fields: {', '.join(missing)}")

        return cls(
            name=c["name"],
            title=c["title"],
            email=c["email"],
            phone=c["phone"],
            location=c["location"],
            preferred_locations=c.get("preferred_locations", ["Ohio", "Remote"]),
            summary=c["summary"],
            certifications=data.get("certifications", []),
            education=data.get("education", []),
            skills=data.get("skills", {}),
            experience=data.get("experience", []),
            target_roles=data.get("target_roles", []),
        )

    def all_keywords(self) -> List[str]:
        """Aggregate all searchable domain keywords from skills, certs, and roles."""
        keywords = set()
        for cat, slist in self.skills.items():
            for s in slist:
                keywords.add(s)
        for cert in self.certifications:
            keywords.add(cert["name"])
            if "issuer" in cert:
                keywords.add(cert["issuer"])
        for exp in self.experience:
            if "role" in exp:
                keywords.add(exp["role"])
        return sorted(list(keywords))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the profile to a dictionary."""
        return asdict(self)


@dataclass
class JobPosting:
    """Represents a healthcare or coding job opportunity."""

    id: str
    title: str
    company: str
    location: str
    is_remote: bool
    description: str
    url: str = ""
    posted_date: str = ""
    salary_range: str = ""
    employment_type: str = "Full-time"
    source: str = "Curated Healthcare Database"
    category: str = "Medical Coding"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the job posting to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobPosting":
        """Instantiate a JobPosting from a dictionary."""
        return cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", "")),
            company=str(data.get("company", "")),
            location=str(data.get("location", "")),
            is_remote=bool(data.get("is_remote", False)),
            description=str(data.get("description", "")),
            url=str(data.get("url", "")),
            posted_date=str(data.get("posted_date", "")),
            salary_range=str(data.get("salary_range", "")),
            employment_type=str(data.get("employment_type", "Full-time")),
            source=str(data.get("source", "Curated Healthcare Database")),
            category=str(data.get("category", "Medical Coding")),
        )


@dataclass
class MatchResult:
    """Results and actionable insights from ATS matching analysis."""

    job: JobPosting
    score: float  # 0.0 to 100.0
    matched_skills: List[str]
    missing_skills: List[str]
    is_cpc_required: bool
    is_dental_relevant: bool
    strengths: List[str]
    improvement_tips: List[str]
    recommended_pitch: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize match results to a dictionary."""
        d = asdict(self)
        d["job"] = self.job.to_dict()
        return d


@dataclass
class ApplicationRecord:
    """Application tracking record stored in SQLite."""

    id: Optional[int]
    job_title: str
    company: str
    location: str
    status: str  # Must align with ApplicationStatus
    applied_date: str
    match_score: float
    notes: str = ""
    job_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the record to a dictionary."""
        return asdict(self)
