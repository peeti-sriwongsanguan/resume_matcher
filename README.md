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
