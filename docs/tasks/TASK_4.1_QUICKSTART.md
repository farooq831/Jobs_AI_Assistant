# Task 4.1: Data Cleaning - Quick Start Guide

Get the data cleaning module up and running in 5 minutes!

## Prerequisites

- Python 3.7 or higher
- Backend dependencies installed (`pip install -r requirements.txt`)
- Flask app running

## Quick Setup

### 1. Verify Installation

```bash
cd backend
python -c "from data_processor import DataProcessor; print('✓ Data processor ready')"
```

### 2. Run Tests

```bash
python test_data_cleaning.py
```

Expected output:
```
✓ ALL TESTS PASSED!
```

### 3. Start Flask Server

```bash
python app.py
```

Server should start on `http://localhost:5000`

## Basic Usage

### Option 1: Python API

Create a file `test_cleaning.py`:

```python
from data_processor import clean_job_data

# Sample dirty data
jobs = [
    {
        "title": "Software Engineer",
        "company": "Google",
        "location": "NYC",
        "salary": "$100k-$150k"
    },
    {
        "title": "software engineer",  # Duplicate
        "company": "google",
        "location": "new york city",
        "salary": "$100,000-$150,000"
    },
    {
        "title": "Data Scientist",
        "company": "Amazon",
        "location": "Seattle",
        "salary": "120k-160k"
    }
]

# Clean the data
cleaned_jobs, stats = clean_job_data(jobs)

print(f"Cleaned {len(cleaned_jobs)} jobs")
print(f"Removed {stats['duplicates_removed']} duplicates")
print(f"Normalized {stats['locations_normalized']} locations")
print(f"Normalized {stats['salaries_normalized']} salaries")

# Show cleaned jobs
for job in cleaned_jobs:
    print(f"\n{job['title']} at {job['company']}")
    print(f"  Location: {job['location']}")
    if 'salary_min' in job:
        print(f"  Salary: ${job['salary_min']:,.0f} - ${job['salary_max']:,.0f}")
```

Run it:
```bash
python test_cleaning.py
```

### Option 2: REST API

First, scrape some jobs:
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "software engineer",
    "location": "New York",
    "num_jobs": 10
  }'
```

Check cleaning stats:
```bash
curl http://localhost:5000/api/clean-data/stats
```

Clean and save:
```bash
curl -X POST http://localhost:5000/api/clean-data \
  -H "Content-Type: application/json" \
  -d '{"save": true}'
```

## Common Use Cases

### 1. Clean Stored Jobs

```bash
curl -X POST http://localhost:5000/api/clean-data -H "Content-Type: application/json" -d '{"save": true}'
```

### 2. Clean Specific Jobs

```python
from data_processor import DataProcessor

processor = DataProcessor()
jobs = [...]  # Your jobs here
cleaned_jobs, stats = processor.clean_data(jobs)
```

### 3. Just Normalize Location

```python
from data_processor import normalize_location

location = normalize_location("NYC")
print(location)  # "New York"
```

### 4. Just Normalize Salary

```python
from data_processor import normalize_salary

salary = normalize_salary("$100k-$150k")
print(salary)
# {'min': 100000, 'max': 150000, 'currency': 'USD', 'period': 'yearly'}
```

## Verify It's Working

### Test 1: Check Statistics

```bash
curl http://localhost:5000/api/clean-data/stats
```

Should return:
```json
{
  "success": true,
  "total_jobs": X,
  "potential_duplicates": X,
  "incomplete_entries": X,
  ...
}
```

### Test 2: Clean Sample Data

```bash
curl -X POST http://localhost:5000/api/clean-data \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {"title": "Engineer", "company": "Google", "location": "NYC", "salary": "$100k"},
      {"title": "engineer", "company": "google", "location": "nyc", "salary": "$100,000"}
    ]
  }'
```

Should return 1 cleaned job with normalized data.

## What Gets Cleaned?

### Duplicates
- Before: Two jobs with same title/company/location
- After: One unique job

### Incomplete Entries
- Before: Job missing title, company, or location
- After: Removed from results

### Locations
- Before: "NYC", "SF", "LA"
- After: "New York", "San Francisco", "Los Angeles"

### Salaries
- Before: "$100k-$150k", "100,000-150,000"
- After: `salary_min: 100000, salary_max: 150000`

## Quick API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/clean-data` | POST | Clean jobs (with optional save) |
| `/api/clean-data/stats` | GET | Get cleaning statistics |

## Troubleshooting

### Error: "Module not found"
```bash
cd backend
pip install -r requirements.txt
```

### Error: "No jobs to clean"
First scrape some jobs or provide jobs in request body.

### Tests Failing
```bash
# Check Python version
python --version  # Should be 3.7+

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. ✓ Basic cleaning works → Read TASK_4.1_README.md for advanced features
2. ✓ Tests pass → Check TASK_4.1_ARCHITECTURE.md for technical details
3. ✓ Integration needed → See API documentation in TASK_4.1_README.md

## Need Help?

- **Full documentation**: TASK_4.1_README.md
- **Architecture**: TASK_4.1_ARCHITECTURE.md
- **Test examples**: backend/test_data_cleaning.py

---

**Time to complete**: ~5 minutes  
**Status**: Ready to use  
**Version**: 1.0
