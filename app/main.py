from flask import Blueprint, render_template, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from app.resume_parser import ResumeParser

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
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
                return jsonify(
                    {'error': 'Failed to parse resume', 'details': parsed_data.get('error', 'Unknown error')})

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

    return render_template('index.html')