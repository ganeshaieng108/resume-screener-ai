"""
Resume Screening AI Tool
Main Streamlit application entry point.
"""

import streamlit as st
import tempfile
import os
from pathlib import Path

# Page configuration - must be first Streamlit call
st.set_page_config(
    page_title="Resume Screener AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import utilities
from utils.resume_parser import parse_resume
from utils.skill_extractor import extract_skills, extract_education, extract_experience
from utils.matcher import calculate_match_score, get_skill_gaps
from utils.visualizer import (
    create_score_gauge,
    create_skills_radar,
    create_skills_breakdown_chart,
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root palette ── */
:root {
    --navy:   #0B1D3A;
    --blue:   #1A56DB;
    --sky:    #EFF6FF;
    --slate:  #64748B;
    --white:  #FFFFFF;
    --border: #DBEAFE;
    --success:#059669;
    --warn:   #D97706;
    --danger: #DC2626;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--white);
    color: var(--navy);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1280px; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, var(--navy) 0%, #1e3a6e 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: var(--white);
    margin: 0;
    line-height: 1.2;
}
.hero p {
    color: #93C5FD;
    font-size: 1rem;
    margin: 0.4rem 0 0;
    font-weight: 300;
}
.hero-icon { font-size: 3.5rem; }

/* ── Section cards ── */
.card {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(11,29,58,.05);
}
.card-title {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--blue);
    margin-bottom: 1rem;
}

/* ── Score badge ── */
.score-badge {
    font-family: 'DM Serif Display', serif;
    font-size: 4rem;
    line-height: 1;
    color: var(--navy);
}
.score-label {
    font-size: 0.85rem;
    color: var(--slate);
    margin-top: 0.3rem;
}

/* ── Skill chips ── */
.chip-wrap { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; }
.chip {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
}
.chip-match  { background: #D1FAE5; color: #065F46; }
.chip-miss   { background: #FEE2E2; color: #991B1B; }
.chip-neutral{ background: #EFF6FF; color: #1D4ED8; }

/* ── Progress bar override ── */
.stProgress > div > div { background: var(--blue) !important; border-radius: 999px; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: var(--sky);
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 1rem;
}

/* ── Primary button ── */
.stButton > button {
    background: var(--blue) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    width: 100% !important;
    transition: opacity .2s;
}
.stButton > button:hover { opacity: 0.88; }

/* ── Divider ── */
hr { border: none; border-top: 1.5px solid var(--border); margin: 1.5rem 0; }

/* ── Recommendation box ── */
.rec-box {
    background: #EFF6FF;
    border-left: 4px solid var(--blue);
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.2rem;
    margin-top: 0.6rem;
    font-size: 0.9rem;
    color: var(--navy);
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
  <span class="hero-icon">🎯</span>
  <div>
    <h1>Resume Screener AI</h1>
    <p>Instantly match candidates to job descriptions with deep NLP analysis</p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Layout: two columns ───────────────────────────────────────────────────────
left, right = st.columns([1, 1.4], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL — Inputs
# ══════════════════════════════════════════════════════════════════════════════
with left:
    # ── Resume upload ──
    st.markdown('<div class="card-title">📄 Upload Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drag & drop or browse",
        type=["pdf", "docx"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.success(f"✓  {uploaded_file.name}  ({uploaded_file.size // 1024} KB)")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Job description ──
    st.markdown('<div class="card-title">💼 Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "Paste the full job description here",
        height=260,
        placeholder="We are looking for a Data Scientist with 3+ years of experience in Python, SQL, Machine Learning…",
        label_visibility="collapsed",
    )

    word_count = len(jd_text.split()) if jd_text.strip() else 0
    if jd_text.strip():
        color = "#059669" if word_count >= 50 else "#D97706"
        st.markdown(
            f'<p style="font-size:.8rem;color:{color};margin-top:.3rem">'
            f'{"✓" if word_count >= 50 else "⚠"} {word_count} words'
            f'{"" if word_count >= 50 else " — add more detail for accuracy"}</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sample JD helper ──
    with st.expander("📋 Load a sample job description"):
        st.markdown(
            """
**Data Scientist — Sample JD**  
Copy and paste below 👇
```
We are looking for a skilled Data Scientist with 3+ years of experience.

Requirements:
- Proficiency in Python, SQL, and R
- Experience with Machine Learning frameworks (scikit-learn, TensorFlow, PyTorch)
- Strong knowledge of Statistics and Probability
- Experience with data visualization (Tableau, Power BI, Matplotlib)
- Familiarity with cloud platforms (AWS, GCP, or Azure)
- Docker and Kubernetes experience preferred
- Excellent communication and teamwork skills

Education:
- Bachelor's or Master's degree in Computer Science, Statistics, or related field

Responsibilities:
- Build and deploy machine learning models
- Analyze large datasets to extract actionable insights
- Collaborate with cross-functional teams
- Present findings to non-technical stakeholders
```
"""
        )

    # ── Analyze button ──
    analyze_clicked = st.button("🔍 Analyze Resume", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Results
# ══════════════════════════════════════════════════════════════════════════════
with right:

    # ── Placeholder state ──
    if not analyze_clicked:
        st.markdown(
            """
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
            height:520px;border:2px dashed #DBEAFE;border-radius:20px;color:#94A3B8;text-align:center;padding:2rem;">
  <div style="font-size:4rem;margin-bottom:1rem">📊</div>
  <div style="font-size:1.1rem;font-weight:500">Results will appear here</div>
  <div style="font-size:.85rem;margin-top:.5rem">Upload a resume and paste a job description, then click Analyze</div>
</div>
""",
            unsafe_allow_html=True,
        )

    # ── Run analysis ──
    if analyze_clicked:
        # ── Validation ──
        errors = []
        if not uploaded_file:
            errors.append("Please upload a resume (PDF or DOCX).")
        if not jd_text.strip():
            errors.append("Please paste a job description.")
        elif word_count < 20:
            errors.append("Job description is too short (min 20 words) for accurate matching.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            with st.spinner("Analyzing resume…"):
                # ── Save upload to temp file ──
                suffix = Path(uploaded_file.name).suffix.lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                try:
                    # 1. Parse
                    resume_text = parse_resume(tmp_path)

                    if not resume_text or len(resume_text.split()) < 30:
                        st.error(
                            "⚠️ Could not extract enough text from this file. "
                            "Check that it's not scanned/image-only."
                        )
                        st.stop()

                    # 2. Extract structured data
                    resume_skills = extract_skills(resume_text)
                    jd_skills     = extract_skills(jd_text)
                    education     = extract_education(resume_text)
                    exp_years     = extract_experience(resume_text)
                    req_exp_years = extract_experience(jd_text)

                    # 3. Match
                    scores = calculate_match_score(
                        resume_text, jd_text,
                        resume_skills, jd_skills,
                        exp_years, req_exp_years,
                        education,
                    )
                    matched_skills, missing_skills = get_skill_gaps(resume_skills, jd_skills)

                    overall = scores["overall"]

                finally:
                    os.unlink(tmp_path)

            # ══════════════════════════════════════════════════════════════
            # RESULTS
            # ══════════════════════════════════════════════════════════════

            # ── Score gauge ──
            gauge_color = (
                "#059669" if overall >= 70 else
                "#D97706" if overall >= 45 else
                "#DC2626"
            )
            label = (
                "Strong Match 🟢" if overall >= 70 else
                "Partial Match 🟡" if overall >= 45 else
                "Weak Match 🔴"
            )

            col_g, col_m = st.columns([1, 1])
            with col_g:
                fig_gauge = create_score_gauge(overall)
                st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

            with col_m:
                st.markdown(
                    f"""
<div style="padding:1rem 0">
  <div class="score-badge" style="color:{gauge_color}">{overall}%</div>
  <div class="score-label">{label}</div>
  <hr style="margin:.8rem 0">
  <table style="width:100%;font-size:.85rem;border-collapse:collapse;">
    <tr><td style="color:var(--slate);padding:.25rem 0">Skills match</td>
        <td style="font-weight:600;text-align:right">{scores['skills']}%</td></tr>
    <tr><td style="color:var(--slate);padding:.25rem 0">Experience fit</td>
        <td style="font-weight:600;text-align:right">{scores['experience']}%</td></tr>
    <tr><td style="color:var(--slate);padding:.25rem 0">Education fit</td>
        <td style="font-weight:600;text-align:right">{scores['education']}%</td></tr>
    <tr><td style="color:var(--slate);padding:.25rem 0">Content similarity</td>
        <td style="font-weight:600;text-align:right">{scores['tfidf']}%</td></tr>
  </table>
</div>
""",
                    unsafe_allow_html=True,
                )

            st.markdown("<hr>", unsafe_allow_html=True)

            # ── Skills breakdown ──
            st.markdown('<div class="card-title">🛠 Skills Analysis</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f'<div style="font-size:.8rem;color:#059669;font-weight:600;margin-bottom:.4rem">'
                    f'✓ Matched Skills ({len(matched_skills)})</div>',
                    unsafe_allow_html=True,
                )
                chips = "".join(
                    f'<span class="chip chip-match">{s}</span>' for s in sorted(matched_skills)
                ) or "<span style='color:#94A3B8;font-size:.85rem'>None detected</span>"
                st.markdown(f'<div class="chip-wrap">{chips}</div>', unsafe_allow_html=True)

            with c2:
                st.markdown(
                    f'<div style="font-size:.8rem;color:#DC2626;font-weight:600;margin-bottom:.4rem">'
                    f'✗ Missing Skills ({len(missing_skills)})</div>',
                    unsafe_allow_html=True,
                )
                chips = "".join(
                    f'<span class="chip chip-miss">{s}</span>' for s in sorted(missing_skills)
                ) or "<span style='color:#059669;font-size:.85rem'>No gaps found!</span>"
                st.markdown(f'<div class="chip-wrap">{chips}</div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            # ── Experience & Education ──
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="card-title">⏱ Experience</div>', unsafe_allow_html=True)
                req_label = f"{req_exp_years}+ yrs required" if req_exp_years > 0 else "Not specified"
                has_label  = f"{exp_years} yrs detected" if exp_years > 0 else "Not detected"
                exp_ok = exp_years >= req_exp_years if req_exp_years > 0 else True
                st.markdown(
                    f"""
<div style="font-size:.9rem">
  <div style="margin-bottom:.5rem">📋 Resume: <strong>{has_label}</strong></div>
  <div style="margin-bottom:.8rem">📌 Job req: <strong>{req_label}</strong></div>
  <div style="padding:.5rem .8rem;border-radius:8px;background:{'#D1FAE5' if exp_ok else '#FEE2E2'};
              color:{'#065F46' if exp_ok else '#991B1B'};font-size:.85rem;font-weight:500">
    {'✓ Meets requirement' if exp_ok else '✗ Experience gap'}
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

            with c4:
                st.markdown('<div class="card-title">🎓 Education</div>', unsafe_allow_html=True)
                edu_display = education if education else "Not detected"
                st.markdown(
                    f"""
<div style="font-size:.9rem">
  <div style="margin-bottom:.8rem">📋 Resume: <strong>{edu_display}</strong></div>
  <div style="padding:.5rem .8rem;border-radius:8px;
              background:{'#D1FAE5' if scores['education'] >= 60 else '#FFF7ED'};
              color:{'#065F46' if scores['education'] >= 60 else '#92400E'};
              font-size:.85rem;font-weight:500">
    {'✓ Education match' if scores['education'] >= 60 else '⚠ Education unclear or not matching'}
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

            st.markdown("<hr>", unsafe_allow_html=True)

            # ── Radar chart ──
            if jd_skills:
                st.markdown('<div class="card-title">📡 Skills Radar</div>', unsafe_allow_html=True)
                fig_radar = create_skills_radar(resume_skills, jd_skills)
                if fig_radar:
                    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

            # ── Score breakdown bar ──
            st.markdown('<div class="card-title">📊 Score Breakdown</div>', unsafe_allow_html=True)
            fig_bar = create_skills_breakdown_chart(scores)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

            st.markdown("<hr>", unsafe_allow_html=True)

            # ── Recommendations ──
            st.markdown('<div class="card-title">💡 Recommendations</div>', unsafe_allow_html=True)
            recs = []

            if missing_skills:
                top_missing = ", ".join(sorted(missing_skills)[:5])
                recs.append(f"Add hands-on projects or certifications for: **{top_missing}**.")

            if not exp_ok and req_exp_years > 0:
                gap = req_exp_years - exp_years
                recs.append(
                    f"Experience gap of ~{gap} year(s). Highlight freelance, open-source, "
                    f"or academic projects to demonstrate applied experience."
                )

            if scores["education"] < 60:
                recs.append(
                    "Clearly list your highest degree, institution, and graduation year at the top of your resume."
                )

            if scores["tfidf"] < 50:
                recs.append(
                    "Use more keywords from the job description naturally throughout your resume "
                    "(summary, experience bullets, skills section)."
                )

            if overall >= 75:
                recs.append("Strong match! Tailor your cover letter to emphasize shared values and impact metrics.")

            if not recs:
                recs.append("Resume looks well-aligned. Customize each application for the specific company context.")

            for r in recs:
                st.markdown(f'<div class="rec-box">• {r}</div>', unsafe_allow_html=True)

            # ── Download text report ──
            st.markdown("<hr>", unsafe_allow_html=True)
            report_lines = [
                "RESUME SCREENING REPORT",
                "=" * 40,
                f"Overall Match Score : {overall}%",
                f"Skills Score        : {scores['skills']}%",
                f"Experience Score    : {scores['experience']}%",
                f"Education Score     : {scores['education']}%",
                f"TF-IDF Similarity   : {scores['tfidf']}%",
                "",
                f"Matched Skills ({len(matched_skills)}): {', '.join(sorted(matched_skills)) or 'None'}",
                f"Missing Skills ({len(missing_skills)}): {', '.join(sorted(missing_skills)) or 'None'}",
                "",
                f"Experience Detected : {exp_years} years",
                f"Education Detected  : {education or 'Not found'}",
                "",
                "RECOMMENDATIONS",
                "-" * 40,
            ] + [f"• {r}" for r in recs]

            st.download_button(
                "⬇️ Download Report (.txt)",
                data="\n".join(report_lines),
                file_name="screening_report.txt",
                mime="text/plain",
                use_container_width=True,
            )
