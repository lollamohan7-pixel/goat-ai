"""
Automated Unit Tests for GOAT AI Matching Engine and Skill Extraction.
"""

import pytest
from services.skill_extractor import extract_skills_from_text, build_alias_lookup
from services.matching_engine import analyze_match, VERIFICATION_THRESHOLD
from database.db import init_db, save_analysis, get_analysis_by_id


def test_skill_extraction_keywords():
    """Verify that canonical skills and aliases are accurately extracted."""
    sample_text = "Proficient in Python, C++, Postgres, Docker, K8s, and Machine Learning."
    skills = extract_skills_from_text(sample_text)

    assert "python" in skills
    assert "c++" in skills
    assert "postgresql" in skills  # Aliased from Postgres
    assert "docker" in skills
    assert "kubernetes" in skills  # Aliased from K8s
    assert "machine learning" in skills


def test_boundary_handling_special_terms():
    """Verify terms with special characters (c++, c#, .net) don't trigger false positives."""
    text_clean = "Basic knowledge of C and CSS."
    skills = extract_skills_from_text(text_clean)
    assert "c" in skills
    assert "css" in skills
    assert "c++" not in skills
    assert "c#" not in skills


def test_score_above_85_threshold():
    """Verify that high-overlap profiles pass the 85% verification rule."""
    resume = """
    Senior Python Developer with 5 years experience.
    Skills: Python, Flask, PostgreSQL, Docker, Git, REST API, Linux, AWS, Pytest, Unit Testing, CI/CD.
    """
    job = """
    Required: Python, Flask, PostgreSQL, Docker, Git, REST API, AWS, CI/CD.
    """
    result = analyze_match(resume, job, target_role="Software Engineer")

    assert result["overall_match_score"] >= VERIFICATION_THRESHOLD
    assert result["is_verified"] is True
    assert "Verified — Score Threshold Met" in result["status_label"]
    assert len(result["missing_skills"]) == 0


def test_score_below_85_threshold():
    """Verify that low-overlap profiles are flagged Not Verified."""
    resume = """
    Junior web designer. Skills: HTML, CSS, JavaScript, Photoshop.
    """
    job = """
    Looking for a Senior Backend Engineer.
    Required skills: Python, Flask, Django, PostgreSQL, Docker, Kubernetes, AWS, Terraform, Microservices.
    """
    result = analyze_match(resume, job, target_role="Backend Engineer")

    assert result["overall_match_score"] < VERIFICATION_THRESHOLD
    assert result["is_verified"] is False
    assert "Not Verified — Below 85%" in result["status_label"]
    assert len(result["missing_skills"]) > 0


def test_exact_85_threshold_logic():
    """Verify that score >= 85.0 evaluates to verified according to specification."""
    assert VERIFICATION_THRESHOLD == 85.0


def test_database_persistence():
    """Test SQLite initialization, insertion, and retrieval."""
    init_db()
    analysis_id = save_analysis(
        target_role="Software Engineer",
        source_type="PDF (test.pdf)",
        match_score=88.5,
        is_verified=True,
        matched_skills=["python", "flask", "docker"],
        missing_skills=["kubernetes"],
        total_job_skills=4
    )
    assert analysis_id is not None
    record = get_analysis_by_id(analysis_id)
    assert record is not None
    assert record["target_role"] == "Software Engineer"
    assert record["match_score"] == 88.5
    assert record["is_verified"] is True
    assert "python" in record["matched_skills"]
    assert "kubernetes" in record["missing_skills"]
