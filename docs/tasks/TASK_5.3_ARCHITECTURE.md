# Task 5.3: Score Integration - Technical Architecture

## Overview

This document describes the technical architecture of the score integration system, detailing how job scores are stored, managed, and retrieved within the application's data model.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Frontend, API Clients, Tests)                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Endpoints (Flask)                       │
│  /api/score-job                                                  │
│  /api/score-jobs                                                 │
│  /api/score-stored-jobs/<user_id>                               │
│  /api/score-thresholds                                          │
│  /api/update-weights                                            │
│  /api/jobs-by-highlight/<color>                                 │
│  /api/jobs-by-score                                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                         │
│                                                                  │
│  ┌──────────────────┐    ┌─────────────────────┐              │
│  │   JobScorer      │◄───┤  KeywordExtractor   │              │
│  │  (Task 5.2)      │    │    (Task 5.1)       │              │
│  └────────┬─────────┘    └─────────────────────┘              │
│           │                                                     │
│           │ score_job()                                        │
│           │ score_jobs()                                       │
│           │ calculate_statistics()                             │
│           │                                                     │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              JobStorageManager (Enhanced)                 │  │
│  │                                                           │  │
│  │  Core Methods (Task 3.3):                               │  │
│  │    - save_jobs()                                         │  │
│  │    - get_all_jobs()                                      │  │
│  │    - get_job_by_id()                                     │  │
│  │                                                           │  │
│  │  New Score Methods (Task 5.3):                          │  │
│  │    - update_job_score()                                  │  │
│  │    - update_jobs_scores()                                │  │
│  │    - get_jobs_by_highlight()                            │  │
│  │    - get_scored_jobs()                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└───────────┬──────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Persistence Layer                             │
│                                                                  │
│  ┌──────────────────┐                                          │
│  │   jobs.json      │  Stores job data with scores             │
│  │                  │  {                                        │
│  │                  │    "jobs": [                              │
│  │                  │      {                                    │
│  │                  │        "id": "...",                       │
│  │                  │        "title": "...",                    │
│  │                  │        "score": {...},                    │
│  │                  │        "scored_at": "..."                 │
│  │                  │      }                                    │
│  │                  │    ]                                      │
│  │                  │  }                                        │
│  └──────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Scoring Workflow

```
User Request → API Endpoint → JobScorer
                                   ↓
                        Calculate Score Components
                                   ↓
                        ┌──────────────────────┐
                        │ Keyword Match (50%)  │
                        │ Salary Match (25%)   │
                        │ Location Match (15%) │
                        │ Job Type Match (10%) │
                        └──────────┬───────────┘
                                   ↓
                        Calculate Overall Score
                                   ↓
                        Determine Highlight Color
                                   ↓
                        Return Score Object
                                   ↓
                        (Optional) Save to Storage
                                   ↓
                        Return to Client
```

### 2. Storage Integration Workflow

```
Score Calculation → Score Object
                         ↓
                  Storage Manager
                         ↓
            ┌────────────┴────────────┐
            ▼                         ▼
    Single Update              Batch Update
    update_job_score()         update_jobs_scores()
            │                         │
            └────────────┬────────────┘
                         ▼
                Read jobs.json
                         ↓
                Find job(s) by ID
                         ▼
                Add/Update score field
                         ↓
                Add scored_at timestamp
                         ▼
                Write jobs.json
                         ▼
                Return success/stats
```

### 3. Retrieval Workflow

```
Client Request
      ↓
┌─────┴─────────────────────────┐
│                               │
▼                               ▼
By Highlight                   By Score Range
get_jobs_by_highlight()       get_scored_jobs()
      │                              │
      ▼                              ▼
Filter where                   Filter where
score.highlight == color       min_score <= score <= max_score
      │                              │
      └──────────┬───────────────────┘
                 ▼
          Return filtered jobs
```

## Data Structures

### Job Object (with Score)

```json
{
  "id": "abc123def456",
  "title": "Senior Python Developer",
  "company": "Tech Corporation",
  "location": "New York",
  "salary": "$120,000 - $150,000",
  "job_type": "Remote",
  "description": "Looking for experienced Python developer...",
  "link": "https://example.com/job/12345",
  "source": "indeed",
  "scraped_at": "2025-11-12T10:30:00.000Z",
  
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
    },
    "match_details": {
      "matched_keywords": ["python", "flask", "api"],
      "missing_keywords": ["kubernetes"],
      "salary_in_range": true,
      "location_match": "exact",
      "job_type_match": "exact"
    }
  },
  "scored_at": "2025-11-12T10:31:00.000Z"
}
```

### Score Object Schema

```python
{
    "overall_score": float,      # 0-100, weighted combination
    "highlight": str,             # "red" | "yellow" | "white"
    "component_scores": {
        "keyword_match": float,   # 0-100
        "salary_match": float,    # 0-100
        "location_match": float,  # 0-100
        "job_type_match": float   # 0-100
    },
    "weights_used": {
        "keyword_match": float,   # Weight applied
        "salary_match": float,
        "location_match": float,
        "job_type_match": float
    },
    "match_details": {            # Optional detailed breakdown
        "matched_keywords": List[str],
        "missing_keywords": List[str],
        "salary_in_range": bool,
        "location_match": str,
        "job_type_match": str
    }
}
```

## Component Integration

### Integration with Task 5.1 (Keyword Extraction)

```python
# Task 5.3 uses keyword extractor from Task 5.1
from keyword_extractor import get_keyword_extractor

extractor = get_keyword_extractor()

# Extract resume keywords
resume_keywords = extractor.extract_resume_keywords(resume_text)

# Use in scoring
score = scorer.score_job(job, user_prefs, resume_keywords)
```

### Integration with Task 5.2 (Scoring Algorithm)

```python
# Task 5.3 uses job scorer from Task 5.2
from job_scorer import get_job_scorer

scorer = get_job_scorer()

# Score job using algorithm from Task 5.2
score_result = scorer.score_job(job, user_preferences, resume_keywords)

# Save to storage (Task 5.3 addition)
storage.update_job_score(job['id'], score_result)
```

### Integration with Task 3.3 (Storage)

```python
# Task 5.3 extends storage manager from Task 3.3
from storage_manager import JobStorageManager

storage = JobStorageManager()

# Original Task 3.3 methods still work
storage.save_jobs(jobs, source="indeed")
all_jobs = storage.get_all_jobs()

# New Task 5.3 methods
storage.update_job_score(job_id, score_data)
storage.update_jobs_scores(job_scores_dict)
white_jobs = storage.get_jobs_by_highlight('white')
high_score_jobs = storage.get_scored_jobs(min_score=80)
```

### Integration with Task 4.2 (Filtering)

```python
# Filtering preserves score data
from data_processor import filter_jobs

# Jobs with scores
scored_jobs = [...]

# Filter - scores are preserved
filtered_jobs = filter_jobs(
    scored_jobs,
    location="New York",
    salary_min=100000,
    job_types=["Remote"]
)

# Scores still present in filtered_jobs
for job in filtered_jobs:
    print(f"{job['title']}: {job['score']['overall_score']}")
```

## API Endpoint Architecture

### Endpoint Design Pattern

All scoring endpoints follow this pattern:

```python
@app.route('/api/endpoint-name', methods=['POST'])
def endpoint_function():
    try:
        # 1. Extract and validate input
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # 2. Perform business logic
        scorer = get_job_scorer()
        result = scorer.score_job(...)
        
        # 3. (Optional) Update storage
        storage = JobStorageManager()
        storage.update_job_score(...)
        
        # 4. Return success response
        return jsonify({
            "success": True,
            "data": result,
            "message": "Success message"
        }), 200
        
    except Exception as e:
        # 5. Handle errors
        return error_response(str(e), 500)
```

### Error Handling

```python
# Standardized error response
def error_response(message, status_code):
    return jsonify({
        "success": False,
        "message": message
    }), status_code

# Applied in all endpoints
try:
    # ... endpoint logic ...
except ValueError as e:
    return error_response(f"Validation error: {str(e)}", 400)
except KeyError as e:
    return error_response(f"Missing field: {str(e)}", 400)
except Exception as e:
    return error_response(f"Internal error: {str(e)}", 500)
```

## Storage Architecture

### File Structure

```
backend/data/
├── jobs.json           # Jobs with scores
├── metadata.json       # Storage metadata
└── scraping_errors.json
```

### Atomic Updates

```python
def _write_json(self, filepath, data):
    """Atomic write using temp file"""
    # 1. Write to temporary file
    temp_filepath = f"{filepath}.tmp"
    with open(temp_filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    # 2. Atomic rename (overwrites original)
    os.replace(temp_filepath, filepath)
```

### Thread Safety

```python
class JobStorageManager:
    def __init__(self, storage_dir='data'):
        self.lock = Lock()  # Thread-safe operations
    
    def update_job_score(self, job_id, score_data):
        with self.lock:  # Acquire lock
            # ... update logic ...
            pass
        # Lock automatically released
```

## Performance Considerations

### Batch Operations

```python
# ❌ Inefficient: Multiple individual updates
for job_id, score in job_scores.items():
    storage.update_job_score(job_id, score)  # File I/O each time

# ✅ Efficient: Single batch update
storage.update_jobs_scores(job_scores)  # File I/O once
```

### Filtering Optimization

```python
# In-memory filtering for scored jobs
def get_jobs_by_highlight(self, highlight):
    all_jobs = self.get_all_jobs()  # Single read
    return [job for job in all_jobs 
            if job.get('score', {}).get('highlight') == highlight]
```

### Caching Strategy

```python
# Future enhancement: Cache frequently accessed data
_cache = {
    'all_jobs': None,
    'last_read': None
}

def get_all_jobs(self):
    # Check cache validity (e.g., 5-second TTL)
    if self._cache_valid():
        return _cache['all_jobs']
    
    # Read and update cache
    jobs = self._read_json(self.jobs_file)
    _cache['all_jobs'] = jobs
    _cache['last_read'] = time.time()
    return jobs
```

## Security Considerations

### Input Validation

```python
# Validate weights sum to 1.0
def _validate_weights(weights):
    total = sum(weights.values())
    if not (0.99 <= total <= 1.01):
        raise ValueError(f"Weights must sum to 1.0, got {total}")

# Validate highlight values
def get_jobs_by_highlight(self, highlight):
    if highlight not in ['red', 'yellow', 'white']:
        raise ValueError("Invalid highlight color")
```

### Data Integrity

```python
# Preserve original data when adding scores
def update_job_score(self, job_id, score_data):
    # Don't overwrite existing fields
    job['score'] = score_data
    job['scored_at'] = datetime.now().isoformat()
    # Other fields (title, company, etc.) unchanged
```

## Testing Architecture

```
test_score_integration.py
├── TestScoreIntegration
│   ├── Storage Integration Tests
│   │   ├── test_save_jobs_with_scores
│   │   ├── test_update_single_job_score
│   │   ├── test_update_multiple_job_scores
│   │   ├── test_get_jobs_by_highlight
│   │   └── test_get_jobs_by_score_range
│   ├── Data Processing Tests
│   │   ├── test_data_cleaning_preserves_scores
│   │   └── test_filtering_preserves_scores
│   ├── Integration Tests
│   │   ├── test_end_to_end_scoring_workflow
│   │   └── test_score_statistics_calculation
│   └── Error Handling Tests
│       ├── test_update_score_for_nonexistent_job
│       ├── test_get_jobs_by_invalid_highlight
│       └── test_bulk_update_with_partial_failures
└── TestScoreDataStructure
    ├── test_score_structure
    ├── test_highlight_values
    └── test_score_ranges
```

## Future Enhancements

### 1. Score History Tracking
```python
"score_history": [
    {"score": 85.5, "timestamp": "2025-11-12T10:31:00"},
    {"score": 82.0, "timestamp": "2025-11-10T15:20:00"}
]
```

### 2. Database Integration
```python
# Replace JSON with SQLAlchemy/PostgreSQL
class JobScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(64), db.ForeignKey('job.id'))
    overall_score = db.Column(db.Float)
    highlight = db.Column(db.String(10))
    scored_at = db.Column(db.DateTime)
```

### 3. Real-time Score Updates
```python
# WebSocket for live score updates
@socketio.on('score_job')
def handle_score_job(data):
    score = scorer.score_job(data['job'], data['prefs'])
    emit('score_updated', score)
```

## Conclusion

The score integration architecture provides a robust, scalable foundation for managing job match scores. It seamlessly integrates with existing modules while maintaining data integrity, performance, and extensibility.
