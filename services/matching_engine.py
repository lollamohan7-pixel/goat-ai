"""
Matching Engine Service for GOAT AI.
Performs transparent skill overlap calculation, TF-IDF cosine similarity,
and computes an explainable composite match score with the 85% verification rule.
"""

from typing import Dict, List, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.skill_extractor import extract_skills_from_text, get_skill_category

VERIFICATION_THRESHOLD = 85.0


def calculate_tfidf_similarity(resume_text: str, job_text: str) -> float:
    """
    Compute cosine similarity between resume and job description using TF-IDF vectors.
    Returns a score normalized between 0.0 and 100.0.
    """
    if not resume_text or not job_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=2500
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Rescale similarity score (raw cosine is typically 0.1 to 0.6 for resumes)
        scaled_score = min(100.0, float(similarity) * 160.0)
        return round(scaled_score, 1)
    except Exception:
        return 0.0


def analyze_match(resume_text: str, job_text: str, target_role: str = "") -> Dict[str, Any]:
    """
    Analyze the resume against the job description.
    Returns a comprehensive dictionary with matched skills, missing skills,
    composite score, explainable breakdown, and 85% verification status.
    """
    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_text)

    # Calculate Matched and Missing Skills
    matched_skills = [s for s in job_skills if s in resume_skills]
    missing_skills = [s for s in job_skills if s not in resume_skills]
    additional_candidate_skills = [s for s in resume_skills if s not in job_skills]

    # Calculate Skill Overlap Score (0 to 100)
    total_job_skills = len(job_skills)
    if total_job_skills > 0:
        skill_coverage_score = (len(matched_skills) / total_job_skills) * 100.0
    else:
        skill_coverage_score = 0.0

    # Calculate Contextual Text Similarity using TF-IDF
    context_similarity_score = calculate_tfidf_similarity(resume_text, job_text)

    # Composite Score Calculation:
    # 75% weighted towards explicit skill keyword coverage
    # 25% weighted towards contextual semantic overlap
    if total_job_skills > 0:
        composite_score = (0.75 * skill_coverage_score) + (0.25 * context_similarity_score)
    else:
        # If no explicit skills identified in job description, rely on TF-IDF
        composite_score = context_similarity_score

    # Clamp score between 0 and 100
    final_score = max(0.0, min(100.0, round(composite_score, 1)))

    # Apply 85% Verification Rule
    is_verified = final_score >= VERIFICATION_THRESHOLD
    status_label = "Verified — Score Threshold Met" if is_verified else "Not Verified — Below 85%"

    # Transparent, Explainable Score Breakdown
    if total_job_skills > 0:
        explanation = (
            f"Overall score of {round(final_score)}% is derived from matching {len(matched_skills)} of "
            f"{total_job_skills} required skills ({round(skill_coverage_score)}% skill coverage) combined with "
            f"contextual document similarity ({round(context_similarity_score)}%)."
        )
    else:
        explanation = (
            f"Overall score of {round(final_score)}% is based on contextual document similarity because no standard "
            f"technical skills were recognized in the provided job description."
        )

    # Categorize Missing Skills for Targeted Action
    missing_by_category: Dict[str, List[str]] = {}
    for skill in missing_skills:
        cat = get_skill_category(skill)
        missing_by_category.setdefault(cat, []).append(skill)

    return {
        "overall_match_score": final_score,
        "skill_coverage_score": round(skill_coverage_score, 1),
        "context_similarity_score": round(context_similarity_score, 1),
        "is_verified": is_verified,
        "status_label": status_label,
        "verification_threshold": VERIFICATION_THRESHOLD,
        "score_explanation": explanation,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_candidate_skills": additional_candidate_skills,
        "total_job_skills": total_job_skills,
        "total_resume_skills": len(resume_skills),
        "missing_by_category": missing_by_category,
        "target_role": target_role
    }
