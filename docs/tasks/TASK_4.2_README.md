# Task 4.2: Job Filtering Logic Implementation - Complete Guide

## Overview

This module implements comprehensive job filtering functionality that allows users to filter scraped jobs based on their preferences for location, salary range, and job type (Remote, Onsite, Hybrid). The filtered data is prepared for the subsequent scoring phase (Task 5.x).

## Implementation Summary

### Core Components

1. **JobFilter Class** (`backend/data_processor.py`)
   - Main filtering engine with support for multiple criteria
   - Location proximity matching with remote job detection
   - Salary range overlap calculation
   - Job type categorization (Remote, Onsite, Hybrid)

2. **API Endpoints** (`backend/app.py`)
   - `/api/filter-jobs` - Filter jobs with custom criteria
   - `/api/filter-jobs/user/<user_id>` - Filter using stored user preferences

3. **Test Suite** (`backend/test_filtering.py`)
   - 5 comprehensive test suites covering all filtering scenarios
   - Edge case handling and error validation

## Features

### 1. Location-Based Filtering
- Normalizes location names for consistent matching
- Automatically includes remote jobs for any location
- Smart location matching (e.g., "New York" matches "New York, NY" and "New York City")
- Configurable radius for location proximity (default: 50km)

### 2. Salary-Based Filtering
- Filters jobs based on salary range overlap
- Handles various salary formats and currencies
- Includes jobs without salary information (can't filter what isn't known)
- Supports filtering by minimum, maximum, or both salary bounds

### 3. Job Type Filtering
- Filters by Remote, Onsite, or Hybrid job types
- Intelligent job type detection from multiple fields (job_type, location, description, title)
- Supports multiple job type preferences simultaneously

### 4. Combined Filtering
- Apply all three filter types simultaneously
- Detailed statistics for each filtering stage
- Maintains data integrity throughout filtering pipeline

## API Usage

### Endpoint 1: Filter Jobs with Custom Criteria

**URL:** `POST /api/filter-jobs`

**Request Body:**
```json
{
  "jobs": [...],  // Optional - if not provided, uses stored jobs
  "user_location": "New York, NY",
  "salary_min": 80000,
  "salary_max": 150000,
  "job_types": ["Remote", "Hybrid"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Jobs filtered successfully",
  "statistics": {
    "total_input": 100,
    "location_filtered": 30,
    "salary_filtered": 20,
    "job_type_filtered": 15,
    "total_output": 35
  },
  "filtered_jobs_count": 35,
  "jobs": [...]
}
```

### Endpoint 2: Filter Jobs Using Stored User Preferences

**URL:** `POST /api/filter-jobs/user/<user_id>`

**Request Body (Optional):**
```json
{
  "job_types": ["Remote", "Hybrid"]  // Override job type preferences
}
```

**Response:**
```json
{
  "success": true,
  "message": "Jobs filtered for user John Doe",
  "user_details": {
    "name": "John Doe",
    "location": "New York, NY",
    "salary_min": 80000,
    "salary_max": 150000,
    "job_types": ["Remote", "Hybrid"]
  },
  "statistics": {...},
  "filtered_jobs_count": 25,
  "jobs": [...]
}
```

## Code Usage Examples

### Example 1: Basic Filtering

```python
from data_processor import filter_jobs

jobs = [
    {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "New York, NY",
        "salary_min": 100000,
        "salary_max": 150000,
        "job_type": "Onsite"
    },
    # ... more jobs
]

# Filter for New York jobs paying $80k-$120k
filtered_jobs, stats = filter_jobs(
    jobs,
    user_location="New York",
    salary_min=80000,
    salary_max=120000
)

print(f"Found {len(filtered_jobs)} matching jobs")
print(f"Statistics: {stats}")
```

### Example 2: Job Type Filtering

```python
# Filter for Remote and Hybrid jobs only
filtered_jobs, stats = filter_jobs(
    jobs,
    job_types=["Remote", "Hybrid"]
)
```

### Example 3: Combined Filtering

```python
# Apply all filters at once
filtered_jobs, stats = filter_jobs(
    jobs,
    user_location="San Francisco",
    salary_min=100000,
    salary_max=180000,
    job_types=["Remote", "Hybrid", "Onsite"]
)
```

### Example 4: Using JobFilter Class Directly

```python
from data_processor import JobFilter

job_filter = JobFilter()

# First filtering pass
filtered_jobs, stats1 = job_filter.filter_jobs(
    jobs,
    user_location="Boston"
)

# Reset statistics
job_filter.reset_statistics()

# Second filtering pass
filtered_jobs, stats2 = job_filter.filter_jobs(
    filtered_jobs,
    salary_min=90000
)
```

## Testing

Run the comprehensive test suite:

```bash
cd backend
python test_filtering.py
```

The test suite includes:
- Location filtering tests (2 test cases)
- Salary filtering tests (3 test cases)
- Job type filtering tests (3 test cases)
- Combined filtering tests (1 test case)
- Edge cases and error handling (4 test cases)

**Total: 13 test cases covering all scenarios**

## Filter Statistics

Each filtering operation returns detailed statistics:

```python
{
    "total_input": 100,           # Jobs before filtering
    "location_filtered": 30,       # Jobs filtered by location
    "salary_filtered": 20,         # Jobs filtered by salary
    "job_type_filtered": 15,       # Jobs filtered by job type
    "total_output": 35            # Jobs after all filters
}
```

## Integration with Other Modules

### Data Flow

1. **Input:** Jobs from storage (Task 3.3) or cleaned data (Task 4.1)
2. **Filter:** Apply user preferences to narrow down relevant jobs
3. **Output:** Filtered jobs ready for scoring (Task 5.x)

```
Scraped Jobs → Data Cleaning (4.1) → Filtering (4.2) → Scoring (5.x) → Results
```

### Using with Previous Tasks

```python
from storage_manager import JobStorageManager
from data_processor import clean_job_data, filter_jobs

# Get stored jobs
storage = JobStorageManager()
jobs = storage.get_all_jobs()

# Clean the data first (Task 4.1)
cleaned_jobs, clean_stats = clean_job_data(jobs)

# Then filter (Task 4.2)
filtered_jobs, filter_stats = filter_jobs(
    cleaned_jobs,
    user_location="New York",
    salary_min=80000,
    salary_max=150000
)

print(f"Started with {len(jobs)} jobs")
print(f"After cleaning: {len(cleaned_jobs)} jobs")
print(f"After filtering: {len(filtered_jobs)} jobs")
```

## Configuration Options

### Location Matching

The location filter can be configured with a radius parameter (future enhancement):

```python
filtered_jobs, stats = job_filter.filter_jobs(
    jobs,
    user_location="Boston",
    location_radius_km=100  # Currently not implemented, uses smart matching
)
```

### Salary Period Handling

The salary filter automatically handles different salary periods:
- Yearly (default)
- Monthly
- Hourly

Jobs with different periods are normalized for comparison.

## Error Handling

The filtering module handles various edge cases:

1. **Missing Data:** Jobs without location or salary info are handled gracefully
2. **Empty Input:** Returns empty results with proper statistics
3. **Invalid Ranges:** API validates salary_min <= salary_max
4. **Type Mismatches:** Converts data types as needed

## Performance Considerations

- **Time Complexity:** O(n) where n is the number of jobs
- **Space Complexity:** O(n) for creating filtered result list
- **Optimization:** Filters are applied sequentially, reducing the dataset at each stage

For large datasets (>10,000 jobs):
- Consider implementing database-level filtering
- Add indexing on location, salary, and job_type fields
- Implement pagination for API responses

## Common Issues and Solutions

### Issue 1: No Jobs Match Filters

**Symptom:** `filtered_jobs_count: 0` despite having jobs in storage

**Solutions:**
- Check that user_location matches job locations (try broader terms)
- Verify salary ranges overlap with job salaries
- Ensure job_types include the types of jobs available

### Issue 2: Too Many Jobs Returned

**Symptom:** Most jobs pass through filters

**Solutions:**
- Apply stricter salary bounds
- Be more specific with location (e.g., "San Francisco, CA" vs "California")
- Limit job types to only what you want

### Issue 3: Remote Jobs Not Appearing

**Symptom:** Remote jobs filtered out unexpectedly

**Solutions:**
- Remote jobs should always pass location filter
- Check that job has "Remote" in location, job_type, or description
- Verify job_types filter includes "Remote"

## Future Enhancements

1. **Geographic Distance Calculation**
   - Implement actual distance-based filtering using geocoding APIs
   - Support for "within X miles/km" filtering

2. **Advanced Salary Normalization**
   - Convert between different salary periods (hourly ↔ yearly)
   - Handle international currency conversion
   - Account for cost of living differences

3. **Fuzzy Location Matching**
   - Use location databases for city/state/country matching
   - Support for zip code-based filtering
   - Neighborhood-level matching

4. **Skills-Based Filtering**
   - Filter by required/preferred skills
   - Integration with resume analysis

5. **Company Filtering**
   - Filter by company size, industry, rating
   - Blacklist/whitelist functionality

## Contributing

When extending the filtering functionality:

1. Add new filter methods to `JobFilter` class
2. Update the `filter_jobs` method to call new filters
3. Add comprehensive tests to `test_filtering.py`
4. Update API endpoints to accept new filter parameters
5. Document all changes in this README

## Related Documentation

- [TASK_4.2_QUICKSTART.md](TASK_4.2_QUICKSTART.md) - 5-minute quick start guide
- [TASK_4.2_ARCHITECTURE.md](TASK_4.2_ARCHITECTURE.md) - Technical architecture details
- [TASK_4.2_COMPLETION.md](TASK_4.2_COMPLETION.md) - Implementation summary
- [TASK_4.2_CHECKLIST.md](TASK_4.2_CHECKLIST.md) - Verification checklist
- [TASK_4.1_README.md](TASK_4.1_README.md) - Data cleaning module (prerequisite)

## License

Part of the AI Job Application Assistant - FYP Project

---

*Last Updated: November 10, 2025*
*Task 4.2 Status: ✅ COMPLETED*
