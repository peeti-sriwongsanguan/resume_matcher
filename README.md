# Resume Matcher App

This application matches resumes with job listings.

## Application Architecture

```mermaid
flowchart TD
    A[User] -->|Uploads Resume| B[Web Application]
    B --> C[Resume Parser]
    C --> D[Skill Extractor]
    E[Job Scraper] -->|Scrapes job listings| F[Job Database]
    F --> G[Matching Engine]
    D --> G
    G --> H[Results Display]
    H --> B
    B -->|Shows match percentages| A
```

## Project Structure

```
resume_matcher/
│
├── .dockerignore
├── Dockerfile
├── Makefile
├── docker-compose.yml
├── environment.yml
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── resume_parser.py
│   ├── job_scraper.py
│   └── matching_engine.py
├── tests/
│   └── test_main.py
└── README.md
```
