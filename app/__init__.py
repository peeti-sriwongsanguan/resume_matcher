import os
from flask import Flask
from app.resume_parser import ResumeParser
from app.database import DatabaseManager

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def create_app(test_config=None):
    app = Flask(__name__, template_folder='../templates')

    # Configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER=UPLOAD_FOLDER,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max-limit
        DATABASE_URI='sqlite:///resume_matcher.db'
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    db_manager = DatabaseManager(app.config['DATABASE_URI'])
    app.db_manager = db_manager

    # Initialize ResumeParser
    resume_parser = ResumeParser()
    app.resume_parser = resume_parser

    # Register blueprints
    from app import main
    app.register_blueprint(main.bp)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    return app