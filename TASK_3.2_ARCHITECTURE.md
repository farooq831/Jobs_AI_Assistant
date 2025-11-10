# Task 3.2: Dynamic Scraping - Architecture Documentation

## System Architecture

This document provides detailed technical architecture for the Selenium-based dynamic scraping implementation.

---

## Table of Contents

1. [Overview](#overview)
2. [Component Architecture](#component-architecture)
3. [Class Design](#class-design)
4. [Data Flow](#data-flow)
5. [Selenium Integration](#selenium-integration)
6. [Anti-Blocking Strategy](#anti-blocking-strategy)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)

---

## Overview

### Purpose

Task 3.2 extends the static scraping capabilities (Task 3.1) with dynamic content handling using Selenium WebDriver to:
- Execute JavaScript on job board pages
- Handle lazy-loaded content
- Navigate pagination dynamically
- Implement sophisticated anti-blocking mechanisms

### Key Technologies

- **Selenium WebDriver**: Browser automation
- **Chrome/Chromium**: Headless browser engine
- **BeautifulSoup**: HTML parsing (same as Task 3.1)
- **Flask**: REST API endpoints
- **Python 3.8+**: Core language

---

## Component Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Flask API Layer                       │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ /api/scrape-jobs     │  │/api/scrape-jobs-     │        │
│  │ (Static - Task 3.1)  │  │dynamic (Task 3.2)    │        │
│  └──────────┬───────────┘  └──────────┬───────────┘        │
└─────────────┼──────────────────────────┼────────────────────┘
              │                          │
              v                          v
┌─────────────────────────┐  ┌──────────────────────────────┐
│   Static Scrapers       │  │   Selenium Scrapers          │
│  ┌──────────────────┐   │  │  ┌────────────────────────┐  │
│  │ BaseScraper      │   │  │  │ SeleniumScraper        │  │
│  │   (Abstract)     │   │  │  │   (Abstract)           │  │
│  └────────┬─────────┘   │  │  └──────────┬─────────────┘  │
│           │              │  │             │                │
│     ┌─────┴─────┐       │  │     ┌───────┴──────┐        │
│     │           │        │  │     │              │        │
│  ┌──v────┐  ┌──v───┐    │  │  ┌──v─────┐  ┌────v──────┐ │
│  │Indeed │  │Glass │    │  │  │Indeed  │  │Glassdoor  │ │
│  │Scraper│  │door  │    │  │  │Selenium│  │Selenium   │ │
│  └───────┘  └──────┘    │  │  └────────┘  └───────────┘ │
└─────────────────────────┘  └──────────────────────────────┘
              │                          │
              v                          v
┌─────────────────────────────────────────────────────────────┐
│                      External Job Boards                     │
│              (Indeed, Glassdoor, etc.)                       │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
Jobs_AI_Assistant/
├── backend/
│   ├── app.py                            # Flask API with endpoints
│   ├── scrapers/
│   │   ├── __init__.py                   # Package initialization
│   │   ├── base_scraper.py               # Static base class
│   │   ├── selenium_scraper.py           # ✨ Selenium base class
│   │   ├── indeed_scraper.py             # Static Indeed scraper
│   │   ├── indeed_selenium_scraper.py    # ✨ Selenium Indeed scraper
│   │   ├── glassdoor_scraper.py          # Static Glassdoor scraper
│   │   └── glassdoor_selenium_scraper.py # ✨ Selenium Glassdoor scraper
│   ├── test_scraper.py                   # Tests for static scrapers
│   └── test_selenium_scraper.py          # ✨ Tests for Selenium scrapers
├── setup_task_3.2.sh                     # ✨ Setup script
└── TASK_3.2_*.md                         # ✨ Documentation

✨ = New in Task 3.2
```

---

## Class Design

### 1. SeleniumScraper (Abstract Base Class)

```python
class SeleniumScraper(ABC):
    """
    Abstract base class for Selenium-based job scrapers
    
    Responsibilities:
    - WebDriver initialization and configuration
    - Anti-detection mechanisms
    - Page navigation and element interaction
    - Context manager support
    """
    
    # Class-level constants
    USER_AGENTS: List[str]     # Rotation pool
    
    # Instance attributes
    driver: webdriver.Chrome    # Selenium driver
    headless: bool             # Run mode
    user_agent: str            # Current UA
    min_delay: float           # Rate limiting
    max_delay: float           # Rate limiting
    page_load_timeout: int     # Timeout config
    element_timeout: int       # Timeout config
```

#### Key Methods

##### Driver Management

```python
def _setup_driver() -> webdriver.Chrome:
    """
    Configure and initialize Chrome WebDriver
    
    Configurations:
    - Headless mode
    - User agent
    - Anti-detection flags
    - Performance options
    - Privacy settings
    """

def start_driver() -> None:
    """Initialize driver if not already started"""

def close_driver() -> None:
    """Cleanup and close driver"""
```

##### Navigation

```python
def get_page(url: str, wait_for_element: Optional[tuple] = None, 
             max_retries: int = 3) -> bool:
    """
    Navigate to URL with retry logic
    
    Args:
        url: Target URL
        wait_for_element: Tuple of (By.METHOD, 'selector')
        max_retries: Retry attempts
        
    Returns:
        Success status
    """
```

##### Interaction

```python
def scroll_page(scroll_pause_time: float = 1.0, 
                num_scrolls: int = 3) -> None:
    """
    Scroll page to load lazy content
    
    Behavior:
    - Progressive scrolling
    - Variable positions
    - Human-like timing
    """

def click_element(by: By, selector: str, timeout: int = 10) -> bool:
    """
    Click element with wait
    
    Features:
    - Wait for clickability
    - Scroll into view
    - Error handling
    """
```

##### Data Extraction

```python
def get_soup() -> BeautifulSoup:
    """Extract BeautifulSoup from current page"""

def extract_salary(salary_text: str) -> Dict[str, Optional[int]]:
    """Parse salary information"""

def clean_text(text: str) -> str:
    """Normalize text data"""
```

##### Pagination

```python
def handle_pagination(next_button_selector: tuple, 
                     max_pages: int = 5) -> List[BeautifulSoup]:
    """
    Navigate through pages and collect content
    
    Strategy:
    - Click next button
    - Wait for page load
    - Apply delays
    - Handle failures gracefully
    """
```

##### Abstract Methods

```python
@abstractmethod
def build_search_url(job_title: str, location: str, 
                     page: int = 0) -> str:
    """Build platform-specific search URL"""

@abstractmethod
def extract_jobs(soup: BeautifulSoup) -> List[Dict]:
    """Extract jobs from parsed HTML"""
```

##### Main Scraping Method

```python
def scrape_jobs(job_title: str, location: str, 
                num_pages: int = 1) -> List[Dict]:
    """
    Main scraping workflow
    
    Steps:
    1. Start driver
    2. For each page:
       a. Build URL
       b. Navigate to page
       c. Scroll for lazy content
       d. Extract jobs
       e. Apply delays
    3. Close driver
    4. Return all jobs
    """
```

### 2. IndeedSeleniumScraper

```python
class IndeedSeleniumScraper(SeleniumScraper):
    """
    Indeed-specific Selenium scraper
    
    Indeed Specifics:
    - URL structure: /jobs?q={title}&l={location}&start={offset}
    - Pagination: 10 jobs per page, start parameter
    - Job cards: div.job_seen_beacon or div[data-jk]
    - Dynamic loading: Lazy-loaded cards
    """
```

#### Implementation Details

##### URL Building

```python
def build_search_url(job_title: str, location: str, page: int = 0) -> str:
    """
    Indeed URL pattern:
    https://indeed.com/jobs?q=Software+Engineer&l=New+York&start=0
    
    Pagination: start = page * 10
    """
```

##### Job Extraction

```python
def extract_jobs(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract from Indeed job cards
    
    Selectors (tried in order):
    1. div.job_seen_beacon
    2. div.cardOutline
    3. td.resultContent
    4. div[data-jk]
    
    Extracted fields:
    - Title: h2.jobTitle > a
    - Company: span.companyName
    - Location: div.companyLocation
    - Salary: div.salary-snippet
    - Type: div.metadata
    - Description: div.job-snippet
    - Link: Constructed from data-jk
    """
```

##### Pagination Handling

```python
def scrape_with_pagination(job_title: str, location: str, 
                           num_pages: int = 1) -> List[Dict]:
    """
    Indeed pagination approaches:
    1. Click next button: a[aria-label="Next Page"]
    2. XPath: //a[contains(text(), 'Next')]
    3. Direct URL: Build next page URL
    
    Fallback strategy ensures reliability
    """
```

### 3. GlassdoorSeleniumScraper

```python
class GlassdoorSeleniumScraper(SeleniumScraper):
    """
    Glassdoor-specific Selenium scraper
    
    Glassdoor Specifics:
    - URL structure: Complex with multiple parameters
    - Pagination: page parameter (starts at 1)
    - Job cards: li.react-job-listing or li[data-test="jobListing"]
    - Popups: Login/signup modals need handling
    """
```

#### Implementation Details

##### Popup Handling

```python
def handle_popup() -> bool:
    """
    Close Glassdoor popups
    
    Attempts (in order):
    1. button[aria-label="Close"]
    2. button.modal_closeIcon
    3. .CloseButton class
    4. XPath: //button[contains(text(), 'Close')]
    
    Returns: True if popup closed
    """
```

##### Job Extraction

```python
def extract_jobs(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract from Glassdoor job cards
    
    Selectors (tried in order):
    1. li.react-job-listing
    2. li[data-test="jobListing"]
    3. article.job-listing
    4. div.jobContainer
    
    Special handling:
    - Salary: Remove "Glassdoor est." prefix
    - Company: Multiple possible locations
    - Badges: Remote/hybrid indicators
    """
```

---

## Data Flow

### Scraping Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. API Request                                               │
│    POST /api/scrape-jobs-dynamic                            │
│    {job_titles, location, num_pages, sources, headless}     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      v
┌─────────────────────────────────────────────────────────────┐
│ 2. Initialize Scrapers                                       │
│    - Create IndeedSeleniumScraper(headless=True)            │
│    - Create GlassdoorSeleniumScraper(headless=True)         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      v
┌─────────────────────────────────────────────────────────────┐
│ 3. For Each Job Title                                        │
│    - Build search URL                                        │
│    - Start WebDriver                                         │
│    └─────────┐                                              │
│              v                                               │
│    ┌─────────────────────────────────────────┐             │
│    │ 4. For Each Page                         │             │
│    │    - Navigate to URL                     │             │
│    │    - Wait for elements                   │             │
│    │    - Scroll page                         │             │
│    │    - Extract HTML                        │             │
│    │    - Parse with BeautifulSoup           │             │
│    │    - Extract job cards                   │             │
│    │    - Validate data                       │             │
│    │    - Apply delays                        │             │
│    │    - Next page or break                  │             │
│    └─────────────────────────────────────────┘             │
│    - Close WebDriver                                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      v
┌─────────────────────────────────────────────────────────────┐
│ 5. Aggregate Results                                         │
│    - Combine jobs from all sources                          │
│    - Store in scraped_jobs_store                            │
│    - Generate scraping statistics                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      v
┌─────────────────────────────────────────────────────────────┐
│ 6. API Response                                              │
│    {success, scrape_id, total_jobs, results, jobs[]}       │
└─────────────────────────────────────────────────────────────┘
```

### Data Structure

#### Job Object

```python
{
    "source": str,              # "Indeed" or "Glassdoor"
    "title": str,               # Job title
    "company": str,             # Company name
    "location": str,            # Job location
    "salary": {                 # Parsed salary (optional)
        "min": int,             # Minimum salary
        "max": int,             # Maximum salary
        "raw": str              # Original text
    },
    "job_type": str,            # "Remote", "Full-time", etc.
    "description": str,         # Job description snippet
    "link": str                 # Direct link to job posting
}
```

---

## Selenium Integration

### WebDriver Configuration

```python
chrome_options = Options()

# Stealth configurations
chrome_options.add_argument('--headless=new')
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Performance
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

# Privacy
chrome_options.add_argument('--incognito')

driver = webdriver.Chrome(options=chrome_options)

# Remove webdriver property
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

### Wait Strategies

```python
# Explicit wait for element
WebDriverWait(driver, timeout).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
)

# Implicit wait (set once)
driver.implicitly_wait(element_timeout)

# Page load timeout
driver.set_page_load_timeout(page_load_timeout)
```

---

## Anti-Blocking Strategy

### Multi-Layer Approach

#### Layer 1: User Agent Rotation
- 6+ modern user agents
- Random selection per instance
- Covers multiple browsers and OS

#### Layer 2: Request Timing
```python
# Random delays
delay = random.uniform(min_delay, max_delay)
time.sleep(delay)

# Configurable ranges (default: 2-5 seconds)
```

#### Layer 3: Human Behavior Simulation
```python
# Progressive scrolling
for i in range(num_scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    # Scroll back up slightly
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
```

#### Layer 4: Browser Fingerprinting
- Headless mode with proper flags
- Remove automation indicators
- Set realistic window size
- Proper language preferences

#### Layer 5: Error Recovery
```python
# Retry logic with exponential backoff
for attempt in range(max_retries):
    try:
        # Operation
        break
    except TimeoutException:
        wait_time = (attempt + 1) * delay
        time.sleep(wait_time)
```

---

## Error Handling

### Exception Hierarchy

```
Exception
├── WebDriverException          # Selenium-specific
│   ├── TimeoutException        # Page load timeout
│   ├── NoSuchElementException  # Element not found
│   └── SessionNotCreatedException  # Driver init failed
└── StandardExceptions
    ├── ConnectionError         # Network issues
    └── ValueError              # Invalid input
```

### Handling Strategy

```python
try:
    # Primary operation
    driver.get(url)
    element = driver.find_element(By.CSS_SELECTOR, selector)
except TimeoutException:
    # Retry with increased wait
    WebDriverWait(driver, timeout * 2).until(...)
except NoSuchElementException:
    # Try alternative selector
    element = driver.find_element(By.XPATH, xpath)
except WebDriverException as e:
    # Log and continue
    print(f"WebDriver error: {e}")
    return []
finally:
    # Always cleanup
    driver.quit()
```

---

## Performance Optimization

### Resource Management

```python
# Context manager pattern
with SeleniumScraper() as scraper:
    jobs = scraper.scrape_jobs(...)
# Driver automatically closed
```

### Memory Optimization
- Close browser between scraping sessions
- Clear browser cache periodically
- Limit concurrent browser instances
- Use headless mode in production

### Speed Optimization
- Reduce delays for trusted environments
- Disable images: `chrome_options.add_argument('--blink-settings=imagesEnabled=false')`
- Minimize scrolling iterations
- Cache frequently used data

### Parallel Scraping (Future)
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    for title in job_titles:
        future = executor.submit(scraper.scrape_jobs, title, location)
        futures.append(future)
    
    results = [f.result() for f in futures]
```

---

## Testing Architecture

### Test Levels

1. **Unit Tests**: Individual methods
2. **Integration Tests**: Complete scraping workflow
3. **E2E Tests**: API endpoints with live scraping

### Test Structure

```python
def test_indeed_selenium():
    # Setup
    scraper = IndeedSeleniumScraper(headless=True)
    
    # Execute
    jobs = scraper.scrape_jobs("Software Engineer", "New York", 1)
    
    # Assert
    assert len(jobs) > 0
    assert all('title' in job for job in jobs)
    
    # Cleanup (handled by context manager)
```

---

## Security Considerations

### Rate Limiting
- Respect robots.txt
- Implement exponential backoff
- Monitor for 429 responses
- Limit requests per minute

### Data Privacy
- Don't store personal information
- Comply with GDPR/CCPA
- Clear cookies between sessions
- Use incognito mode

### Legal Compliance
- Review website Terms of Service
- Implement opt-out mechanisms
- Add proper user agent identification
- Respect robots.txt directives

---

## Monitoring and Logging

### Logging Strategy

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Scraping page {page}")
logger.warning(f"No jobs found on page {page}")
logger.error(f"Failed to load page: {error}")
```

### Metrics to Track
- Success rate per source
- Average jobs per page
- Scraping duration
- Error frequency
- Rate limit occurrences

---

## Future Architecture Considerations

### Scalability
- Distributed scraping with Celery
- Queue-based job processing
- Database persistence (PostgreSQL)
- Redis caching layer

### Reliability
- Proxy rotation
- CAPTCHA solving service integration
- Automatic selector updating
- Fallback strategies

### Extensibility
- Plugin architecture for new sources
- Configuration-driven selectors
- Custom parser injection
- Webhook notifications

---

**Last Updated**: 2025-11-09  
**Version**: 1.0.0  
**Task**: 3.2 - Dynamic Scraping using Selenium
