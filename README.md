# 🩺 JobsFind: Career Navigator & ATS Job Matcher

A customized Python career navigation and ATS matching suite tailored for **Sri Lakshmi Sravya Reddy Kovvuri**, highlighting your unique value proposition: **AAPC Certified Professional Coder (CPC)** + **Former Dentist (BDS)**.

---

## 🌟 Key Features

1. **Intelligent ATS Resume Matcher (`matcher.py`)**
   - Automatically scores any job description (0–100%) against your credentials, coding systems, compliance standards, and clinical experience.
   - Highlights your **competitive edge** (e.g. dental clinical expertise for dental billing, physician documentation translation for CDI).
   - Flags **matched competencies** and identifies **missing keywords** or skill gaps.

2. **Job Search & Aggregator (`job_finder.py`)**
   - Pre-loaded with curated healthcare opportunities across Ohio (Cleveland Clinic, OhioHealth, Premier Health Dayton, Dayton Children's, UC Health) and national remote employers (Optum, Elevance Health, Heartland Dental).
   - Integration with live remote job feeds.
   - Filters by role category (Medical Coding, Dental Coding & Cross-Coding, CDI, Revenue Cycle) and location (Ohio Only, Remote Only).

3. **Tailored Cover Letter Generator (`cover_letter.py`)**
   - Automatically generates a custom, professional cover letter for any job.
   - Articulates your distinctive story: combining hands-on diagnostic dentistry with AAPC CPC coding accuracy to minimize denials and ensure compliant documentation.

4. **Application Tracker (`tracker.py`)**
   - SQLite database (`job_applications.db`) for tracking opportunities across stages: *Saved*, *Applied*, *Interviewing*, *Offer*, *Rejected*.
   - View KPIs, manage notes, and export to CSV.

5. **Interactive Web Dashboard (`app.py`)**
   - Clean, modern Streamlit UI with tabs for exploring jobs, testing ATS match scores, generating cover letters, tracking applications, and viewing your skills matrix.

6. **CLI Utility (`main.py`)**
   - Fast terminal commands for searching, scoring job descriptions, and generating letters.

---

## 🚀 Quick Start Guide

### 1. Activate Environment

```bash
cd /Users/krishnajyothiswarooppothamsetti/.gemini/antigravity-ide/scratch/jobsfind
source .venv/bin/activate
```

### 2. Launch the Web Application

```bash
streamlit run app.py
```
*The app will automatically open in your browser at `http://localhost:8501`.*

---

## 💻 CLI Commands

### View Profile Summary
```bash
python main.py profile
```

### Search Matching Jobs
```bash
# Search all jobs
python main.py search

# Filter for Ohio-only positions
python main.py search --location "Ohio Only"

# Search by keyword (e.g. dental, cdi, outpatient)
python main.py search --keywords "dental"
```

### Test ATS Match on Any Job Posting
```bash
# Pass raw job description directly
python main.py match --title "Outpatient Coder" --company "Mercy Health" --text "Looking for a CPC certified coder with ICD-10 and CPT experience..."

# Or test against a text file
python main.py match --file path/to/job_description.txt
```

### Generate a Tailored Cover Letter
```bash
# Generate for curated job (e.g. Cleveland Clinic)
python main.py cover-letter --id oh-cc-001

# Generate and save to file
python main.py cover-letter --id rem-dent-004 --save Heartland_Cover_Letter.txt
```

---

## 📁 Project Structure

```
jobsfind/
├── .venv/                      # Python virtual environment
├── requirements.txt            # Project dependencies
├── resume_profile.json         # Structured JSON profile extracted from resume
├── models.py                   # Data models (CandidateProfile, JobPosting, MatchResult)
├── matcher.py                  # ATS scoring & keyword analysis engine
├── job_finder.py               # Job search & curated healthcare database
├── cover_letter.py             # Tailored cover letter generator
├── tracker.py                  # Local SQLite application tracker
├── main.py                     # Command-line interface (CLI)
├── app.py                      # Streamlit web dashboard
├── test_matcher.py             # Automated unit tests
└── README.md                   # Documentation and user guide
```
