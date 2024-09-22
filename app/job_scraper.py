import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import re
from app.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndeedJobScraper:
    def __init__(self):
        self.base_url = "https://www.indeed.com/jobs"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.db_manager = DatabaseManager()

    def scrape_jobs(self, query, location, num_pages=1):
        all_jobs = []
        for page in range(num_pages):
            url = f"{self.base_url}?q={query}&l={location}&start={page * 10}"
            logger.info(f"Scraping page {page + 1}: {url}")

            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = self._parse_jobs(soup)
                all_jobs.extend(jobs)

                # Store jobs in the database
                for job in jobs:
                    self.db_manager.add_job(job)
            else:
                logger.error(f"Failed to retrieve page {page + 1}. Status code: {response.status_code}")

            # Respect rate limits
            time.sleep(random.uniform(1, 3))

        return all_jobs

    def _parse_jobs(self, soup):
        job_listings = []
        for div in soup.find_all('div', class_='job_seen_beacon'):
            title = div.find('h2', class_='jobTitle')
            company = div.find('span', class_='companyName')
            location = div.find('div', class_='companyLocation')
            salary = div.find('div', class_='metadata salary-snippet-container')
            description = div.find('div', class_='job-snippet')

            if title and company and location:
                job_data = {
                    'title': title.text.strip(),
                    'company': company.text.strip(),
                    'location': location.text.strip(),
                    'url': 'https://www.indeed.com' + div.find('a')['href'] if div.find('a') else None,
                    'salary': salary.text.strip() if salary else 'Not provided',
                    'description': description.text.strip() if description else 'No description available',
                    'skills': ','.join(self._extract_skills(description.text if description else ''))
                }
                job_listings.append(job_data)

        return job_listings

    def _extract_skills(self, description):
        # This is a basic skill extraction. You might want to expand this list and improve the extraction logic.
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
        all_skills = [skill for job in jobs for skill in job['skills'].split(',')]
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
    scraper = IndeedJobScraper()
    summary = scraper.scrape_and_store_jobs("software engineer", "New York", num_pages=2)

    print("\nJob Scraping Complete!")
    print(f"Total Jobs Scraped: {summary['total_jobs']}")
    print(f"Unique Companies: {summary['unique_companies']}")
    print(f"Locations: {', '.join(summary['locations'])}")
    print(f"Top Skills: {', '.join(summary['top_skills'])}")


if __name__ == "__main__":
    main()