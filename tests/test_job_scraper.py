import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.job_scraper import IndeedJobScraper


def test_job_scraper():
    scraper = IndeedJobScraper()
    jobs = scraper.scrape_jobs("software engineer", "New York", num_pages=1)
    summary = scraper.get_job_summary(jobs)

    print("Job Scraper Test Results:")
    print(f"Total Jobs Scraped: {summary['total_jobs']}")
    print(f"Unique Companies: {summary['unique_companies']}")
    print(f"Locations: {', '.join(summary['locations'])}")
    print(f"Top Skills: {', '.join(summary['top_skills'])}")

    print("\nSample Job Listing:")
    if jobs:
        job = jobs[0]
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Salary: {job['salary']}")
        print(f"Skills: {', '.join(job['skills'])}")
        print(f"Description: {job['description'][:100]}...")  # Print first 100 characters of description
    else:
        print("No jobs found.")


if __name__ == "__main__":
    test_job_scraper()