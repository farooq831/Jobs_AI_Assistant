# Task 7.1: Excel Export - 5-Minute Quickstart

Get the Excel export functionality running in 5 minutes!

## Prerequisites

```bash
# Ensure you're in the backend directory
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant/backend
```

## Step 1: Verify Dependencies (30 seconds)

```bash
# Check if openpyxl is installed
python3 -c "import openpyxl; print('✓ openpyxl installed')"

# If not installed:
pip install openpyxl
```

## Step 2: Run the Demo (1 minute)

```bash
# Run the interactive demo
python3 demo_excel_export.py
```

This creates two sample Excel files:
- `demo_jobs_only.xlsx` - Jobs with color-coding
- `demo_jobs_with_tips.xlsx` - Jobs + resume tips

**Open these files to see the formatting!**

## Step 3: Test Basic Export (1 minute)

```python
# Create test_quick.py
from excel_exporter import export_jobs_to_file

jobs = [{
    'title': 'Python Developer',
    'company': 'Tech Corp',
    'location': 'Remote',
    'salary': '$120k',
    'job_type': 'Remote',
    'description': 'Great opportunity...',
    'link': 'https://example.com',
    'score': {'overall_score': 85, 'highlight': 'green'}
}]

export_jobs_to_file(jobs, 'test_output.xlsx')
print("✓ Created test_output.xlsx")
```

```bash
# Run it
python3 test_quick.py

# Check the file
ls -lh test_output.xlsx
```

## Step 4: Start the API Server (1 minute)

```bash
# Start Flask server
python3 app.py
```

Server starts on `http://localhost:5000`

## Step 5: Test API Endpoint (1 minute)

```python
# test_api_export.py
import requests
import json

# Sample jobs
jobs = [{
    'title': 'Senior Developer',
    'company': 'StartupXYZ',
    'location': 'San Francisco, CA',
    'salary': '$130k-$160k',
    'job_type': 'Hybrid',
    'description': 'Join our amazing team...',
    'link': 'https://example.com/job1',
    'score': {'overall_score': 88, 'highlight': 'green'}
}]

# Call export endpoint
response = requests.post('http://localhost:5000/api/export/excel',
    json={
        'jobs': jobs,
        'filename': 'api_test.xlsx'
    }
)

# Save file
if response.status_code == 200:
    with open('api_test.xlsx', 'wb') as f:
        f.write(response.content)
    print('✓ Downloaded api_test.xlsx')
else:
    print(f'✗ Error: {response.status_code}')
```

```bash
python3 test_api_export.py
```

## Quick Command Reference

### Export Jobs Only
```python
from excel_exporter import export_jobs_to_file
export_jobs_to_file(jobs, 'output.xlsx', include_tips_sheet=False)
```

### Export with Tips
```python
export_jobs_to_file(jobs, 'output.xlsx', resume_tips=tips, include_tips_sheet=True)
```

### Export to Memory
```python
from excel_exporter import export_jobs_to_excel
excel_bytes = export_jobs_to_excel(jobs, tips)
```

### API: Export Custom Jobs
```bash
curl -X POST http://localhost:5000/api/export/excel \
  -H "Content-Type: application/json" \
  -d '{"jobs": [...]}' \
  --output jobs.xlsx
```

### API: Export Stored Jobs
```bash
curl http://localhost:5000/api/export/excel/stored-jobs/user123 \
  --output user_jobs.xlsx
```

### API: Quick Export
```bash
curl http://localhost:5000/api/export/excel/quick/user123 \
  --output quick_export.xlsx
```

## Verify It Works

### 1. Check File Exists
```bash
ls -lh *.xlsx
```

### 2. Open in Excel/LibreOffice
```bash
# Linux
libreoffice demo_jobs_with_tips.xlsx &

# macOS
open demo_jobs_with_tips.xlsx

# Windows
start demo_jobs_with_tips.xlsx
```

### 3. Verify Features
- [ ] Green/Yellow/Red color coding on rows
- [ ] Frozen header row (scroll down, headers stay)
- [ ] Auto-filter dropdowns on headers
- [ ] "Resume Tips" sheet tab (if tips included)
- [ ] Cell comments on header (hover over "Job Title")
- [ ] Properly formatted data

## Common Issues

### "ModuleNotFoundError: No module named 'openpyxl'"
```bash
pip install openpyxl
```

### "Cannot export empty jobs list"
Ensure jobs array has at least one job with required fields.

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process
kill -9 <PID>

# Or use different port
export FLASK_PORT=5001
python3 app.py
```

### Excel file is corrupted
- Check job data has valid score field
- Ensure no special characters in filename
- Verify sufficient disk space

## Sample Data Structure

### Minimal Job Object
```python
{
    'title': 'Job Title',
    'company': 'Company Name',
    'location': 'Location',
    'salary': 'Salary Range',
    'job_type': 'Remote/Onsite/Hybrid',
    'description': 'Job description text',
    'link': 'https://...',
    'score': {
        'overall_score': 75,  # 0-100
        'highlight': 'yellow'  # red/yellow/white/green
    }
}
```

### Minimal Tips Object
```python
{
    'summary': 'Brief resume summary',
    'overall_assessment': {
        'strength_score': 70,
        'completeness': 'Good',
        'ats_compatibility': 'Fair'
    },
    'critical_tips': [],
    'important_tips': [],
    'optional_tips': []
}
```

## Next Steps

1. **Integrate with existing data**: Use jobs from storage_manager
2. **Add to frontend**: Create download button in UI
3. **Customize colors**: Modify ExcelExporter.COLORS
4. **Add filters**: Export only high-scoring jobs
5. **Schedule exports**: Auto-export weekly summaries

## Full Documentation

For complete details, see `TASK_7.1_README.md`

## Run Tests

```bash
# Full test suite (if pytest installed)
python3 -m pytest test_excel_export.py -v

# Manual verification
python3 demo_excel_export.py
```

---

**Time to Complete:** ~5 minutes  
**Difficulty:** Easy  
**Prerequisites:** Python 3, openpyxl  

✅ **You're ready to export jobs to Excel!**
