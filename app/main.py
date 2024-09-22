from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
import os
from werkzeug.utils import secure_filename
from app.resume_parser import ResumeParser
from app.job_scraper import IndeedJobScraper
from app.matching_engine import MatchingEngine

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Parse the resume
        parser = ResumeParser()
        resume_id, parsed_data = parser.parse_resume(filepath, filename)

        if resume_id is None:
            return jsonify({'error': 'Failed to parse resume', 'details': parsed_data.get('error', 'Unknown error')})

        # Return the parsed data
        return jsonify({
            'resume_id': resume_id,
            'name': parsed_data.get('name'),
            'email': parsed_data.get('email'),
            'phone': parsed_data.get('phone'),
            'skills': parsed_data.get('skills'),
            'experience': parsed_data.get('experience'),
            'education': parsed_data.get('education')
        })
    else:
        return jsonify({'error': 'File type not allowed'})

@bp.route('/resume/<int:resume_id>')
def view_resume(resume_id):
    # Fetch resume data from database
    resume_data = current_app.db_manager.get_resume(resume_id)
    if resume_data is None:
        return render_template('error.html', message="Resume not found"), 404
    return render_template('resume.html', resume=resume_data)

@bp.route('/matches/<int:resume_id>')
def view_matches(resume_id):
    matching_engine = MatchingEngine()
    matches = matching_engine.get_top_matches(resume_id, limit=10)
    return render_template('matches.html', matches=matches, resume_id=resume_id)

@bp.route('/scrape_jobs')
def scrape_jobs():
    scraper = IndeedJobScraper()
    jobs = scraper.scrape_jobs("software engineer", "New York", num_pages=2)
    return jsonify({'message': f'Scraped {len(jobs)} jobs'})

@bp.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200