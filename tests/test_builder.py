"""
Unit Tests for GOAT AI Resume Builder PDF Generation Service.
Tests Modern Minimalist and Classic ATS layouts, XML escaping, edge cases,
and byte stream validity.
"""

import io
import pytest
from services.resume_builder_pdf import generate_resume_pdf, safe_text, _parse_bullet_list


@pytest.fixture
def sample_resume_data():
    """Sample comprehensive resume data payload."""
    return {
        "full_name": "Jordan Hayes",
        "headline": "Lead Full Stack Software Engineer",
        "contact": {
            "email": "jordan.hayes@example.com",
            "phone": "+1 (555) 349-2819",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/jordanhayes",
            "github": "github.com/jordanhayes",
            "portfolio": "jordanhayes.dev"
        },
        "summary": "Full Stack Engineer with 6+ years of experience designing high-throughput distributed systems and responsive user interfaces.",
        "skills": {
            "languages": "Python, TypeScript, Go, SQL, Bash",
            "frameworks": "Flask, FastAPI, React, Node.js, Next.js",
            "cloud_devops": "Docker, Kubernetes, AWS (ECS, S3, RDS), Terraform, CI/CD",
            "databases": "PostgreSQL, Redis, DynamoDB"
        },
        "experience": [
            {
                "role": "Senior Software Engineer",
                "company": "Apex Cloud Systems",
                "location": "San Francisco, CA",
                "start_date": "2022-04",
                "end_date": "Present",
                "current": True,
                "bullets": [
                    "Spearheaded redesign of the billing microservice, handling 15M daily transactions with 99.99% uptime.",
                    "Reduced p95 API response latency by 38% via PostgreSQL connection pooling and Redis caching."
                ]
            },
            {
                "role": "Software Engineer",
                "company": "DataVibe Analytics",
                "location": "Austin, TX",
                "start_date": "2019-06",
                "end_date": "2022-03",
                "current": False,
                "bullets": (
                    "Built full-stack analytics dashboards with React and Flask.\n"
                    "Automated integration testing and container builds using GitHub Actions."
                )
            }
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "school": "University of Texas at Austin",
                "location": "Austin, TX",
                "graduation_year": "2019",
                "gpa": "3.88 / 4.0",
                "honors": "Magna Cum Laude"
            }
        ],
        "projects": [
            {
                "title": "GOAT AI Resume Matcher",
                "technologies": "Python, Flask, PyMuPDF, scikit-learn",
                "link": "github.com/jordanhayes/goat-ai",
                "bullets": [
                    "Engineered transparent NLP skill extraction and contextual similarity scoring.",
                    "Integrated ReportLab for instantaneous PDF generation."
                ]
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect – Associate",
                "issuer": "Amazon Web Services",
                "date": "2023",
                "credential_id": "AWS-829103"
            }
        ],
        "achievements": [
            "Winner — Austin Cloud Hackathon 2021 (Top 1% out of 250 teams)",
            "Speaker at PyTexas 2023 on Microservices Optimization"
        ],
        "languages": [
            {"name": "English", "proficiency": "Native"},
            {"name": "Spanish", "proficiency": "Professional Working"}
        ]
    }


def test_safe_text_escaping():
    """Verify that dangerous XML characters (&, <, >) are escaped cleanly."""
    raw = "Skills: C++ & Python (<10ms latency) & AT&T experience"
    escaped = safe_text(raw)
    assert "&amp;" in escaped
    assert "&lt;" in escaped
    assert "<" not in escaped
    assert safe_text(None) == ""
    assert safe_text(123) == "123"


def test_parse_bullet_list():
    """Verify that bullet list helper handles both lists and raw multiline strings."""
    # List input
    items = ["Line 1", "  Line 2  ", ""]
    parsed = _parse_bullet_list(items)
    assert parsed == ["Line 1", "Line 2"]

    # String with dashes and asterisks
    raw_str = "- Bullet one\n* Bullet two\n• Bullet three"
    parsed_str = _parse_bullet_list(raw_str)
    assert parsed_str == ["Bullet one", "Bullet two", "Bullet three"]

    # Empty / None
    assert _parse_bullet_list(None) == []
    assert _parse_bullet_list("") == []


def test_generate_pdf_modern_layout(sample_resume_data):
    """Verify that generating a modern layout returns a non-empty, valid PDF byte stream."""
    pdf_buffer = generate_resume_pdf(sample_resume_data, template_style="modern")
    assert isinstance(pdf_buffer, io.BytesIO)
    content = pdf_buffer.getvalue()
    assert len(content) > 1000
    assert content.startswith(b"%PDF-")  # Standard PDF file header magic number


def test_generate_pdf_classic_layout(sample_resume_data):
    """Verify that generating a classic ATS layout returns a valid PDF byte stream."""
    pdf_buffer = generate_resume_pdf(sample_resume_data, template_style="classic")
    assert isinstance(pdf_buffer, io.BytesIO)
    content = pdf_buffer.getvalue()
    assert len(content) > 1000
    assert content.startswith(b"%PDF-")


def test_generate_pdf_minimal_empty_data():
    """Verify that minimal or empty inputs do not raise unhandled exceptions."""
    minimal_data = {
        "full_name": "Jane Doe",
        "contact": {}
    }
    pdf_buffer = generate_resume_pdf(minimal_data, template_style="modern")
    content = pdf_buffer.getvalue()
    assert len(content) > 500
    assert content.startswith(b"%PDF-")


def test_generate_pdf_special_characters_no_crash():
    """Ensure that special characters in all fields parse without XML syntax errors."""
    data_with_specials = {
        "full_name": "Renée O'Connor & Sons <CEO>",
        "headline": "Lead C++ & C# Developer",
        "contact": {
            "email": "renee+dev@example.com",
            "location": "Zürich & Berlin"
        },
        "summary": "Specialized in Low Latency (<1ms) & High Frequency Trading.",
        "skills": {
            "core": "C++, C#, AT&T Unix, <templates>"
        },
        "experience": [
            {
                "role": "Staff Engineer <Trading>",
                "company": "B & M Capital",
                "bullets": ["Optimized throughput & reduced latency by <50%."]
            }
        ]
    }
    pdf_buffer = generate_resume_pdf(data_with_specials, template_style="classic")
    assert pdf_buffer.getvalue().startswith(b"%PDF-")


# ============================================================================
# Route & Endpoint Integration Tests (Step 2)
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_route_builder_page_get(client):
    """Verify that GET /builder renders the resume builder template successfully."""
    response = client.get('/builder')
    assert response.status_code == 200
    assert b"Professional Resume Builder" in response.data
    assert b"GOAT" in response.data


def test_api_builder_download_pdf_success_modern(client, sample_resume_data):
    """Verify that POST /api/builder/download-pdf with modern style generates and returns a valid PDF."""
    response = client.post(
        '/api/builder/download-pdf',
        json={**sample_resume_data, "template_style": "modern"}
    )
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.data.startswith(b"%PDF-")
    cd_header = response.headers.get('Content-Disposition', '')
    assert 'attachment' in cd_header
    assert 'Jordan_Hayes_GOAT_Resume.pdf' in cd_header


def test_api_builder_download_pdf_success_classic(client, sample_resume_data):
    """Verify that POST /api/builder/download-pdf with classic style generates and returns a valid PDF."""
    response = client.post(
        '/api/builder/download-pdf',
        json={**sample_resume_data, "template_style": "classic"}
    )
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.data.startswith(b"%PDF-")
    cd_header = response.headers.get('Content-Disposition', '')
    assert 'attachment' in cd_header


def test_api_builder_download_pdf_empty_payload(client):
    """Verify that empty payload returns HTTP 400 Bad Request."""
    response = client.post('/api/builder/download-pdf', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'empty' in data['error'].lower()


def test_api_builder_download_pdf_non_json(client):
    """Verify that non-JSON request returns HTTP 400."""
    response = client.post(
        '/api/builder/download-pdf',
        data="not-a-json-payload",
        content_type="text/plain"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_api_builder_download_pdf_special_characters_filename(client):
    """Verify that special characters in name are sanitized cleanly in download filename."""
    payload = {
        "full_name": "Dr. Sarah O'Connor / M.D. & Eng.",
        "summary": "Specialist in machine learning applications."
    }
    response = client.post('/api/builder/download-pdf', json=payload)
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.data.startswith(b"%PDF-")
    cd_header = response.headers.get('Content-Disposition', '')
    # Slashes and quotes stripped from filename
    assert "/" not in cd_header.split("filename=")[-1]
    assert "Dr_Sarah_OConnor__MD__Eng_GOAT_Resume.pdf" in cd_header


# ============================================================================
# Guided Form, Navigation & Contract Tests (Step 3)
# ============================================================================

def test_builder_form_renders_all_guided_sections(client):
    """Verify that GET /builder renders all 9 guided resume form sections and preview elements."""
    response = client.get('/builder')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # 1. Personal & Contact
    assert 'Personal &amp; Contact Details' in html or 'Personal & Contact Details' in html
    assert 'id="fullName"' in html
    assert 'id="headline"' in html
    assert 'id="email"' in html
    assert 'id="phone"' in html
    assert 'id="location"' in html
    assert 'id="linkedin"' in html
    assert 'id="github"' in html
    assert 'id="portfolio"' in html

    # 2. Professional Summary
    assert 'Professional Summary' in html
    assert 'id="summary"' in html

    # 3. Technical Skills
    assert 'Technical Skills' in html
    assert 'id="skillsLanguages"' in html
    assert 'id="skillsFrameworks"' in html
    assert 'id="skillsTools"' in html
    assert 'id="skillsDatabases"' in html

    # 4. Experience & Internships
    assert 'Work Experience &amp; Internships' in html or 'Work Experience & Internships' in html
    assert 'id="experienceListContainer"' in html
    assert 'id="addExperienceBtn"' in html

    # 5. Education
    assert 'Education' in html
    assert 'id="educationListContainer"' in html
    assert 'id="addEducationBtn"' in html

    # 6. Projects
    assert 'Projects' in html
    assert 'id="projectsListContainer"' in html
    assert 'id="addProjectBtn"' in html

    # 7. Certifications
    assert 'Certifications' in html
    assert 'id="certificationsListContainer"' in html
    assert 'id="addCertificationBtn"' in html

    # 8. Achievements
    assert 'Achievements' in html
    assert 'id="achievements"' in html

    # 9. Languages
    assert 'Languages' in html
    assert 'id="languagesListContainer"' in html
    assert 'id="addLanguageBtn"' in html

    # Template selector buttons
    assert 'id="templateModernBtn"' in html
    assert 'id="templateClassicBtn"' in html

    # Live preview container and paper sheet
    assert 'id="resumePaperSheet"' in html
    assert 'id="rpName"' in html
    assert 'id="rpContact"' in html
    assert 'id="downloadPdfBtn"' in html


def test_index_navigation_contains_builder_link(client):
    """Verify that the existing index.html navigation links to the Resume Builder."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'href="/builder"' in html
    assert 'Resume Builder' in html


def test_builder_static_js_served(client):
    """Verify that static/js/builder.js is served with proper content."""
    response = client.get('/static/js/builder.js')
    assert response.status_code == 200
    js = response.data.decode('utf-8')
    assert 'serializeResumeData' in js
    assert 'updateLivePreview' in js
    assert 'addExperienceEntry' in js
    assert 'addEducationEntry' in js


def test_full_contract_payload_roundtrip(client):
    """Verify that a comprehensive payload matching builder.js serializeResumeData() succeeds."""
    payload = {
        "template_style": "modern",
        "full_name": "Maya Patel",
        "headline": "Lead DevOps & Cloud Architect",
        "contact": {
            "email": "maya.patel@example.com",
            "phone": "+1 (555) 019-4821",
            "location": "Seattle, WA",
            "linkedin": "linkedin.com/in/mayapatel",
            "github": "github.com/mayapatel",
            "portfolio": "mayapatel.cloud"
        },
        "summary": "Cloud Solutions Architect specializing in Kubernetes cluster orchestration, Terraform IaC, and zero-downtime CI/CD deployments.",
        "skills": {
            "languages": "Go, Python, Bash",
            "frameworks": "FastAPI, Gin",
            "cloud_devops": "Kubernetes, Docker, AWS, Terraform, Helm, ArgoCD",
            "databases": "PostgreSQL, Redis"
        },
        "experience": [
            {
                "role": "Staff DevOps Engineer",
                "company": "Nimbus Infrastructure",
                "location": "Seattle, WA",
                "start_date": "2021-03",
                "end_date": "Present",
                "current": True,
                "bullets": "Managed multi-region EKS clusters serving 50M requests daily.\nAutomated infrastructure provisioning with Terraform, cutting spin-up times by 70%."
            }
        ],
        "education": [
            {
                "degree": "M.S. in Computer Engineering",
                "school": "University of Washington",
                "location": "Seattle, WA",
                "graduation_year": "2020",
                "gpa": "3.92 / 4.0",
                "honors": "Graduate Research Fellow"
            }
        ],
        "projects": [
            {
                "title": "KubeGuard — Kubernetes Security Sentinel",
                "technologies": "Go, Kubernetes API, Prometheus",
                "link": "github.com/mayapatel/kubeguard",
                "bullets": "Built an open-source policy controller preventing misconfigured RBAC."
            }
        ],
        "certifications": [
            {
                "name": "Certified Kubernetes Administrator (CKA)",
                "issuer": "CNCF / Linux Foundation",
                "date": "2022",
                "credential_id": "CKA-981240"
            }
        ],
        "achievements": [
            "Featured Speaker at KubeCon North America 2023",
            "Top Open Source Contributor to CNCF tooling"
        ],
        "languages": [
            {"name": "English", "proficiency": "Native"},
            {"name": "Gujarati", "proficiency": "Native / Bilingual"}
        ]
    }

    response = client.post('/api/builder/download-pdf', json=payload)
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.data.startswith(b"%PDF-")
    cd_header = response.headers.get('Content-Disposition', '')
    assert 'Maya_Patel_GOAT_Resume.pdf' in cd_header


def test_payload_with_only_whitespace_returns_400(client):
    """Verify that a payload with only whitespace fields is rejected with 400."""
    whitespace_payload = {
        "full_name": "   ",
        "summary": "   ",
        "skills": {
            "languages": "  ",
            "frameworks": ""
        },
        "experience": [],
        "education": []
    }
    response = client.post('/api/builder/download-pdf', json=whitespace_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


# ============================================================================
# Regression & Privacy Compliance Tests (Step 4)
# ============================================================================

def test_builder_template_contains_match_button(client):
    """Verify that builder template contains the 'Match with Job' action button."""
    response = client.get('/builder')
    assert response.status_code == 200
    assert b"id=\"analyzeMatchBtn\"" in response.data
    assert b"Match with Job" in response.data


def test_existing_analyzer_endpoint_regression(client):
    """Verify that original POST /api/analyze endpoint functions normally."""
    job_desc = "Seeking a Python backend engineer with Flask, PostgreSQL, and Docker experience."
    resume_text = "Experienced Developer with Python, Flask, PostgreSQL, Git, and Docker skills."

    response = client.post(
        '/api/analyze',
        data={
            'job_description': job_desc,
            'resume_text': resume_text,
            'target_role': 'Software Engineer'
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'overall_match_score' in data
    assert 'matched_skills' in data
    assert 'roadmap' in data
    assert 'python' in data['matched_skills']
    assert data['analysis_id'] is not None


def test_existing_history_and_report_download_regression(client):
    """Verify that /api/history and /api/download-report/<id> continue working."""
    # Run analysis first to create a record
    res = client.post(
        '/api/analyze',
        data={
            'job_description': 'Require Python, SQL, Git, and Unit Testing.',
            'resume_text': 'Skills: Python, SQL, Git, Pytest, Unit Testing.',
            'target_role': 'Software Engineer'
        }
    )
    analysis_id = res.get_json()['analysis_id']

    # Retrieve history
    hist_res = client.get('/api/history')
    assert hist_res.status_code == 200
    history = hist_res.get_json().get('history', [])
    assert any(item['id'] == analysis_id for item in history)

    # Download report PDF
    report_res = client.get(f'/api/download-report/{analysis_id}')
    assert report_res.status_code == 200
    assert report_res.mimetype == 'application/pdf'
    assert report_res.data.startswith(b"%PDF-")


def test_privacy_compliance_no_full_resume_in_db():
    """Verify that SQLite does not store full resume text by design."""
    from database.db import get_db_connection
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(analysis_records);")
        columns = [row[1] for row in cursor.fetchall()]
        # Verify prohibited columns are NOT present
        assert "resume_text" not in columns
        assert "full_resume" not in columns
        assert "document_content" not in columns
    finally:
        conn.close()



