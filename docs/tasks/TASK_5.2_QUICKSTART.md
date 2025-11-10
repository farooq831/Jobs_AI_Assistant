# Task 5.2: Job Scoring Algorithm - 5-Minute Quick Start

## Quick Setup (2 minutes)

### 1. Verify Dependencies
```bash
cd "d:\7 Semester\FYP_Jobs_Ai_Assistant\backend"

# Check if spaCy is installed
python -c "import spacy; print('spaCy OK')"

# If not installed:
pip install spacy
python -m spacy download en_core_web_sm
```

### 2. Run Tests
```bash
python test_scoring.py
```

Expected output: **36 tests passing ✅**

## Quick Test (3 minutes)

### Test 1: Score a Single Job

```python
# test_quick_score.py
from job_scorer import get_job_scorer

# Sample job
job = {
    'title': 'Python Developer',
    'description': 'Python, Django, AWS required',
    'location': 'Remote',
    'salary': {'min': 80000, 'max': 120000},
    'job_type': 'Remote'
}

# User preferences
user_prefs = {
    'location': 'New York',
    'salary_min': 70000,
    'salary_max': 110000,
    'job_titles': ['Python Developer'],
    'job_types': ['Remote']
}

# Score it
scorer = get_job_scorer()
result = scorer.score_job(job, user_prefs)

print(f"Score: {result['overall_score']}")
print(f"Highlight: {result['highlight']}")
print(f"Components: {result['component_scores']}")
```

Run:
```bash
python test_quick_score.py
```

Expected output:
```
Score: 75.5
Highlight: white
Components: {'keyword_match': 80.0, 'salary_match': 90.0, ...}
```

### Test 2: API Endpoint Test

```bash
# Start Flask server
python app.py
```

In another terminal:
```bash
# Test score-job endpoint
curl -X POST http://localhost:5000/api/score-job ^
  -H "Content-Type: application/json" ^
  -d "{\"job\": {\"title\": \"Python Developer\", \"description\": \"Python required\", \"location\": \"Remote\", \"salary\": {\"min\": 80000, \"max\": 100000}}, \"user_id\": 1}"
```

### Test 3: With Resume Keywords

```python
from job_scorer import get_job_scorer
from keyword_extractor import get_keyword_extractor

# Sample resume
resume_text = """
Senior Python Developer
Skills: Python, Django, Flask, AWS, Docker
5 years experience
"""

# Extract keywords
extractor = get_keyword_extractor()
resume_keywords = extractor.extract_resume_keywords(resume_text)

# Score job with resume
job = {
    'title': 'Senior Python Developer',
    'description': 'Need Python, Django, and AWS experience',
    'location': 'Remote',
    'salary': {'min': 90000, 'max': 130000}
}

user_prefs = {
    'location': 'Anywhere',
    'salary_min': 85000,
    'salary_max': 125000,
    'job_titles': ['Python Developer'],
    'job_types': ['Remote']
}

scorer = get_job_scorer()
result = scorer.score_job(job, user_prefs, resume_keywords)

print(f"With Resume Score: {result['overall_score']}")
print(f"Keyword Match: {result['component_scores']['keyword_match']}")
```

## API Quick Reference

### 1. Score Single Job
```bash
POST /api/score-job
Body: {"job": {...}, "user_id": 1, "resume_id": "optional"}
```

### 2. Score Multiple Jobs
```bash
POST /api/score-jobs
Body: {"jobs": [...], "user_id": 1}
```

### 3. Score All Stored Jobs
```bash
GET /api/score-stored-jobs/1?resume_id=abc&min_score=50
```

### 4. Get Thresholds
```bash
GET /api/score-thresholds
```

### 5. Update Weights
```bash
POST /api/update-weights
Body: {"weights": {"keyword_match": 0.5, "salary_match": 0.25, "location_match": 0.15, "job_type_match": 0.1}}
```

## Common Use Cases

### Case 1: Find Best Matches
```python
scorer = get_job_scorer()
scored_jobs = scorer.score_multiple_jobs(all_jobs, user_prefs, resume_keywords)

# Get top 10 matches
top_matches = scored_jobs[:10]

for job in top_matches:
    if job['score']['highlight'] == 'white':
        print(f"✅ {job['title']}: {job['score']['overall_score']}")
```

### Case 2: Filter by Score
```python
# Get only good matches (white)
good_matches = [j for j in scored_jobs if j['score']['highlight'] == 'white']

# Get jobs above 80 score
excellent = [j for j in scored_jobs if j['score']['overall_score'] >= 80]
```

### Case 3: Custom Weights
```python
# Prioritize location over salary
custom_weights = {
    'keyword_match': 0.50,
    'salary_match': 0.15,
    'location_match': 0.25,
    'job_type_match': 0.10
}

scorer = get_job_scorer(weights=custom_weights)
result = scorer.score_job(job, user_prefs)
```

### Case 4: Get Statistics
```python
scored_jobs = scorer.score_multiple_jobs(jobs, user_prefs)
stats = scorer.get_score_statistics(scored_jobs)

print(f"Average Score: {stats['average_score']}")
print(f"Good Matches: {stats['white_count']}")
print(f"Fair Matches: {stats['yellow_count']}")
print(f"Poor Matches: {stats['red_count']}")
```

## Troubleshooting

### Issue: spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### Issue: Weights don't sum to 1.0
```python
# ❌ Invalid
weights = {'keyword_match': 0.5, 'salary_match': 0.3}  # Only sums to 0.8

# ✅ Valid
weights = {
    'keyword_match': 0.5,
    'salary_match': 0.25,
    'location_match': 0.15,
    'job_type_match': 0.10
}
```

### Issue: Low keyword scores
Make sure to provide resume keywords for better matching:
```python
resume_keywords = extractor.extract_resume_keywords(resume_text)
result = scorer.score_job(job, user_prefs, resume_keywords)
```

## Next Steps

1. ✅ Read full documentation: `TASK_5.2_README.md`
2. ✅ Understand architecture: `TASK_5.2_ARCHITECTURE.md`
3. ✅ Review test cases: `test_scoring.py`
4. 🔄 Integrate with frontend for visualization
5. 🔄 Implement Task 5.3 for data model integration

## Performance Tips

1. **Reuse scorer instance**: Use `get_job_scorer()` singleton
2. **Batch scoring**: Use `score_multiple_jobs()` instead of loop
3. **Cache resume keywords**: Extract once, reuse for all jobs
4. **Filter before scoring**: Use Task 4.2 filters to reduce job count

## That's It!

You now have a working job scoring system. All 36 tests should pass, and you can score jobs via Python or REST API.

**Time to complete**: ~5 minutes ⏱️  
**Difficulty**: Easy 🟢  
**Status**: Ready to use ✅
