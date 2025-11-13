# Task 7.3: Excel Upload for Status Tracking - Technical Architecture

## System Overview

The Excel Upload system provides a robust mechanism for tracking job application statuses through Excel file uploads. It integrates parsing, validation, and storage management into a cohesive workflow.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend / Client                        │
│  - Upload Excel files                                            │
│  - Display validation results                                    │
│  - Show status summaries                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Flask API Layer (app.py)                   │
│                                                                   │
│  Endpoints:                                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ POST /api/upload/excel                                    │  │
│  │ POST /api/upload/excel/validate                           │  │
│  │ POST /api/upload/excel/apply-updates                      │  │
│  │ PUT  /api/jobs/status/<job_id>                            │  │
│  │ GET  /api/jobs/status?status=<status>                     │  │
│  │ GET  /api/jobs/status/summary                             │  │
│  │ PUT  /api/jobs/batch-status                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────┬──────────────────────────┬─────────────────────┘
                 │                          │
                 ▼                          ▼
┌────────────────────────────┐  ┌──────────────────────────────┐
│   ExcelUploader Module     │  │  JobStorageManager Module    │
│  (excel_uploader.py)       │  │  (storage_manager.py)        │
│                            │  │                              │
│  - Parse Excel files       │  │  - Store job data            │
│  - Validate data           │  │  - Update statuses           │
│  - Extract status updates  │  │  - Track history             │
│  - Column mapping          │  │  - Query by status           │
│  - Date parsing            │  │  - Generate summaries        │
└────────────────┬───────────┘  └──────────┬───────────────────┘
                 │                         │
                 │                         │
                 ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                          │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  jobs.json  │  │ metadata.json│  │ scraping_errors.json│   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. ExcelUploader Class (`excel_uploader.py`)

**Responsibilities**:
- Parse Excel files (.xlsx, .xls)
- Detect and map column headers
- Validate data integrity
- Normalize status values
- Parse date formats
- Generate validation reports
- Cross-validate against stored jobs
- Extract status update records

**Key Methods**:

```python
class ExcelUploader:
    # Parsing
    parse_excel_file(file_path, sheet_name) -> Dict
    parse_excel_bytes(file_bytes, sheet_name) -> Dict
    
    # Validation
    validate_against_stored_jobs(parsed_data, stored_jobs) -> Dict
    get_status_updates(parsed_data, stored_jobs) -> List
    
    # Internal processing
    _find_header_row(sheet) -> int
    _map_columns(sheet, header_row) -> Dict
    _parse_row(sheet, row_idx, column_mapping) -> Dict
    _normalize_status(status, row_idx) -> str
    _parse_date(date_value, row_idx) -> str
    _validate_row(row_data) -> None
    _generate_summary(data_rows) -> Dict
```

**Data Flow**:
```
Excel File → Load Workbook → Find Headers → Map Columns →
Parse Rows → Validate Data → Normalize Values → Generate Summary
```

### 2. JobStorageManager Enhancements (`storage_manager.py`)

**New Methods for Status Tracking**:

```python
class JobStorageManager:
    # Status updates
    update_job_status(job_id, status, applied_date, notes) -> Dict
    batch_update_job_statuses(status_updates) -> Dict
    
    # Queries
    get_jobs_by_status(status) -> List[Dict]
    get_status_summary() -> Dict
```

**Status History Structure**:
```python
{
    "job_id": "job123",
    "title": "Software Engineer",
    "company": "Tech Corp",
    "application_status": "Interview",  # Current status
    "applied_date": "2025-11-10",
    "application_notes": "Technical interview next week",
    "status_history": [
        {
            "old_status": null,
            "new_status": "Applied",
            "timestamp": "2025-11-10T09:00:00",
            "notes": "Applied via LinkedIn"
        },
        {
            "old_status": "Applied",
            "new_status": "Interview",
            "timestamp": "2025-11-13T14:30:00",
            "notes": "Technical interview next week"
        }
    ],
    "last_updated": "2025-11-13T14:30:00"
}
```

### 3. API Layer (`app.py`)

**Request Processing Flow**:

```
Client Request → Flask Route → Validation → Business Logic →
Storage Operations → Response Formatting → JSON Response
```

**Error Handling Hierarchy**:
```
ExcelUploadError (Custom exceptions)
    ↓
Flask Error Handlers
    ↓
JSON Error Responses with HTTP status codes
```

## Data Validation Pipeline

### Stage 1: File Validation
```
┌──────────────┐
│ File Upload  │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ Check file exists   │
│ Verify extension    │
│ Check file size     │
└─────────┬───────────┘
          │
          ▼
    Valid? ────No────► Error Response
          │
         Yes
          ▼
```

### Stage 2: Excel Parsing
```
┌──────────────────┐
│ Load Workbook    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Find Header Row  │
│ (Check rows 1-10)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Map Columns      │
│ (Match variants) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Validate Columns │
│ (Check required) │
└────────┬─────────┘
         │
         ▼
    Valid? ────No────► Error Response
         │
        Yes
         ▼
```

### Stage 3: Row Validation
```
For each row:
┌────────────────────┐
│ Extract Values     │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Normalize Status   │
│ Parse Date         │
│ Trim Strings       │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Check Required     │
│ Fields Present     │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Validate Status    │
│ Value              │
└────────┬───────────┘
         │
         ▼
    Valid? ────No────► Add to Errors
         │
        Yes
         │
         ▼
    Add to Valid Rows
```

### Stage 4: Cross-Validation
```
┌──────────────────────┐
│ Load Stored Jobs     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Match by job_id      │
└──────────┬───────────┘
           │
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
Matched      New Jobs
Jobs             │
    │            │
    ▼            ▼
Compare      Report as
Details      New
    │
    ▼
Discrepancies?
    │
   Yes → Report Mismatch
    │
   No → Matched
```

## Column Detection Algorithm

### Flexible Mapping Strategy

```python
EXPECTED_COLUMNS = {
    'job_id': ['job_id', 'id', 'job id', 'jobid'],
    'title': ['title', 'job_title', 'job title', 'position'],
    'company': ['company', 'company_name', 'company name', 'employer'],
    'status': ['status', 'application_status', 'application status', 'app_status'],
    'applied_date': ['applied_date', 'applied date', 'date_applied', 'date applied'],
    'notes': ['notes', 'comments', 'note', 'comment', 'remarks']
}
```

**Detection Process**:
1. Read header row (scan rows 1-10)
2. Normalize column names (lowercase, trim)
3. Match against expected variations
4. Build column index mapping
5. Validate required columns present

## Status Normalization

### Case-Insensitive Handling

```python
STATUS_NORMALIZATION = {
    'applied': 'Applied',
    'interview': 'Interview',
    'offer': 'Offer',
    'rejected': 'Rejected',
    'pending': 'Pending'
}

# Input variations accepted:
# "applied", "APPLIED", "Applied" → "Applied"
# "interview", "INTERVIEW", "Interview" → "Interview"
```

## Date Parsing Strategy

### Multi-Format Support

```python
SUPPORTED_FORMATS = [
    '%Y-%m-%d',      # 2025-11-13
    '%m/%d/%Y',      # 11/13/2025
    '%d/%m/%Y',      # 13/11/2025
    '%Y/%m/%d',      # 2025/11/13
    '%m-%d-%Y',      # 11-13-2025
    '%d-%m-%Y'       # 13-11-2025
]
```

**Parsing Flow**:
```
Date Value → Is datetime object? ──Yes──► Convert to ISO
     │                                        format
     No
     │
     ▼
Try each format → Success? ──Yes──► Return ISO
     │                │               format
     │               No
     │                │
     ▼                ▼
Next format     Add warning,
                return None
```

## Error and Warning System

### Error Types

**Parsing Errors** (Block processing):
- File not found
- Invalid file format
- Missing required columns
- Invalid sheet name

**Validation Errors** (Row-level):
- Missing required fields
- Empty job_id
- Invalid data types

**Warnings** (Non-blocking):
- Invalid status values
- Unparseable dates
- Data format issues

### Error Response Structure

```json
{
    "success": false,
    "errors": [
        {
            "row": 5,
            "errors": ["Missing required field: company"]
        }
    ],
    "warnings": [
        {
            "row": 3,
            "field": "status",
            "message": "Invalid status 'InProgress'. Valid values: Applied, Interview, Offer, Rejected, Pending"
        }
    ]
}
```

## Status Update Extraction

### Update Detection Algorithm

```python
For each parsed job:
    1. Find matching job in storage by job_id
    2. If not found → Skip (can't update non-existent job)
    3. If found:
        a. Compare current status with parsed status
        b. If different → Create update record
        c. If same → Skip (no update needed)
```

### Update Record Structure

```json
{
    "job_id": "job123",
    "old_status": "Applied",
    "new_status": "Interview",
    "applied_date": "2025-11-13",
    "notes": "Phone screening completed",
    "timestamp": "2025-11-13T14:30:00"
}
```

## Batch Update Processing

### Transaction-like Behavior

```python
def batch_update_job_statuses(updates):
    with self.lock:  # Thread-safe
        data = load_jobs()
        jobs_lookup = create_lookup(data)
        
        for update in updates:
            if job_id in jobs_lookup:
                apply_update(job)
                track_history(job, update)
        
        save_jobs(data)  # Single write operation
        
        return summary
```

### Atomic Operations

- All updates processed in memory first
- Single file write at the end
- Thread-safe with locking
- Rollback on errors (data not saved)

## Performance Characteristics

### Parsing Performance

```
File Size    | Rows   | Parse Time | Memory
-------------|--------|------------|--------
100 KB       | 1,000  | ~1 sec     | ~5 MB
1 MB         | 10,000 | ~10 sec    | ~50 MB
10 MB        | 100,000| ~100 sec   | ~500 MB
```

### Optimization Strategies

1. **Streaming for Large Files**: Process rows incrementally
2. **Column Mapping Cache**: Reuse column detection results
3. **Batch Operations**: Single write for multiple updates
4. **Efficient Lookups**: Dictionary-based job_id indexing

### Scalability Limits

- **Max File Size**: 10 MB (configurable)
- **Max Rows**: ~100,000 (memory dependent)
- **Concurrent Uploads**: Thread-safe with locking
- **Storage Size**: Limited by disk space

## Security Considerations

### Input Validation

```python
# File validation
- Check file extension
- Verify file size
- Scan for malicious content (optional)

# Data validation
- Sanitize all string inputs
- Validate against whitelist (status values)
- Prevent code injection
- Limit input lengths
```

### Access Control Points

```
API Endpoints → Authentication → Authorization →
Rate Limiting → Business Logic
```

### Error Message Security

- No internal paths exposed
- No sensitive data in errors
- Generic error messages for security issues
- Detailed logs server-side only

## Testing Strategy

### Test Coverage

```
Unit Tests (27 test cases):
├── Excel Parsing (10 tests)
│   ├── Valid files
│   ├── Invalid formats
│   ├── Missing columns
│   └── Edge cases
│
├── Validation (8 tests)
│   ├── Status normalization
│   ├── Date parsing
│   ├── Required fields
│   └── Cross-validation
│
└── Storage Integration (9 tests)
    ├── Status updates
    ├── Batch operations
    ├── History tracking
    └── Queries
```

### Integration Testing

```python
# End-to-end workflow test
1. Create sample Excel file
2. Upload via API
3. Validate response
4. Apply updates
5. Query updated data
6. Verify status history
```

## Data Flow Example

### Complete Upload Workflow

```
User uploads job_applications.xlsx
    ↓
Flask receives multipart/form-data
    ↓
ExcelUploader.parse_excel_bytes()
    ↓
Load workbook from bytes
    ↓
Find header row (row 1)
    ↓
Map columns: {job_id: 0, title: 1, company: 2, status: 3}
    ↓
Parse row 2: {job_id: 'job1', title: 'Engineer', company: 'Corp', status: 'applied'}
    ↓
Normalize: status 'applied' → 'Applied'
    ↓
Validate: All required fields present ✓
    ↓
Add to valid rows
    ↓
Generate summary: 1 job, 1 Applied
    ↓
Return parse result
    ↓
Cross-validate against storage
    ↓
Find job1 in storage (match found)
    ↓
Compare: Old status 'Pending' ≠ New status 'Applied'
    ↓
Create update record
    ↓
Apply batch update
    ↓
Update job1.application_status = 'Applied'
    ↓
Add to job1.status_history
    ↓
Save jobs.json
    ↓
Return success response
```

## Extension Points

### Custom Validators

```python
class CustomExcelUploader(ExcelUploader):
    def _validate_row(self, row_data):
        super()._validate_row(row_data)
        # Add custom validation logic
        self._validate_company_name(row_data)
        self._validate_date_range(row_data)
```

### Additional Columns

```python
# Extend column mapping
EXPECTED_COLUMNS.update({
    'salary': ['salary', 'compensation', 'pay'],
    'location': ['location', 'city', 'office'],
    'remote': ['remote', 'work_from_home', 'wfh']
})
```

### Custom Status Values

```python
# Add new statuses
VALID_STATUSES.update({
    'Withdrawn', 'Ghosted', 'Negotiating'
})

STATUS_NORMALIZATION.update({
    'withdrawn': 'Withdrawn',
    'ghosted': 'Ghosted',
    'negotiating': 'Negotiating'
})
```

## Monitoring and Logging

### Log Levels

```python
DEBUG: Column mapping details, row-by-row processing
INFO: Parse results, update summaries
WARNING: Data validation warnings, format issues
ERROR: Parse failures, update errors
```

### Metrics to Track

- Upload success rate
- Average parse time
- Validation error frequency
- Update success rate
- Common error types

## Future Enhancements

### Planned Improvements

1. **CSV Support**: Add CSV file parsing
2. **Async Processing**: Handle large files asynchronously
3. **Webhooks**: Notify on status changes
4. **Audit Trail**: Detailed change logs
5. **Rollback**: Undo batch updates
6. **Scheduled Imports**: Automatic periodic imports
7. **Email Integration**: Parse status from emails

### Scalability Roadmap

1. **Database Backend**: Replace JSON with SQL
2. **Caching Layer**: Redis for frequent queries
3. **Queue System**: Background job processing
4. **Microservices**: Separate parsing service
5. **Cloud Storage**: S3 for file uploads

---

This architecture provides a solid foundation for job application status tracking with room for future enhancements and scalability improvements.
