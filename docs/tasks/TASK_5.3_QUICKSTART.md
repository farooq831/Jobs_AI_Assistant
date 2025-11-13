# Task 5.3: Score Integration - Quick Start Guide

Get up and running with score integration in 5 minutes!

## Prerequisites

```bash
# Ensure backend is set up
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant/backend

# Dependencies should already be installed from previous tasks
# If not, install them:
pip3 install -r ../requirements.txt
```

## Step 1: Start the Backend (30 seconds)

```bash
cd backend
python3 app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

## Step 2: Test Score Integration (2 minutes)

### Quick Test Script

Save this as `quick_test_score.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Sample job
job = {
    "title": "Python Developer",
    "company": "Tech Corp",
    "location": "New York",
    "salary": "$120,000",
    "job_type": "Remote",
    "description": "Looking for Python expert with Flask",
    "link": "https://example.com/job1"
}

# User preferences
prefs = {
    "location": "New York",
    "salary_min": 100000,
    "salary_max": 150000,
    "job_titles": ["Python Developer"],
    "job_types": ["Remote", "Hybrid"]
}

# Score the job
print("1. Scoring a single job...")
response = requests.post(f"{BASE_URL}/api/score-job", json={
    "job": job,
    "user_preferences": prefs
})

result = response.json()
print(f"   ✓ Score: {result['score']['overall_score']}")
print(f"   ✓ Highlight: {result['score']['highlight']}")
print(f"   ✓ Component Scores: {result['score']['component_scores']}")

# Get thresholds
print("\n2. Getting score thresholds...")
response = requests.get(f"{BASE_URL}/api/score-thresholds")
result = response.json()
print(f"   ✓ Red threshold: < {result['thresholds']['red']}")
print(f"   ✓ Yellow threshold: < {result['thresholds']['yellow']}")

print("\n✅ Score integration is working!")
```

Run it:
```bash
python3 quick_test_score.py
```

## Step 3: Score Stored Jobs (1 minute)

### Save some jobs first

```python
import requests

# Save user details
response = requests.post('http://localhost:5000/api/user-details', json={
    "name": "Test User",
    "location": "New York",
    "salary_min": 100000,
    "salary_max": 150000,
    "job_titles": ["Python Developer"],
    "job_types": ["Remote"]
})

user_id = response.json()['user_id']

# Scrape some jobs (or use test data)
from storage_manager import JobStorageManager

storage = JobStorageManager()
test_jobs = [
    {
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "location": "New York",
        "salary": "$130,000",
        "job_type": "Remote",
        "description": "Python Flask development",
        "link": "https://example.com/job1"
    },
    {
        "title": "Junior Developer",
        "company": "Startup Inc",
        "location": "Austin",
        "salary": "$60,000",
        "job_type": "Onsite",
        "description": "Entry level position",
        "link": "https://example.com/job2"
    }
]

storage.save_jobs(test_jobs, source="test")
```

### Score them

```python
# Score all stored jobs for user
response = requests.post(f'http://localhost:5000/api/score-stored-jobs/{user_id}')

result = response.json()
print(f"Statistics:")
print(f"  Average Score: {result['statistics']['average_score']}")
print(f"  Red: {result['statistics']['red_count']}")
print(f"  Yellow: {result['statistics']['yellow_count']}")
print(f"  White: {result['statistics']['white_count']}")
```

## Step 4: Filter by Score (30 seconds)

```python
# Get high-scoring jobs (>= 70)
response = requests.get('http://localhost:5000/api/jobs-by-score?min_score=70')
high_score_jobs = response.json()['jobs']

print(f"Found {len(high_score_jobs)} high-scoring jobs")

# Get jobs by highlight
response = requests.get('http://localhost:5000/api/jobs-by-highlight/white')
white_jobs = response.json()['jobs']

print(f"Found {len(white_jobs)} excellent matches")
```

## Common Operations

### Score a Single Job
```bash
curl -X POST http://localhost:5000/api/score-job \
  -H "Content-Type: application/json" \
  -d '{
    "job": {...},
    "user_preferences": {...}
  }'
```

### Score Multiple Jobs
```bash
curl -X POST http://localhost:5000/api/score-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [...],
    "user_preferences": {...},
    "save_to_storage": true
  }'
```

### Get Score Thresholds
```bash
curl http://localhost:5000/api/score-thresholds
```

### Update Scoring Weights
```bash
curl -X POST http://localhost:5000/api/update-weights \
  -H "Content-Type: application/json" \
  -d '{
    "weights": {
      "keyword_match": 0.6,
      "salary_match": 0.2,
      "location_match": 0.1,
      "job_type_match": 0.1
    }
  }'
```

### Filter by Highlight
```bash
# Get red jobs (poor matches)
curl http://localhost:5000/api/jobs-by-highlight/red

# Get yellow jobs (fair matches)
curl http://localhost:5000/api/jobs-by-highlight/yellow

# Get white jobs (good matches)
curl http://localhost:5000/api/jobs-by-highlight/white
```

### Filter by Score Range
```bash
# Get jobs with score >= 80
curl http://localhost:5000/api/jobs-by-score?min_score=80

# Get jobs with score between 50 and 75
curl http://localhost:5000/api/jobs-by-score?min_score=50&max_score=75
```

## Running Tests

```bash
cd backend
python3 test_score_integration.py
```

Expected output:
```
test_bulk_update_with_partial_failures ... ok
test_data_cleaning_preserves_scores ... ok
test_end_to_end_scoring_workflow ... ok
test_filtering_preserves_scores ... ok
test_get_jobs_by_highlight ... ok
test_get_jobs_by_score_range ... ok
...
----------------------------------------------------------------------
Ran 18 tests in X.XXXs

OK
```

## Troubleshooting

### "Module not found" errors
```bash
# Install dependencies
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
pip3 install -r requirements.txt
```

### Backend not running
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process if needed
kill -9 <PID>

# Start backend
cd backend
python3 app.py
```

### Scores not saving
- Verify storage directory exists: `backend/data/`
- Check file permissions
- Review backend logs for errors

## Next Steps

1. **Read Full Documentation**: See `TASK_5.3_README.md`
2. **Understand Architecture**: See `TASK_5.3_ARCHITECTURE.md`
3. **View Completion Report**: See `TASK_5.3_COMPLETION.md`
4. **Check All Features**: See `TASK_5.3_CHECKLIST.md`

## Summary

You've now:
- ✅ Started the backend with score integration
- ✅ Scored jobs and retrieved scores
- ✅ Filtered jobs by score and highlight
- ✅ Updated scoring weights
- ✅ Understood the core API endpoints

**Total time: ~5 minutes**

For more detailed information, see the full README and architecture documentation!
