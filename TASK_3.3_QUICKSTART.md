# Task 3.3: Quick Start Guide

Get started with the Storage Manager in 5 minutes!

---

## Prerequisites

- Python 3.8+
- Flask backend running
- Completed Task 3.1 & 3.2 (scrapers)

---

## Step 1: Initialize Storage (30 seconds)

```python
from storage_manager import JobStorageManager

# Create storage instance
storage = JobStorageManager(storage_dir='data')

# That's it! Storage is ready to use.
# Files created automatically:
# - data/jobs.json
# - data/metadata.json
# - data/scraping_errors.json
```

---

## Step 2: Save Your First Jobs (1 minute)

```python
# Sample job data
jobs = [
    {
        "title": "Software Engineer",
        "company": "Google",
        "location": "New York, NY",
        "link": "https://careers.google.com/job/123",
        "description": "Join our team...",
        "job_type": "Full-time",
        "salary": {"min": 100000, "max": 150000}
    },
    {
        "title": "Data Scientist",
        "company": "Microsoft",
        "location": "Seattle, WA",
        "link": "https://careers.microsoft.com/job/456",
        "description": "Analyze data...",
        "job_type": "Full-time",
        "salary": {"min": 120000, "max": 170000}
    }
]

# Save jobs
result = storage.save_jobs(jobs, source="indeed")

print(f"✓ Added {result['added']} jobs")
print(f"✓ Skipped {result['skipped']} duplicates")
print(f"✓ Total in storage: {result['total']}")
```

**Expected Output:**
```
✓ Added 2 jobs
✓ Skipped 0 duplicates
✓ Total in storage: 2
```

---

## Step 3: Retrieve Jobs (30 seconds)

```python
# Get all jobs
all_jobs = storage.get_all_jobs()
print(f"Total jobs: {len(all_jobs)}")

# Filter by source
indeed_jobs = storage.get_all_jobs(filters={"source": "indeed"})
print(f"Indeed jobs: {len(indeed_jobs)}")

# Get specific job
job = storage.get_job_by_id(all_jobs[0]['id'])
print(f"Job title: {job['title']}")
```

---

## Step 4: Use with Scrapers (2 minutes)

```python
from scrapers.indeed_scraper import IndeedScraper
from storage_manager import JobStorageManager

# Initialize
scraper = IndeedScraper()
storage = JobStorageManager()

# Scrape jobs
jobs = scraper.scrape_jobs(
    job_title="Software Engineer",
    location="New York",
    num_pages=1
)

# Save to storage (with automatic deduplication)
result = storage.save_jobs(jobs, source="indeed")

print(f"✓ Scraped and saved {result['added']} jobs")
```

---

## Step 5: Add Retry Logic (1 minute)

```python
from scrapers.indeed_scraper import IndeedScraper
from scrapers.retry_scraper import RetryScraper, RetryConfig

# Create retry-enabled scraper
scraper = IndeedScraper()
config = RetryConfig(max_retries=3, initial_delay=1.0)
retry_scraper = RetryScraper(scraper, config)

# Scrape with automatic retries
result = retry_scraper.scrape_jobs_with_retry(
    "Software Engineer",
    "New York",
    num_pages=1
)

if result["success"]:
    print(f"✓ Succeeded after {result['total_attempts']} attempts")
    print(f"✓ Got {len(result['jobs'])} jobs")
    
    # Save to storage
    storage = JobStorageManager()
    storage.save_jobs(result["jobs"], source="indeed")
```

---

## Step 6: Use REST API (1 minute)

### Start the Flask server
```bash
cd backend
python app.py
```

### Test endpoints
```bash
# Get all stored jobs
curl http://localhost:5000/api/storage/jobs

# Get statistics
curl http://localhost:5000/api/storage/statistics

# Scrape and auto-save
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_titles": ["Software Engineer"],
    "location": "New York",
    "num_pages": 1,
    "sources": ["indeed"]
  }'
```

---

## Quick Test

Run the test suite to verify everything works:

```bash
cd backend
python test_storage_simple.py
```

**Expected Output:**
```
=== Testing Basic Storage Operations ===

1. Initializing storage...
   ✓ Storage initialized

2. Creating test jobs...
   ✓ Created 5 test jobs

...

==================================================
✓ ALL TESTS PASSED
==================================================
```

---

## Common Tasks

### Check Storage Statistics
```python
stats = storage.get_statistics()
print(f"Total jobs: {stats['total_jobs']}")
print(f"By source: {stats['jobs_by_source']}")
print(f"Errors: {stats['error_count']}")
```

### Export Jobs
```python
storage.export_to_json(
    'data/export.json',
    filters={"source": "indeed"}
)
print("✓ Exported to data/export.json")
```

### Clear All Jobs
```python
storage.clear_all_jobs()
print("✓ All jobs cleared")
```

### Delete Single Job
```python
jobs = storage.get_all_jobs()
storage.delete_job(jobs[0]['id'])
print("✓ Job deleted")
```

### View Recent Errors
```python
errors = storage.get_recent_errors(limit=5)
for error in errors:
    print(f"{error['timestamp']}: {error['error']}")
```

---

## API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/storage/jobs` | GET | List jobs |
| `/api/storage/jobs/<id>` | GET | Get job |
| `/api/storage/jobs/<id>` | DELETE | Delete job |
| `/api/storage/statistics` | GET | Get stats |
| `/api/storage/errors` | GET | Get errors |
| `/api/storage/export` | POST | Export jobs |

---

## Troubleshooting

### Issue: "Permission denied" error
**Solution:**
```bash
chmod 755 backend/data
```

### Issue: Jobs not appearing
**Solution:**
```python
# Check if they were skipped as duplicates
result = storage.save_jobs(jobs, source="test")
print(f"Skipped: {result['skipped']}")  # If > 0, they're duplicates
```

### Issue: Storage growing too large
**Solution:**
```python
# Clear old jobs
storage.clear_all_jobs()

# Or export and archive
storage.export_to_json('archive.json')
storage.clear_all_jobs()
```

---

## Next Steps

1. ✅ **Integration**: Use storage in your scraping pipeline
2. ✅ **Monitoring**: Check statistics regularly
3. ✅ **Automation**: Set up scheduled scraping with storage
4. ⏭️ **Phase 4**: Integrate with data processing module
5. ⏭️ **Phase 5**: Use stored data for job matching

---

## Complete Example

```python
"""
Complete example: Scrape, retry, save, and query
"""
from scrapers.indeed_scraper import IndeedScraper
from scrapers.retry_scraper import RetryScraper, RetryConfig
from storage_manager import JobStorageManager

# 1. Setup
scraper = IndeedScraper()
retry_config = RetryConfig(max_retries=3, initial_delay=1.0)
retry_scraper = RetryScraper(scraper, retry_config)
storage = JobStorageManager()

# 2. Scrape with retry
print("Scraping jobs...")
result = retry_scraper.scrape_jobs_with_retry(
    "Software Engineer",
    "New York",
    num_pages=2
)

if result["success"]:
    print(f"✓ Scraped {len(result['jobs'])} jobs")
    
    # 3. Save to storage
    save_result = storage.save_jobs(result["jobs"], source="indeed")
    print(f"✓ Saved {save_result['added']} new jobs")
    print(f"✓ Skipped {save_result['skipped']} duplicates")
    
    # 4. Query and display
    all_jobs = storage.get_all_jobs()
    print(f"\nTotal jobs in storage: {len(all_jobs)}")
    
    # Show first 3 jobs
    for i, job in enumerate(all_jobs[:3], 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Link: {job['link']}")
    
    # 5. Statistics
    stats = storage.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Total jobs: {stats['total_jobs']}")
    print(f"   By source: {stats['jobs_by_source']}")
else:
    print(f"✗ Scraping failed: {result.get('final_error')}")

print("\n✓ Done!")
```

---

## You're Ready! 🚀

The storage system is now:
- ✅ Initialized
- ✅ Tested
- ✅ Integrated with scrapers
- ✅ Ready for production use

**Time to complete: ~5 minutes**

---

*Quick Start Guide - Task 3.3*  
*Last Updated: November 10, 2025*
