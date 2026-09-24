"""
Command-line interface (CLI) for JobsFind Career Navigator and ATS Matcher.
Provides commands for searching jobs, evaluating ATS match, and generating cover letters.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from config import settings, setup_logging
from exceptions import JobsFindError, ProfileError
from models import CandidateProfile, JobPosting
from matcher import ATSMatcher
from job_finder import JobFinderService
from cover_letter import CoverLetterGenerator
from resume_generator import TailoredResumeGenerator, CURATED_HEALTHCARE_JOBS

logger = logging.getLogger("jobsfind.cli")


def display_profile(profile: CandidateProfile) -> None:
    """Print formatted summary of candidate profile."""
    print("=" * 70)
    print(f"CANDIDATE: {profile.name}")
    print(f"TITLE:     {profile.title}")
    print(f"LOCATION:  {profile.location}")
    print(f"CONTACT:   {profile.email} | {profile.phone}")
    print("=" * 70)
    print("\n[ACTIVE CERTIFICATIONS]")
    for c in profile.certifications:
        print(f"  * {c['name']} - {c.get('issuer', '')} ({c.get('location', '')}, {c.get('date', '')})")

    print("\n[CLINICAL & CODING SKILLS]")
    for category, skills in profile.skills.items():
        print(f"  * {category.replace('_', ' ').title()}: {', '.join(skills)}")

    print("\n[TARGET ROLES]")
    for r in profile.target_roles:
        print(f"  * {r}")
    print("=" * 70)


def search_command(finder: JobFinderService, matcher: ATSMatcher, args: argparse.Namespace) -> None:
    """Search and score job postings based on CLI arguments."""
    print(f"\nSearching jobs (Location: {args.location}, Category: {args.category}, Keywords: {args.keywords or 'All'})...\n")
    jobs = finder.search_jobs(
        keywords=args.keywords,
        location_filter=args.location,
        category_filter=args.category,
        include_live=args.live
    )

    scored_jobs = [(j, matcher.match(j)) for j in jobs]
    scored_jobs.sort(key=lambda x: x[1].score, reverse=True)

    print(f"Found {len(scored_jobs)} relevant opportunities:\n")
    for job, result in scored_jobs:
        score_color = "🟢" if result.score >= 80 else ("🟡" if result.score >= 60 else "⚪")
        print(f"{score_color} [{result.score}% Match] {job.title}")
        print(f"   Company: {job.company} | Location: {job.location}")
        print(f"   Salary:  {job.salary_range} | Type: {job.employment_type}")
        print(f"   ID:      {job.id} | Link: {job.url}")
        if result.strengths:
            print(f"   Key Advantage: {result.strengths[0]}")
        print("-" * 65)


def match_text_command(matcher: ATSMatcher, args: argparse.Namespace) -> None:
    """Evaluate raw job description text from file or argument against candidate profile."""
    content = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.is_file():
            print(f"Error: Job description file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")
    elif args.text:
        content = args.text
    else:
        print("Error: Please provide job text via --text or --file.", file=sys.stderr)
        sys.exit(1)

    temp_job = JobPosting(
        id="custom-input",
        title=args.title or "Target Job Opportunity",
        company=args.company or "Prospective Employer",
        location=args.location or "Ohio / Remote",
        is_remote=True,
        description=content
    )

    result = matcher.match(temp_job)

    print("=" * 70)
    print(f"ATS MATCH ANALYSIS FOR: {temp_job.title} at {temp_job.company}")
    print("=" * 70)
    print(f"OVERALL ATS FIT SCORE: {result.score}%")
    print(f"CPC Requirement Detected: {'YES (Matched)' if result.is_cpc_required else 'No explicit mention'}")
    print(f"Dental Synergies Detected: {'YES (High clinician advantage)' if result.is_dental_relevant else 'Standard Healthcare'}")

    print("\n[MATCHED SKILLS & KEYWORDS]")
    for skill in result.matched_skills:
        print(f"  ✓ {skill}")

    if result.missing_skills:
        print("\n[MISSING KEYWORDS IN POSTING]")
        for skill in result.missing_skills:
            print(f"  ✗ {skill}")

    print("\n[RECOMMENDED PITCH]")
    print(f"  > {result.recommended_pitch}")
    print("=" * 70)


def cover_letter_command(
    profile: CandidateProfile,
    finder: JobFinderService,
    matcher: ATSMatcher,
    args: argparse.Namespace
) -> None:
    """Generate and optionally save a tailored cover letter."""
    gen = CoverLetterGenerator(profile)
    target_job: Optional[JobPosting] = None
    if args.id:
        for j in finder.cached_jobs:
            if j.id == args.id:
                target_job = j
                break
        if not target_job:
            print(f"Warning: Curated job ID '{args.id}' not found. Generating with generic parameters.", file=sys.stderr)

    if not target_job:
        target_job = JobPosting(
            id=args.id or "target-01",
            title=args.title or "Certified Medical Coder",
            company=args.company or "Healthcare Organization",
            location="Ohio / Remote",
            is_remote=True,
            description="Seeking CPC certified coder with clinical documentation and ICD-10 knowledge."
        )

    result = matcher.match(target_job)
    letter = gen.generate(target_job, result)
    print("\n" + "=" * 70)
    print("GENERATED TAILORED COVER LETTER")
    print("=" * 70)
    print(letter)
    print("=" * 70)

    if args.save:
        out_path = Path(args.save)
        out_path.write_text(letter, encoding="utf-8")
        print(f"\nSaved cover letter to: {out_path.resolve()}")


def resume_command(
    profile: CandidateProfile,
    finder: JobFinderService,
    matcher: ATSMatcher,
    args: argparse.Namespace
) -> None:
    """Generate tailored ATS-optimized resumes."""
    gen = TailoredResumeGenerator(profile, matcher)

    if args.all:
        out_dir = Path(args.outdir or "tailored_resumes")
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nGenerating tailored ATS resumes (Markdown & PDF) for all {len(CURATED_HEALTHCARE_JOBS)} curated jobs...\n")
        for job in CURATED_HEALTHCARE_JOBS:
            res = matcher.match(job)
            clean_co = "".join(c for c in job.company if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")

            # Markdown
            out_file_md = out_dir / f"Sri_Kovvuri_Resume_{job.id}_{clean_co}.md"
            resume_text = gen.generate(job, res)
            out_file_md.write_text(resume_text, encoding="utf-8")

            # PDF
            out_file_pdf = out_dir / f"Sri_Kovvuri_Resume_{job.id}_{clean_co}.pdf"
            gen.generate_pdf(job, out_file_pdf, res)

            print(f"  ✓ [{res.score}% Fit] Saved: {out_file_pdf.name} & {out_file_md.name}")
        print(f"\nAll resumes saved to: {out_dir.resolve()}\n")
        return

    target_job: Optional[JobPosting] = None
    if args.id:
        for j in finder.cached_jobs:
            if j.id == args.id:
                target_job = j
                break
        if not target_job:
            print(f"Error: Curated job ID '{args.id}' not found.", file=sys.stderr)
            sys.exit(1)
    elif args.file or args.text:
        content = ""
        if args.file:
            fpath = Path(args.file)
            if not fpath.is_file():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)
            content = fpath.read_text(encoding="utf-8")
        else:
            content = args.text or ""

        target_job = JobPosting(
            id="custom-resume-target",
            title=args.title or "Certified Medical Coder",
            company=args.company or "Healthcare Organization",
            location="Ohio / Remote",
            is_remote=True,
            description=content
        )
    else:
        target_job = finder.cached_jobs[0]

    result = matcher.match(target_job)
    is_pdf = args.pdf or (args.save and args.save.lower().endswith(".pdf"))

    if is_pdf:
        save_path = Path(args.save or f"Sri_Kovvuri_Resume_{target_job.company.replace(' ', '_')}.pdf")
        gen.generate_pdf(target_job, save_path, result)
        print(f"\nSaved tailored ATS PDF resume to: {save_path.resolve()}")
    elif args.save:
        out_path = Path(args.save)
        resume = gen.generate(target_job, result)
        out_path.write_text(resume, encoding="utf-8")
        print(f"\nSaved tailored ATS resume to: {out_path.resolve()}")
    else:
        resume = gen.generate(target_job, result)
        print("\n" + "=" * 70)
        print(f"TAILORED ATS RESUME FOR: {target_job.title} at {target_job.company} (Fit: {result.score}%)")
        print("=" * 70)
        print(resume)
        print("=" * 70)


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="jobsfind",
        description="JobsFind: Enterprise Career Navigator & ATS Job Matcher"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Profile command
    subparsers.add_parser("profile", help="Display candidate profile and extracted resume skills")

    # Search command
    search_p = subparsers.add_parser("search", help="Search curated and remote job listings")
    search_p.add_argument("--location", default="All", choices=["All", "Ohio Only", "Remote Only"], help="Filter by location")
    search_p.add_argument(
        "--category",
        default="All",
        choices=["All", "Medical Coding", "Clinical Documentation Improvement", "Dental Coding & Cross-Coding", "Revenue Cycle & Denials"],
        help="Filter by role category"
    )
    search_p.add_argument("--keywords", default=None, help="Filter keywords (e.g. 'cpc', 'dental', 'cdi')")
    search_p.add_argument("--live", action="store_true", help="Include live remote public feeds")

    # Match command
    match_p = subparsers.add_parser("match", help="Match a specific job description against resume")
    match_p.add_argument("--text", help="Raw job description text")
    match_p.add_argument("--file", help="Path to text file containing job description")
    match_p.add_argument("--title", default="Medical Coder", help="Job title")
    match_p.add_argument("--company", default="Healthcare System", help="Company name")
    match_p.add_argument("--location", default="Ohio", help="Location")

    # Cover letter command
    cl_p = subparsers.add_parser("cover-letter", help="Generate a tailored cover letter")
    cl_p.add_argument("--id", help="Curated job ID to generate letter for (e.g. oh-cc-001)")
    cl_p.add_argument("--title", help="Custom job title")
    cl_p.add_argument("--company", help="Custom company name")
    cl_p.add_argument("--save", help="Optional output text filename to save")

    # Resume command
    res_p = subparsers.add_parser("resume", help="Generate a tailored ATS-optimized resume for a job")
    res_p.add_argument("--id", help="Curated job ID to tailor resume for (e.g. oh-cc-001, rem-dent-004)")
    res_p.add_argument("--all", action="store_true", help="Generate tailored resumes for all curated jobs")
    res_p.add_argument("--pdf", action="store_true", help="Compile resume directly to PDF")
    res_p.add_argument("--outdir", default="tailored_resumes", help="Output directory when generating with --all")
    res_p.add_argument("--title", help="Custom job title")
    res_p.add_argument("--company", help="Custom company name")
    res_p.add_argument("--text", help="Raw job description text")
    res_p.add_argument("--file", help="Path to text file with job description")
    res_p.add_argument("--save", help="Optional output filename (.md or .pdf) to save")

    return parser


def main() -> None:
    """Entry point for CLI execution."""
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    try:
        profile = CandidateProfile.load_from_json(settings.profile_path)
    except ProfileError as exc:
        print(f"Configuration Error: {exc}", file=sys.stderr)
        sys.exit(1)

    matcher = ATSMatcher(profile)
    finder = JobFinderService()

    if args.command == "profile" or len(sys.argv) == 1:
        display_profile(profile)
    elif args.command == "search":
        search_command(finder, matcher, args)
    elif args.command == "match":
        match_text_command(matcher, args)
    elif args.command == "cover-letter":
        cover_letter_command(profile, finder, matcher, args)
    elif args.command == "resume":
        resume_command(profile, finder, matcher, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
