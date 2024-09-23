import fitz  # PyMuPDF
import pdfplumber
import pytesseract
import io
from docx import Document
import spacy
import re
import os
import logging
from app.database import DatabaseManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self, db_manager):
        self.nlp = None
        self.db_manager = db_manager

    def load_nlp(self):
        if self.nlp is None:
            logger.info("Loading spaCy model...")
            self.nlp = spacy.load("en_core_web_sm")
        return self.nlp

    def parse_resume(self, filepath, filename):
        file_extension = os.path.splitext(filename)[1].lower()
        try:
            if file_extension == '.pdf':
                text = self.parse_pdf(filepath)
            elif file_extension == '.docx':
                text = self.parse_docx(filepath)
            else:
                return None, {"error": "Unsupported file format"}

            if not text:
                return None, {"error": "Failed to extract text from file"}

            resume_data = self.extract_information(text)
            return resume_data
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return None

    def parse_pdf(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                # Try PyMuPDF first
                pdf_document = fitz.open(filepath)
                text = ""
                for page in pdf_document:
                    text += page.get_text()

                # If PyMuPDF doesn't extract much text, try pdfplumber with OCR
                if len(text.strip()) < 100:
                    text = self.extract_text_from_pdf(file)

            return self.clean_text(text)
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            return ""

    def extract_text_from_pdf(self, file):
        text = ""
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=1)
                    if not page_text:
                        image = page.to_image()
                        page_text = pytesseract.image_to_string(image.original, config='--psm 6')
                    text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF with pdfplumber and OCR: {str(e)}")
            return ""

    def parse_docx(self, filepath):
        try:
            doc = Document(filepath)
            text = " ".join([paragraph.text for paragraph in doc.paragraphs])
            return self.clean_text(text)
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            return ""

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_information(self, text):
        nlp = self.load_nlp()
        doc = nlp(text)

        return {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(doc),
            "experience": self.extract_experience(doc),
            "education": self.extract_education(doc)
        }

    def extract_name(self, text):
        # Split the text into lines
        lines = text.split('\n')

        # Regular expression for a full name (2-3 words, each starting with a capital letter)
        name_pattern = r'^([A-Z][a-z]+ (?:[A-Z][a-z]+ )?[A-Z][a-z]+)$'

        # Check the first few lines for a match
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            match = re.match(name_pattern, line)
            if match:
                return match.group(1)

        # If no match found, try a more lenient pattern
        lenient_pattern = r'^([A-Z][a-z]+ [A-Z][a-z]+)'
        for line in lines[:5]:
            line = line.strip()
            match = re.match(lenient_pattern, line)
            if match:
                return match.group(1)

        # If still no match, return Unknown
        return "Unknown"

    def extract_email(self, text):
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_regex, text)
        return match.group(0) if match else None

    def extract_phone(self, text):
        phone_regex = r'''(?x)
            (?:\+?1[-.\s]?)?              # optional country code
            (?:
                \(?\d{3}\)?[-.\s]?        # area code
                \d{3}[-.\s]?              # first 3 digits
                \d{4}                     # last 4 digits
                |
                \d{3}[-.\s]?              # area code without parentheses
                \d{3}[-.\s]?              # first 3 digits
                \d{4}                     # last 4 digits
            )
            (?:[-.\s]?(?:ext|x|ext.)\s?\d{1,5})?  # optional extension
        '''
        matches = re.findall(phone_regex, text, re.VERBOSE)
        if matches:
            # Return the first match, cleaned up
            return re.sub(r'\s', '', matches[0])
        return None

    def extract_skills(self, doc):
        skill_keywords = set([
            'python', 'java', 'c++', 'javascript', 'react', 'node.js', 'sql',
            'machine learning', 'data analysis', 'tableau', 'power bi', 'excel',
            'aws', 'azure', 'cloud computing', 'docker', 'kubernetes', 'git',
            'agile', 'scrum', 'project management', 'data science', 'ai',
            'artificial intelligence', 'nlp', 'natural language processing',
            'data visualization', 'statistical analysis', 'r', 'scala', 'hadoop',
            'spark', 'big data', 'data engineering', 'etl', 'data warehousing'
        ])
        skills = [token.text.lower() for token in doc if token.text.lower() in skill_keywords]
        return list(set(skills))

    def extract_experience(self, doc):
        experience_keywords = ['experience', 'work history', 'employment']
        experience_sections = []
        current_section = []
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in experience_keywords):
                if current_section:
                    experience_sections.append(' '.join(current_section))
                current_section = [sent.text]
            elif current_section:
                current_section.append(sent.text)

        if current_section:
            experience_sections.append(' '.join(current_section))

        return ' '.join(experience_sections)[:1000]  # Limit to 1000 characters

    def extract_education(self, doc):
        education_keywords = ['education', 'university', 'college', 'degree']
        education_sections = []
        current_section = []
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in education_keywords):
                if current_section:
                    education_sections.append(' '.join(current_section))
                current_section = [sent.text]
            elif current_section:
                current_section.append(sent.text)

        if current_section:
            education_sections.append(' '.join(current_section))

        return ' '.join(education_sections)[:500]  # Limit to 500 characters