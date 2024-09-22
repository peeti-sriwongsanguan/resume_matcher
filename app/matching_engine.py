import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class MatchingEngine:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.vectorizer = TfidfVectorizer()

    def preprocess_text(self, text):
        doc = self.nlp(text.lower())
        return ' '.join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

    def calculate_keyword_score(self, resume_skills, job_skills):
        resume_skills_set = set(resume_skills)
        job_skills_set = set(job_skills)
        matching_skills = resume_skills_set.intersection(job_skills_set)
        return len(matching_skills) / len(job_skills_set) if job_skills_set else 0

    def calculate_semantic_similarity(self, resume_text, job_description):
        preprocessed_resume = self.preprocess_text(resume_text)
        preprocessed_job = self.preprocess_text(job_description)
        tfidf_matrix = self.vectorizer.fit_transform([preprocessed_resume, preprocessed_job])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    def calculate_experience_score(self, resume_experience, required_experience):
        # Simple scoring based on years of experience
        resume_years = self.extract_years_of_experience(resume_experience)
        required_years = self.extract_years_of_experience(required_experience)
        if resume_years >= required_years:
            return 1.0
        else:
            return resume_years / required_years

    def extract_years_of_experience(self, experience_text):
        # This is a simplistic extraction. You might want to improve this.
        doc = self.nlp(experience_text.lower())
        for ent in doc.ents:
            if ent.label_ == "DATE" and "year" in ent.text:
                return int(ent.text.split()[0])
        return 0

    def match_resume_to_job(self, resume, job):
        keyword_score = self.calculate_keyword_score(resume['skills'], job['skills'])
        semantic_score = self.calculate_semantic_similarity(
            ' '.join(resume['experience']) + ' ' + ' '.join(resume['education']),
            job['description']
        )
        experience_score = self.calculate_experience_score(
            ' '.join(resume['experience']),
            job.get('required_experience', '')
        )

        # Weighted average of scores
        total_score = (keyword_score * 0.4 + semantic_score * 0.4 + experience_score * 0.2) * 100

        return {
            'total_score': round(total_score, 2),
            'keyword_score': round(keyword_score * 100, 2),
            'semantic_score': round(semantic_score * 100, 2),
            'experience_score': round(experience_score * 100, 2)
        }

    def rank_jobs_for_resume(self, resume, jobs):
        job_matches = []
        for job in jobs:
            match_result = self.match_resume_to_job(resume, job)
            job_matches.append((job, match_result))

        # Sort jobs by total score in descending order
        return sorted(job_matches, key=lambda x: x[1]['total_score'], reverse=True)