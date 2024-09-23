import sys
import os
import uuid
import pytest
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DatabaseManager

@pytest.fixture
def db_manager():
    return DatabaseManager('sqlite:///test.db')

def test_database(db_manager):
    # Test adding and retrieving a resume
    resume_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'skills': 'python,java,sql',
        'experience': '5 years as software engineer',
        'education': 'BS in Computer Science',
        'created_at': datetime.datetime.utcnow()

    }
    resume_id = db_manager.add_resume(resume_data)
    retrieved_resume = db_manager.get_resume(resume_id)
    assert retrieved_resume.name == 'John Doe'

    # Test adding and retrieving a job
    job_data = {
        'id': str(uuid.uuid4()),
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'New York, NY',
        'description': 'Exciting opportunity for a skilled software engineer',
        'skills': 'python,java,sql',
        'salary': '$100,000 - $150,000',
        'url': 'https://example.com/job',
        'created_at': datetime.datetime.utcnow()
    }
    job_id = db_manager.add_job(job_data)
    retrieved_job = db_manager.get_job(job_id)
    assert retrieved_job is not None
    assert retrieved_job.title == 'Software Engineer'

    # Test adding and retrieving a match result
    match_data = {
        'resume_id': resume_id,
        'job_id': job_id,  # Use the actual job_id, not 'test_job_123'
        'total_score': 85.5,
        'keyword_score': 90.0,
        'semantic_score': 80.0,
        'experience_score': 85.0,
        'created_at': datetime.datetime.utcnow()

    }
    match_id = db_manager.add_match_result(match_data)
    retrieved_matches = db_manager.get_match_results(resume_id=resume_id)
    assert len(retrieved_matches) == 1
    assert retrieved_matches[0].total_score == 85.5

    print("All database tests passed!")

if __name__ == "__main__":
    pytest.main([__file__])