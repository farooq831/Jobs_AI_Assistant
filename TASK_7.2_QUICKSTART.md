# Task 7.2: CSV and PDF Export - Quick Start Guide

## 5-Minute Quick Start

### Prerequisites
```bash
# Install required dependency
pip install reportlab==4.0.7
```

### 1. Basic CSV Export (1 minute)

```python
from csv_pdf_exporter import export_jobs_to_csv

# Sample jobs
jobs = [
    {
        'title': 'Python Developer',
        'company': 'Tech Corp',
        'location': 'San Francisco, CA',
        'salary': '$120k-$150k',
        'job_type': 'Remote',
        'description': 'Looking for Python expert...',
        'link': 'https://example.com/job1',
        'score': {'overall_score': 85, 'highlight': 'green'}
    }
]

# Export to CSV
csv_file = export_jobs_to_csv(jobs)

# Save to disk
with open('jobs.csv', 'wb') as f:
    f.write(csv_file.getvalue())

print("✓ CSV export complete!")
```

### 2. Basic PDF Export (1 minute)

```python
from csv_pdf_exporter import export_jobs_to_pdf

# Export to PDF
pdf_file = export_jobs_to_pdf(jobs)

# Save to disk
with open('jobs.pdf', 'wb') as f:
    f.write(pdf_file.getvalue())

print("✓ PDF export complete!")
```

### 3. Use API Endpoints (1 minute)

```bash
# Start Flask server
cd backend
python app.py

# In another terminal - CSV export
curl -X POST http://localhost:5000/api/export/csv \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [{
      "title": "Python Developer",
      "company": "Tech Corp",
      "location": "San Francisco",
      "salary": "$120k",
      "job_type": "Remote",
      "score": {"overall_score": 85, "highlight": "green"}
    }]
  }' \
  --output jobs.csv

# PDF export
curl -X POST http://localhost:5000/api/export/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [{
      "title": "Python Developer",
      "company": "Tech Corp",
      "location": "San Francisco",
      "salary": "$120k",
      "job_type": "Remote",
      "score": {"overall_score": 85, "highlight": "green"}
    }]
  }' \
  --output jobs.pdf
```

### 4. Run Demo Script (1 minute)

```bash
cd backend
python demo_csv_pdf_export.py
```

**Output**: Creates 5 demo files showing all export features!

### 5. Run Tests (1 minute)

```bash
cd backend
pytest test_csv_pdf_export.py -v
```

**Expected**: 27/27 tests passing ✓

## Common Use Cases

### Export with Custom Columns
```python
# CSV without descriptions (compact)
csv_file = export_jobs_to_csv(
    jobs,
    include_scores=True,
    include_description=False
)
```

### Export with Resume Tips
```python
tips = {
    'summary': 'Your resume needs improvement...',
    'overall_assessment': {
        'strength_score': 72,
        'completeness': 'Good'
    },
    'critical_tips': [...]
}

pdf_file = export_jobs_to_pdf(
    jobs,
    resume_tips=tips,
    include_tips=True
)
```

### Quick Export from Storage
```bash
# Export all jobs for a user
curl http://localhost:5000/api/export/csv/quick/user123 \
  --output user_jobs.csv

curl http://localhost:5000/api/export/pdf/quick/user123 \
  --output user_jobs.pdf
```

### Export with Filtering
```bash
# Export only high-scoring jobs
curl "http://localhost:5000/api/export/csv/stored-jobs/user123?min_score=70" \
  --output high_score_jobs.csv

# Export only excellent matches
curl "http://localhost:5000/api/export/pdf/stored-jobs/user123?highlight_filter=green" \
  --output excellent_jobs.pdf
```

## Feature Overview

### CSV Export Options
| Option | Default | Description |
|--------|---------|-------------|
| `include_scores` | `true` | Include score columns |
| `include_description` | `true` | Include job description |

### PDF Export Options
| Option | Default | Description |
|--------|---------|-------------|
| `include_tips` | `true` | Include resume tips section |
| `resume_tips` | `null` | Resume optimization tips |

### Color Coding (PDF)
- 🟢 **Green**: Excellent match (≥85%)
- ⚪ **White**: Good match (70-84%)
- 🟡 **Yellow**: Fair match (40-69%)
- 🔴 **Red**: Poor match (<40%)

## Troubleshooting

### Issue: ImportError for reportlab
```bash
pip install reportlab==4.0.7
```

### Issue: Empty CSV file
- Ensure jobs list is not empty
- Check that jobs have required fields

### Issue: PDF shows "N/A" for scores
- Verify jobs have 'score' dictionary
- Ensure score contains 'overall_score' and 'highlight'

### Issue: API endpoint returns 404
- Verify Flask server is running
- Check endpoint URL spelling
- Ensure user_id exists in storage

## API Endpoint Reference

### CSV Endpoints
- `POST /api/export/csv` - Custom export
- `GET /api/export/csv/stored-jobs/<user_id>` - Export stored jobs
- `GET /api/export/csv/quick/<user_id>` - Quick export

### PDF Endpoints
- `POST /api/export/pdf` - Custom export
- `GET /api/export/pdf/stored-jobs/<user_id>` - Export stored jobs
- `POST /api/export/pdf/with-resume/<resume_id>` - Export with tips
- `GET /api/export/pdf/quick/<user_id>` - Quick export

## Next Steps

1. **Integrate with Frontend**: Add export buttons to UI
2. **Customize Templates**: Modify PDF styles in `PDFExporter` class
3. **Add Automation**: Schedule automated exports
4. **Email Integration**: Send exports via email

## Support Files

- **Full Documentation**: `TASK_7.2_COMPLETION_REPORT.md`
- **Test Suite**: `backend/test_csv_pdf_export.py`
- **Demo Script**: `backend/demo_csv_pdf_export.py`
- **Source Code**: `backend/csv_pdf_exporter.py`

---

**Quick Start Complete!** 🎉

You now have CSV and PDF export functionality working. Check the completion report for detailed implementation information.
