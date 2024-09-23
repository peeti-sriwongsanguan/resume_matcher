from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
# import datetime
import logging
import uuid
import sqlite3
from datetime import datetime
import json

Base = declarative_base()

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(String(50), primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    skills = Column(Text)
    experience = Column(Text)
    education = Column(Text)
    created_at = Column(String(50))

    def __init__(self, **kwargs):
        super(Resume, self).__init__(**kwargs)
        if 'id' not in kwargs:
            self.id = str(uuid.uuid4())
        if 'created_at' not in kwargs:
            # Convert datetime to ISO format string before saving
            self.created_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(kwargs['created_at'], datetime.datetime):
            # Convert datetime to ISO format string if passed as a datetime
            self.created_at = kwargs['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            # Otherwise, assume created_at is passed as a string
            self.created_at = kwargs['created_at']


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(String(50), primary_key=True)
    title = Column(String(100))
    company = Column(String(100))
    location = Column(String(100))
    description = Column(Text)
    skills = Column(Text)
    salary = Column(String(50))
    url = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

class MatchResult(Base):
    __tablename__ = 'match_results'

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(50), ForeignKey('resumes.id'))
    job_id = Column(String(50), ForeignKey('jobs.id'))
    total_score = Column(Float)
    keyword_score = Column(Float)
    semantic_score = Column(Float)
    experience_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume")
    job = relationship("Job")


class DatabaseManager:
    def __init__(self, db_path='resume_matcher.db'):
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            experience TEXT,
            education TEXT,
            created_at TEXT
        )
        ''')
        conn.commit()
        conn.close()

    def add_resume(self, resume_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            resume_id = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()

            # Ensure all data is in string format
            name = str(resume_data.get('name', ''))
            email = str(resume_data.get('email', ''))
            phone = str(resume_data.get('phone', ''))
            skills = json.dumps(resume_data.get('skills', []))  # Convert list to JSON string
            experience = str(resume_data.get('experience', ''))
            education = str(resume_data.get('education', ''))

            cursor.execute('''
            INSERT INTO resumes (id, name, email, phone, skills, experience, education, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                resume_id,
                name,
                email,
                phone,
                skills,
                experience,
                education,
                created_at
            ))
            conn.commit()
            return resume_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error adding resume: {str(e)}")
            logger.error(f"Resume data: {resume_data}")
            raise
        finally:
            conn.close()

    def get_resume(self, resume_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
            result = cursor.fetchone()
            if result:
                resume_dict = dict(zip(['id', 'name', 'email', 'phone', 'skills', 'experience', 'education', 'created_at'], result))
                resume_dict['skills'] = json.loads(resume_dict['skills'])  # Convert JSON string back to list
                return resume_dict
            return None
        finally:
            conn.close()

    def add_job(self, job_data):
        with self.Session() as session:
            try:
                existing_job = session.query(Job).filter_by(id=job_data['id']).first()
                if existing_job:
                    for key, value in job_data.items():
                        setattr(existing_job, key, value)
                else:
                    job = Job(**job_data)
                    session.add(job)
                session.commit()
                return job_data['id']
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding/updating job: {str(e)}")
                raise

    def add_match_result(self, match_data):
        with self.Session() as session:
            try:
                if 'id' not in match_data:
                    match_data['id'] = str(uuid.uuid4())
                match_result = MatchResult(**match_data)
                session.add(match_result)
                session.commit()
                logger.info(f"Match result added with ID {match_result.id}")
                return match_result.id
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding match result: {str(e)}")
                raise

    # def get_resume(self, resume_id):
    #     with self.Session() as session:
    #         resume = session.query(Resume).filter(Resume.id == resume_id).first()
    #         if resume is None:
    #             logger.warning(f"No resume found with id: {resume_id}")
    #         return resume

    def get_job(self, job_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            result = cursor.fetchone()
            if result:
                return dict(zip(['id', 'title', 'company', 'location', 'description', 'skills', 'salary', 'url', 'created_at'], result))
            logger.warning(f"No job found with id: {job_id}")
            return None
        finally:
            conn.close()

    def get_match_results(self, resume_id=None, job_id=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM match_results WHERE 1=1"
            params = []
            if resume_id:
                query += " AND resume_id = ?"
                params.append(resume_id)
            if job_id:
                query += " AND job_id = ?"
                params.append(job_id)
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(zip(['id', 'resume_id', 'job_id', 'total_score', 'keyword_score', 'semantic_score', 'experience_score', 'created_at'], row)) for row in results]
        finally:
            conn.close()