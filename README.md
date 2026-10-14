# 🐐 GOAT AI — Resume & Job Match Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

**GOAT AI** is an intelligent full-stack career acceleration web application designed to help students, recent graduates, and software engineering applicants analyze their resumes against real-world job descriptions. 

It calculates an **explainable skill-match score**, identifies missing competencies, flags vague statements with before-and-after rewrites, and generates a **personalized learning roadmap** from fundamentals to advanced portfolio projects.

---

## 🌟 Key Features

1. **Multi-Format Resume Parsing**
   - Extracts readable textual hierarchy from **PDF** (`PyMuPDF`) and **Word** (`python-docx`) documents.
   - Graceful fallback for malformed or scanned documents.
   - Privacy-centric: Resumes are processed in memory and never permanently stored.

2. **Explainable Match Scoring Engine**
   - Natural language skill extraction across 250+ technical tools, frameworks, and methodologies.
   - Combines **explicit keyword overlap** with **TF-IDF cosine similarity** for contextual relevance.
   - 100% transparent score calculation (no black-box vanity metrics).

3. **85% Algorithmic Verification Threshold**
   - **Score &ge; 85%**: Displays `✓ Verified — Score Threshold Met`.
   - **Score < 85%**: Displays `⚠️ Not Verified — Below 85%`.
   - *Clear Methodological Disclaimer:* Internal heuristic metric measuring keyword density and alignment. It does not certify candidate credentials or legal identity.

4. **Targeted Missing Skills Analysis**
   - Prioritizes absent employer requirements.
   - Distinguishes between programming languages, frameworks, cloud tooling, and databases.
   - Semantic alias resolution (e.g., `Postgres` &rarr; `PostgreSQL`, `K8s` &rarr; `Kubernetes`).

5. **Personalized 3-Tier Learning Roadmap**
   - **Level 1 (Beginner):** Core documentation and foundational commands.
   - **Level 2 (Intermediate):** Practical integration exercises and portfolio project blueprints.
   - **Level 3 (Advanced):** Production optimization, concurrency, and security considerations.

6. **Action-Oriented Resume Bullet Enhancements**
   - Identifies passive phrasing and missing metrics.
   - Supplies concrete before-and-after rewrites utilizing the XYZ formula (*Accomplished [X], as measured by [Y], by doing [Z]*).

7. **Downloadable PDF Assessment Reports**
   - Generates an official, publication-quality PDF report using ReportLab.

8. **Audit Trail & History**
   - Lightweight SQLite storage persists privacy-compliant analysis metadata and scores for quick historical comparison.

---

## 🏗️ Architecture & Project Structure

```text
goat.ai/
├── app.py                      # Core Flask Application & API Routes
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment Variable Template
├── .env                        # Local Environment Secrets
├── .gitignore                  # Git Ignore Specifications
├── README.md                   # Complete Documentation
├── database/
│   ├── __init__.py
│   └── db.py                   # SQLite Database Management & Schema
├── services/
│   ├── __init__.py
│   ├── resume_parser.py        # PDF (PyMuPDF) & DOCX Parsing Engine
│   ├── skill_extractor.py      # Boundary-Safe Skill Extraction & Taxonomy
│   ├── matching_engine.py      # TF-IDF Cosine Similarity & 85% Rule
│   ├── recommendations.py      # 3-Tier Roadmap & Bullet Rewrite Suggestions
│   └── report_generator.py     # Downloadable PDF Report Generator
├── static/
│   ├── css/
│   │   └── style.css           # Futuristic Dark Navy Glassmorphism Stylesheet
│   └── js/
│       └── script.js           # Drag-and-Drop, Animations, & Fetch API Client
├── templates/
│   └── index.html              # Responsive Semantic HTML5 Interface
└── tests/
    ├── __init__.py
    └── test_matching.py        # Pytest Automated Test Suite
```

---

## 🚀 Quickstart Guide (Local Development)

### 1. Prerequisites
- **Python 3.10+**
- **Git**
- **VS Code** (or your preferred editor)

### 2. Clone and Setup
Open your terminal (PowerShell or Bash) and execute:

```powershell
# 1. Clone repository
git clone https://github.com/your-username/goat-ai.git
cd goat-ai

# 2. Create Python virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Mac / Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
*(Optional: Add an `AI_API_KEY` if you wish to use Gemini or OpenAI API for enhanced LLM recommendations; otherwise, GOAT AI runs automatically with its curated expert knowledge base!)*

### 4. Run the Application
```powershell
python app.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```powershell
pytest -v
```

This validates:
- Keyword boundary extraction (ensuring `c++` or `c#` are not falsely confused with `c`).
- Alias mapping (e.g. `postgres` &rarr; `postgresql`).
- Exact &gt;= 85% score threshold verification status.
- Database persistence and record retrieval.

---

## 🌐 Production Deployment Guide

You can easily deploy GOAT AI on modern Python cloud platforms:

### Option A: Render.com (Recommended - Free Tier Available)
1. Push your repository to **GitHub**.
2. Log into [Render.com](https://render.com) and click **New Web Service**.
3. Select your GitHub repository.
4. Set the following fields:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (or `python app.py`)
5. Add any environment variables (`SECRET_KEY`, etc.).
6. Click **Deploy Web Service**!

### Option B: PythonAnywhere
1. Create a free account at [PythonAnywhere](https://www.pythonanywhere.com/).
2. Open a Bash console, clone your repo, and install `requirements.txt`.
3. In the **Web** tab, configure a Flask application pointing to `app.py`.

---

## 📜 Ethical & Compliance Disclaimers
- **Heuristic Evaluation Only:** GOAT AI evaluates textual alignment between applicant resumes and employer descriptions. Match scores do not predict hiring outcomes or guarantee interviews.
- **Verification Rule:** The 85% "Verified" badge is strictly an algorithmic alignment indicator; it does not authenticate real-world certifications, employment tenure, or legal identity.
- **Truth in Resumes:** Users are instructed never to fabricate skills, achievements, or employment history.

---

## 📄 License
Distributed under the **MIT License**. Created with ❤️ for aspiring engineers.
