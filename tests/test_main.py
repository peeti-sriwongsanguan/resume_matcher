import pytest
import io
import json
from app import create_app
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
    with unittest.mock.patch('app.resume_parser.parse_pdf') as mock_parse_pdf, \
         unittest.mock.patch('app.resume_parser.extract_information') as mock_extract:
        mock_parse_pdf.return_value = "Sample PDF content"
        mock_extract.return_value = {
            "skills": ["python", "java"],
            "experience": ["Company A", "Company B"],
            "education": ["University X"],
            "contact_info": {"email": "test@example.com", "phone": "1234567890"}
        }
        data = {
            'file': (io.BytesIO(b"fake pdf content"), 'test.pdf')
        }
        response = client.post('/', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert 'skills' in json_data
        assert 'experience' in json_data
        assert 'education' in json_data
        assert 'contact_info' in json_data

def test_no_file_upload(client):
    response = client.post('/', data={}, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'error' in json_data
    assert json_data['error'] == 'No file part'

def test_invalid_file_type(client):
    data = {
        'file': (io.BytesIO(b"Invalid file content"), 'resume.txt')
    }
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'error' in json_data
    assert json_data['error'] == 'File type not allowed'