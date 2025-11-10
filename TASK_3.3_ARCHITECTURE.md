# Task 3.3: Storage Architecture

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │   Scraping   │───────▶│   Storage    │                  │
│  │  Endpoints   │        │  Endpoints   │                  │
│  └──────────────┘        └──────────────┘                  │
│         │                        │                          │
│         ▼                        ▼                          │
│  ┌──────────────────────────────────────┐                  │
│  │      Job Storage Manager             │                  │
│  │  - Save/Retrieve Jobs                │                  │
│  │  - Deduplication                     │                  │
│  │  - Validation                        │                  │
│  │  - Statistics                        │                  │
│  └──────────────────────────────────────┘                  │
│                  │                                          │
└──────────────────┼──────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Persistent Storage │
         ├─────────────────────┤
         │  - jobs.json        │
         │  - metadata.json    │
         │  - errors.json      │
         └─────────────────────┘
```

---

## Component Architecture

### 1. Storage Manager (`storage_manager.py`)

```
JobStorageManager
├── Initialization
│   ├── Create storage directory
│   ├── Initialize JSON files
│   └── Setup thread lock
│
├── Core Operations
│   ├── save_jobs()
│   │   ├── Validate job data
│   │   ├── Check for duplicates
│   │   ├── Add metadata (id, source, timestamp)
│   │   └── Write to storage
│   │
│   ├── get_all_jobs()
│   │   ├── Read from storage
│   │   ├── Apply filters
│   │   └── Return results
│   │
│   └── delete_job()
│       ├── Find job by ID
│       ├── Remove from storage
│       └── Update metadata
│
├── Helper Methods
│   ├── _read_json()          # Retry logic for reads
│   ├── _write_json()         # Atomic writes
│   ├── _generate_job_hash()  # Duplicate detection
│   ├── _validate_job()       # Data validation
│   └── _update_metadata()    # Track operations
│
└── Utilities
    ├── get_statistics()      # Storage metrics
    ├── export_to_json()      # Export functionality
    └── get_recent_errors()   # Error tracking
```

### 2. Retry Scraper (`scrapers/retry_scraper.py`)

```
RetryScraper
├── Configuration
│   └── RetryConfig
│       ├── max_retries
│       ├── initial_delay
│       ├── max_delay
│       ├── exponential_base
│       └── retry_on_exceptions
│
├── Core Methods
│   ├── scrape_jobs_with_retry()
│   │   ├── Track attempt number
│   │   ├── Execute scraper
│   │   ├── Handle failures
│   │   ├── Apply exponential backoff
│   │   └── Record statistics
│   │
│   └── scrape_multiple_with_retry()
│       ├── Iterate job titles
│       ├── Scrape each with retry
│       └── Aggregate results
│
└── Statistics
    ├── get_attempt_statistics()
    └── clear_attempt_history()
```

---

## Data Flow

### Scraping to Storage Flow

```
1. Client Request
   │
   ▼
2. Flask Endpoint (/api/scrape-jobs)
   │
   ├─▶ Validate request data
   │
   ▼
3. Initialize Scrapers
   │
   ├─▶ IndeedScraper
   ├─▶ GlassdoorScraper
   │
   ▼
4. Execute Scraping
   │
   ├─▶ For each job title:
   │   ├─▶ Build search URL
   │   ├─▶ Make HTTP request
   │   ├─▶ Parse HTML
   │   └─▶ Extract job data
   │
   ▼
5. Aggregate Results
   │
   └─▶ all_jobs[] (list of job dicts)
       │
       ▼
6. Save to Memory Store
   │
   └─▶ scraped_jobs_store[scrape_id]
       │
       ▼
7. Save to Persistent Storage
   │
   └─▶ storage_manager.save_jobs()
       │
       ├─▶ Validate each job
       ├─▶ Check for duplicates (hash)
       ├─▶ Add metadata (id, source, timestamp)
       ├─▶ Write to jobs.json (atomic)
       └─▶ Update metadata.json
           │
           ▼
8. Return Response
   │
   └─▶ {
         "success": true,
         "total_jobs": 50,
         "storage_result": {
           "added": 45,
           "skipped": 5,
           "invalid": 0
         }
       }
```

### Retry Flow with Exponential Backoff

```
Attempt 1
│
├─▶ Execute scraper.scrape_jobs()
│
├─ Success? ──YES──▶ Return results
│
└─ NO (Exception)
    │
    ├─▶ Log error
    ├─▶ Calculate delay = initial_delay * (base ^ 0) = 1s
    ├─▶ Sleep(1s)
    │
    ▼
Attempt 2
│
├─▶ Execute scraper.scrape_jobs()
│
├─ Success? ──YES──▶ Return results
│
└─ NO (Exception)
    │
    ├─▶ Log error
    ├─▶ Calculate delay = initial_delay * (base ^ 1) = 2s
    ├─▶ Sleep(2s)
    │
    ▼
Attempt 3
│
├─▶ Execute scraper.scrape_jobs()
│
├─ Success? ──YES──▶ Return results
│
└─ NO (Exception)
    │
    ├─▶ Log error
    ├─▶ Calculate delay = initial_delay * (base ^ 2) = 4s
    ├─▶ Sleep(4s)
    │
    ▼
Attempt 4 (Final)
│
├─▶ Execute scraper.scrape_jobs()
│
├─ Success? ──YES──▶ Return results
│
└─ NO (Exception)
    │
    ├─▶ Log final error
    └─▶ Return failure result with all attempt data
```

---

## Thread Safety

### Lock-Based Concurrency Control

```python
class JobStorageManager:
    def __init__(self):
        self.lock = Lock()  # Thread lock for critical sections
    
    def save_jobs(self, jobs):
        with self.lock:  # Acquire lock
            # Critical section - only one thread at a time
            data = self._read_json(self.jobs_file)
            # ... process data ...
            self._write_json(self.jobs_file, data)
        # Lock automatically released
```

**Benefits:**
- Prevents race conditions
- Ensures data consistency
- Supports concurrent API requests

---

## File I/O Architecture

### Atomic Write Pattern

```python
def _write_json(self, filepath, data):
    # Step 1: Write to temporary file
    temp_filepath = f"{filepath}.tmp"
    with open(temp_filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Step 2: Atomic rename (OS-level operation)
    os.replace(temp_filepath, filepath)
    
    # Benefits:
    # - No partial writes
    # - No corruption on crash
    # - Other processes see complete file or old file
```

### Retry Pattern for I/O

```python
def _read_json(self, filepath, max_retries=3):
    for attempt in range(max_retries):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            if attempt < max_retries - 1:
                delay = 0.5 * (attempt + 1)  # Exponential backoff
                time.sleep(delay)
            else:
                # Log error and return None
                logger.error(f"Failed after {max_retries} attempts")
                return None
```

---

## Deduplication Strategy

### Hash-Based Approach

```
Job Data
│
├─▶ Primary: Use job URL
│   └─▶ hash(job['link'])
│
└─▶ Fallback: Use composite key
    └─▶ hash(title + "|" + company + "|" + location)
    
Hash Function: MD5 (fast, sufficient for deduplication)
Result: 32-character hexadecimal string

Storage:
{
  "id": "abc123...",  # MD5 hash
  "title": "...",
  "link": "..."
}

Deduplication Check:
1. Calculate hash of new job
2. Check if hash exists in existing job set
3. Skip if duplicate, add if unique
```

---

## Error Handling Architecture

### Three-Layer Error Handling

```
Layer 1: I/O Operations
├─▶ Retry with exponential backoff
├─▶ Log to errors.json
└─▶ Return None on total failure

Layer 2: Scraping Operations  
├─▶ Try-catch per scraper
├─▶ Continue with other scrapers on failure
├─▶ Record failure in scraping_results
└─▶ Return partial results

Layer 3: API Endpoints
├─▶ Validate input data
├─▶ Handle exceptions from storage/scrapers
├─▶ Return appropriate HTTP status
└─▶ Include error message in response
```

### Error Logging

```json
{
  "errors": [
    {
      "timestamp": "2025-11-10T12:34:56",
      "operation": "save_jobs",
      "error": "Permission denied: /data/jobs.json"
    }
  ]
}
```

**Features:**
- Circular buffer (last 100 errors)
- Timestamped entries
- Operation context
- Retrievable via API

---

## Statistics Architecture

### Metrics Collected

```
Metadata (metadata.json):
├─▶ created_at: ISO timestamp
├─▶ last_updated: ISO timestamp
├─▶ total_scrapes: count
├─▶ successful_scrapes: count
└─▶ failed_scrapes: count

Job Statistics:
├─▶ total_jobs: int
├─▶ jobs_by_source: {source: count}
├─▶ storage_size_bytes: int
└─▶ error_count: int

Retry Statistics:
├─▶ total_attempts: int
├─▶ successful: int
├─▶ failed: int
├─▶ success_rate: float (%)
├─▶ average_retries: float
└─▶ average_time: float (seconds)
```

---

## API Architecture

### RESTful Design

```
Resource: Jobs
├─▶ GET    /api/storage/jobs           # List all
├─▶ GET    /api/storage/jobs/<id>      # Get one
├─▶ DELETE /api/storage/jobs/<id>      # Delete one
└─▶ DELETE /api/storage/jobs           # Delete all

Resource: Statistics
└─▶ GET    /api/storage/statistics     # Get metrics

Resource: Errors
└─▶ GET    /api/storage/errors         # Get error log

Action: Export
└─▶ POST   /api/storage/export         # Export jobs
```

### Response Format

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "error": null
}
```

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Save jobs | O(n*m) | n=new jobs, m=existing (hash check) |
| Get all jobs | O(n) | n=total jobs |
| Get by ID | O(n) | Linear search |
| Delete by ID | O(n) | Linear search + filter |
| Statistics | O(n) | Iterate all jobs |

### Space Complexity

| Component | Space | Notes |
|-----------|-------|-------|
| jobs.json | ~500B/job | Depends on description length |
| metadata.json | ~200B | Fixed size |
| errors.json | ~20KB | Max 100 errors * ~200B |
| In-memory | ~1KB/job | Python objects |

### Optimization Opportunities

1. **Indexing**: Add in-memory index for ID lookups (O(1))
2. **Pagination**: Implement lazy loading for large datasets
3. **Compression**: Gzip storage files for large datasets
4. **Caching**: Cache frequently accessed jobs
5. **Database**: Migrate to SQL for better query performance

---

## Security Considerations

### File Security
- Storage directory permissions (755)
- Input validation on file paths
- Prevent directory traversal attacks
- Sanitize filenames

### Data Validation
- Required field checks
- Type validation
- Length limits
- SQL injection prevention (if migrating to DB)

### API Security
- Rate limiting (future)
- Authentication (future)
- Input sanitization
- Error message sanitization

---

## Scalability

### Current Limitations
- Single-file storage (contention on writes)
- Linear search for queries
- No distributed support
- Memory-resident job lists

### Scaling Strategies

**Horizontal Scaling:**
- Shard jobs by source
- Multiple storage instances
- Load balancer for API

**Vertical Scaling:**
- Migrate to database (PostgreSQL)
- Add indexing
- Implement caching layer
- Use connection pooling

**Recommended Database Schema:**
```sql
CREATE TABLE jobs (
    id VARCHAR(32) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    link TEXT NOT NULL,
    description TEXT,
    job_type VARCHAR(50),
    salary_min INTEGER,
    salary_max INTEGER,
    source VARCHAR(50),
    scraped_at TIMESTAMP,
    INDEX idx_source (source),
    INDEX idx_location (location),
    INDEX idx_scraped_at (scraped_at)
);
```

---

## Monitoring & Observability

### Key Metrics to Track

1. **Storage Metrics**
   - Total jobs stored
   - Growth rate
   - Storage size
   - Duplicate rate

2. **Performance Metrics**
   - Average save time
   - Average retrieval time
   - API response times
   - Retry rates

3. **Error Metrics**
   - Error frequency
   - Error types
   - Failed scrape rate
   - Storage failures

### Logging Strategy

```python
import logging

logger = logging.getLogger(__name__)

# Info: Normal operations
logger.info(f"Saved {count} jobs")

# Warning: Recoverable issues
logger.warning(f"Duplicate job skipped: {job_id}")

# Error: Failures
logger.error(f"Failed to write: {error}")
```

---

## Future Architecture

### Microservices Approach

```
┌─────────────────┐
│   API Gateway   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Scraper│ │Storage│
│Service│ │Service│
└───┬───┘ └──┬────┘
    │        │
    └───┬────┘
        │
    ┌───▼───┐
    │Message│
    │ Queue │
    └───┬───┘
        │
    ┌───▼────┐
    │Database│
    └────────┘
```

---

*Architecture Documentation - Task 3.3*  
*Last Updated: November 10, 2025*
