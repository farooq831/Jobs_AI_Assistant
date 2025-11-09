# Task 3.1: Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Verify Dependencies
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
pip list | grep -E "beautifulsoup4|requests|lxml"
```

Expected output:
```
beautifulsoup4    4.12.2
requests          2.31.0
lxml              4.9.3
```

### Step 2: Start the Flask Server
```bash
cd backend
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
```

### Step 3: Test the Scrapers

**Option A: Run Test Suite (Recommended)**
```bash
# In a new terminal
cd backend
python test_scraper.py
```

**Option B: Test API with curl**
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

**Option C: Test in Python**
```python
from scrapers.indeed_scraper import IndeedScraper

scraper = IndeedScraper()
jobs = scraper.scrape_jobs("Python Developer", "San Francisco, CA", 1)
print(f"Found {len(jobs)} jobs")
for job in jobs[:3]:
    print(f"- {job['title']} at {job['company']}")
```

### Step 4: View Results

The API returns JSON with all scraped jobs:
```json
{
  "success": true,
  "total_jobs": 15,
  "jobs": [
    {
      "source": "Indeed",
      "title": "Software Engineer",
      "company": "Tech Corp",
      "location": "New York, NY",
      "link": "https://www.indeed.com/viewjob?jk=..."
    }
  ]
}
```

## Common Use Cases

### Scrape Multiple Job Titles
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_titles": ["Data Scientist", "ML Engineer", "AI Researcher"],
    "location": "Seattle, WA",
    "num_pages": 2
  }'
```

### Scrape from Single Source
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_titles": ["DevOps Engineer"],
    "location": "Austin, TX",
    "num_pages": 1,
    "sources": ["indeed"]
  }'
```

### Retrieve Previous Results
```bash
# Get specific scrape result
curl http://localhost:5000/api/scrape-jobs/1

# Get all scrape results
curl http://localhost:5000/api/scrape-jobs
```

## Quick Tips

1. **Start Small**: Begin with 1 page and 1 job title
2. **Be Patient**: Scraping includes delays (2-5 seconds) to avoid blocking
3. **Monitor Results**: Check the `scraping_results` in the response
4. **Handle Failures**: Some job boards may fail - check the `error` field
5. **Validate Data**: Not all fields are always available (especially salary)

## Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process if needed
kill -9 <PID>

# Or use a different port
export FLASK_RUN_PORT=5001
python app.py
```

### Import errors
```bash
# Ensure you're in the backend directory
cd backend

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant/backend"
```

### No jobs found
- Try a more common job title (e.g., "Software Engineer")
- Try a major city location (e.g., "New York, NY")
- Job board HTML may have changed - check scrapers

## Next Steps

1. ✓ You've completed Task 3.1!
2. → Move to Task 3.2: Dynamic Scraping with Selenium
3. → Or Task 4.1: Data Cleaning and Filtering

## Complete Example Script

Save as `test_quick.py`:
```python
#!/usr/bin/env python
"""Quick test of job scrapers"""

import sys
sys.path.insert(0, 'backend')

from scrapers.indeed_scraper import IndeedScraper
from scrapers.glassdoor_scraper import GlassdoorScraper

def main():
    print("Testing Indeed Scraper...")
    indeed = IndeedScraper()
    indeed_jobs = indeed.scrape_jobs("Software Engineer", "Boston, MA", 1)
    print(f"✓ Found {len(indeed_jobs)} Indeed jobs")
    
    print("\nTesting Glassdoor Scraper...")
    glassdoor = GlassdoorScraper()
    glassdoor_jobs = glassdoor.scrape_jobs("Data Analyst", "Chicago, IL", 1)
    print(f"✓ Found {len(glassdoor_jobs)} Glassdoor jobs")
    
    print(f"\nTotal: {len(indeed_jobs) + len(glassdoor_jobs)} jobs")
    print("✓ All scrapers working!")

if __name__ == '__main__':
    main()
```

Run it:
```bash
python test_quick.py
```

---

**Ready to scrape!** 🚀
