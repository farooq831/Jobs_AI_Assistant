# Task 4.2: Job Filtering Logic - Technical Architecture

## Architecture Overview

The job filtering system is designed as a modular, extensible component that processes job listings through multiple filter stages to match user preferences.

```
┌─────────────────────────────────────────────────────────────┐
│                    Job Filtering Pipeline                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Input Jobs    │
                    │  (List[Dict])   │
                    └────────┬────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   Location Filter      │
                │  - Normalize locations │
                │  - Match user location │
                │  - Include remote jobs │
                └───────────┬────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │   Salary Filter        │
                │  - Parse salary ranges │
                │  - Check overlap       │
                │  - Include unknown     │
                └───────────┬────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │   Job Type Filter      │
                │  - Detect job type     │
                │  - Match preferences   │
                │  - Smart categorization│
                └───────────┬────────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │  Filtered Jobs  │
                    │  + Statistics   │
                    └─────────────────┘
```

## Component Architecture

### 1. JobFilter Class

**File:** `backend/data_processor.py`

**Responsibilities:**
- Orchestrate filtering pipeline
- Maintain filter statistics
- Provide filter method interfaces

**Key Methods:**

```python
class JobFilter:
    def filter_jobs(jobs, user_location, salary_min, 
                   salary_max, job_types) -> (List[Dict], Dict)
    
    def _filter_by_location(jobs, user_location, radius_km) -> List[Dict]
    
    def _filter_by_salary(jobs, salary_min, salary_max) -> List[Dict]
    
    def _filter_by_job_type(jobs, preferred_types) -> List[Dict]
    
    def _is_remote_job(job) -> bool
    
    def get_filter_statistics() -> Dict
    
    def reset_statistics() -> None
```

**Design Patterns:**
- **Strategy Pattern:** Each filter type is a separate strategy
- **Pipeline Pattern:** Filters applied sequentially
- **Statistics Pattern:** Tracks metrics at each stage

### 2. Filter Stages

#### Stage 1: Location Filter

**Algorithm:**
```
FOR each job IN jobs:
    IF job is remote:
        INCLUDE job
    ELSE:
        normalized_job_loc = normalize(job.location)
        normalized_user_loc = normalize(user_location)
        
        IF normalized_user_loc IN normalized_job_loc OR
           normalized_job_loc IN normalized_user_loc:
            INCLUDE job
        ELSE:
            EXCLUDE job
```

**Remote Detection Logic:**
```python
def _is_remote_job(job):
    indicators = [
        'remote' in job_type,
        'remote' in location,
        'work from home' in description,
        'wfh' in description,
        location in ['remote', 'anywhere', 'virtual']
    ]
    return any(indicators)
```

**Location Normalization:**
- Lowercase conversion
- Whitespace normalization
- Abbreviation expansion (NY → New York)
- City/state separation

#### Stage 2: Salary Filter

**Algorithm:**
```
FOR each job IN jobs:
    IF job has NO salary info:
        INCLUDE job  // Can't filter unknown
    ELSE:
        job_min = job.salary_min
        job_max = job.salary_max
        
        // Check for overlap
        IF user_salary_min > job_max:
            EXCLUDE job  // User wants more than job offers
        ELSE IF user_salary_max < job_min:
            EXCLUDE job  // User wants less than job requires
        ELSE:
            INCLUDE job  // Ranges overlap
```

**Salary Range Overlap Logic:**
```
User Range:    [----user_min========user_max----]
Job Range:           [--job_min====job_max--]
                          ↑
                      Overlap → INCLUDE

User Range:    [----user_min====user_max----]
Job Range:                                      [--job_min====job_max--]
                                                No overlap → EXCLUDE
```

**Edge Cases:**
- Missing salary_min: Use only salary_max for comparison
- Missing salary_max: Use only salary_min for comparison
- Both missing: Include job (can't filter)
- Invalid values: Convert to float or include

#### Stage 3: Job Type Filter

**Algorithm:**
```
FOR each job IN jobs:
    job_type = detect_job_type(job)
    
    IF job_type MATCHES ANY preferred_type:
        INCLUDE job
    ELSE:
        EXCLUDE job
```

**Job Type Detection:**
```python
def detect_job_type(job):
    # Priority order:
    1. Explicit job_type field
    2. Remote detection (location, description, title)
    3. Hybrid keywords in description/title
    4. Default to Onsite
    
    if job.job_type:
        return job.job_type
    elif is_remote_job(job):
        return 'remote'
    elif 'hybrid' in job.description or 'hybrid' in job.title:
        return 'hybrid'
    else:
        return 'onsite'
```

### 3. API Layer

**File:** `backend/app.py`

**Endpoints:**

```python
# Endpoint 1: General filtering
POST /api/filter-jobs
Input: {
    jobs: List[Dict],  // Optional
    user_location: str,
    salary_min: float,
    salary_max: float,
    job_types: List[str]
}
Output: {
    success: bool,
    statistics: Dict,
    filtered_jobs_count: int,
    jobs: List[Dict]
}

# Endpoint 2: User-specific filtering
POST /api/filter-jobs/user/<user_id>
Input: {
    job_types: List[str]  // Optional override
}
Output: {
    success: bool,
    user_details: Dict,
    statistics: Dict,
    filtered_jobs_count: int,
    jobs: List[Dict]
}
```

**Request Flow:**
```
Client Request
      ↓
Validate Input
      ↓
Load Jobs (storage or request)
      ↓
Extract Filter Criteria
      ↓
Apply Filters (JobFilter)
      ↓
Format Response
      ↓
Send JSON Response
```

## Data Flow Architecture

```
┌─────────────────┐
│  Job Storage    │ ← Task 3.3 (Scraped Jobs)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Cleaning   │ ← Task 4.1 (Optional but recommended)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Job Filtering   │ ← Task 4.2 (THIS MODULE)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Job Scoring     │ ← Task 5.x (Next phase)
└─────────────────┘
```

## Filter Statistics Architecture

Statistics are tracked at each stage to provide insights:

```python
{
    'total_input': int,           # Jobs at start
    'location_filtered': int,     # Removed by location
    'salary_filtered': int,       # Removed by salary
    'job_type_filtered': int,     # Removed by job type
    'total_output': int          # Jobs remaining
}
```

**Statistics Flow:**
```
100 jobs → Location Filter → 70 jobs (30 filtered)
70 jobs  → Salary Filter   → 50 jobs (20 filtered)
50 jobs  → Job Type Filter → 35 jobs (15 filtered)

Final Statistics:
- total_input: 100
- location_filtered: 30
- salary_filtered: 20
- job_type_filtered: 15
- total_output: 35
```

## Performance Architecture

### Time Complexity

- **Location Filter:** O(n) - Single pass through jobs
- **Salary Filter:** O(n) - Single pass through jobs
- **Job Type Filter:** O(n) - Single pass through jobs
- **Overall:** O(n) - Sequential filters, no nested loops

### Space Complexity

- **Input Jobs:** O(n)
- **Filtered Results:** O(n) worst case (all jobs pass)
- **Statistics:** O(1) - Fixed size dictionary
- **Overall:** O(n)

### Optimization Strategies

1. **Early Termination:** Not applicable (must check all jobs)
2. **Sequential Filtering:** Each stage reduces dataset size
3. **In-Memory Processing:** Fast for datasets < 100K jobs
4. **Future:** Database-level filtering for larger datasets

### Scalability Considerations

**Current Implementation (In-Memory):**
- Suitable for: < 10,000 jobs
- Response time: < 1 second
- Memory usage: ~ job_count × 5KB

**Future Scaling (Database):**
```python
# Pseudo-code for database filtering
def filter_jobs_db(criteria):
    query = build_sql_query(criteria)
    # SELECT * FROM jobs WHERE
    #   location LIKE '%{user_location}%' AND
    #   salary_min <= {user_max} AND
    #   salary_max >= {user_min} AND
    #   job_type IN ({job_types})
    return execute_query(query)
```

## Error Handling Architecture

```python
try:
    # Validate input
    if salary_min > salary_max:
        raise ValueError("Invalid salary range")
    
    # Apply filters
    filtered_jobs = filter_jobs(...)
    
    # Return success
    return {"success": True, "jobs": filtered_jobs}
    
except ValueError as e:
    # Client error (400)
    return {"success": False, "message": str(e)}, 400
    
except Exception as e:
    # Server error (500)
    log_error(e)
    return {"success": False, "message": "Internal error"}, 500
```

**Error Handling Layers:**

1. **Input Validation:** Check data types, ranges, required fields
2. **Data Validation:** Handle missing/malformed job data
3. **Processing Errors:** Catch exceptions during filtering
4. **Response Errors:** Ensure valid JSON responses

## Testing Architecture

```
Test Suite (test_filtering.py)
│
├── Unit Tests
│   ├── test_location_filtering()
│   ├── test_salary_filtering()
│   └── test_job_type_filtering()
│
├── Integration Tests
│   └── test_combined_filtering()
│
└── Edge Case Tests
    └── test_edge_cases()
```

**Test Coverage:**
- Location matching: 2 test cases
- Salary range overlap: 3 test cases
- Job type detection: 3 test cases
- Combined filtering: 1 test case
- Edge cases: 4 test cases
- **Total: 13 test cases**

## Security Considerations

1. **Input Sanitization:**
   - Validate all user inputs
   - Prevent SQL injection (when using database)
   - Limit string lengths

2. **Data Privacy:**
   - User details stored in memory (not persistent)
   - No sensitive data in logs
   - Statistics don't expose individual jobs

3. **Rate Limiting:**
   - Future: Add rate limiting on API endpoints
   - Prevent abuse of filtering operations

## Integration Points

### Input Integrations

1. **Storage Manager (Task 3.3)**
   ```python
   storage = JobStorageManager()
   jobs = storage.get_all_jobs()
   ```

2. **Data Processor (Task 4.1)**
   ```python
   cleaned_jobs, stats = clean_job_data(jobs)
   ```

3. **User Details (Task 2.1)**
   ```python
   user = user_details_store[user_id]
   filter_jobs(jobs, user_location=user['location'])
   ```

### Output Integrations

1. **Job Scoring (Task 5.x - Future)**
   ```python
   filtered_jobs, stats = filter_jobs(...)
   scored_jobs = score_jobs(filtered_jobs, user_preferences)
   ```

2. **Export Module (Task 7.x - Future)**
   ```python
   filtered_jobs, stats = filter_jobs(...)
   export_to_excel(filtered_jobs, filename="filtered_jobs.xlsx")
   ```

## Configuration Architecture

**Current Configuration (Hardcoded):**
```python
LOCATION_RADIUS_KM = 50  # Default radius for location matching
REQUIRED_FIELDS = ['title', 'company', 'location']
```

**Future Configuration (Config File):**
```yaml
# config/filtering.yaml
filtering:
  location:
    radius_km: 50
    include_remote: true
    normalize: true
  
  salary:
    currency: USD
    period: yearly
    include_unknown: true
  
  job_type:
    auto_detect: true
    categories: [Remote, Onsite, Hybrid]
```

## Extension Points

### Adding New Filter Types

```python
class JobFilter:
    def _filter_by_skills(self, jobs, required_skills):
        """Filter by required skills"""
        filtered = []
        for job in jobs:
            job_skills = self._extract_skills(job)
            if any(skill in job_skills for skill in required_skills):
                filtered.append(job)
        return filtered
    
    def filter_jobs(self, jobs, ..., required_skills=None):
        # ... existing filters ...
        
        if required_skills:
            filtered_jobs = self._filter_by_skills(
                filtered_jobs, 
                required_skills
            )
```

### Adding Custom Validators

```python
def validate_filter_criteria(criteria):
    """Custom validation for filter criteria"""
    if 'salary_min' in criteria and 'salary_max' in criteria:
        if criteria['salary_min'] > criteria['salary_max']:
            raise ValueError("Invalid salary range")
    
    if 'job_types' in criteria:
        valid_types = ['Remote', 'Onsite', 'Hybrid']
        for jt in criteria['job_types']:
            if jt not in valid_types:
                raise ValueError(f"Invalid job type: {jt}")
```

## Design Decisions

### Why Sequential Filtering?

**Decision:** Apply filters sequentially (location → salary → job type)

**Rationale:**
- Reduces dataset size at each stage
- Easier to track statistics per filter
- Simplifies debugging
- No performance penalty vs parallel

**Alternative Considered:** Apply all filters simultaneously
- **Rejected:** Harder to track which filter excluded each job

### Why Include Jobs with Missing Data?

**Decision:** Include jobs without salary/location info

**Rationale:**
- User might still be interested
- Better to show and let user decide
- Avoids losing potentially good matches

**Alternative Considered:** Exclude incomplete jobs
- **Rejected:** Too restrictive, loses valuable opportunities

### Why Normalize Locations?

**Decision:** Normalize location names before comparison

**Rationale:**
- "NYC" should match "New York City"
- "SF" should match "San Francisco"
- Improves match quality

**Alternative Considered:** Exact string matching only
- **Rejected:** Misses too many valid matches

## Monitoring and Logging

**Logging Levels:**
```python
INFO: High-level operations
  - "Starting job filtering for 100 jobs"
  - "Job filtering complete. 35 jobs remaining"

DEBUG: Detailed operations
  - "Duplicate found: Engineer at TechCorp"
  - "Normalized location: 'NYC' -> 'New York'"

ERROR: Failures
  - "Error filtering jobs: Invalid salary range"
```

**Metrics to Track:**
- Total jobs filtered per request
- Average filter execution time
- Most common filter criteria
- Filter success/failure rates

---

*Last Updated: November 10, 2025*
*Architecture Version: 1.0*
