import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.matching_engine import MatchingEngine

def test_matching_engine():
    engine = MatchingEngine()

    resume = {
        'skills': ['python', 'machine learning', 'data analysis', 'sql'],
        'experience': ['5 years of experience in software development',
                       'Worked on multiple machine learning projects'],
        'education': ["Bachelor's degree in Computer Science"]
    }

    jobs = [
        {
            'title': 'Data Scientist',
            'description': 'We are looking for a data scientist with strong Python and machine learning skills.',
            'skills': ['python', 'machine learning', 'statistics', 'data visualization'],
            'required_experience': '3 years of experience in data science'
        },
        {
            'title': 'Software Engineer',
            'description': 'Seeking a software engineer with experience in web development and databases.',
            'skills': ['java', 'javascript', 'sql', 'rest api'],
            'required_experience': '5 years of software development experience'
        }
    ]

    ranked_jobs = engine.rank_jobs_for_resume(resume, jobs)

    print("Matching Engine Test Results:")
    for job, match_result in ranked_jobs:
        print(f"\nJob Title: {job['title']}")
        print(f"Total Score: {match_result['total_score']}%")
        print(f"Keyword Score: {match_result['keyword_score']}%")
        print(f"Semantic Score: {match_result['semantic_score']}%")
        print(f"Experience Score: {match_result['experience_score']}%")

if __name__ == "__main__":
    test_matching_engine()