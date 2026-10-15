"""
GOAT AI — AI Resume & Job Match Analyzer
Main Flask Application Server
"""

import os
import json
import re
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

from services.resume_parser import extract_resume_text, ResumeParserError
from services.matching_engine import analyze_match
from services.recommendations import get_recommendations_and_roadmap
from services.report_generator import generate_pdf_report
from services.resume_builder_pdf import generate_resume_pdf
from database.db import init_db, save_analysis, get_analysis_by_id, get_recent_history

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'goat-ai-default-secret-key-34821')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB maximum request size

# Initialize SQLite database tables on startup
init_db()


@app.route('/')
def index():
    """Render the primary landing page and analyzer dashboard."""
    return render_template('index.html')


@app.route('/builder')
def resume_builder():
    """Render the guided resume builder interface."""
    return render_template('builder.html')


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    Core API endpoint to process resume, evaluate job description,
    calculate match score, and generate personalized recommendations.
    """
    try:
        job_description = request.form.get('job_description', '').strip()
        target_role = request.form.get('target_role', 'General Role').strip()

        if not job_description:
            return jsonify({'error': 'Please provide a job description to compare against.'}), 400

        # Extract resume text from file upload or raw pasted text
        resume_file = request.files.get('resume_file')
        resume_text_raw = request.form.get('resume_text', '').strip()

        try:
            resume_text, source_type = extract_resume_text(
                file_storage=resume_file,
                raw_text=resume_text_raw
            )
        except ResumeParserError as pe:
            return jsonify({'error': str(pe)}), 400

        # Perform NLP & Skill Overlap Match Analysis
        match_data = analyze_match(
            resume_text=resume_text,
            job_text=job_description,
            target_role=target_role
        )

        # Generate Personalized Roadmap and Bullet Point Rewrites
        rec_data = get_recommendations_and_roadmap(
            resume_text=resume_text,
            job_text=job_description,
            missing_skills=match_data['missing_skills']
        )

        # Save privacy-compliant summary to SQLite
        analysis_id = save_analysis(
            target_role=target_role,
            source_type=source_type,
            match_score=match_data['overall_match_score'],
            is_verified=match_data['is_verified'],
            matched_skills=match_data['matched_skills'],
            missing_skills=match_data['missing_skills'],
            total_job_skills=match_data['total_job_skills']
        )

        # Return comprehensive response for the frontend
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'target_role': target_role,
            'source_type': source_type,
            'overall_match_score': match_data['overall_match_score'],
            'skill_coverage_score': match_data['skill_coverage_score'],
            'context_similarity_score': match_data['context_similarity_score'],
            'is_verified': match_data['is_verified'],
            'status_label': match_data['status_label'],
            'score_explanation': match_data['score_explanation'],
            'matched_skills': match_data['matched_skills'],
            'missing_skills': match_data['missing_skills'],
            'missing_by_category': match_data['missing_by_category'],
            'total_job_skills': match_data['total_job_skills'],
            'roadmap': rec_data['roadmap'],
            'suggestions': rec_data['suggestions'],
            'recommendation_source': rec_data['source']
        })

    except Exception as e:
        # Catch unexpected errors cleanly
        return jsonify({'error': f'An unexpected error occurred during analysis: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
def api_history():
    """Retrieve the recent analysis history records."""
    try:
        history = get_recent_history(limit=15)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': f'Could not retrieve history: {str(e)}'}), 500


@app.route('/api/download-report/<int:analysis_id>', methods=['GET'])
def download_report(analysis_id):
    """Generate and return a downloadable PDF report for a given analysis record."""
    try:
        record = get_analysis_by_id(analysis_id)
        if not record:
            return jsonify({'error': 'Analysis record not found'}), 404

        # Generate roadmap for the report
        rec_data = get_recommendations_and_roadmap(
            resume_text="",
            job_text="",
            missing_skills=record['missing_skills']
        )

        report_payload = {
            'target_role': record['target_role'],
            'source_type': record['source_type'],
            'match_score': record['match_score'],
            'is_verified': record['is_verified'],
            'matched_skills': record['matched_skills'],
            'missing_skills': record['missing_skills'],
            'roadmap': rec_data['roadmap'],
            'created_at': record['created_at']
        }

        pdf_buffer = generate_pdf_report(report_payload)

        filename = f"GOAT_AI_Match_Report_{analysis_id}.pdf"
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500


@app.route('/api/builder/download-pdf', methods=['POST'])
def api_builder_download_pdf():
    """
    Generate and stream an ATS-friendly PDF resume from submitted resume data.
    Validates payload structure and ensures privacy (no persistence of full text).
    """
    try:
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({'error': 'Invalid request: JSON body required.'}), 400

        # Validate that payload has at least some meaningful non-empty content
        def _has_text(val):
            if not val:
                return False
            if isinstance(val, str):
                return bool(val.strip())
            if isinstance(val, list):
                return any(_has_text(x) for x in val)
            if isinstance(val, dict):
                return any(_has_text(v) for v in val.values())
            return True

        has_content = any([
            _has_text(data.get('full_name')),
            _has_text(data.get('summary')),
            _has_text(data.get('skills')),
            _has_text(data.get('experience')),
            _has_text(data.get('education')),
            _has_text(data.get('projects')),
            _has_text(data.get('certifications')),
            _has_text(data.get('achievements')),
            _has_text(data.get('languages'))
        ])
        if not has_content:
            return jsonify({'error': 'Resume data cannot be empty. Please provide at least your name or one resume section.'}), 400

        template_style = str(data.get('template_style', 'modern')).lower().strip()
        if template_style not in ['modern', 'classic']:
            template_style = 'modern'

        pdf_buffer = generate_resume_pdf(data, template_style=template_style)

        # Sanitize full name for safe attachment filename
        raw_name = str(data.get('full_name') or 'Resume').strip()
        clean_name = re.sub(r'[^a-zA-Z0-9_\- ]', '', raw_name).strip().replace(' ', '_')
        if not clean_name:
            clean_name = 'Resume'
        filename = f"{clean_name}_GOAT_Resume.pdf"

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'Failed to generate resume PDF: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f">> [GOAT AI] Server running at: http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
