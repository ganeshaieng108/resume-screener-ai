# 🎯 Resume Screener AI

A production-ready Streamlit web application that analyses resumes against job descriptions using NLP and machine learning, providing detailed match scores and actionable recommendations.

---

## ✨ Features

| Feature | Details |
|---|---|
| **File Support** | PDF (.pdf) and Word (.docx) resumes |
| **Skill Extraction** | 100+ technical & soft skills via keyword taxonomy |
| **NLP Matching** | TF-IDF + cosine similarity for semantic fit |
| **Weighted Scoring** | Skills 40% · Experience 25% · Education 15% · TF-IDF 20% |
| **Visualisations** | Gauge chart · Radar chart · Breakdown bars (Plotly) |
| **Recommendations** | Tailored suggestions for every gap found |
| **Report Export** | One-click .txt report download |

---

## 🖥 Screenshots (description)

1. **Input panel** — Left column with file uploader and job-description textarea. A word-count indicator warns when the JD is too short. A collapsible panel provides a sample JD for testing.

2. **Score gauge** — Semicircular dial coloured green/amber/red (≥70 / 45–69 / <45). Sits beside a table breaking down each sub-score.

3. **Skills chips** — Two columns: matched skills (green chips) and missing skills (red chips).

4. **Experience & Education cards** — Side-by-side, each with a coloured status pill.

5. **Radar chart** — Overlaid polygons comparing required vs candidate skills.

6. **Score breakdown bars** — Horizontal bars for all four scoring dimensions.

7. **Recommendations** — Blue-bordered suggestion cards at the bottom.

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone or download this folder
git clone <your-repo-url> resume-screener
cd resume-screener

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**.

---

## 🧪 Sample Usage

1. Open the app in your browser.
2. Click **Load a sample job description** (in the expander) and copy the text into the textarea.
3. Upload any PDF or DOCX resume (or create a short one with a few skills listed).
4. Click **🔍 Analyze Resume**.
5. View the match score, skills radar, and recommendations.

### Sample Job Description (for testing)

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
- Analyse large datasets to extract actionable insights
- Collaborate with cross-functional teams
- Present findings to non-technical stakeholders
```

---

## 📂 Project Structure

```
resume-screener/
├── app.py                  # Main Streamlit application
├── utils/
│   ├── __init__.py
│   ├── resume_parser.py    # Extract text from PDF / DOCX
│   ├── skill_extractor.py  # Keyword-based skill, education & experience extraction
│   ├── matcher.py          # Weighted scoring engine (TF-IDF + heuristics)
│   └── visualizer.py       # Plotly chart builders
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🌐 Deployment to Streamlit Cloud

1. Push this folder to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo and `app.py` as the entry point.
4. Click **Deploy** — Streamlit Cloud installs `requirements.txt` automatically.
5. No API keys or secrets are needed (all processing is local).

---

## 🔮 Future Improvements

- **Semantic skill matching** — use sentence-transformer embeddings instead of keyword lists for fuzzy skill recognition.
- **ATS score simulation** — parse common ATS keyword filters and flag resume formatting issues.
- **PDF report export** — generate a branded PDF report (reportlab / WeasyPrint).
- **Multi-language support** — detect language and apply locale-aware parsing.
- **Feedback loop** — let recruiters rate matches to fine-tune weights over time.
- **Database integration** — store and rank multiple candidates against one JD.
- **LinkedIn / GitHub import** — parse public profiles directly via URL.

---

## 📄 Licence

MIT — free to use, modify, and distribute.
