import pdfplumber
from docx import Document
import spacy
import re
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nlp = None

def load_nlp():
    global nlp
    if nlp is None:
        logger.info("Loading spaCy model...")
        nlp = spacy.load("en_core_web_sm")
    return nlp

def parse_resume(file, filename):
    file_extension = os.path.splitext(filename)[1].lower()
    try:
        if file_extension == '.pdf':
            text = parse_pdf(file)
        elif file_extension == '.docx':
            text = parse_docx(file)
        else:
            return {"error": "Unsupported file format"}

        return extract_information(text)
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        return {"error": str(e)}

def parse_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        raise ValueError(f"Failed to parse PDF: {str(e)}")

def parse_docx(file):
    try:
        doc = Document(file)
        text = " ".join([paragraph.text for paragraph in doc.paragraphs])
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error parsing DOCX: {str(e)}")
        raise ValueError(f"Failed to parse DOCX: {str(e)}")

def clean_text(text):
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Add more text cleaning steps as needed
    return text

def extract_information(text):
    nlp = load_nlp()
    doc = nlp(text)

    return {
        "skills": extract_skills(doc),
        "experience": extract_experience(doc),
        "education": extract_education(doc),
        "contact_info": extract_contact_info(doc)
    }



def extract_skills(doc):
    # Consider loading this from a configuration file
    skill_keywords = set(['python', 'java', 'c++', 'javascript', 'react', 'node.js', 'sql', 'machine learning', 'data analysis'])
    skills = [token.text.lower() for token in doc if token.text.lower() in skill_keywords]
    return list(set(skills))


def extract_experience(doc):
    experience = []
    for ent in doc.ents:
        if ent.label_ == "ORG":
            experience.append(ent.text)
    return experience


def extract_education(doc):
    education_keywords = set(['university', 'college', 'bachelor', 'master', 'phd', 'degree'])
    education = []
    for sent in doc.sents:
        if any(token.text.lower() in education_keywords for token in sent):
            education.append(sent.text)
    return education


def extract_contact_info(doc):
    # This is a simple example. You might want to use more sophisticated methods.
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'

    email = re.findall(email_pattern, doc.text)
    phone = re.findall(phone_pattern, doc.text)

    return {
        "email": email[0] if email else None,
        "phone": phone[0] if phone else None
    }