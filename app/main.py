from flask import Blueprint, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from app.resume_parser import parse_resume

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
            parsed_resume = parse_resume(file, filename)
            return jsonify(parsed_resume)
        else:
            return jsonify({'error': 'File type not allowed'})
    return render_template('index.html')