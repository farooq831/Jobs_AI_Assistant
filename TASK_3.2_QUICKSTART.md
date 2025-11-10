# Task 3.2: Dynamic Scraping - Quick Start Guide

## 5-Minute Setup and Test

This guide will get you up and running with Selenium-based job scraping in under 5 minutes.

---

## Step 1: Setup (2 minutes)

### Automated Setup

```bash
# Run the setup script
bash setup_task_3.2.sh
```

That's it! The script will install Chrome/Chromium, ChromeDriver, and verify everything is working.

### Manual Setup (if automated fails)

```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser chromium-chromedriver

# Install Python dependencies (if not already done)
pip install -r requirements.txt
```

---

## Step 2: First Scrape (1 minute)

### Using Python

Create a file `test_scrape.py`:

```python
from backend.scrapers.indeed_selenium_scraper import IndeedSeleniumScraper

# Create scraper
scraper = IndeedSeleniumScraper(headless=True)

# Scrape jobs
jobs = scraper.scrape_jobs(
    job_title="Software Engineer",
    location="San Francisco",
    num_pages=1
)

# Print results
print(f"Found {len(jobs)} jobs!")
for job in jobs[:3]:  # Show first 3
    print(f"\n{job['title']} at {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Link: {job['link']}")
```

Run it:

```bash
python test_scrape.py
```

---

## Step 3: Use the API (2 minutes)

### Start the Backend

```bash
# Terminal 1: Start Flask server
python backend/app.py
```

### Make API Request

```bash
# Terminal 2: Send scraping request
curl -X POST http://localhost:5000/api/scrape-jobs-dynamic \
  -H "Content-Type: application/json" \
  -d '{
    "job_titles": ["Python Developer"],
    "location": "New York",
    "num_pages": 1,
    "sources": ["indeed"],
    "headless": true
  }'
```

---

## Quick Examples

### Example 1: Scrape Multiple Job Titles

```python
from backend.scrapers.indeed_selenium_scraper import IndeedSeleniumScraper

scraper = IndeedSeleniumScraper(headless=True)

job_titles = ["Data Scientist", "Machine Learning Engineer"]
all_jobs = []

for title in job_titles:
    jobs = scraper.scrape_jobs(title, "Remote", num_pages=1)
    all_jobs.extend(jobs)

print(f"Total jobs found: {len(all_jobs)}")
```

### Example 2: Scrape with Context Manager

```python
from backend.scrapers.glassdoor_selenium_scraper import GlassdoorSeleniumScraper

# Automatically cleans up browser
with GlassdoorSeleniumScraper(headless=True) as scraper:
    jobs = scraper.scrape_jobs("Backend Developer", "Austin", num_pages=2)
    print(f"Found {len(jobs)} jobs")
```

### Example 3: Debug Mode (Visible Browser)

```python
# Watch the scraper work in real-time
scraper = IndeedSeleniumScraper(headless=False)
jobs = scraper.scrape_jobs("Frontend Developer", "Seattle", num_pages=1)
```

### Example 4: Custom Configuration

```python
scraper = IndeedSeleniumScraper(headless=True)

# Adjust delays to avoid rate limiting
scraper.min_delay = 3
scraper.max_delay = 6

# Scrape
jobs = scraper.scrape_jobs("DevOps Engineer", "Boston", num_pages=2)
```

---

## API Quick Reference

### Endpoint

```
POST /api/scrape-jobs-dynamic
```

### Minimal Request

```json
{
  "job_titles": ["Software Engineer"],
  "location": "San Francisco"
}
```

### Full Request

```json
{
  "job_titles": ["Software Engineer", "Full Stack Developer"],
  "location": "San Francisco, CA",
  "num_pages": 2,
  "sources": ["indeed", "glassdoor"],
  "headless": true
}
```

### Response

```json
{
  "success": true,
  "scrape_id": 1,
  "total_jobs": 35,
  "scraping_results": {
    "indeed": {"success": true, "count": 20},
    "glassdoor": {"success": true, "count": 15}
  },
  "jobs": [
    {
      "source": "Indeed",
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "salary": {"min": 120000, "max": 180000},
      "job_type": "Full-time, Remote",
      "description": "We are looking for...",
      "link": "https://indeed.com/viewjob?jk=..."
    }
  ]
}
```

---

## Testing

### Run Full Test Suite

```bash
python backend/test_selenium_scraper.py
```

### Quick Test

```python
# Test Indeed scraper
from backend.scrapers.indeed_selenium_scraper import IndeedSeleniumScraper

scraper = IndeedSeleniumScraper(headless=True)
jobs = scraper.scrape_jobs("Test", "Remote", num_pages=1)
print(f"✓ Test passed! Found {len(jobs)} jobs")
```

---

## Common Issues

### Issue: ChromeDriver not found

**Solution**:
```bash
sudo apt-get install chromium-chromedriver
```

### Issue: No jobs found

**Causes**:
- Rate limiting (wait 5 minutes)
- Website structure changed
- Network issues

**Solution**:
```python
# Try with visible browser to debug
scraper = IndeedSeleniumScraper(headless=False)
```

### Issue: Browser opens but doesn't work

**Solution**:
```bash
# Check Chrome and ChromeDriver versions match
google-chrome --version
chromedriver --version
```

---

## Next Steps

### Learn More
- Read `TASK_3.2_README.md` for complete documentation
- Check `TASK_3.2_ARCHITECTURE.md` for technical details
- Review `TASK_3.2_SUMMARY.md` for implementation overview

### Integrate with Frontend
1. Start the Flask backend: `python backend/app.py`
2. Use the API from your frontend
3. Display scraped jobs to users

### Customize
- Adjust delays in `selenium_scraper.py`
- Add more user agents for rotation
- Modify selectors for new website structures
- Add support for more job boards

---

## Comparison: When to Use What?

### Use Static Scraping (Task 3.1)
- Quick tests
- Simple job boards
- Low resource usage needed
- Speed is priority

### Use Dynamic Scraping (Task 3.2)
- Production use
- JavaScript-heavy sites
- Pagination required
- Reliability is priority

---

## Tips for Success

1. **Start with 1 page**: Test with `num_pages=1` first
2. **Use headless mode**: Faster and more efficient
3. **Respect delays**: Don't decrease min/max delays too much
4. **Monitor rate limits**: If you get blocked, wait longer between requests
5. **Check results**: Always validate the scraped data

---

## Example Workflow

```python
# Complete workflow example
from backend.scrapers.indeed_selenium_scraper import IndeedSeleniumScraper
import json

# 1. Setup scraper
scraper = IndeedSeleniumScraper(headless=True)

# 2. Define search parameters
job_titles = ["Python Developer", "Django Developer"]
location = "Remote"

# 3. Scrape jobs
all_jobs = []
for title in job_titles:
    print(f"Scraping: {title}...")
    jobs = scraper.scrape_jobs(title, location, num_pages=2)
    all_jobs.extend(jobs)
    print(f"  Found {len(jobs)} jobs")

# 4. Filter and process
filtered_jobs = [
    job for job in all_jobs 
    if job['salary'] and job['salary']['min'] >= 80000
]

# 5. Save results
with open('jobs.json', 'w') as f:
    json.dump(filtered_jobs, f, indent=2, default=str)

print(f"\nTotal: {len(all_jobs)} jobs")
print(f"Filtered: {len(filtered_jobs)} jobs")
print("Saved to jobs.json")
```

---

## Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in terminal
2. **Run tests**: `python backend/test_selenium_scraper.py`
3. **Debug visually**: Set `headless=False` to see what's happening
4. **Read docs**: Check `TASK_3.2_README.md` for detailed troubleshooting

---

**Ready to scrape!** 🚀

Start with the examples above and customize as needed. The scrapers are designed to be flexible and easy to use.

---

**Last Updated**: 2025-11-09  
**Task**: 3.2 - Dynamic Scraping using Selenium
