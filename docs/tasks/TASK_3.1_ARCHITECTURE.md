# Task 3.1: Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Application                       │
│                  (Frontend / API Consumer)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP POST /api/scrape-jobs
                            │ HTTP GET /api/scrape-jobs/:id
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Flask Backend                           │
│                        (app.py)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Scraping API Endpoints                     │   │
│  │  • POST /api/scrape-jobs                            │   │
│  │  • GET /api/scrape-jobs/:id                         │   │
│  │  • GET /api/scrape-jobs                             │   │
│  └────────────┬────────────────────────┬─────────────────┘   │
└───────────────┼────────────────────────┼──────────────────────┘
                │                        │
                │                        │
    ┌───────────▼───────────┐ ┌─────────▼──────────┐
    │  IndeedScraper       │ │ GlassdoorScraper  │
    │  (indeed_scraper.py) │ │ (glassdoor_scraper.py)│
    └───────────┬───────────┘ └─────────┬──────────┘
                │                        │
                │   extends              │   extends
                └───────────┬────────────┘
                            │
                ┌───────────▼───────────┐
                │    BaseScraper        │
                │  (base_scraper.py)    │
                │                       │
                │  • make_request()     │
                │  • parse_html()       │
                │  • clean_text()       │
                │  • extract_salary()   │
                │  • validate_job_data()│
                └───────────┬───────────┘
                            │
                ┌───────────▼───────────┐
                │   External Services   │
                │                       │
                │  • Indeed.com         │
                │  • Glassdoor.com      │
                └───────────────────────┘
```

## Component Breakdown

### 1. Flask Backend (app.py)
**Purpose**: Provides REST API endpoints for job scraping

**Responsibilities**:
- Receive scraping requests from clients
- Validate input parameters
- Orchestrate scraping across multiple sources
- Store and retrieve scraping results
- Handle errors and return appropriate responses

**Key Functions**:
- `scrape_jobs()`: Main endpoint for initiating scraping
- `get_scraped_jobs()`: Retrieve specific scraping results
- `get_all_scraped_jobs()`: List all scraping results

**Data Storage**: In-memory dictionary (temporary)
```python
scraped_jobs_store = {
    1: {
        "job_titles": [...],
        "location": "...",
        "jobs": [...],
        "total_jobs": 25,
        "scraping_results": {...}
    }
}
```

### 2. BaseScraper (base_scraper.py)
**Purpose**: Abstract base class providing common scraping functionality

**Responsibilities**:
- HTTP request handling with retries
- Rate limiting and anti-blocking measures
- HTML parsing with BeautifulSoup
- Text cleaning and normalization
- Salary extraction and parsing
- Job data validation

**Key Methods**:
- `make_request(url)`: Fetch webpage with error handling
- `parse_html(html)`: Parse HTML with BeautifulSoup
- `clean_text(text)`: Clean and normalize text
- `extract_salary(text)`: Parse salary from text
- `scrape_jobs(title, location, pages)`: Main scraping workflow
- `validate_job_data(job)`: Ensure job has required fields

**Anti-Blocking Features**:
- Random delays (2-5 seconds)
- Realistic user agents
- Session management
- Retry logic (3 attempts)
- Rate limit detection

### 3. IndeedScraper (indeed_scraper.py)
**Purpose**: Indeed-specific scraping implementation

**Responsibilities**:
- Build Indeed search URLs
- Parse Indeed job cards
- Extract Indeed-specific elements

**Key Methods**:
- `build_search_url(title, location, page)`: Generate Indeed URLs
- `extract_jobs(soup)`: Parse job listings from Indeed page
- `_extract_job_from_card(card)`: Extract data from single job card
- `get_job_details(url)`: Fetch full job description

**Indeed-Specific Selectors**:
```python
job_cards = soup.find_all('div', class_='job_seen_beacon')
title = card.find('h2', class_='jobTitle')
company = card.find('span', class_='companyName')
location = card.find('div', class_='companyLocation')
salary = card.find('div', class_='salary-snippet')
```

**URL Format**:
```
https://www.indeed.com/jobs?q={title}&l={location}&start={page*10}
```

### 4. GlassdoorScraper (glassdoor_scraper.py)
**Purpose**: Glassdoor-specific scraping implementation

**Responsibilities**:
- Build Glassdoor search URLs
- Parse Glassdoor job cards
- Extract Glassdoor-specific elements

**Key Methods**:
- `build_search_url(title, location, page)`: Generate Glassdoor URLs
- `extract_jobs(soup)`: Parse job listings from Glassdoor page
- `_extract_job_from_card(card)`: Extract data from single job card
- `get_job_details(url)`: Fetch full job description

**Glassdoor-Specific Selectors**:
```python
job_cards = soup.find_all('li', class_='react-job-listing')
title = card.find('a', class_='job-title')
company = card.find('div', class_='employer-name')
location = card.find('div', class_='location')
salary = card.find('div', class_='salary')
```

**URL Format**:
```
https://www.glassdoor.com/Job/jobs.htm?sc.keyword={title}&locId={location}&page={page+1}
```

## Data Flow

### Scraping Request Flow
```
1. Client → POST /api/scrape-jobs
   {
     "job_titles": ["Software Engineer"],
     "location": "NYC",
     "num_pages": 2,
     "sources": ["indeed", "glassdoor"]
   }

2. Flask validates input
   ├─ Check job_titles is list
   ├─ Check location is string
   └─ Validate num_pages (1-5)

3. For each source:
   ├─ Initialize scraper (Indeed/Glassdoor)
   └─ For each job_title:
       └─ scrape_jobs(title, location, pages)
           ├─ For each page:
           │   ├─ build_search_url()
           │   ├─ make_request()
           │   ├─ parse_html()
           │   └─ extract_jobs()
           │       └─ For each job card:
           │           ├─ _extract_job_from_card()
           │           └─ validate_job_data()
           └─ Return all jobs

4. Aggregate results from all sources

5. Store in scraped_jobs_store with unique ID

6. Return response to client
   {
     "success": true,
     "scrape_id": 1,
     "total_jobs": 25,
     "jobs": [...]
   }
```

### Job Extraction Flow
```
HTML Page
    │
    ▼
BeautifulSoup Parser
    │
    ▼
Find Job Cards (multiple selectors tried)
    │
    ▼
For Each Card:
    ├─ Extract title → clean_text()
    ├─ Extract company → clean_text()
    ├─ Extract location → clean_text()
    ├─ Extract salary → extract_salary()
    ├─ Extract job_type → clean_text()
    ├─ Extract description → clean_text()
    └─ Build job link → URL formatting
    │
    ▼
Validate Job Data
    │
    ▼
Return Job Object
```

## Design Patterns

### 1. Template Method Pattern
`BaseScraper` defines the scraping algorithm structure, with subclasses implementing specific steps:
```python
# Template in BaseScraper
def scrape_jobs(self, job_title, location, num_pages):
    for page in range(num_pages):
        url = self.build_search_url(job_title, location, page)  # Implemented by subclass
        response = self.make_request(url)                        # Common method
        soup = self.parse_html(response.text)                    # Common method
        jobs = self.extract_jobs(soup)                          # Implemented by subclass
```

### 2. Strategy Pattern
Different scraping strategies (Indeed, Glassdoor) are encapsulated in separate classes that implement the same interface.

### 3. Decorator Pattern
The `make_request()` method decorates HTTP requests with:
- Retry logic
- Timeouts
- Error handling
- Rate limiting

## Error Handling Strategy

### Levels of Error Handling

1. **Request Level** (BaseScraper.make_request)
   - Network errors → Retry up to 3 times
   - Timeouts → Log and return None
   - HTTP errors → Log status code, retry

2. **Parsing Level** (Scraper.extract_jobs)
   - Missing elements → Try alternative selectors
   - Invalid data → Skip job, continue with next
   - HTML structure changes → Log warning, return empty list

3. **API Level** (app.py)
   - Validation errors → Return 400 with error details
   - Scraping failures → Partial results with error info
   - Server errors → Return 500 with error message

### Error Response Format
```json
{
  "success": false,
  "message": "Error description",
  "errors": {
    "field": "Specific error"
  }
}
```

## Performance Considerations

### Request Delays
- Minimum: 2 seconds between requests
- Maximum: 5 seconds between requests
- Purpose: Avoid rate limiting and detection

### Pagination Limits
- Maximum pages per query: 5
- Purpose: Reasonable response time and avoid blocking

### Memory Usage
- Jobs stored in memory (temporary)
- Future: Migrate to database (Task 3.3)

### Timeout Settings
- Request timeout: 10 seconds
- Purpose: Prevent hanging requests

## Scalability Considerations

### Current Limitations
- Single-threaded execution
- In-memory storage
- No persistent storage

### Future Enhancements (Not in Task 3.1)
1. **Async Scraping**: Use asyncio/aiohttp for parallel requests
2. **Database Storage**: PostgreSQL/MongoDB for persistence
3. **Caching**: Redis for caching scraped results
4. **Queue System**: Celery for background job processing
5. **Proxy Rotation**: Use proxy pool for IP rotation

## Testing Architecture

### Test Levels

1. **Unit Tests** (Individual methods)
   - `test_clean_text()`
   - `test_extract_salary()`
   - `test_validate_job_data()`

2. **Integration Tests** (Full scraping flow)
   - `test_indeed_scraper()`
   - `test_glassdoor_scraper()`

3. **API Tests** (End-to-end)
   - `test_api_endpoint()`

### Test Structure
```python
def test_scraper():
    1. Initialize scraper
    2. Call scrape_jobs()
    3. Validate results:
       ├─ Count > 0
       ├─ All jobs valid
       └─ Required fields present
    4. Check field coverage
```

## Security Considerations

### Current Implementation
- No authentication required
- CORS enabled for all origins
- No rate limiting on API

### Recommendations for Production
1. Add API authentication (JWT tokens)
2. Implement rate limiting (Flask-Limiter)
3. Restrict CORS to specific domains
4. Add input sanitization
5. Use HTTPS only
6. Monitor for abuse

## Monitoring and Logging

### Current Logging
```python
print(f"Scraping page {page + 1}: {url}")
print(f"Extracted {len(jobs)} jobs from page {page + 1}")
print(f"Error scraping page: {str(e)}")
```

### Recommended for Production
1. Use Python `logging` module
2. Log levels: DEBUG, INFO, WARNING, ERROR
3. Log to file and console
4. Include timestamps and context
5. Monitor success/failure rates
6. Alert on high error rates

## Dependencies

### Direct Dependencies
- `beautifulsoup4`: HTML parsing
- `requests`: HTTP requests
- `lxml`: Fast HTML parser
- `Flask`: Web framework
- `Flask-CORS`: CORS support

### System Requirements
- Python 3.8+
- Internet connection
- ~100MB disk space

## Configuration

### Environment Variables (Optional)
```bash
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
MIN_DELAY=2  # Minimum delay between requests
MAX_DELAY=5  # Maximum delay between requests
```

### Scraper Configuration
```python
# In BaseScraper.__init__()
self.min_delay = 2
self.max_delay = 5
max_retries = 3
timeout = 10
```

## Maintenance

### Regular Checks
1. **Monitor success rates**: Track scraping success/failure ratio
2. **Verify selectors**: Job boards change HTML frequently
3. **Update user agents**: Keep user agent strings current
4. **Check rate limits**: Adjust delays if needed

### When Scraping Stops Working
1. Inspect current HTML structure of job board
2. Update selectors in scraper files
3. Test with `test_scraper.py`
4. Deploy updated scrapers

---

**Architecture Version**: 1.0  
**Last Updated**: November 9, 2025  
**Task**: 3.1 - Static Scraping with BeautifulSoup
