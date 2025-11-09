# Task 3.1: Static Scraping with BeautifulSoup - README

## Overview

This module implements static web scraping functionality for Indeed and Glassdoor job boards using BeautifulSoup4. The scrapers extract job listings with the following information:
- Job title
- Company name
- Location
- Salary (when available)
- Job type (Remote, Onsite, Hybrid, Full-time, Part-time, etc.)
- Job description snippet
- Job listing link

## Architecture

### Module Structure

```
backend/
├── scrapers/
│   ├── __init__.py              # Package initialization
│   ├── base_scraper.py          # Abstract base class with common functionality
│   ├── indeed_scraper.py        # Indeed-specific scraper implementation
│   └── glassdoor_scraper.py     # Glassdoor-specific scraper implementation
├── app.py                       # Flask API with scraping endpoints
└── test_scraper.py              # Comprehensive test suite
```

### Class Hierarchy

```
BaseScraper (Abstract Base Class)
├── Common methods: make_request, parse_html, clean_text, extract_salary
├── Anti-blocking: User agents, delays, retries
└── Abstract methods: build_search_url, extract_jobs

IndeedScraper (extends BaseScraper)
├── Indeed-specific URL building
└── Indeed-specific job card parsing

GlassdoorScraper (extends BaseScraper)
├── Glassdoor-specific URL building
└── Glassdoor-specific job card parsing
```

## Features

### BaseScraper Features
- **HTTP Request Handling**: Robust request handling with retries and timeout
- **Rate Limiting Protection**: Random delays between requests (2-5 seconds)
- **User Agent Rotation**: Prevents detection as a bot
- **Error Handling**: Graceful error handling with logging
- **Data Cleaning**: Text normalization and whitespace removal
- **Salary Parsing**: Extracts min/max salary from various text formats

### Indeed Scraper
- Searches Indeed.com job listings
- Handles pagination (10 jobs per page)
- Extracts job cards using multiple selector strategies
- Supports fetching full job details

### Glassdoor Scraper
- Searches Glassdoor.com job listings
- Handles pagination
- Extracts job cards using multiple selector strategies
- Supports fetching full job details

## API Endpoints

### 1. Scrape Jobs
**POST** `/api/scrape-jobs`

Scrapes jobs from specified job boards.

**Request Body:**
```json
{
  "job_titles": ["Software Engineer", "Data Scientist"],
  "location": "New York, NY",
  "num_pages": 2,
  "sources": ["indeed", "glassdoor"]
}
```

**Parameters:**
- `job_titles` (array, required): List of job titles to search for
- `location` (string, required): Location to search in
- `num_pages` (integer, optional): Number of pages to scrape per job title (1-5, default: 1)
- `sources` (array, optional): Job boards to scrape from ["indeed", "glassdoor"] (default: both)

**Response (201):**
```json
{
  "success": true,
  "message": "Scraped 25 jobs successfully",
  "scrape_id": 1,
  "total_jobs": 25,
  "scraping_results": {
    "indeed": {
      "success": true,
      "count": 15,
      "error": null
    },
    "glassdoor": {
      "success": true,
      "count": 10,
      "error": null
    }
  },
  "jobs": [
    {
      "source": "Indeed",
      "title": "Software Engineer",
      "company": "Tech Corp",
      "location": "New York, NY",
      "salary": {
        "min": 80000,
        "max": 120000,
        "raw": "$80,000 - $120,000"
      },
      "job_type": "Remote",
      "description": "We are seeking a talented software engineer...",
      "link": "https://www.indeed.com/viewjob?jk=abc123"
    }
  ]
}
```

### 2. Get Scraped Jobs
**GET** `/api/scrape-jobs/<scrape_id>`

Retrieves previously scraped jobs by ID.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "job_titles": ["Software Engineer"],
    "location": "New York, NY",
    "num_pages": 1,
    "sources": ["indeed"],
    "jobs": [...],
    "total_jobs": 15,
    "scraping_results": {...}
  }
}
```

### 3. Get All Scraped Jobs
**GET** `/api/scrape-jobs`

Retrieves all scraped job results.

**Response (200):**
```json
{
  "success": true,
  "count": 3,
  "data": {
    "1": {...},
    "2": {...},
    "3": {...}
  }
}
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Dependencies
All required dependencies are in `requirements.txt`:
- `beautifulsoup4==4.12.2` - HTML parsing
- `requests==2.31.0` - HTTP requests
- `lxml==4.9.3` - Fast HTML parser
- `Flask==2.2.5` - Web framework
- `Flask-CORS==4.0.0` - CORS support

### Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r ../requirements.txt
```

2. **Verify installation:**
```bash
python -c "import bs4, requests, lxml; print('All dependencies installed successfully')"
```

## Usage

### Command Line Usage

**Test Indeed Scraper:**
```python
from scrapers.indeed_scraper import IndeedScraper

scraper = IndeedScraper()
jobs = scraper.scrape_jobs("Python Developer", "San Francisco, CA", num_pages=2)
print(f"Found {len(jobs)} jobs")
```

**Test Glassdoor Scraper:**
```python
from scrapers.glassdoor_scraper import GlassdoorScraper

scraper = GlassdoorScraper()
jobs = scraper.scrape_jobs("Data Analyst", "Boston, MA", num_pages=1)
print(f"Found {len(jobs)} jobs")
```

### API Usage

**Start the Flask server:**
```bash
cd backend
python app.py
```

**Make API request:**
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_titles": ["Software Engineer"],
    "location": "New York, NY",
    "num_pages": 1,
    "sources": ["indeed"]
  }'
```

## Testing

### Run Test Suite

```bash
cd backend
python test_scraper.py
```

The test suite includes:
1. **Indeed Scraper Test**: Tests scraping functionality and data validation
2. **Glassdoor Scraper Test**: Tests scraping functionality and data validation
3. **API Endpoint Test**: Tests Flask API endpoints

**Test Output Example:**
```
============================================================
JOB SCRAPER TEST SUITE
============================================================

============================================================
Testing Indeed Scraper
============================================================

Searching for: Software Engineer
Location: New York, NY
Pages: 1

Scraping...

✓ Successfully scraped 10 jobs from Indeed

------------------------------------------------------------
Sample Job (First Result):
------------------------------------------------------------
{
  "source": "Indeed",
  "title": "Software Engineer",
  "company": "Tech Company",
  ...
}

------------------------------------------------------------
Data Validation:
------------------------------------------------------------
Valid jobs: 10/10

Field coverage:
  title: 10/10 (100.0%)
  company: 10/10 (100.0%)
  location: 10/10 (100.0%)
  salary: 5/10 (50.0%)
  job_type: 7/10 (70.0%)
  description: 10/10 (100.0%)
  link: 10/10 (100.0%)

============================================================
TEST SUMMARY
============================================================
Indeed: ✓ PASSED
Glassdoor: ✓ PASSED
Api: ✓ PASSED

============================================================
ALL TESTS PASSED ✓
============================================================
```

## Anti-Blocking Measures

The scrapers implement several anti-blocking techniques:

1. **User Agent Spoofing**: Uses realistic browser user agents
2. **Request Delays**: Random delays between requests (2-5 seconds)
3. **Retry Logic**: Automatically retries failed requests up to 3 times
4. **Rate Limit Handling**: Detects and handles 429 (Too Many Requests) responses
5. **Timeout Protection**: 10-second timeout for each request
6. **Session Management**: Maintains session state for better performance

## Data Structure

### Job Object Schema

```python
{
  "source": str,        # "Indeed" or "Glassdoor"
  "title": str,         # Job title
  "company": str,       # Company name
  "location": str,      # Job location
  "salary": {           # Salary information (may be None)
    "min": int,         # Minimum salary
    "max": int,         # Maximum salary
    "raw": str          # Original salary text
  },
  "job_type": str,      # e.g., "Remote", "Full-time", "Hybrid"
  "description": str,   # Job description snippet
  "link": str          # Direct link to job posting
}
```

## Error Handling

The scrapers handle various error scenarios:

1. **Network Errors**: Connection timeouts, DNS failures
2. **HTTP Errors**: 404, 429, 500+ status codes
3. **Parsing Errors**: Missing elements, changed HTML structure
4. **Validation Errors**: Invalid or incomplete job data

All errors are logged with context for debugging.

## Limitations

1. **Static Content Only**: This module uses BeautifulSoup and only scrapes static HTML. JavaScript-rendered content is not captured. See Task 3.2 for Selenium-based dynamic scraping.

2. **Rate Limiting**: Job boards may rate limit excessive requests. The scrapers implement delays but aggressive scraping may still be blocked.

3. **HTML Structure Changes**: Job board websites frequently change their HTML structure. Scrapers use multiple selector strategies but may require updates.

4. **Incomplete Data**: Not all job listings include salary or job type information. Fields may be None/null.

5. **Page Limits**: Recommended to scrape 1-3 pages per query to avoid detection and rate limiting.

## Best Practices

1. **Respectful Scraping**: Use reasonable delays and limit the number of pages
2. **Error Monitoring**: Monitor scraping results for high error rates
3. **Data Validation**: Always validate scraped data before using
4. **Regular Updates**: Check and update selectors if scraping stops working
5. **Fallback Sources**: Use multiple job boards to ensure data availability

## Troubleshooting

### No Jobs Found
- Check if the job board's HTML structure has changed
- Verify the search URL is correctly formatted
- Try different job titles or locations

### Request Timeouts
- Increase timeout in `make_request()` method
- Check internet connection
- Job board may be experiencing issues

### Rate Limiting
- Increase delays between requests
- Reduce number of pages to scrape
- Wait before retrying

### Validation Failures
- Check which required fields are missing
- Update selectors in `_extract_job_from_card()` method
- Enable debug logging for more details

## Future Enhancements

1. **Dynamic Scraping**: Implement Selenium for JavaScript-rendered content (Task 3.2)
2. **More Job Boards**: Add LinkedIn, Monster, ZipRecruiter scrapers
3. **Proxy Support**: Rotate proxies to avoid IP-based blocking
4. **Data Storage**: Save scraped jobs to database instead of memory
5. **Scheduling**: Automated periodic scraping with cron jobs
6. **Duplicate Detection**: Identify and merge duplicate job listings

## Related Tasks

- **Task 3.2**: Dynamic Scraping using Selenium
- **Task 3.3**: Manage Scraping Data Storage
- **Task 4.1**: Data Cleaning
- **Task 4.2**: Filtering Logic Implementation

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test output for specific error messages
3. Inspect HTML structure of target job boards
4. Update selectors in scraper files as needed

---

**Task 3.1 Status**: ✓ COMPLETED
**Date**: November 9, 2025
