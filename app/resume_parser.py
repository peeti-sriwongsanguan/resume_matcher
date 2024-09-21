import pdfplumber
from docx import Document
import spacy
import re
import os
import logging
from datetime import datetime

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

    sections = identify_sections(doc)

    return {
        "personal_info": extract_personal_info(doc),
        "skills": extract_skills(doc, sections.get("skills", doc)),
        "experience": extract_experience(doc, sections.get("experience", doc)),
        "education": extract_education(doc, sections.get("education", doc)),
        "contact_info": extract_contact_info(doc)
    }


def identify_sections(doc):
    sections = {}
    current_section = None
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in ["experience", "work history"]):
            current_section = "experience"
            sections[current_section] = []
        elif any(keyword in sent.text.lower() for keyword in ["education", "academic"]):
            current_section = "education"
            sections[current_section] = []
        elif any(keyword in sent.text.lower() for keyword in ["skills", "competencies"]):
            current_section = "skills"
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(sent)
    return {k: doc[v[0].start:v[-1].end] if v else doc for k, v in sections.items()}

def extract_personal_info(doc):
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), None)
    return {"name": name}

def extract_skills(doc, skills_section):
    skill_keywords = set(['python', 'java', 'c++', 'javascript', 'react', 'node.js', 'sql', 'machine learning', 'data analysis'])
    # Add more skills to this set
    skills = [token.text.lower() for token in skills_section if token.text.lower() in skill_keywords]
    return list(set(skills))

def extract_experience(doc, experience_section):
    experiences = []
    current_experience = {}
    for ent in experience_section.ents:
        if ent.label_ == "ORG" and not current_experience.get("company"):
            current_experience["company"] = ent.text
        elif ent.label_ == "DATE":
            if not current_experience.get("start_date"):
                current_experience["start_date"] = ent.text
            else:
                current_experience["end_date"] = ent.text
        if len(current_experience) == 3:
            experiences.append(current_experience)
            current_experience = {}
    return experiences

def extract_education(doc, education_section):
    education = []
    education_keywords = set(['university', 'college', 'bachelor', 'master', 'phd', 'degree'])
    for sent in education_section.sents:
        if any(token.text.lower() in education_keywords for token in sent):
            edu_info = {
                "degree": next((token.text for token in sent if token.text.lower() in ['bachelor', 'master', 'phd']), None),
                "institution": next((ent.text for ent in sent.ents if ent.label_ == "ORG"), None),
                "graduation_date": next((ent.text for ent in sent.ents if ent.label_ == "DATE"), None)
            }
            education.append(edu_info)
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