import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.job_scraper import AdzunaJobScraper

@pytest.fixture
def scraper():
    return AdzunaJobScraper()

def test_job_scraper(scraper):
    jobs = scraper.scrape_jobs("software engineer", "London", num_pages=1)
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
        print(f"Skills: {job['skills']}")
        print(f"Description: {job['description'][:100]}...")  # Print first 100 characters of description
    else:
        print("No jobs found.")

    # Add some assertions to verify the scraper is working correctly
    assert len(jobs) > 0, "No jobs were scraped"
    assert summary['total_jobs'] > 0, "Total jobs should be greater than 0"
    assert summary['unique_companies'] > 0, "Should have at least one unique company"
    assert len(summary['locations']) > 0, "Should have at least one location"
    assert len(summary['top_skills']) > 0, "Should have at least one top skill"

if __name__ == "__main__":
    scraper = AdzunaJobScraper()
    test_job_scraper(scraper)