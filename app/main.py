from flask import Blueprint, render_template, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from app.job_scraper import AdzunaJobScraper
from app.matching_engine import MatchingEngine

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    """Check if the file has one of the allowed extensions."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET'])
def index():
    """Render the homepage."""
    print(f"Available templates: {current_app.jinja_env.list_templates()}")
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            current_app.logger.info(f"File saved to: {filepath}")

            # Use the ResumeParser instance attached to the app
            resume_data = current_app.resume_parser.parse_resume(filepath, filename)

            if resume_data is None:
                return jsonify({'error': 'Failed to parse resume'}), 500

            current_app.logger.info(f"Resume data after parsing: {resume_data}")

            # Ensure all required fields are present
            required_fields = ['name', 'email', 'phone', 'skills', 'experience', 'education']
            for field in required_fields:
                if field not in resume_data:
                    resume_data[field] = '' if field != 'skills' else []

            current_app.logger.info(f"Resume data before adding to database: {resume_data}")

            resume_id = current_app.db_manager.add_resume(resume_data)

            return jsonify({
                'resume_id': resume_id,
                'name': resume_data.get('name'),
                'email': resume_data.get('email'),
                'phone': resume_data.get('phone'),
                'skills': resume_data.get('skills'),
                'experience': resume_data.get('experience'),
                'education': resume_data.get('education')
            }), 200
        except Exception as e:
            current_app.logger.error(f"Error processing resume: {str(e)}", exc_info=True)
            return jsonify({'error': 'An error occurred while processing the resume'}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@bp.route('/resume/<string:resume_id>')
def view_resume(resume_id):
    """Display the parsed resume details."""
    resume_data = current_app.db_manager.get_resume(resume_id)
    if resume_data is None:
        return render_template('error.html', message="Resume not found"), 404
    return render_template('resume.html', resume=resume_data)

@bp.route('/matches/<string:resume_id>')
def view_matches(resume_id):
    """Display the top matches for a given resume."""
    matching_engine = MatchingEngine()
    matches = matching_engine.get_top_matches(resume_id, limit=10)
    return render_template('matches.html', matches=matches, resume_id=resume_id)

@bp.route('/api/jobs/search', methods=['GET'])
def search_jobs():
    """Search for jobs using the Adzuna job scraper."""
    query = request.args.get('query', 'software engineer')
    location = request.args.get('location', 'London')
    page = int(request.args.get('page', 1))
    results_per_page = int(request.args.get('results_per_page', 10))

    scraper = AdzunaJobScraper()
    try:
        jobs = scraper.scrape_jobs(query, location, num_pages=page, results_per_page=results_per_page)
        return jsonify({
            'query': query,
            'location': location,
            'page': page,
            'results_per_page': results_per_page,
            'jobs': jobs
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/scrape_jobs')
def scrape_jobs():
    """Scrape jobs from Adzuna."""
    scraper = AdzunaJobScraper()
    jobs = scraper.scrape_jobs("software engineer", "London", num_pages=2)
    return jsonify({'message': f'Scraped {len(jobs)} jobs'})

@bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

@bp.errorhandler(404)
def resource_not_found(e):
    """Handle 404 errors."""
    return jsonify(error=str(e)), 404

@bp.errorhandler(400)
def bad_request(e):
    """Handle 400 errors."""
    return jsonify(error=str(e)), 400

@bp.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    return jsonify(error=str(e)), 500