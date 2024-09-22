import PyPDF2
from docx import Document
import spacy
import re
import os
import logging
from app.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self):
        self.nlp = None
        self.db_manager = DatabaseManager()

    def load_nlp(self):
        if self.nlp is None:
            logger.info("Loading spaCy model...")
            self.nlp = spacy.load("en_core_web_sm")
        return self.nlp

    def parse_resume(self, file, filename):
        file_extension = os.path.splitext(filename)[1].lower()
        try:
            if file_extension == '.pdf':
                text = self.parse_pdf(file)
            elif file_extension == '.docx':
                text = self.parse_docx(file)
            else:
                return None, {"error": "Unsupported file format"}

            if not text:
                return None, {"error": "Failed to extract text from file"}

            resume_data = self.extract_information(text)
            resume_id = self.db_manager.add_resume(resume_data)
            return resume_id, resume_data
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return None, {"error": str(e)}

    def parse_pdf(self, file):
        try:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page in range(pdf_reader.numPages):
                text += pdf_reader.getPage(page).extractText()
            return self.clean_text(text)
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            return ""

    def parse_docx(self, file):
        try:
            doc = Document(file)
            text = " ".join([paragraph.text for paragraph in doc.paragraphs])
            return self.clean_text(text)
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            return ""

    def clean_text(self, text):
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_information(self, text):
        nlp = self.load_nlp()
        doc = nlp(text)

        return {
            "name": self.extract_name(doc),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": ",".join(self.extract_skills(doc)),
            "experience": self.extract_experience(doc),
            "education": self.extract_education(doc)
        }

    def extract_name(self, doc):
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None

    def extract_email(self, text):
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_regex, text)
        return match.group(0) if match else None

    def extract_phone(self, text):
        phone_regex = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        match = re.search(phone_regex, text)
        return match.group(0) if match else None

    def extract_skills(self, doc):
        skill_keywords = set(['python', 'java', 'c++', 'javascript', 'react', 'node.js', 'sql', 'machine learning', 'data analysis'])
        skills = [token.text.lower() for token in doc if token.text.lower() in skill_keywords]
        return list(set(skills))

    def extract_experience(self, doc):
        # improve it.
        experience_keywords = ['experience', 'work history', 'employment']
        experience_sentences = [sent.text for sent in doc.sents if any(keyword in sent.text.lower() for keyword in experience_keywords)]
        return " ".join(experience_sentences)

    def extract_education(self, doc):
        # This is a simple. Improve it.
        education_keywords = ['education', 'university', 'college', 'degree']
        education_sentences = [sent.text for sent in doc.sents if any(keyword in sent.text.lower() for keyword in education_keywords)]
        return " ".join(education_sentences)