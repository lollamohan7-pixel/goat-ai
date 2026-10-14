"""
Database Management Service for GOAT AI.
Uses SQLite to store privacy-compliant analysis metadata, scores, and timestamps.
Full resumes are never persisted to protect applicant privacy.
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

DATABASE_PATH = os.getenv("DATABASE_PATH", "database/goat_ai.db")


def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection configured with dictionary row access."""
    # Ensure database directory exists
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the SQLite database schema if not already created."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_role TEXT,
                source_type TEXT,
                match_score REAL NOT NULL,
                is_verified INTEGER NOT NULL,
                matched_skills TEXT,
                missing_skills TEXT,
                total_job_skills INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    finally:
        conn.close()


def save_analysis(
    target_role: str,
    source_type: str,
    match_score: float,
    is_verified: bool,
    matched_skills: List[str],
    missing_skills: List[str],
    total_job_skills: int
) -> int:
    """
    Persist analysis summary metadata to the database.
    Returns the newly created analysis ID.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analysis_records (
                target_role,
                source_type,
                match_score,
                is_verified,
                matched_skills,
                missing_skills,
                total_job_skills,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            target_role or "General Role",
            source_type or "Resume",
            round(match_score, 1),
            1 if is_verified else 0,
            json.dumps(matched_skills),
            json.dumps(missing_skills),
            total_job_skills,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve an analysis record by its primary key ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analysis_records WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        if not row:
            return None

        return {
            "id": row["id"],
            "target_role": row["target_role"],
            "source_type": row["source_type"],
            "match_score": row["match_score"],
            "is_verified": bool(row["is_verified"]),
            "matched_skills": json.loads(row["matched_skills"] or "[]"),
            "missing_skills": json.loads(row["missing_skills"] or "[]"),
            "total_job_skills": row["total_job_skills"],
            "created_at": row["created_at"]
        }
    finally:
        conn.close()


def get_recent_history(limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieve recent analysis runs ordered by creation timestamp descending."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, target_role, source_type, match_score, is_verified, created_at
            FROM analysis_records
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "target_role": row["target_role"],
                "source_type": row["source_type"],
                "match_score": row["match_score"],
                "is_verified": bool(row["is_verified"]),
                "created_at": row["created_at"]
            }
            for row in rows
        ]
    finally:
        conn.close()
