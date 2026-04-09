"""
matcher.py
Calculate match score between a resume and a job description.

Scoring weights (configurable at the top of this file):
  - Skills similarity   : 40%
  - TF-IDF similarity   : 20%
  - Experience fit      : 25%
  - Education fit       : 15%
"""

import re
from typing import Set, Tuple, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Weights (must sum to 1.0) ─────────────────────────────────────────────────
W_SKILLS     = 0.40
W_TFIDF      = 0.20
W_EXPERIENCE = 0.25
W_EDUCATION  = 0.15

# ── Education tier map ────────────────────────────────────────────────────────
EDU_TIER = {
    "PhD":         5,
    "Master's":    4,
    "MBA":         4,
    "Bachelor's":  3,
    "Associate's": 2,
    "Diploma":     1,
    None:          0,
}

DEGREE_KEYWORDS = {
    5: ["phd", "doctorate", "doctoral"],
    4: ["master", "ms ", "m.s", "mtech", "m.tech", "mba"],
    3: ["bachelor", "bs ", "b.s", "btech", "b.tech", "undergraduate", "degree"],
    2: ["associate"],
    1: ["diploma", "certificate"],
}


def calculate_match_score(
    resume_text: str,
    jd_text: str,
    resume_skills: Set[str],
    jd_skills: Set[str],
    exp_years: int,
    req_exp_years: int,
    education: str | None,
) -> Dict[str, int]:
    """
    Return a dict with keys: overall, skills, tfidf, experience, education.
    All values are integers in [0, 100].
    """
    skills_score  = _skills_score(resume_skills, jd_skills)
    tfidf_score   = _tfidf_score(resume_text, jd_text)
    exp_score     = _experience_score(exp_years, req_exp_years)
    edu_score     = _education_score(education, jd_text)

    overall = int(
        W_SKILLS     * skills_score
        + W_TFIDF    * tfidf_score
        + W_EXPERIENCE * exp_score
        + W_EDUCATION  * edu_score
    )
    overall = max(0, min(100, overall))

    return {
        "overall":    overall,
        "skills":     int(skills_score),
        "tfidf":      int(tfidf_score),
        "experience": int(exp_score),
        "education":  int(edu_score),
    }


def get_skill_gaps(
    resume_skills: Set[str],
    jd_skills: Set[str],
) -> Tuple[Set[str], Set[str]]:
    """
    Return (matched_skills, missing_skills) where both sets contain
    display-friendly canonical skill names.
    """
    # Normalise to lowercase for comparison
    resume_lower = {s.lower() for s in resume_skills}
    jd_lower     = {s.lower() for s in jd_skills}

    matched_lower = resume_lower & jd_lower
    missing_lower = jd_lower - resume_lower

    # Map back to display names using the original sets
    def _display(norm_set, original_set):
        low2disp = {s.lower(): s for s in original_set}
        return {low2disp[n] for n in norm_set if n in low2disp}

    matched = _display(matched_lower, resume_skills | jd_skills)
    missing = _display(missing_lower, jd_skills)

    return matched, missing


# ── Private scoring functions ─────────────────────────────────────────────────

def _skills_score(resume_skills: Set[str], jd_skills: Set[str]) -> float:
    """Jaccard-style match weighted toward JD coverage."""
    if not jd_skills:
        return 50.0  # neutral if JD has no extractable skills

    resume_lower = {s.lower() for s in resume_skills}
    jd_lower     = {s.lower() for s in jd_skills}

    matched = resume_lower & jd_lower
    # Coverage: what fraction of required skills does the candidate have?
    coverage = len(matched) / len(jd_lower)
    return min(100.0, coverage * 100)


def _tfidf_score(resume_text: str, jd_text: str) -> float:
    """Cosine similarity between TF-IDF vectors of resume and JD."""
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )
        corpus = [resume_text, jd_text]
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(sim) * 100, 1)
    except Exception:
        return 0.0


def _experience_score(actual: int, required: int) -> float:
    """
    Score experience fit:
    - If no requirement stated → 70 (neutral).
    - If actual >= required   → 100.
    - If actual == 0          → 20.
    - Linear interpolation in between.
    """
    if required <= 0:
        return 70.0
    if actual >= required:
        return 100.0
    if actual <= 0:
        return 20.0
    ratio = actual / required
    return round(20 + ratio * 80, 1)


def _education_score(education: str | None, jd_text: str) -> float:
    """
    Compare detected education tier to the tier required by the JD.
    Falls back to 60 if the JD doesn't mention education requirements.
    """
    candidate_tier = EDU_TIER.get(education, 0)
    required_tier  = _detect_required_edu_tier(jd_text)

    if required_tier == 0:
        # JD doesn't specify → give benefit of the doubt
        return 70.0 if candidate_tier >= 3 else 50.0

    if candidate_tier >= required_tier:
        return 100.0
    if candidate_tier == 0:
        return 20.0

    # Partial credit
    ratio = candidate_tier / required_tier
    return round(20 + ratio * 80, 1)


def _detect_required_edu_tier(jd_text: str) -> int:
    """Detect the education tier required in a job description."""
    lower = jd_text.lower()
    for tier in sorted(DEGREE_KEYWORDS.keys(), reverse=True):
        for kw in DEGREE_KEYWORDS[tier]:
            if kw in lower:
                return tier
    return 0
