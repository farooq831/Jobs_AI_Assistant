# Project Scope and Requirements — AI Job Application Assistant

Date: November 8, 2025

This document finalizes the project scope and lists the technical and non-technical requirements for the AI Job Application Assistant MVP.

## Project Scope (MVP)
- Collect job listings from at least two major boards (Indeed, Glassdoor) using static and dynamic scraping.
- Allow users to input personal details and job preferences (location, salary range, job titles, job types).
- Accept resume upload (PDF/DOCX) or manual skills input and extract text for analysis.
- Clean and normalize scraped data, filter by user preferences, and score job matches using an NLP-based keyword approach.
- Provide resume optimization suggestions based on job descriptions and resume keywords.
- Export filtered and scored job listings to Excel (.xlsx) with color-coded highlights and an optional comments sheet for resume tips; support CSV and PDF exports.
- Provide a basic application tracker to store and update statuses (Applied, Interview, Offer, Rejected, Pending) using SQLite or JSON.
- Deliver a responsive web UI for input, results, and tracker. Keep authentication out of MVP (optional future enhancement).

## Acceptance Criteria (MVP)
- Scraper returns structured job entries (title, company, location, salary, job type, description, url) for both target boards for at least 80% of test queries.
- Filtering respects user-selected location, salary range, and job type preferences.
- Scoring returns a numeric score and color category (Red/Yellow/White) for each job with reproducible logic.
- Resume extraction returns a plain-text set of skills/keywords from uploaded PDF/DOCX files for >90% of common resume samples.
- Excel export includes scores and color-coded rows and contains a separate sheet with resume tips.
- Application tracker persists status updates and surface them in the UI.

## Technical Requirements
- Backend
  - Language: Python 3.9+.
  - Framework: Flask (preferred for MVP) or Django (if you prefer batteries-included).
  - Endpoints: form submission, file upload, job search trigger, results retrieval, export endpoints, tracker CRUD.

- Web Scraping
  - Static scraping: requests + BeautifulSoup for HTML parsing.
  - Dynamic scraping: Selenium with headless Chrome (chromedriver) to handle JS-loaded pages.
  - Anti-blocking: configurable user-agent rotation, randomized short delays, and retry logic.
  - Rate limiting and robots.txt compliance: prefer polite scraping and flag sites that forbid scraping.

- NLP & Data Processing
  - Use spaCy for tokenization and keyword extraction; fallback to simple regex/token heuristics for vocab detection.
  - Pandas for data cleaning/normalization and salary parsing helpers.
  - openpyxl for `.xlsx` export and formatting.

- Storage
  - MVP: SQLite (file) or JSON files for scraped data and tracker state.
  - Exported files saved temporarily for user download and cleaned up periodically.

- Frontend
  - React.js (preferred) or simple HTML/CSS/Bootstrap for rapid MVP.
  - Forms for user input, file upload, results table with sorting/filtering, and tracker UI.

- Testing & CI
  - Unit tests for scraper parsing functions, scoring function, resume extraction, and export functions (pytest).
  - Basic integration tests for full flow (input → scrape → filter → export).

- Dev environment
  - Virtual environment: venv or pipenv.
  - Requirements: `requirements.txt` listing pinned packages for reproducibility.

## Non-Technical Requirements
- Stakeholders & Communication
  - Regular weekly check-ins; demo prototype at the end of each sprint.
  - Keep PRD and tasks updated in the repo.

- Legal & Privacy
  - Do not store or transmit resumes off-user device without consent; encrypt any persisted personal data at rest.
  - Be mindful of terms of service for scraped sites; prefer public job board pages and consider using official APIs where available.

- Accessibility & UX
  - Make forms accessible (labels, tab order) and the results table readable on mobile/desktop.
  - Provide clear error messages for failed uploads or scraping timeouts.

- Scheduling & Deliverables
  - Follow timeline in `PRD.md` with iterative cadence: 2-week cycles for major modules.
  - Provide documentation (README, setup guide) with reproducible steps to run locally.

## Risks and Mitigations (short)
- Scraping blocks: use Selenium & throttling; fallback to APIs.
- Data quality: implement deduplication and heuristics for salary/location normalization.
- Privacy concerns: local processing, encrypt storage, provide data deletion instructions.

## Next Steps
- Implement basic backend endpoints and scaffold frontend forms.
- Create `requirements.txt` and initialize git with a feature branch for `scraper-mvp`.
- Implement a simple static scraper for one site as a proof-of-concept.

---

File location: `docs/project_scope_and_requirements.md` — use this as the canonical finalized scope for Phase 1 Task 1.1.
