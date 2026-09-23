"""
Data models for candidate profile, job listings, match results, and application tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json
from pathlib import Path


@dataclass
class CandidateProfile:
    name: str
    title: str
    email: str
    phone: str
    location: str
    preferred_locations: List[str]
    summary: str
    certifications: List[Dict[str, str]]
    education: List[Dict[str, str]]
    skills: Dict[str, List[str]]
    experience: List[Dict[str, Any]]
    target_roles: List[str]

    @classmethod
    def load_from_json(cls, file_path: Path) -> "CandidateProfile":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        c = data["candidate"]
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
        keywords = set()
        for cat, slist in self.skills.items():
            for s in slist:
                keywords.add(s)
        for cert in self.certifications:
            keywords.add(cert["name"])
            if "issuer" in cert:
                keywords.add(cert["issuer"])
        for exp in self.experience:
            keywords.add(exp["role"])
        return sorted(list(keywords))


@dataclass
class JobPosting:
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


@dataclass
class MatchResult:
    job: JobPosting
    score: float  # 0 to 100
    matched_skills: List[str]
    missing_skills: List[str]
    is_cpc_required: bool
    is_dental_relevant: bool
    strengths: List[str]
    improvement_tips: List[str]
    recommended_pitch: str


@dataclass
class ApplicationRecord:
    id: Optional[int]
    job_title: str
    company: str
    location: str
    status: str  # Saved, Applied, Interviewing, Offer, Rejected
    applied_date: str
    match_score: float
    notes: str = ""
    job_url: str = ""
