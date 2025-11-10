# Task 4.1: Data Cleaning - Complete Documentation

## Overview

Task 4.1 implements comprehensive data cleaning and normalization for scraped job data. This module removes duplicates, filters out incomplete entries, and normalizes location names and salary information to ensure high-quality, consistent data for job matching.

## Features Implemented

### 1. Duplicate Removal
- **Hash-based deduplication**: Uses MD5 hashing of title, company, and location
- **Case-insensitive matching**: "Google" and "google" are treated as the same
- **Preserves first occurrence**: Keeps the first unique job entry encountered

### 2. Incomplete Entry Filtering
- **Required fields validation**: Ensures title, company, and location are present
- **Empty string detection**: Removes entries with whitespace-only fields
- **Detailed logging**: Tracks which fields are missing for debugging

### 3. Location Normalization
- **Common abbreviations**: NYC → New York, SF → San Francisco, LA → Los Angeles
- **Country codes**: USA → United States, UK → United Kingdom, UAE → United Arab Emirates
- **Whitespace cleanup**: Removes extra spaces and standardizes formatting
- **Title case conversion**: Ensures consistent capitalization
- **Original preservation**: Stores original location for reference

### 4. Salary Normalization
- **Multiple format support**: 
  - "$100,000 - $150,000"
  - "$50k-$70k"
  - "100k - 120k"
  - "$80,000/year"
  - "60-80k"
- **Currency detection**: USD ($), GBP (£), EUR (€), INR (₹)
- **Period detection**: yearly, monthly, hourly
- **Structured output**: Separate min/max values with currency and period
- **Original preservation**: Keeps original salary string for reference

## Project Structure

```
backend/
├── data_processor.py          # Main data cleaning module
├── app.py                     # Updated with cleaning endpoints
├── test_data_cleaning.py      # Comprehensive test suite
└── storage_manager.py         # Storage integration
```

## API Endpoints

### POST `/api/clean-data`

Clean and normalize job data.

**Request Body:**
```json
{
  "jobs": [...],    // Optional: jobs to clean (uses stored jobs if omitted)
  "save": true      // Optional: save cleaned data back to storage
}
```

**Response:**
```json
{
  "success": true,
  "message": "Data cleaning completed successfully",
  "statistics": {
    "total_processed": 100,
    "duplicates_removed": 15,
    "incomplete_removed": 8,
    "locations_normalized": 45,
    "salaries_normalized": 62,
    "errors": 0
  },
  "cleaned_jobs_count": 77,
  "jobs": [...]
}
```

### GET `/api/clean-data/stats`

Get statistics about stored jobs and potential cleaning improvements.

**Response:**
```json
{
  "success": true,
  "total_jobs": 100,
  "potential_duplicates": 15,
  "incomplete_entries": 8,
  "unnormalized_locations": 45,
  "unnormalized_salaries": 62,
  "recommendation": "Run /api/clean-data with save=true to clean the data"
}
```

## Usage Examples

### Python API

```python
from data_processor import DataProcessor, clean_job_data

# Initialize processor
processor = DataProcessor()

# Clean job data
jobs = [
    {
        "title": "Software Engineer",
        "company": "Google",
        "location": "NYC",
        "salary": "$100k-$150k"
    },
    # ... more jobs
]

cleaned_jobs, stats = clean_job_data(jobs)

print(f"Cleaned {len(cleaned_jobs)} jobs")
print(f"Removed {stats['duplicates_removed']} duplicates")
print(f"Removed {stats['incomplete_removed']} incomplete entries")
```

### Convenience Functions

```python
from data_processor import normalize_location, normalize_salary

# Normalize a location
location = normalize_location("NYC")
print(location)  # "New York"

# Normalize a salary
salary = normalize_salary("$100k-$150k")
print(salary)
# {'min': 100000, 'max': 150000, 'currency': 'USD', 'period': 'yearly'}
```

### REST API Usage

```bash
# Clean stored jobs and save
curl -X POST http://localhost:5000/api/clean-data \
  -H "Content-Type: application/json" \
  -d '{"save": true}'

# Clean specific jobs without saving
curl -X POST http://localhost:5000/api/clean-data \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {"title": "Engineer", "company": "Google", "location": "NYC"}
    ]
  }'

# Get cleaning statistics
curl http://localhost:5000/api/clean-data/stats
```

## Data Processor Class

### Main Methods

#### `clean_data(jobs: List[Dict]) -> Tuple[List[Dict], Dict]`
Main cleaning pipeline that applies all cleaning steps.

**Parameters:**
- `jobs`: List of job dictionaries to clean

**Returns:**
- Tuple of (cleaned_jobs, statistics_dict)

#### `_remove_duplicates(jobs: List[Dict]) -> List[Dict]`
Removes duplicate job entries based on title, company, and location.

#### `_remove_incomplete_entries(jobs: List[Dict]) -> List[Dict]`
Removes jobs missing required fields (title, company, location).

#### `_normalize_locations(jobs: List[Dict]) -> List[Dict]`
Normalizes location names to standard formats.

#### `_normalize_salaries(jobs: List[Dict]) -> List[Dict]`
Parses and normalizes salary information.

## Testing

### Run All Tests

```bash
cd backend
python test_data_cleaning.py
```

### Test Coverage

The test suite includes:
1. ✓ Duplicate removal tests
2. ✓ Incomplete entry removal tests
3. ✓ Location normalization tests
4. ✓ Salary normalization tests
5. ✓ Full cleaning pipeline test
6. ✓ Convenience function tests
7. ✓ Edge case and error handling tests

### Expected Output

```
======================================================================
 DATA CLEANING MODULE TEST SUITE
======================================================================

============================================================
TEST: Remove Duplicates
============================================================
Original jobs: 4
Unique jobs: 2
Duplicates removed: 2
✓ Test passed: Duplicates removed correctly

[... more tests ...]

======================================================================
 TEST SUMMARY
======================================================================
Total tests: 7
Passed: 7
Failed: 0

✓ ALL TESTS PASSED!
```

## Configuration

### Location Mappings

Customize location normalization in `DataProcessor.LOCATION_MAPPINGS`:

```python
LOCATION_MAPPINGS = {
    'ny': 'new york',
    'nyc': 'new york',
    'sf': 'san francisco',
    # Add more mappings...
}
```

### Required Fields

Customize required fields in `DataProcessor.REQUIRED_FIELDS`:

```python
REQUIRED_FIELDS = ['title', 'company', 'location']
# Add more required fields as needed
```

### Salary Patterns

Add custom salary regex patterns in `DataProcessor.SALARY_PATTERNS`:

```python
SALARY_PATTERNS = [
    r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)?',
    # Add more patterns...
]
```

## Integration with Storage Manager

The data processor integrates seamlessly with the storage manager:

```python
from storage_manager import JobStorageManager
from data_processor import clean_job_data

# Load jobs from storage
storage = JobStorageManager()
jobs = storage.get_all_jobs()

# Clean the data
cleaned_jobs, stats = clean_job_data(jobs)

# Save back to storage
storage.clear_jobs()
for job in cleaned_jobs:
    storage.add_job(job)
```

## Statistics Tracking

The processor tracks detailed statistics:

```python
{
    'total_processed': 100,      # Total jobs processed
    'duplicates_removed': 15,     # Number of duplicates removed
    'incomplete_removed': 8,      # Incomplete entries removed
    'locations_normalized': 45,   # Locations normalized
    'salaries_normalized': 62,    # Salaries normalized
    'errors': 0                   # Errors encountered
}
```

## Error Handling

- **Graceful degradation**: Continues processing even if individual items fail
- **Detailed logging**: Logs warnings for unparseable data
- **Statistics tracking**: Counts errors without stopping execution
- **Safe defaults**: Returns None or original value if normalization fails

## Performance Considerations

- **O(n) complexity**: Linear time processing for most operations
- **Hash-based deduplication**: O(n) with O(n) space for hash storage
- **Regex compilation**: Patterns compiled once and reused
- **Thread-safe**: Can be used with storage manager's thread locks

## Future Enhancements

Potential improvements for future versions:
1. Machine learning-based location matching
2. Fuzzy matching for company names
3. Currency conversion support
4. Configurable normalization rules via JSON
5. Batch processing for large datasets
6. More sophisticated salary parsing with ML
7. Integration with external location APIs

## Troubleshooting

### Common Issues

1. **Salaries not parsing**
   - Check salary format matches supported patterns
   - Add custom patterns to `SALARY_PATTERNS`
   - Check logs for parsing errors

2. **Locations not normalizing**
   - Add custom mappings to `LOCATION_MAPPINGS`
   - Check for special characters or formatting

3. **Too many duplicates removed**
   - Review hash generation logic
   - Check if case sensitivity is desired
   - Adjust duplicate detection criteria

## Dependencies

- Python 3.7+
- Standard library only (no external dependencies for core functionality)
- Integration requires: Flask, storage_manager

## License

Part of the AI Job Application Assistant project.

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Review test cases for usage examples
3. Refer to TASK_4.1_ARCHITECTURE.md for technical details
4. Consult TASK_4.1_QUICKSTART.md for quick setup

---

**Status**: ✓ Complete and Tested  
**Version**: 1.0  
**Date**: November 10, 2025
