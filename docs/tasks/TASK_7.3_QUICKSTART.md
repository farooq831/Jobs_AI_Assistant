# Task 7.3: Excel Upload for Status Tracking - Quick Start Guide

## Get Started in 5 Minutes! 🚀

### 1. Prerequisites Check (30 seconds)

```bash
# Check Python version
python3 --version  # Should be 3.7+

# Install openpyxl if needed
pip install openpyxl
```

### 2. Start the Backend (1 minute)

```bash
# Navigate to backend directory
cd Jobs_AI_Assistant/backend

# Start Flask server
python3 app.py
```

Server will start at `http://localhost:5000`

### 3. Create Sample Excel File (1 minute)

Create a file named `job_applications.xlsx` with these columns:

| job_id | title | company | status | applied_date | notes |
|--------|-------|---------|--------|--------------|-------|
| job1 | Software Engineer | Tech Corp | Applied | 2025-11-10 | Applied via LinkedIn |
| job2 | Data Analyst | Data Inc | Interview | 2025-11-11 | Phone screen completed |
| job3 | Product Manager | Product Co | Offer | 2025-11-12 | Received offer! |

**Valid Status Values**: Applied, Interview, Offer, Rejected, Pending

### 4. Upload and Parse (1 minute)

```bash
# Upload Excel file
curl -X POST http://localhost:5000/api/upload/excel \
  -F "file=@job_applications.xlsx"
```

**Expected Output**:
```json
{
  "success": true,
  "total_rows": 3,
  "valid_rows": 3,
  "summary": {
    "total_jobs": 3,
    "status_counts": {
      "Applied": 1,
      "Interview": 1,
      "Offer": 1
    }
  }
}
```

### 5. Apply Status Updates (30 seconds)

```bash
# Validate and apply updates
curl -X POST http://localhost:5000/api/upload/excel/apply-updates \
  -F "file=@job_applications.xlsx"
```

### 6. Check Results (1 minute)

```bash
# Get status summary
curl http://localhost:5000/api/jobs/status/summary

# Get jobs by status
curl http://localhost:5000/api/jobs/status?status=Interview

# Update single job
curl -X PUT http://localhost:5000/api/jobs/status/job1 \
  -H "Content-Type: application/json" \
  -d '{"status": "Interview", "notes": "Second round scheduled"}'
```

## Quick Reference

### API Endpoints

```bash
# Upload Excel
POST /api/upload/excel

# Validate Excel
POST /api/upload/excel/validate

# Apply updates
POST /api/upload/excel/apply-updates

# Update single job
PUT /api/jobs/status/<job_id>

# Get by status
GET /api/jobs/status?status=<status>

# Get summary
GET /api/jobs/status/summary

# Batch update
PUT /api/jobs/batch-status
```

### Status Values

✅ **Applied** - Application submitted  
✅ **Interview** - Interview scheduled/completed  
✅ **Offer** - Job offer received  
✅ **Rejected** - Application rejected  
✅ **Pending** - Application in progress  

### Required Excel Columns

- ✅ `job_id` - Unique identifier
- ✅ `title` - Job title
- ✅ `company` - Company name

### Optional Excel Columns

- `status` - Application status
- `applied_date` - Date applied (YYYY-MM-DD)
- `notes` - Additional notes

## Common Use Cases

### Use Case 1: Track New Applications

```excel
job_id | title | company | status | applied_date | notes
job123 | Engineer | Corp | Applied | 2025-11-13 | Via referral
```

Upload → Apply Updates → Done!

### Use Case 2: Update Interview Status

```excel
job_id | status | notes
job123 | Interview | Technical round next week
```

Upload → Apply Updates → Status tracked!

### Use Case 3: Record Offer

```bash
curl -X PUT http://localhost:5000/api/jobs/status/job123 \
  -H "Content-Type: application/json" \
  -d '{"status": "Offer", "notes": "Offer received - reviewing"}'
```

### Use Case 4: Bulk Status Update

```bash
curl -X PUT http://localhost:5000/api/jobs/batch-status \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {"job_id": "job1", "status": "Interview"},
      {"job_id": "job2", "status": "Rejected"},
      {"job_id": "job3", "status": "Offer"}
    ]
  }'
```

## Quick Demo

```bash
# Run interactive demo
cd backend
python3 demo_excel_upload.py
```

The demo automatically:
- ✓ Creates sample Excel file
- ✓ Parses and validates data
- ✓ Shows status updates
- ✓ Demonstrates all features

## Quick Troubleshooting

**Problem**: File upload fails  
**Fix**: Check file is .xlsx or .xls format

**Problem**: "Missing required columns"  
**Fix**: Ensure job_id, title, company columns exist

**Problem**: "Invalid status"  
**Fix**: Use only: Applied, Interview, Offer, Rejected, Pending

**Problem**: "Job not found"  
**Fix**: Job must exist in storage before status update

## Next Steps

1. ✅ Upload your job applications Excel file
2. ✅ Track application statuses
3. ✅ Update statuses as you progress
4. ✅ View status summary and statistics
5. ✅ Export updated data

## Full Documentation

For complete details, see `TASK_7.3_README.md`

## Testing

```bash
# Run full test suite
python3 test_excel_upload.py

# Expected: All tests pass ✓
```

---

**That's it! You're ready to track job applications! 🎉**
