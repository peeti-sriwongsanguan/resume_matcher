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

def test_pdf_upload(client):
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
            'file': (io.BytesIO(b"%PDF-1.5 fake pdf content"), 'resume.pdf')
        }
        response = client.post('/', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert 'name' in json_data
        assert 'skills' in json_data

def test_docx_upload(client):
    with unittest.mock.patch.object(ResumeParser, 'parse_resume') as mock_parse:
        mock_parse.return_value = (2, {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "0987654321",
            "skills": "javascript,react",
            "experience": "3 years of experience",
            "education": "Master's in Computer Science"
        })
        data = {
            'file': (io.BytesIO(b"PK fake docx content"), 'resume.docx')
        }
        response = client.post('/', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert 'name' in json_data
        assert 'skills' in json_data

def test_invalid_file_upload(client):
    data = {
        'file': (io.BytesIO(b"fake txt content"), 'test_resume.txt')
    }
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'error' in json_data
    assert json_data['error'] == 'File type not allowed'

def test_no_file_upload(client):
    response = client.post('/', data={}, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'error' in json_data
    assert json_data['error'] == 'No file part'