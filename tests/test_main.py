import pytest
import io
import json
from app import create_app
from app.resume_parser import ResumeParser
import unittest.mock

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Resume Matcher" in response.data

def test_file_upload(client):
    with unittest.mock.patch.object(ResumeParser, 'parse_resume') as mock_parse:
        mock_parse.return_value = (1, {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "skills": "python,java",
            "experience": "5 years of experience",
            "education": "Bachelor's in Computer Science"
        })
        data = {
            'file': (io.BytesIO(b"%PDF-1.5 test file content"), 'test.pdf')
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert 'name' in json_data
        assert 'skills' in json_data

def test_no_file_upload(client):
    response = client.post('/upload', data={}, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'error' in json_data
    assert json_data['error'] == 'No file part'

def test_invalid_file_type(client):
    data = {
        'file': (io.BytesIO(b"Invalid file content"), 'resume.txt')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'error' in json_data
    assert json_data['error'] == 'File type not allowed'