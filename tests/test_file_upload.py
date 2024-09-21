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

def test_pdf_upload(client):
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
            'file': (io.BytesIO(b"fake pdf content"), 'test_resume.pdf')
        }
        response = client.post('/', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert 'skills' in json_data
        assert 'experience' in json_data
        assert 'education' in json_data
        assert 'contact_info' in json_data

def test_docx_upload(client):
    with unittest.mock.patch('app.resume_parser.parse_docx') as mock_parse_docx, \
         unittest.mock.patch('app.resume_parser.extract_information') as mock_extract:
        mock_parse_docx.return_value = "Sample DOCX content"
        mock_extract.return_value = {
            "skills": ["python", "java"],
            "experience": ["Company A", "Company B"],
            "education": ["University X"],
            "contact_info": {"email": "test@example.com", "phone": "1234567890"}
        }
        data = {
            'file': (io.BytesIO(b"fake docx content"), 'test_resume.docx')
        }
        response = client.post('/', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert 'skills' in json_data
        assert 'experience' in json_data
        assert 'education' in json_data
        assert 'contact_info' in json_data

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