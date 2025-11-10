# Task 4.1: Data Cleaning - Technical Architecture

## System Overview

The Data Cleaning module is a critical component of the AI Job Application Assistant that ensures data quality by removing duplicates, filtering incomplete entries, and normalizing inconsistent data formats.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│  (Frontend, CLI, Tests, External APIs)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP/REST or Direct Python API
                     │
┌────────────────────┴────────────────────────────────────────┐
│                     Flask API Layer                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POST /api/clean-data                               │   │
│  │  GET  /api/clean-data/stats                         │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Function Calls
                     │
┌────────────────────┴────────────────────────────────────────┐
│              Data Processor Module                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  DataProcessor Class                                 │   │
│  │  ├─ clean_data()                                     │   │
│  │  ├─ _remove_duplicates()                            │   │
│  │  ├─ _remove_incomplete_entries()                    │   │
│  │  ├─ _normalize_locations()                          │   │
│  │  └─ _normalize_salaries()                           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Convenience Functions                               │   │
│  │  ├─ clean_job_data()                                │   │
│  │  ├─ normalize_location()                            │   │
│  │  └─ normalize_salary()                              │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Read/Write
                     │
┌────────────────────┴────────────────────────────────────────┐
│              Storage Manager                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  JobStorageManager                                   │   │
│  │  ├─ get_all_jobs()                                   │   │
│  │  ├─ add_job()                                        │   │
│  │  └─ clear_jobs()                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ File I/O
                     │
┌────────────────────┴────────────────────────────────────────┐
│              Data Storage (JSON Files)                       │
│  ├─ data/jobs.json                                          │
│  ├─ data/metadata.json                                      │
│  └─ data/scraping_errors.json                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. DataProcessor Class

**Purpose**: Core data cleaning engine

**Responsibilities**:
- Remove duplicate job entries
- Filter incomplete data
- Normalize location names
- Normalize salary information
- Track statistics

**Key Attributes**:
```python
LOCATION_MAPPINGS: Dict[str, str]  # Abbreviation → Full name
SALARY_PATTERNS: List[str]         # Regex patterns for salary parsing
REQUIRED_FIELDS: List[str]         # Mandatory job fields
stats: Dict[str, int]              # Cleaning statistics
```

**Design Patterns**:
- **Strategy Pattern**: Different normalization strategies for locations and salaries
- **Pipeline Pattern**: Sequential processing steps in clean_data()
- **Factory Pattern**: Convenience functions create processor instances

### 2. Deduplication System

**Algorithm**: Hash-based deduplication using MD5

**Process**:
```python
1. Generate signature: f"{title}|{company}|{location}".lower()
2. Compute hash: hashlib.md5(signature.encode()).hexdigest()
3. Track seen hashes in Set
4. Keep first occurrence, discard subsequent matches
```

**Complexity**:
- Time: O(n) where n = number of jobs
- Space: O(n) for hash storage

**Advantages**:
- Fast lookup (O(1) average)
- Case-insensitive matching
- Memory efficient (32-character hashes vs full objects)

### 3. Location Normalization

**Three-Phase Process**:

**Phase 1: Preprocessing**
```python
1. Convert to lowercase
2. Strip whitespace
3. Normalize internal spacing
```

**Phase 2: Mapping**
```python
1. Match abbreviations (NYC → new york)
2. Expand country codes (USA → united states)
3. Handle special cases (DC, UK, UAE)
```

**Phase 3: Formatting**
```python
1. Apply Title Case
2. Fix known uppercase abbreviations
3. Store original for reference
```

**Example Flow**:
```
"  NYC  " → "nyc" → "new york" → "New York"
```

### 4. Salary Normalization

**Multi-Pattern Parsing**:

**Pattern 1**: Standard format
```regex
\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)?
```
Matches: "$100,000 - $150,000", "$80,000/year"

**Pattern 2**: K-notation
```regex
(\d{1,3})k?\s*-\s*(\d{1,3})k
```
Matches: "100k-150k", "50k - 70k"

**Pattern 3**: Simple range
```regex
\$?(\d{1,3}(?:,\d{3})*)\s*-\s*\$?(\d{1,3}(?:,\d{3})*)
```
Matches: "100000-150000"

**Extraction Process**:
```python
1. Try each pattern in sequence
2. Extract min and max values
3. Handle k-notation (multiply by 1000)
4. Auto-scale small values
5. Detect currency symbols
6. Detect period (yearly/monthly/hourly)
7. Return structured dict or None
```

**Output Structure**:
```python
{
    'min': float,        # Minimum salary
    'max': float,        # Maximum salary
    'currency': str,     # USD, GBP, EUR, INR
    'period': str        # yearly, monthly, hourly
}
```

### 5. Incomplete Entry Filtering

**Validation Logic**:
```python
is_complete = all(
    job.get(field) and str(job.get(field)).strip()
    for field in REQUIRED_FIELDS
)
```

**Checks**:
1. Field exists in dictionary
2. Field value is not None
3. Field value is not empty string
4. Field value is not whitespace-only

**Required Fields**:
- `title`: Job title
- `company`: Company name
- `location`: Job location

### 6. Statistics Tracking

**Metrics Collected**:
```python
{
    'total_processed': int,      # Total jobs input
    'duplicates_removed': int,   # Duplicate count
    'incomplete_removed': int,   # Incomplete entries
    'locations_normalized': int, # Location changes
    'salaries_normalized': int,  # Salary parsing successes
    'errors': int                # Processing errors
}
```

**Usage**: Progress tracking, quality metrics, debugging

## Data Flow

### Cleaning Pipeline

```
Input Jobs (List[Dict])
         │
         ▼
┌────────────────────┐
│ Remove Duplicates  │ ──► Stats: duplicates_removed
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Remove Incomplete  │ ──► Stats: incomplete_removed
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Normalize Locations│ ──► Stats: locations_normalized
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Normalize Salaries │ ──► Stats: salaries_normalized
└────────┬───────────┘
         │
         ▼
Cleaned Jobs (List[Dict]) + Statistics (Dict)
```

### Job Transformation

**Before Cleaning**:
```python
{
    "title": "Software Engineer",
    "company": "Google",
    "location": "NYC",
    "salary": "$100k-$150k",
    "description": "Python developer"
}
```

**After Cleaning**:
```python
{
    "title": "Software Engineer",
    "company": "Google",
    "location": "New York",
    "original_location": "NYC",
    "salary": "$100k-$150k",
    "salary_min": 100000.0,
    "salary_max": 150000.0,
    "salary_currency": "USD",
    "salary_period": "yearly",
    "original_salary": "$100k-$150k",
    "description": "Python developer"
}
```

## API Integration

### REST Endpoints

**POST /api/clean-data**
```python
@app.route('/api/clean-data', methods=['POST'])
def clean_data():
    # 1. Get jobs (from request or storage)
    # 2. Call clean_job_data()
    # 3. Optionally save to storage
    # 4. Return cleaned jobs + stats
```

**GET /api/clean-data/stats**
```python
@app.route('/api/clean-data/stats', methods=['GET'])
def get_cleaning_stats():
    # 1. Load jobs from storage
    # 2. Analyze for potential issues
    # 3. Return statistics + recommendations
```

## Error Handling

### Strategy

1. **Graceful Degradation**: Continue processing even if individual items fail
2. **Detailed Logging**: Log warnings for debugging
3. **Safe Defaults**: Return None or original value if normalization fails
4. **Statistics Tracking**: Count errors without stopping execution

### Example

```python
try:
    normalized = self._normalize_single_salary(salary)
    if normalized:
        job['salary_min'] = normalized['min']
        # ... success
    else:
        logger.warning(f"Could not parse salary: {salary}")
        # Continue with next job
except Exception as e:
    logger.error(f"Error normalizing salary: {e}")
    self.stats['errors'] += 1
    # Continue processing
```

## Performance Optimization

### Techniques Used

1. **Hash-based Deduplication**: O(1) lookups vs O(n) comparisons
2. **Single Pass Processing**: Each step iterates once
3. **Lazy Evaluation**: Only normalize if needed
4. **Regex Pre-compilation**: Patterns compiled once (future improvement)
5. **In-place Updates**: Modify job dicts directly

### Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Remove Duplicates | O(n) | O(n) |
| Remove Incomplete | O(n) | O(1) |
| Normalize Locations | O(n × m) | O(1) |
| Normalize Salaries | O(n × p) | O(1) |
| **Total** | **O(n × max(m, p))** | **O(n)** |

Where:
- n = number of jobs
- m = number of location mappings
- p = number of salary patterns

For typical usage (m ≈ 20, p ≈ 3): **Effectively O(n)**

## Thread Safety

**Current Status**: Not thread-safe

**Considerations**:
- Shared stats dictionary can have race conditions
- Integration with storage_manager provides thread locks

**Future Enhancement**:
```python
from threading import Lock

class DataProcessor:
    def __init__(self):
        self.lock = Lock()
        self.stats = {...}
    
    def clean_data(self, jobs):
        with self.lock:
            # ... cleaning logic
```

## Testing Architecture

### Test Structure

```
test_data_cleaning.py
├── test_remove_duplicates()
├── test_remove_incomplete_entries()
├── test_normalize_locations()
├── test_normalize_salaries()
├── test_full_cleaning_pipeline()
├── test_convenience_functions()
└── test_edge_cases()
```

### Coverage

- **Unit Tests**: Individual methods
- **Integration Tests**: Full pipeline
- **Edge Cases**: None, empty, invalid data
- **Regression Tests**: Known failure cases

## Extensibility

### Adding Location Mappings

```python
DataProcessor.LOCATION_MAPPINGS['pdx'] = 'portland'
```

### Adding Salary Patterns

```python
DataProcessor.SALARY_PATTERNS.append(
    r'custom_pattern_here'
)
```

### Custom Required Fields

```python
DataProcessor.REQUIRED_FIELDS.extend(['job_type', 'salary'])
```

## Dependencies

### Core
- Python 3.7+
- hashlib (standard library)
- re (standard library)
- logging (standard library)

### Integration
- Flask (REST API)
- storage_manager (data persistence)

## Security Considerations

1. **Input Validation**: Check job structure before processing
2. **Regex DoS**: Use simple patterns to avoid catastrophic backtracking
3. **Memory Limits**: Consider batch processing for very large datasets
4. **Data Privacy**: Original data preserved but can be configured to discard

## Future Enhancements

### Phase 1
- Machine learning-based location matching
- Fuzzy company name matching
- Currency conversion API integration

### Phase 2
- Configurable normalization rules (JSON config)
- Batch processing with progress callbacks
- Distributed processing support

### Phase 3
- Real-time cleaning stream processing
- ML-based salary prediction for missing data
- Integration with job board APIs for validation

## Version History

- **1.0** (Nov 10, 2025): Initial implementation
  - Duplicate removal
  - Incomplete entry filtering
  - Location normalization
  - Salary normalization
  - REST API integration
  - Comprehensive test suite

---

**Architecture Status**: ✓ Production Ready  
**Version**: 1.0  
**Last Updated**: November 10, 2025
