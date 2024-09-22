from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    skills = Column(Text)
    experience = Column(Text)
    education = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    company = Column(String(100))
    location = Column(String(100))
    description = Column(Text)
    skills = Column(Text)
    salary = Column(String(50))
    url = Column(String(200))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class MatchResult(Base):
    __tablename__ = 'match_results'

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    job_id = Column(Integer, ForeignKey('jobs.id'))
    total_score = Column(Float)
    keyword_score = Column(Float)
    semantic_score = Column(Float)
    experience_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("Resume")
    job = relationship("Job")

class DatabaseManager:
    def __init__(self, db_url='sqlite:///resume_matcher.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_resume(self, resume_data):
        with self.Session() as session:
            resume = Resume(**resume_data)
            session.add(resume)
            session.commit()
            return resume.id

    def add_job(self, job_data):
        with self.Session() as session:
            job = Job(**job_data)
            session.add(job)
            session.commit()
            return job.id

    def add_match_result(self, match_data):
        with self.Session() as session:
            match_result = MatchResult(**match_data)
            session.add(match_result)
            session.commit()
            return match_result.id

    def get_resume(self, resume_id):
        with self.Session() as session:
            return session.query(Resume).filter(Resume.id == resume_id).first()

    def get_job(self, job_id):
        with self.Session() as session:
            return session.query(Job).filter(Job.id == job_id).first()

    def get_match_results(self, resume_id=None, job_id=None):
        with self.Session() as session:
            query = session.query(MatchResult)
            if resume_id:
                query = query.filter(MatchResult.resume_id == resume_id)
            if job_id:
                query = query.filter(MatchResult.job_id == job_id)
            return query.all()