# Task 5.3: Score Integration into Data Model

## Overview

Task 5.3 integrates the job scoring system into the core data model, enabling persistent storage of match scores and highlight flags alongside job listings. This integration allows for efficient retrieval, filtering, and analysis of scored jobs.

## What Was Implemented

### 1. Storage Integration
- **Enhanced JobStorageManager** to handle score and highlight fields
- Added methods for updating scores on stored jobs
- Implemented filtering by highlight color and score range

### 2. API Endpoints
Seven new endpoints for comprehensive score management:

#### `/api/score-job` (POST)
Score a single job against user preferences.

**Request:**
```json
{
  "job": {
    "title": "Python Developer",
    "company": "Tech Corp",
    "location": "New York",
    "salary": "$120,000",
    "job_type": "Remote",
    "description": "Looking for Python expert...",
    "link": "https://example.com/job"
  },
  "user_preferences": {
    "location": "New York",
    "salary_min": 100000,
    "salary_max": 150000,
    "job_titles": ["Python Developer", "Software Engineer"],
    "job_types": ["Remote", "Hybrid"]
  },
  "resume_keywords": {
    "skills": ["python", "flask", "django"],
    "technologies": ["git", "docker"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "score": {
    "overall_score": 85.5,
    "highlight": "white",
    "component_scores": {
      "keyword_match": 90.0,
      "salary_match": 85.0,
      "location_match": 100.0,
      "job_type_match": 75.0
    },
    "weights_used": {
      "keyword_match": 0.5,
      "salary_match": 0.25,
      "location_match": 0.15,
      "job_type_match": 0.1
    }
  },
  "message": "Job scored successfully"
}
```

#### `/api/score-jobs` (POST)
Score multiple jobs at once.

**Request:**
```json
{
  "jobs": [...],  // Array of job objects
  "user_preferences": {...},
  "resume_keywords": {...},
  "save_to_storage": true  // Optional: automatically save scores
}
```

**Response:**
```json
{
  "success": true,
  "scored_jobs": [...],  // Jobs with score data added
  "storage_update": {
    "success": true,
    "updated": 5,
    "not_found": 0
  },
  "message": "Scored 5 jobs and updated storage"
}
```

#### `/api/score-stored-jobs/<user_id>` (POST)
Score all stored jobs for a specific user.

**Request:**
```json
{
  "filters": {
    "source": "indeed"  // Optional filters
  },
  "resume_id": "resume-123"  // Optional resume ID
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "user-456",
  "total_jobs": 10,
  "scored_jobs": [...],
  "storage_update": {
    "success": true,
    "updated": 10
  },
  "statistics": {
    "total_jobs": 10,
    "average_score": 68.5,
    "highest_score": 92.0,
    "lowest_score": 35.0,
    "red_count": 2,
    "yellow_count": 5,
    "white_count": 3
  },
  "message": "Scored 10 jobs for user user-456"
}
```

#### `/api/score-thresholds` (GET)
Get current scoring thresholds for color highlighting.

**Response:**
```json
{
  "success": true,
  "thresholds": {
    "red": 40,
    "yellow": 70,
    "white": 100
  },
  "description": {
    "red": "Score < 40% - Poor match",
    "yellow": "40% <= Score < 70% - Fair match",
    "white": "Score >= 70% - Good match"
  },
  "message": "Score thresholds retrieved successfully"
}
```

#### `/api/update-weights` (POST)
Update scoring weights dynamically.

**Request:**
```json
{
  "weights": {
    "keyword_match": 0.6,
    "salary_match": 0.2,
    "location_match": 0.1,
    "job_type_match": 0.1
  }
}
```

**Response:**
```json
{
  "success": true,
  "weights": {
    "keyword_match": 0.6,
    "salary_match": 0.2,
    "location_match": 0.1,
    "job_type_match": 0.1
  },
  "message": "Scoring weights updated successfully"
}
```

#### `/api/jobs-by-highlight/<highlight>` (GET)
Get all jobs with a specific highlight color (red, yellow, or white).

**Example:** `GET /api/jobs-by-highlight/white`

**Response:**
```json
{
  "success": true,
  "highlight": "white",
  "total_jobs": 5,
  "jobs": [...],
  "message": "Found 5 jobs with white highlight"
}
```

#### `/api/jobs-by-score` (GET)
Get jobs filtered by score range.

**Example:** `GET /api/jobs-by-score?min_score=70&max_score=90`

**Response:**
```json
{
  "success": true,
  "min_score": 70,
  "max_score": 90,
  "total_jobs": 8,
  "jobs": [...],
  "message": "Found 8 jobs in score range"
}
```

### 3. Storage Manager Enhancements

#### New Methods

**`update_job_score(job_id, score_data)`**
- Updates score for a single job
- Adds `scored_at` timestamp
- Returns success/failure status

**`update_jobs_scores(job_scores)`**
- Batch update scores for multiple jobs
- More efficient than individual updates
- Returns statistics on updates

**`get_jobs_by_highlight(highlight)`**
- Filter jobs by highlight color
- Supports 'red', 'yellow', 'white'
- Returns filtered job list

**`get_scored_jobs(min_score, max_score)`**
- Filter jobs by score range
- Optional min and max parameters
- Returns jobs within range

### 4. Data Structure

Score data is stored directly in job objects:

```json
{
  "id": "abc123",
  "title": "Python Developer",
  "company": "Tech Corp",
  "location": "New York",
  "salary": "$120,000",
  "job_type": "Remote",
  "description": "...",
  "link": "https://example.com/job",
  "source": "indeed",
  "scraped_at": "2025-11-12T10:30:00",
  "score": {
    "overall_score": 85.5,
    "highlight": "white",
    "component_scores": {
      "keyword_match": 90.0,
      "salary_match": 85.0,
      "location_match": 100.0,
      "job_type_match": 75.0
    },
    "weights_used": {
      "keyword_match": 0.5,
      "salary_match": 0.25,
      "location_match": 0.15,
      "job_type_match": 0.1
    }
  },
  "scored_at": "2025-11-12T10:31:00"
}
```

## Usage Examples

### Example 1: Score and Save a Single Job

```python
import requests

job = {
    "title": "Senior Python Developer",
    "company": "Tech Corp",
    "location": "New York",
    "salary": "$120,000 - $150,000",
    "job_type": "Remote",
    "description": "Looking for Python expert with Flask experience",
    "link": "https://example.com/job1"
}

user_prefs = {
    "location": "New York",
    "salary_min": 100000,
    "salary_max": 150000,
    "job_titles": ["Python Developer"],
    "job_types": ["Remote"]
}

response = requests.post('http://localhost:5000/api/score-job', json={
    "job": job,
    "user_preferences": user_prefs
})

result = response.json()
print(f"Score: {result['score']['overall_score']}")
print(f"Highlight: {result['score']['highlight']}")
```

### Example 2: Score All Jobs for a User

```python
response = requests.post(
    'http://localhost:5000/api/score-stored-jobs/user-123',
    json={"resume_id": "resume-456"}
)

result = response.json()
print(f"Statistics:")
print(f"  Average Score: {result['statistics']['average_score']}")
print(f"  Red: {result['statistics']['red_count']}")
print(f"  Yellow: {result['statistics']['yellow_count']}")
print(f"  White: {result['statistics']['white_count']}")
```

### Example 3: Get High-Scoring Jobs

```python
response = requests.get('http://localhost:5000/api/jobs-by-score?min_score=80')

result = response.json()
print(f"Found {result['total_jobs']} high-scoring jobs")
for job in result['jobs']:
    print(f"  - {job['title']} at {job['company']}: {job['score']['overall_score']}")
```

### Example 4: Filter by Highlight Color

```python
response = requests.get('http://localhost:5000/api/jobs-by-highlight/white')

result = response.json()
print(f"Found {result['total_jobs']} excellent matches (white)")
```

## Integration with Existing Modules

### With Task 5.1 (Keyword Extraction)
- Resume keywords from Task 5.1 are used in scoring
- Automatic keyword extraction available via resume_id

### With Task 5.2 (Scoring Algorithm)
- Uses JobScorer from Task 5.2
- Weights and thresholds from Task 5.2 configuration

### With Task 4.2 (Filtering)
- Filtered jobs can be scored
- Scores preserved during filtering operations

### With Task 3.3 (Storage)
- Builds on JobStorageManager from Task 3.3
- Adds score-specific storage methods

## Testing

Comprehensive test suite in `test_score_integration.py`:

```bash
cd backend
python3 test_score_integration.py
```

### Test Coverage
- ✅ Save jobs with scores (18 tests)
- ✅ Update single job score
- ✅ Batch update multiple scores
- ✅ Filter by highlight color
- ✅ Filter by score range
- ✅ Data cleaning preserves scores
- ✅ Filtering preserves scores
- ✅ End-to-end workflow
- ✅ Score statistics calculation
- ✅ Error handling

## Files Modified/Created

### Modified Files
1. **`backend/app.py`**
   - Added import for `get_job_scorer`
   - Added 7 new scoring endpoints

2. **`backend/storage_manager.py`**
   - Added `update_job_score()` method
   - Added `update_jobs_scores()` method
   - Added `get_jobs_by_highlight()` method
   - Added `get_scored_jobs()` method

### New Files
1. **`backend/test_score_integration.py`** (600+ lines)
   - Comprehensive test suite
   - 18 test cases
   - Integration and unit tests

2. **`docs/tasks/TASK_5.3_README.md`** (this file)
3. **`docs/tasks/TASK_5.3_QUICKSTART.md`**
4. **`docs/tasks/TASK_5.3_ARCHITECTURE.md`**
5. **`docs/tasks/TASK_5.3_COMPLETION.md`**
6. **`docs/tasks/TASK_5.3_CHECKLIST.md`**

## Benefits

1. **Persistent Scores**: Scores stored with jobs, no need to recalculate
2. **Efficient Filtering**: Filter by score or highlight color
3. **Statistics**: Track scoring metrics across job sets
4. **Flexible Scoring**: Update weights dynamically
5. **API Access**: RESTful endpoints for all operations
6. **Integration**: Works seamlessly with existing modules

## Next Steps

- **Task 6.1**: Use scores in resume optimization recommendations
- **Task 7.1**: Export jobs with color-coded highlights to Excel
- **Task 8.2**: Track application status with score information
- **Task 9.1**: Display scores in dashboard UI

## Conclusion

Task 5.3 successfully integrates the scoring system into the data model, providing a robust foundation for job matching, filtering, and analysis. The implementation is fully tested, documented, and ready for integration with the frontend and export modules.
