"""
Recommendations & Roadmap Service for GOAT AI.
Generates structured learning roadmaps (beginner, intermediate, advanced),
portfolio project suggestions, and truthful resume bullet-point enhancements.
Includes optional AI API integration with robust offline fallbacks.
"""

import os
import json
from typing import Dict, List, Any, Optional
import requests

# Curated Roadmap Knowledge Base by Skill
ROADMAP_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "docker": {
        "beginner": "Learn Docker basics: container vs virtual machine, Dockerfile syntax, building and running images.",
        "intermediate": "Master multi-container orchestration with Docker Compose, volume persistence, and port mapping.",
        "advanced": "Implement multi-stage production builds, security scanning, and minimal base images (Alpine/Distroless).",
        "project": "Containerize a Flask + PostgreSQL web app with Docker Compose and health checks."
    },
    "kubernetes": {
        "beginner": "Understand Pods, Services, Deployments, and cluster architecture using Minikube or Kind.",
        "intermediate": "Configure ConfigMaps, Secrets, Ingress controllers, and persistent volume claims.",
        "advanced": "Deploy Helm charts, set up Horizontal Pod Autoscalers (HPA), and implement rolling zero-downtime updates.",
        "project": "Deploy a multi-tier microservice architecture with Ingress routing and automated scaling."
    },
    "postgresql": {
        "beginner": "Master SQL fundamentals: SELECT, JOINs, GROUP BY, aggregations, and constraint definitions.",
        "intermediate": "Design normalized schemas (3NF), write stored procedures, and optimize indexing (B-Tree, GIN).",
        "advanced": "Analyze query plans with EXPLAIN ANALYZE, tune connection pooling, and handle concurrent transactions (ACID).",
        "project": "Architect an e-commerce database with complex joins, transaction rollbacks, and composite indexing."
    },
    "aws": {
        "beginner": "Understand core cloud primitives: EC2 instances, S3 storage buckets, and IAM roles & security policies.",
        "intermediate": "Configure VPC subnets, Application Load Balancers, RDS managed databases, and Route 53.",
        "advanced": "Build event-driven serverless workflows with AWS Lambda, API Gateway, SQS queues, and CloudWatch.",
        "project": "Deploy a secure serverless REST API using Lambda, API Gateway, and S3 static frontend hosting."
    },
    "ci/cd": {
        "beginner": "Understand continuous integration concepts: automated testing on pull requests and branch protection.",
        "intermediate": "Write GitHub Actions workflows to build, lint, and test Python applications automatically.",
        "advanced": "Implement deployment pipelines to staging/production with secret management and rollback triggers.",
        "project": "Build an automated GitHub Actions pipeline with pytest unit tests, code coverage, and Docker push."
    },
    "unit testing": {
        "beginner": "Learn test assertions and test discovery using the pytest framework.",
        "intermediate": "Implement fixtures, parameterized tests, and test database rollbacks.",
        "advanced": "Mock external APIs and services using unittest.mock; establish 80%+ test coverage reports.",
        "project": "Write comprehensive unit and integration test suites for REST endpoints and edge cases."
    },
    "rest api": {
        "beginner": "Understand HTTP verbs (GET, POST, PUT, DELETE), status codes (200, 201, 400, 404, 500), and JSON payloads.",
        "intermediate": "Implement request validation, token-based authentication (JWT), pagination, and error handlers.",
        "advanced": "Design idempotent endpoints, rate limiting, OpenAPI/Swagger specifications, and API versioning.",
        "project": "Build a secure RESTful API in Flask with JWT authentication and documented Swagger schemas."
    },
    "machine learning": {
        "beginner": "Study supervised learning: Linear Regression, Logistic Regression, Decision Trees using Scikit-Learn.",
        "intermediate": "Implement model evaluation (Cross-validation, ROC-AUC, F1-Score), feature engineering, and hyperparameter tuning.",
        "advanced": "Build ensemble models (Random Forest, XGBoost) and integrate model artifacts into Flask REST endpoints.",
        "project": "Train and deploy a salary prediction or churn classification model with an interactive web UI."
    },
    "pandas": {
        "beginner": "Master Series, DataFrames, indexing, filtering, and reading CSV/Excel/SQL data.",
        "intermediate": "Perform data cleansing, handling missing values, apply functions, and multi-index groupby operations.",
        "advanced": "Optimize memory usage with categorical types, vectorized operations, and large dataset streaming.",
        "project": "Analyze a Kaggle dataset to uncover business insights with visual charts and clean code."
    },
    "react": {
        "beginner": "Understand JSX, components, props, state, and standard event handling.",
        "intermediate": "Master React Hooks (useState, useEffect, useContext), component lifecycle, and modular CSS.",
        "advanced": "Implement state management (Redux Toolkit or Zustand), performance memoization, and route guards.",
        "project": "Create a responsive single-page web app consuming REST APIs with optimistic UI updates."
    }
}

# General Default Roadmap Items
DEFAULT_ROADMAP = {
    "beginner": [
        "Review foundational documentation and core syntax for the missing technical requirement.",
        "Complete hands-on interactive tutorials and solve 5-10 baseline coding exercises.",
        "Understand real-world architectural use cases and best-practice conventions."
    ],
    "intermediate": [
        "Integrate the missing technology into an existing project to solve a concrete problem.",
        "Write unit tests and verify handling of edge cases and error states.",
        "Connect with databases or external APIs using secure configuration patterns."
    ],
    "advanced": [
        "Optimize runtime performance, caching, and concurrent throughput.",
        "Implement production-grade logging, metrics monitoring, and automated deployment.",
        "Publish documented code with an architectural diagram on GitHub."
    ]
}

# Resume Bullet Point Enhancement Rules
BULLET_IMPROVEMENT_TEMPLATES = [
    {
        "topic": "Backend / API Development",
        "original": "Worked on backend features and fixed API bugs.",
        "recommended": "Architected 6 RESTful API endpoints in Flask handling user authentication and data serialization, reducing API response latency by 25%.",
        "reason": "Specify technologies, action verbs (Architected), and measurable impact (25% faster)."
    },
    {
        "topic": "Database & Query Optimization",
        "original": "Created database tables and wrote SQL queries.",
        "recommended": "Designed normalized relational schemas in PostgreSQL with foreign key constraints and B-Tree indexing, accelerating query retrieval time.",
        "reason": "Demonstrate knowledge of schema design, constraints, and optimization techniques."
    },
    {
        "topic": "Testing & Code Quality",
        "original": "Tested the application before launch.",
        "recommended": "Authored automated unit and integration tests using pytest, raising test coverage to 85% and preventing regression defects during deployment.",
        "reason": "Show verifiable quality habits with tools (pytest) and quantifiable metrics (85% coverage)."
    },
    {
        "topic": "Frontend / Full Stack Integration",
        "original": "Made the website responsive and added buttons.",
        "recommended": "Engineered responsive UI components using semantic HTML5, CSS Grid, and JavaScript Fetch API, achieving seamless cross-device mobile compatibility.",
        "reason": "Highlights professional engineering practices rather than generic visual styling."
    }
]


def generate_curated_roadmap(missing_skills: List[str]) -> Dict[str, List[str]]:
    """
    Build a multi-level learning roadmap tailored to the identified missing skills.
    """
    beginner_tasks = []
    intermediate_tasks = []
    advanced_tasks = []

    skills_to_process = missing_skills[:6] if missing_skills else []

    for skill in skills_to_process:
        s_lower = skill.lower()
        if s_lower in ROADMAP_KNOWLEDGE_BASE:
            info = ROADMAP_KNOWLEDGE_BASE[s_lower]
            beginner_tasks.append(f"[{skill.upper()}] {info['beginner']}")
            intermediate_tasks.append(f"[{skill.upper()}] {info['intermediate']} • Project idea: {info['project']}")
            advanced_tasks.append(f"[{skill.upper()}] {info['advanced']}")
        else:
            beginner_tasks.append(f"[{skill.upper()}] Study fundamentals, core commands, and official documentation for {skill}.")
            intermediate_tasks.append(f"[{skill.upper()}] Build a mini-project implementing {skill} with standard error handling.")
            advanced_tasks.append(f"[{skill.upper()}] Learn production debugging, security best practices, and integration patterns for {skill}.")

    # Fallback to default if no specific missing skills
    if not beginner_tasks:
        beginner_tasks = list(DEFAULT_ROADMAP["beginner"])
        intermediate_tasks = list(DEFAULT_ROADMAP["intermediate"])
        advanced_tasks = list(DEFAULT_ROADMAP["advanced"])

    return {
        "beginner": beginner_tasks,
        "intermediate": intermediate_tasks,
        "advanced": advanced_tasks
    }


def generate_bullet_suggestions(resume_text: str, missing_skills: List[str]) -> List[Dict[str, str]]:
    """
    Provide actionable before-and-after bullet point rewrites tailored to technical resumes.
    """
    suggestions = list(BULLET_IMPROVEMENT_TEMPLATES)
    # If missing skills exist, provide an additional contextual advice note
    if missing_skills:
        top_missing = ", ".join(missing_skills[:3])
        suggestions.append({
            "topic": "Skill Evidence & Project Descriptions",
            "original": f"Interested in learning {top_missing}.",
            "recommended": f"Built a proof-of-concept project integrating {top_missing} with clear README documentation and automated test verification.",
            "reason": "Recruiters look for demonstrated evidence. Replace aspirational claims with tangible project repositories."
        })
    return suggestions


def call_ai_assistant(resume_text: str, job_text: str, missing_skills: List[str]) -> Optional[Dict[str, Any]]:
    """
    Optional AI API integration (e.g. Gemini / OpenAI compatible) if AI_API_KEY is configured.
    Falls back gracefully to curated rules if key is missing or call fails.
    """
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return None

    try:
        # Prompt engineered for concise, truthful recommendations
        prompt = (
            f"You are an expert technical career mentor. A candidate is applying for a job with missing skills: {missing_skills}.\n"
            "Provide:\n"
            "1. A 3-step learning roadmap (beginner, intermediate, advanced) specifically addressing the missing skills.\n"
            "2. Two truthful bullet point rewrites showing how to describe technical projects with metrics.\n"
            "Do NOT fabricate employment history or credentials. Output valid JSON with keys 'roadmap' and 'suggestions'."
        )

        # Call Gemini REST API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        response = requests.post(url, headers=headers, json=payload, timeout=6)
        if response.status_code == 200:
            result_json = response.json()
            raw_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_text)
            return parsed
    except Exception:
        # Silently fall back to deterministic rule-based output
        return None

    return None


def get_recommendations_and_roadmap(
    resume_text: str,
    job_text: str,
    missing_skills: List[str]
) -> Dict[str, Any]:
    """
    Main entry point for generating roadmaps and resume bullet-point enhancements.
    Uses AI if available, otherwise seamlessly uses expert curated rules.
    """
    ai_result = call_ai_assistant(resume_text, job_text, missing_skills)
    if ai_result and "roadmap" in ai_result and "suggestions" in ai_result:
        return {
            "roadmap": ai_result["roadmap"],
            "suggestions": ai_result["suggestions"],
            "source": "AI-Powered Analysis"
        }

    # Deterministic Expert Fallback
    roadmap = generate_curated_roadmap(missing_skills)
    suggestions = generate_bullet_suggestions(resume_text, missing_skills)

    return {
        "roadmap": roadmap,
        "suggestions": suggestions,
        "source": "Curated Domain Framework"
    }
