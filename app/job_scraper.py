import requests
import os
import logging
import re
from dotenv import load_dotenv
from app.database import DatabaseManager
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdzunaJobScraper:
    def __init__(self):
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.api_key = os.getenv('ADZUNA_API_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.db_manager = DatabaseManager()

    def scrape_jobs(self, query, location, num_pages=1, results_per_page=10):
        all_jobs = []
        for page in range(1, num_pages + 1):
            url = f"{self.base_url}/gb/search/{page}"
            params = {
                'app_id': self.app_id,
                'app_key': self.api_key,
                'results_per_page': results_per_page,
                'what': query,
                'where': location,
                'content-type': 'application/json'
            }

            logger.info(f"Scraping page {page}: {url}")

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                jobs = self._parse_jobs(data)
                all_jobs.extend(jobs)

                # Store jobs in the database
                for job in jobs:
                    self.db_manager.add_job(job)
            else:
                logger.error(f"Failed to retrieve page {page}. Status code: {response.status_code}")

        return all_jobs

    def _parse_jobs(self, data):
        jobs = []
        for job in data.get('results', []):
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            salary = f"{salary_min}-{salary_max}" if salary_min and salary_max else "Not provided"

            created_at = job.get('created')
            if created_at:
                created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

            parsed_job = {
                'id': job.get('id'),
                'title': job.get('title'),
                'company': job.get('company', {}).get('display_name'),
                'location': job.get('location', {}).get('display_name'),
                'description': job.get('description'),
                'url': job.get('redirect_url'),
                'salary': salary,
                'skills': ','.join(self._extract_skills(job.get('description', ''))),
                'created_at': created_at
            }
            jobs.append(parsed_job)
        return jobs

    def _extract_skills(self, description):
        common_skills = ['python', 'java', 'c++', 'javascript', 'react', 'node.js', 'sql', 'machine learning',
                         'data analysis']
        found_skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', description.lower()):
                found_skills.append(skill)
        return found_skills

    def get_job_summary(self, jobs):
        total_jobs = len(jobs)
        companies = set(job['company'] for job in jobs)
        locations = set(job['location'] for job in jobs)
        all_skills = [skill for job in jobs for skill in job['skills'].split(',') if job['skills']]
        top_skills = sorted(set(all_skills), key=all_skills.count, reverse=True)[:5]

        return {
            'total_jobs': total_jobs,
            'unique_companies': len(companies),
            'locations': list(locations),
            'top_skills': top_skills
        }

    def scrape_and_store_jobs(self, query, location, num_pages=1):
        jobs = self.scrape_jobs(query, location, num_pages)
        summary = self.get_job_summary(jobs)

        logger.info("Job Scraping Summary:")
        logger.info(f"Total Jobs: {summary['total_jobs']}")
        logger.info(f"Unique Companies: {summary['unique_companies']}")
        logger.info(f"Locations: {', '.join(summary['locations'])}")
        logger.info(f"Top Skills: {', '.join(summary['top_skills'])}")

        return summary


def main():
    scraper = AdzunaJobScraper()
    summary = scraper.scrape_and_store_jobs("software engineer", "London", num_pages=2)

    print("\nJob Scraping Complete!")
    print(f"Total Jobs Scraped: {summary['total_jobs']}")
    print(f"Unique Companies: {summary['unique_companies']}")
    print(f"Locations: {', '.join(summary['locations'])}")
    print(f"Top Skills: {', '.join(summary['top_skills'])}")


if __name__ == "__main__":
    main()