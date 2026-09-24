"""
Streamlit Web Dashboard for JobsFind: Career Navigator & ATS Job Matcher.
Tailored for Sri Lakshmi Sravya Reddy Kovvuri: AAPC Certified Professional Coder (CPC) & Former Dentist (BDS).
"""

import sys
import logging
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
import streamlit as st

from config import settings, setup_logging
from exceptions import ProfileError, DatabaseError
from models import CandidateProfile, JobPosting, MatchResult, ApplicationStatus
from matcher import ATSMatcher
from job_finder import JobFinderService
from cover_letter import CoverLetterGenerator
from tracker import ApplicationTracker

logger = setup_logging()

# Page Configuration
st.set_page_config(
    page_title="JobsFind - Medical Coding & Clinical Career Matcher",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .main-header p {
        color: #e0f2fe;
        font-size: 1.05rem;
        margin-top: 8px;
        margin-bottom: 0;
    }
    .metric-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .badge-high { background-color: #dcfce7; color: #166534; }
    .badge-med { background-color: #fef9c3; color: #854d0e; }
    .badge-low { background-color: #f1f5f9; color: #475569; }
    .job-card {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease-in-out;
    }
    .job-card:hover {
        border-color: #0284c7;
        transform: translateY(-2px);
    }
    .tag {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .tag-missing {
        display: inline-block;
        background: #fee2e2;
        color: #991b1b;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 6px;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Services with Error Boundary
@st.cache_resource
def load_services() -> Tuple[CandidateProfile, ATSMatcher, JobFinderService, CoverLetterGenerator, ApplicationTracker]:
    """Load core application services with central configuration and caching."""
    try:
        profile = CandidateProfile.load_from_json(settings.profile_path)
    except ProfileError as exc:
        logger.error("Failed to load profile from %s: %s", settings.profile_path, exc)
        st.error(f"⚠️ Critical Error: Failed to load candidate profile: {exc}")
        st.stop()

    matcher = ATSMatcher(profile)
    finder = JobFinderService()
    generator = CoverLetterGenerator(profile)
    try:
        tracker = ApplicationTracker(db_path=settings.db_path)
    except DatabaseError as exc:
        logger.error("Failed to connect to database at %s: %s", settings.db_path, exc)
        st.error(f"⚠️ Database Error: {exc}")
        st.stop()

    return profile, matcher, finder, generator, tracker


profile, matcher, finder, generator, tracker = load_services()

# Top Header
st.markdown(f"""
<div class="main-header">
    <h1>🩺 JobsFind Career Navigator</h1>
    <p>Tailored for: <b>{profile.name}</b> | AAPC Certified Professional Coder (CPC) & Former Dentist (BDS)</p>
    <div style="margin-top: 10px; font-size: 0.9rem; color: #bae6fd;">
        📍 <b>Location:</b> {profile.location} &nbsp;|&nbsp; 
        📧 <b>Email:</b> {profile.email} &nbsp;|&nbsp; 
        📞 <b>Phone:</b> {profile.phone} &nbsp;|&nbsp; 
        🎓 <b>AAPC Credential:</b> CPC (Dayton, OH)
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab_explore, tab_ats, tab_cover, tab_tracker, tab_profile = st.tabs([
    "🔎 Job Matches & Explorer",
    "🎯 ATS Resume Matcher (Paste Job)",
    "✍️ Cover Letter Generator",
    "📊 Application Tracker",
    "📋 Candidate Profile & Skills"
])


# ==============================================================================
# TAB 1: JOB MATCHES & EXPLORER
# ==============================================================================
with tab_explore:
    st.subheader("Targeted Healthcare & Medical Coding Positions")
    st.write("Browse opportunities pre-scored against your clinical documentation, AAPC CPC credentials, and dental background.")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_kw = st.text_input("Filter by keywords", placeholder="e.g. CPC, Dental, CDI, ICD-10, Outpatient")
    with col2:
        loc_filter = st.selectbox("Location Filter", ["All", "Ohio Only", "Remote Only"])
    with col3:
        min_score = st.slider("Minimum Match Score", min_value=30, max_value=95, value=50, step=5)

    # Search & Match
    jobs = finder.search_jobs(
        keywords=search_kw,
        location_filter=loc_filter,
        include_live=False  # Stable curated listings
    )

    scored_jobs = []
    for j in jobs:
        res = matcher.match(j)
        if res.score >= min_score:
            scored_jobs.append((j, res))

    scored_jobs.sort(key=lambda x: x[1].score, reverse=True)

    st.markdown(f"**Found {len(scored_jobs)} opportunities matching your criteria:**")

    for job, res in scored_jobs:
        score_class = "badge-high" if res.score >= 80 else ("badge-med" if res.score >= 60 else "badge-low")

        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0; color: #0f172a; font-size: 1.25rem;">{job.title}</h3>
                        <p style="margin: 4px 0 8px 0; color: #475569; font-weight: 500;">
                            🏢 <b>{job.company}</b> &nbsp;|&nbsp; 📍 {job.location} &nbsp;|&nbsp; 💰 {job.salary_range}
                        </p>
                    </div>
                    <div>
                        <span class="metric-badge {score_class}">{res.score}% ATS Match</span>
                    </div>
                </div>
                <p style="color: #334155; font-size: 0.95rem; margin-top: 8px;">{job.description}</p>
            """, unsafe_allow_html=True)

            # Matched Skills Pills
            skill_pills = "".join([f'<span class="tag">✓ {s}</span>' for s in res.matched_skills[:6]])
            st.markdown(f"<div style='margin-bottom: 8px;'><b>Matched Competencies:</b> {skill_pills}</div>", unsafe_allow_html=True)

            if res.strengths:
                st.markdown(f"💡 <span style='color: #0369a1; font-weight: 500;'><b>Your Competitive Edge:</b> {res.strengths[0]}</span>", unsafe_allow_html=True)

            btn_col1, btn_col2, btn_col3 = st.columns([1.5, 1.5, 5])
            with btn_col1:
                if st.button("Save to Tracker", key=f"save_{job.id}"):
                    try:
                        tracker.add_application(
                            job_title=job.title,
                            company=job.company,
                            location=job.location,
                            status=ApplicationStatus.SAVED.value,
                            match_score=res.score,
                            job_url=job.url
                        )
                        st.success("Saved to application tracker!")
                    except DatabaseError as exc:
                        st.error(f"Failed to save application: {exc}")
            with btn_col2:
                if st.button("Generate Pitch", key=f"pitch_{job.id}"):
                    st.info(f"**Application Strategy:** {res.recommended_pitch}")
            with btn_col3:
                if job.url:
                    st.markdown(f"[Apply on Company Website ↗]({job.url})")

            st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# TAB 2: ATS RESUME MATCHER (PASTE JOB DESCRIPTION)
# ==============================================================================
with tab_ats:
    st.subheader("Test Any Job Description Against Your Resume")
    st.write("Copy and paste any job posting from LinkedIn, Indeed, or hospital career portals to evaluate ATS compatibility.")

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        custom_title = st.text_input("Job Title", value="Medical Coder / Clinical Documentation Specialist")
    with col_meta2:
        custom_company = st.text_input("Company / Hospital", value="Healthcare Provider")

    custom_text = st.text_area(
        "Paste Full Job Description Here:",
        height=220,
        placeholder="Paste requirements, qualifications, and responsibilities here..."
    )

    if st.button("Analyze ATS Match Score", type="primary"):
        if not custom_text.strip():
            st.warning("Please paste a job description first.")
        else:
            sample_job = JobPosting(
                id="custom-job",
                title=custom_title,
                company=custom_company,
                location="Ohio / Remote",
                is_remote=True,
                description=custom_text
            )
            analysis = matcher.match(sample_job)

            st.markdown("---")
            score_col1, score_col2, score_col3 = st.columns([1, 1, 1])
            with score_col1:
                st.metric("Overall ATS Match", f"{analysis.score}%")
            with score_col2:
                cpc_status = "✅ Matched (AAPC CPC)" if analysis.is_cpc_required else "ℹ️ Not Explicitly Listed"
                st.metric("CPC Certification", cpc_status)
            with score_col3:
                dental_status = "🌟 High Clinical Advantage" if analysis.is_dental_relevant else "Standard Medical Role"
                st.metric("Dental Synergy", dental_status)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown("### ✅ Matched Resume Skills")
                if analysis.matched_skills:
                    for s in analysis.matched_skills:
                        st.markdown(f"- **{s}**")
                else:
                    st.write("No direct keyword overlaps detected.")

            with col_m2:
                st.markdown("### ⚠️ Missing Keywords or Gaps")
                if analysis.missing_skills:
                    for s in analysis.missing_skills:
                        st.markdown(f"- <span style='color: #b91c1c;'>{s}</span>", unsafe_allow_html=True)
                else:
                    st.write("No critical gaps detected! Your profile addresses all detected requirements.")

            st.markdown("### 💡 Recommended Tailored Application Strategy")
            st.success(analysis.recommended_pitch)

            if analysis.improvement_tips:
                st.markdown("### 📝 Optimization Tips:")
                for tip in analysis.improvement_tips:
                    st.info(tip)


# ==============================================================================
# TAB 3: COVER LETTER GENERATOR
# ==============================================================================
with tab_cover:
    st.subheader("Generate a Tailored Cover Letter")
    st.write("Creates an application letter bridging your dentist clinical background with AAPC CPC compliance.")

    cl_job_source = st.selectbox(
        "Select Job Target",
        ["Select a curated job posting..."] + [f"{j.company} - {j.title} ({j.id})" for j in finder.cached_jobs]
    )

    if cl_job_source != "Select a curated job posting...":
        selected_id = cl_job_source.split("(")[-1].rstrip(")")
        chosen_job = next(j for j in finder.cached_jobs if j.id == selected_id)
        chosen_match = matcher.match(chosen_job)
        letter = generator.generate(chosen_job, chosen_match)

        st.text_area("Custom Generated Cover Letter:", value=letter, height=350)
        st.download_button(
            label="📥 Download Cover Letter (.txt)",
            data=letter,
            file_name=f"Cover_Letter_{chosen_job.company.replace(' ', '_')}.txt",
            mime="text/plain"
        )
    else:
        st.write("Or enter custom job details below:")
        custom_cl_company = st.text_input("Target Company Name", "Mercy Health")
        custom_cl_title = st.text_input("Target Position Title", "Outpatient Coding & Documentation Specialist")
        custom_cl_desc = st.text_area("Brief Job Summary / Requirements", "Looking for CPC certified coder with clinical knowledge of CPT, ICD-10, and EHR documentation.")

        if st.button("Generate Custom Cover Letter"):
            temp_j = JobPosting(
                id="custom-cl",
                title=custom_cl_title,
                company=custom_cl_company,
                location="Ohio / Remote",
                is_remote=True,
                description=custom_cl_desc
            )
            temp_res = matcher.match(temp_j)
            generated_cl = generator.generate(temp_j, temp_res)
            st.text_area("Generated Cover Letter:", value=generated_cl, height=350)
            st.download_button(
                label="📥 Download Cover Letter (.txt)",
                data=generated_cl,
                file_name=f"Cover_Letter_{custom_cl_company.replace(' ', '_')}.txt",
                mime="text/plain"
            )


# ==============================================================================
# TAB 4: APPLICATION TRACKER
# ==============================================================================
with tab_tracker:
    st.subheader("Job Application Tracker")
    st.write("Keep track of your job search progress, interview stages, and offers.")

    stats = tracker.get_statistics()
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("Total Tracked", stats["total"])
    with kpi2:
        st.metric("Saved", stats["saved"])
    with kpi3:
        st.metric("Applied", stats["applied"])
    with kpi4:
        st.metric("Interviewing", stats["interviewing"])
    with kpi5:
        st.metric("Offers", stats["offers"])

    # Quick Add Form
    with st.expander("➕ Add New Application Record"):
        with st.form("add_app_form"):
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                app_title = st.text_input("Job Title", "Certified Medical Coder")
                app_company = st.text_input("Company Name", "Cincinnati Children's")
                app_loc = st.text_input("Location", "Cincinnati, OH / Remote")
            with form_col2:
                app_status = st.selectbox("Status", ApplicationStatus.values())
                app_score = st.number_input("Match Score %", min_value=0.0, max_value=100.0, value=85.0)
                app_url = st.text_input("Job Link / URL", "")
            app_notes = st.text_area("Notes", "Submitted application through hospital portal with tailored dentist+CPC resume.")
            submitted = st.form_submit_button("Save Application")
            if submitted:
                try:
                    tracker.add_application(
                        job_title=app_title,
                        company=app_company,
                        location=app_loc,
                        status=app_status,
                        match_score=app_score,
                        notes=app_notes,
                        job_url=app_url
                    )
                    st.success("Application saved successfully!")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to record application: {exc}")

    # Display Table
    df = tracker.to_dataframe()
    if not df.empty:
        st.dataframe(df, use_container_width=True)

        # CSV Export
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Applications to CSV",
            data=csv_data,
            file_name="Sri_Lakshmi_Job_Applications.csv",
            mime="text/csv"
        )
    else:
        st.info("No applications tracked yet. Click 'Save to Tracker' on any job card in Tab 1 or add one using the form above.")


# ==============================================================================
# TAB 5: CANDIDATE PROFILE & SKILLS MATRIX
# ==============================================================================
with tab_profile:
    st.subheader("Your Profile & Professional Positioning")
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.markdown("### 🎓 Credentials & Education")
        for cert in profile.certifications:
            st.markdown(f"**🏅 {cert['name']}**  \n*{cert['issuer']}* ({cert.get('location', '')})  \nStatus: `{cert.get('status', 'Active')}` | Date: {cert.get('date', '')}")
            
        for edu in profile.education:
            st.markdown(f"**🏛️ {edu['degree']}**  \n*{edu['institution']}*, {edu.get('location', '')}  \nGraduation: {edu.get('graduation_date', '')}")

        st.markdown("### 🎯 Target Roles")
        for role in profile.target_roles:
            st.markdown(f"- {role}")

    with col_p2:
        st.markdown("### 🛠️ Core Competency Matrix")
        for category, skill_list in profile.skills.items():
            cat_title = category.replace("_", " ").title()
            pills = " ".join([f"<span class='tag'>{s}</span>" for s in skill_list])
            st.markdown(f"**{cat_title}:**  \n{pills}", unsafe_allow_html=True)

        st.markdown("### 💼 Clinical & Documentation Experience")
        for exp in profile.experience:
            st.markdown(f"**{exp['role']}** | *{exp['company']}* ({exp['location']}) - `{exp['dates']}`")
            for h in exp["highlights"]:
                st.markdown(f"- {h}")
