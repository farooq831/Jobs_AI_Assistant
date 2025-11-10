# Task 4.2: Job Filtering - 5-Minute Quick Start

Get filtering jobs in under 5 minutes!

## Prerequisites

- ✅ Task 4.1 completed (Data cleaning module)
- ✅ Backend running on `localhost:5000`
- ✅ Jobs stored from Task 3.x (scraping)

## Quick Setup (1 minute)

No additional setup needed! Filtering is built into the existing backend.

## Quick Test (2 minutes)

### Option 1: Test via API (Recommended)

```bash
# Start backend if not running
cd backend
python app.py
```

In another terminal, test the filtering:

```bash
# Test filtering with stored jobs
curl -X POST http://localhost:5000/api/filter-jobs \
  -H "Content-Type: application/json" \
  -d "{
    \"user_location\": \"New York\",
    \"salary_min\": 80000,
    \"salary_max\": 150000,
    \"job_types\": [\"Remote\", \"Hybrid\"]
  }"
```

### Option 2: Run Test Suite

```bash
cd backend
python test_filtering.py
```

Expected output:
```
============================================================
JOB FILTERING TEST SUITE
============================================================

=== Testing Location Filtering ===
✓ Test passed: New York filtering works correctly
✓ Test passed: San Francisco filtering works correctly

=== Testing Salary Filtering ===
✓ Test passed: Salary range filtering works correctly
...

🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉
```

## Quick Usage (2 minutes)

### Python Code

```python
from data_processor import filter_jobs
from storage_manager import JobStorageManager

# Get stored jobs
storage = JobStorageManager()
jobs = storage.get_all_jobs()

# Filter jobs
filtered_jobs, stats = filter_jobs(
    jobs,
    user_location="New York",
    salary_min=80000,
    salary_max=150000,
    job_types=["Remote", "Hybrid"]
)

print(f"Found {len(filtered_jobs)} matching jobs!")
print(f"Filter statistics: {stats}")

# Display results
for job in filtered_jobs[:5]:
    print(f"- {job['title']} at {job['company']}")
    print(f"  Location: {job['location']}")
    print(f"  Salary: ${job.get('salary_min', 'N/A'):,} - ${job.get('salary_max', 'N/A'):,}")
```

### API Request with Postman/Insomnia

**Method:** POST  
**URL:** `http://localhost:5000/api/filter-jobs`  
**Body (JSON):**
```json
{
  "user_location": "San Francisco",
  "salary_min": 100000,
  "salary_max": 180000,
  "job_types": ["Remote", "Onsite"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Jobs filtered successfully",
  "statistics": {
    "total_input": 150,
    "location_filtered": 50,
    "salary_filtered": 30,
    "job_type_filtered": 20,
    "total_output": 50
  },
  "filtered_jobs_count": 50,
  "jobs": [...]
}
```

## Quick Filter Guide

### Filter by Location Only
```python
filtered_jobs, stats = filter_jobs(jobs, user_location="Boston")
```

### Filter by Salary Only
```python
filtered_jobs, stats = filter_jobs(
    jobs,
    salary_min=90000,
    salary_max=140000
)
```

### Filter by Job Type Only
```python
filtered_jobs, stats = filter_jobs(
    jobs,
    job_types=["Remote"]
)
```

### Combine All Filters
```python
filtered_jobs, stats = filter_jobs(
    jobs,
    user_location="Seattle",
    salary_min=100000,
    salary_max=160000,
    job_types=["Remote", "Hybrid"]
)
```

## Quick API Test with cURL

### Test 1: Filter Stored Jobs
```bash
curl -X POST http://localhost:5000/api/filter-jobs \
  -H "Content-Type: application/json" \
  -d '{"user_location": "New York", "salary_min": 80000}'
```

### Test 2: Filter with User Preferences
```bash
# First, get user_id from /api/user-details
curl -X POST http://localhost:5000/api/filter-jobs/user/1 \
  -H "Content-Type: application/json" \
  -d '{"job_types": ["Remote"]}'
```

### Test 3: Filter Custom Job List
```bash
curl -X POST http://localhost:5000/api/filter-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {
        "title": "Software Engineer",
        "company": "TechCo",
        "location": "Remote",
        "salary_min": 100000,
        "salary_max": 150000,
        "job_type": "Remote"
      }
    ],
    "salary_min": 90000,
    "job_types": ["Remote"]
  }'
```

## Quick Troubleshooting

### No jobs returned?
- **Check:** User location spelling matches job locations
- **Try:** Broader location terms ("New York" instead of "New York, NY, 10001")
- **Verify:** Salary range overlaps with available jobs
- **Test:** Remove some filters to see which is too restrictive

### Too many jobs returned?
- **Narrow:** Add more specific location ("San Francisco, CA" not just "California")
- **Restrict:** Tighter salary bounds
- **Limit:** Reduce job_types list

### Remote jobs not showing?
- **Ensure:** Job has "Remote" in location, job_type, or description
- **Include:** "Remote" in job_types filter
- **Note:** Remote jobs match all locations automatically

## Quick Integration Example

```python
# Complete workflow: Scrape → Clean → Filter
from scrapers.indeed_scraper import IndeedScraper
from storage_manager import JobStorageManager
from data_processor import clean_job_data, filter_jobs

# 1. Scrape (or load from storage)
storage = JobStorageManager()
jobs = storage.get_all_jobs()

# 2. Clean
cleaned_jobs, clean_stats = clean_job_data(jobs)

# 3. Filter
filtered_jobs, filter_stats = filter_jobs(
    cleaned_jobs,
    user_location="Austin",
    salary_min=85000,
    job_types=["Remote", "Hybrid"]
)

# 4. Use results
print(f"Scraped: {len(jobs)}")
print(f"Cleaned: {len(cleaned_jobs)}")
print(f"Filtered: {len(filtered_jobs)}")
print(f"Ready for scoring: {len(filtered_jobs)} jobs")
```

## What's Next?

After filtering jobs, proceed to:
- **Task 5.1:** Keyword Extraction
- **Task 5.2:** Job Scoring Algorithm
- **Task 5.3:** Score Integration

## Need More Details?

- Full documentation: [TASK_4.2_README.md](TASK_4.2_README.md)
- Architecture: [TASK_4.2_ARCHITECTURE.md](TASK_4.2_ARCHITECTURE.md)
- Implementation details: [TASK_4.2_COMPLETION.md](TASK_4.2_COMPLETION.md)

---

⏱️ **You should now be filtering jobs in under 5 minutes!**

*Last Updated: November 10, 2025*
