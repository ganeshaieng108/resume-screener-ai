"""
skill_extractor.py
Extract skills, education level, and years of experience from resume text.
Uses keyword matching against a curated tech / soft-skills taxonomy.
"""

import re
from typing import Set, Optional

# ── Master skills taxonomy ────────────────────────────────────────────────────
# Organised by category for easier maintenance.

TECH_SKILLS: dict[str, list[str]] = {
    "Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "r", "go", "golang", "rust", "kotlin", "swift", "scala", "php",
        "ruby", "perl", "matlab", "bash", "shell", "powershell",
    ],
    "Web": [
        "html", "css", "react", "angular", "vue", "node.js", "nodejs",
        "django", "flask", "fastapi", "spring", "express", "next.js",
        "nuxt", "tailwind", "bootstrap", "graphql", "rest", "api",
        "webpack", "vite",
    ],
    "Data & ML": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "neural networks", "tensorflow", "keras", "pytorch",
        "scikit-learn", "sklearn", "xgboost", "lightgbm", "catboost",
        "hugging face", "transformers", "pandas", "numpy", "scipy",
        "matplotlib", "seaborn", "plotly", "jupyter",
    ],
    "Data Engineering": [
        "sql", "nosql", "postgresql", "mysql", "sqlite", "oracle",
        "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
        "spark", "hadoop", "kafka", "airflow", "dbt", "etl",
        "data warehouse", "snowflake", "bigquery", "redshift",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "ci/cd", "github actions",
        "linux", "unix", "nginx", "apache", "microservices",
        "serverless", "lambda",
    ],
    "BI & Analytics": [
        "tableau", "power bi", "looker", "qlik", "excel", "google analytics",
        "data visualization", "a/b testing", "statistics",
    ],
    "Security": [
        "cybersecurity", "penetration testing", "owasp", "siem",
        "encryption", "iam", "sso", "oauth",
    ],
    "Mobile": [
        "android", "ios", "react native", "flutter", "xamarin",
    ],
    "Project / Methods": [
        "agile", "scrum", "kanban", "jira", "confluence", "git", "github",
        "gitlab", "bitbucket", "devops",
    ],
}

SOFT_SKILLS: list[str] = [
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "project management", "time management",
    "collaboration", "adaptability", "creativity", "mentoring",
    "presentation", "negotiation", "customer service", "analytical",
]

# Flatten all skills into a single lookup set (lowercase)
ALL_SKILLS: Set[str] = set()
for skills in TECH_SKILLS.values():
    ALL_SKILLS.update(skills)
ALL_SKILLS.update(SOFT_SKILLS)

# ── Education keywords ────────────────────────────────────────────────────────
DEGREE_PATTERNS = [
    (r"\bph\.?d\.?\b",                   "PhD"),
    (r"\bdoctor(?:ate|al)\b",            "PhD"),
    (r"\bm\.?s\.?\b|\bmaster[s]?\b",     "Master's"),
    (r"\bm\.?tech\.?\b|\bm\.?e\.?\b",    "Master's"),
    (r"\bmba\b",                          "MBA"),
    (r"\bb\.?s\.?\b|\bbachelor[s]?\b",   "Bachelor's"),
    (r"\bb\.?tech\.?\b|\bb\.?e\.?\b",    "Bachelor's"),
    (r"\bassociate[s]?\b",               "Associate's"),
    (r"\bdiploma\b",                     "Diploma"),
]

# ── Date / experience patterns ────────────────────────────────────────────────
YEAR_RE  = re.compile(r"\b(19|20)\d{2}\b")
MONTH_RE = re.compile(
    r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\b",
    re.IGNORECASE,
)
EXPLICIT_EXP_RE = re.compile(
    r"(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)",
    re.IGNORECASE,
)


# ── Public API ────────────────────────────────────────────────────────────────

def extract_skills(text: str) -> Set[str]:
    """
    Return a set of skills found in *text* by matching against the taxonomy.
    Multi-word skills are matched as phrases; single words as whole words.
    """
    if not text:
        return set()

    lower = text.lower()
    found: Set[str] = set()

    for skill in ALL_SKILLS:
        if " " in skill:
            # Phrase match (e.g. "machine learning")
            if skill in lower:
                found.add(_canonical(skill))
        else:
            # Whole-word match
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, lower):
                found.add(_canonical(skill))

    return found


def extract_education(text: str) -> Optional[str]:
    """
    Return the *highest* detected education level, or None if not found.
    """
    if not text:
        return None

    lower = text.lower()
    # Iterate in descending priority order
    for pattern, label in DEGREE_PATTERNS:
        if re.search(pattern, lower):
            return label
    return None


def extract_experience(text: str) -> int:
    """
    Estimate years of experience from the resume text.

    Strategy:
    1. Look for explicit phrases like "5 years of experience".
    2. Fall back to span of years mentioned in the text (max_year - min_year).
    Returns 0 if nothing is found.
    """
    if not text:
        return 0

    # 1. Explicit statement
    matches = EXPLICIT_EXP_RE.findall(text)
    if matches:
        return max(int(m) for m in matches)

    # 2. Year-span heuristic
    years = [int(y) for y in YEAR_RE.findall(text)]
    years = [y for y in years if 1970 <= y <= 2025]
    if len(years) >= 2:
        span = max(years) - min(years)
        # Cap at 40 to avoid noise from birth years, graduation years, etc.
        return min(span, 40)

    return 0


# ── Helpers ───────────────────────────────────────────────────────────────────

def _canonical(skill: str) -> str:
    """Return a display-friendly version of a skill name."""
    DISPLAY_OVERRIDES = {
        "python": "Python", "java": "Java", "javascript": "JavaScript",
        "typescript": "TypeScript", "c++": "C++", "c#": "C#", "r": "R",
        "go": "Go", "golang": "Go", "rust": "Rust", "kotlin": "Kotlin",
        "swift": "Swift", "scala": "Scala", "php": "PHP", "ruby": "Ruby",
        "html": "HTML", "css": "CSS", "react": "React", "angular": "Angular",
        "vue": "Vue.js", "nodejs": "Node.js", "node.js": "Node.js",
        "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
        "sql": "SQL", "nosql": "NoSQL", "postgresql": "PostgreSQL",
        "mysql": "MySQL", "mongodb": "MongoDB", "redis": "Redis",
        "spark": "Apache Spark", "kafka": "Kafka", "airflow": "Airflow",
        "aws": "AWS", "azure": "Azure", "gcp": "GCP", "docker": "Docker",
        "kubernetes": "Kubernetes", "terraform": "Terraform",
        "machine learning": "Machine Learning", "deep learning": "Deep Learning",
        "nlp": "NLP", "natural language processing": "NLP",
        "computer vision": "Computer Vision", "tensorflow": "TensorFlow",
        "pytorch": "PyTorch", "scikit-learn": "scikit-learn", "sklearn": "scikit-learn",
        "pandas": "Pandas", "numpy": "NumPy", "matplotlib": "Matplotlib",
        "tableau": "Tableau", "power bi": "Power BI",
        "git": "Git", "github": "GitHub", "gitlab": "GitLab",
        "agile": "Agile", "scrum": "Scrum",
        "linux": "Linux", "unix": "Unix",
        "ci/cd": "CI/CD", "devops": "DevOps",
        "snowflake": "Snowflake", "bigquery": "BigQuery",
        "leadership": "Leadership", "communication": "Communication",
        "teamwork": "Teamwork", "problem solving": "Problem Solving",
    }
    return DISPLAY_OVERRIDES.get(skill, skill.title())
