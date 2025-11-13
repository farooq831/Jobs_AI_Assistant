# Task 7.2: CSV and PDF Export - Architecture

## System Architecture

### Overview
The CSV and PDF export system provides flexible, multi-format export capabilities for job listings with optional resume optimization tips integration.

```
┌─────────────────────────────────────────────────────────────┐
│                     Export System                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │ CSVExporter  │         │ PDFExporter  │                 │
│  └──────────────┘         └──────────────┘                 │
│         │                         │                         │
│         ├─ Format jobs data       ├─ Professional layout   │
│         ├─ Handle special chars   ├─ Color coding          │
│         ├─ UTF-8 encoding         ├─ Summary statistics    │
│         └─ BytesIO streaming      ├─ Resume tips section   │
│                                   └─ Multi-page support     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Flask)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CSV Endpoints              PDF Endpoints                   │
│  ├─ POST /api/export/csv    ├─ POST /api/export/pdf        │
│  ├─ GET  /csv/stored-jobs   ├─ GET  /pdf/stored-jobs       │
│  └─ GET  /csv/quick         ├─ POST /pdf/with-resume       │
│                              └─ GET  /pdf/quick             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Sources                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Job Data   │  │Resume Analyzer│  │   Storage   │     │
│  │  with Scores │  │     Tips      │  │   Manager   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Module Design

### 1. CSVExporter Class

**Responsibility**: Export job listings to CSV format

**Key Methods**:
```python
class CSVExporter:
    def export_jobs(jobs, include_scores, include_description) -> BytesIO
    def _prepare_job_row(job, include_scores, include_description) -> Dict
    def export_jobs_to_file(jobs, filename, ...) -> None
```

**Design Decisions**:
- Uses Python's `csv.DictWriter` for proper escaping
- Streams output via `StringIO` → `BytesIO` for memory efficiency
- Configurable columns for different use cases
- Truncates long descriptions (500 chars) to prevent unwieldy files

**Column Configuration**:
```
Always Include: Job Title, Company, Location, Salary, Job Type, Link
Optional: Score (%), Match Quality, Keyword Match, Salary Match, Location Match
Optional: Description
```

### 2. PDFExporter Class

**Responsibility**: Generate professional PDF reports with formatting

**Key Methods**:
```python
class PDFExporter:
    def export_jobs(jobs, resume_tips, include_tips) -> BytesIO
    def _add_summary_statistics(story, jobs) -> None
    def _add_resume_tips_section(story, tips) -> None
    def _add_jobs_section(story, jobs) -> None
    def _add_job_entry(story, job, index) -> None
```

**Design Decisions**:
- Uses ReportLab's Platypus for document flow
- Color-codes jobs based on match quality
- Includes summary statistics for quick insights
- Optional resume tips section on first page
- Automatic pagination every 3 jobs

**Layout Structure**:
```
Page 1:
├─ Title: "Job Search Results"
├─ Metadata (date, count)
├─ Summary Statistics Table
├─ Resume Tips Section (optional)
└─ First 1-3 Jobs

Page 2+:
└─ Remaining Jobs (3 per page)
```

**Color Scheme**:
```python
COLORS = {
    'red': (1, 0.8, 0.8),      # Poor match < 40%
    'yellow': (1, 1, 0.6),     # Fair match 40-70%
    'white': (1, 1, 1),        # Good match 70-85%
    'green': (0.8, 1, 0.8),    # Excellent match >= 85%
    'header': (0.27, 0.45, 0.77)
}
```

## API Endpoint Architecture

### Design Patterns

**RESTful Conventions**:
- `POST` for custom data export
- `GET` for stored data export
- Consistent error handling across all endpoints
- Proper HTTP status codes (200, 400, 404, 500)

**Response Format**:
```
Success: File download with proper MIME type
Error: JSON with error message and HTTP status code
```

### Endpoint Categories

#### 1. Custom Export Endpoints
```python
POST /api/export/csv
POST /api/export/pdf
```
- Accept job data in request body
- Allow full customization of options
- Return file download

#### 2. Stored Job Export Endpoints
```python
GET /api/export/{format}/stored-jobs/<user_id>
```
- Retrieve jobs from storage
- Support filtering via query parameters
- Return file download

#### 3. Quick Export Endpoints
```python
GET /api/export/{format}/quick/<user_id>
```
- No customization options
- Fastest export path
- Return file download

#### 4. Resume-Enhanced Export
```python
POST /api/export/pdf/with-resume/<resume_id>
```
- Fetch resume from storage
- Generate personalized tips
- Include tips in PDF

### Query Parameter Support

**Filtering Parameters**:
- `highlight_filter`: red|yellow|white|green
- `min_score`: float (0-100)
- `max_score`: float (0-100)

**Format Parameters**:
- CSV: `include_scores`, `include_description`
- PDF: `include_tips`

## Data Flow

### CSV Export Flow
```
1. Receive job data
2. Validate non-empty
3. Define headers based on options
4. Create StringIO buffer
5. Write CSV rows with proper escaping
6. Convert to BytesIO (UTF-8)
7. Return file download
```

### PDF Export Flow
```
1. Receive job data and tips
2. Validate non-empty
3. Create BytesIO buffer
4. Initialize PDF document
5. Build story (content array):
   ├─ Title and metadata
   ├─ Summary statistics
   ├─ Resume tips (if included)
   └─ Job listings
6. Generate PDF
7. Return file download
```

## Integration Points

### 1. Job Scoring System
```python
# Uses score data for visual indicators
score_data = job.get('score', {})
overall_score = score_data.get('overall_score', 0)
highlight = score_data.get('highlight', 'white')
```

### 2. Resume Analyzer
```python
# Integrates optimization tips
resume_tips = {
    'summary': str,
    'overall_assessment': {...},
    'critical_tips': [...],
    'important_tips': [...],
    'optional_tips': [...]
}
```

### 3. Storage Manager
```python
# Retrieves stored jobs for export
storage = JobStorageManager()
jobs = storage.get_scored_jobs(user_id, min_score, max_score)
jobs_filtered = storage.get_jobs_by_highlight(user_id, highlight)
```

## Performance Considerations

### Memory Efficiency
- **Streaming**: Uses BytesIO to avoid large memory allocations
- **Truncation**: Limits description length to prevent bloat
- **Pagination**: Automatic page breaks in PDF

### Speed Optimizations
- **Quick endpoints**: Skip optional processing
- **Lazy tips generation**: Only when requested
- **Efficient formatting**: Pre-compiled styles

### Scalability
- **Large datasets**: Tested with 50+ jobs
- **Concurrent exports**: Stateless exporters (thread-safe)
- **File size**: ~1KB per job (CSV), ~4KB per job (PDF)

## Error Handling Strategy

### Validation
```python
# Empty jobs check
if not jobs:
    raise ValueError("Cannot export empty jobs list")

# Missing required fields
if 'jobs' not in data:
    return jsonify({'error': 'Missing jobs data'}), 400
```

### Graceful Degradation
```python
# Missing score data - use defaults
if isinstance(score_data, dict):
    overall_score = score_data.get('overall_score', 0)
else:
    overall_score = 0  # Default
    highlight = 'white'  # Default
```

### User-Friendly Messages
```python
# Clear error messages
return jsonify({
    'error': 'No jobs found for this user'
}), 404

return jsonify({
    'error': f'Export failed: {str(e)}'
}), 500
```

## Security Considerations

### Input Validation
- Validate user_id exists
- Check resume_id ownership
- Sanitize filenames
- Limit file sizes

### Data Privacy
- No persistent file storage
- In-memory processing only
- Secure file downloads

## Extension Points

### Future Enhancements
1. **Custom Templates**: PDF template system
2. **Batch Export**: Multiple users at once
3. **Scheduled Exports**: Automated generation
4. **Email Integration**: Send exports via email
5. **Chart Generation**: Visual analytics in PDF
6. **Excel Export**: Use openpyxl directly
7. **Compression**: ZIP multiple formats

### Plugin Architecture
```python
class ExportPlugin:
    def export_jobs(jobs, options) -> BytesIO
    def get_mime_type() -> str
    def get_file_extension() -> str
```

## Testing Strategy

### Unit Tests
- Test each exporter independently
- Verify data formatting
- Check error handling
- Validate file structure

### Integration Tests
- Test API endpoints
- Verify storage integration
- Test filtering logic
- Check file downloads

### Performance Tests
- Large dataset handling (100+ jobs)
- Concurrent export requests
- Memory usage profiling

## Dependencies

### Core Libraries
- `reportlab==4.0.7` - PDF generation
- `csv` (standard library) - CSV formatting
- `io` (standard library) - BytesIO, StringIO

### Optional Dependencies
- `flask` - API endpoints
- `storage_manager` - Job retrieval
- `resume_analyzer` - Tips generation

## Monitoring and Logging

### Key Metrics
- Export count by format
- Average file size
- Export duration
- Error rate

### Logging Points
```python
logger.info(f"Exported {len(jobs)} jobs to CSV")
logger.warning("No jobs to export")
logger.error(f"Export failed: {str(e)}")
```

---

**Architecture Version**: 1.0
**Last Updated**: November 13, 2025
**Status**: Production Ready
