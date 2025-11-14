# Task 8.2: Backend Tracking Logic - 5-Minute Quickstart

Get started with job application status tracking in 5 minutes!

---

## Quick Setup

### 1. Verify Installation (30 seconds)

```bash
cd backend
python3 -c "from storage_manager import JobStorageManager; from application_status import ApplicationStatus; print('✅ All imports successful')"
```

### 2. Run the Demo (2 minutes)

```bash
python3 demo_status_tracking.py
```

Press Enter at each prompt to see 10 interactive demonstrations.

### 3. Test the Implementation (2 minutes)

```bash
python3 test_status_tracking.py
```

Expected: 18/21 tests passing (86% success rate)

---

## Quick Usage Examples

### Example 1: Basic Status Tracking (Python)

```python
from storage_manager import JobStorageManager

# Initialize
storage = JobStorageManager()

# Create history
storage.create_status_history("job_123", "Pending")

# Update status
result = storage.update_job_status_with_history(
    job_id="job_123",
    new_status="Applied",
    notes="Submitted application"
)

# Check result
print(f"Success: {result['success']}")
print(f"New status: {result['new_status']}")
```

### Example 2: API Usage (curl)

```bash
# Start Flask server
python3 app.py

# In another terminal:

# Update status
curl -X PUT http://localhost:5000/api/jobs/status-history/job_123 \
  -H "Content-Type: application/json" \
  -d '{"status": "Applied", "notes": "Submitted via LinkedIn"}'

# Get status history
curl http://localhost:5000/api/jobs/status-history/job_123

# Get summary
curl http://localhost:5000/api/jobs/status-summary/enhanced
```

---

## Key Features at a Glance

| Feature | Description | API Endpoint |
|---------|-------------|--------------|
| Create History | Initialize tracking | `POST /api/jobs/status-history/<job_id>` |
| Update Status | Change with notes | `PUT /api/jobs/status-history/<job_id>` |
| Get History | Full timeline | `GET /api/jobs/status-history/<job_id>` |
| Query by Status | Filter jobs | `GET /api/jobs/status-by-status/<status>` |
| Bulk Update | Multiple jobs | `POST /api/jobs/status-history/bulk` |
| Export Report | Full analytics | `POST /api/jobs/status-report/export` |

---

## Valid Status Transitions

```
Pending → Applied, Interview, Offer, Rejected
Applied → Interview, Offer, Rejected
Interview → Offer, Rejected
Offer → Applied (if declined), Rejected
Rejected → Applied (reapply)
```

---

## File Locations

- **Storage:** `data/status_history.json`
- **Job Records:** `data/jobs.json`
- **Test Suite:** `backend/test_status_tracking.py`
- **Demo Script:** `backend/demo_status_tracking.py`
- **API Endpoints:** `backend/app.py`
- **Storage Logic:** `backend/storage_manager.py`

---

## Quick Troubleshooting

**Problem:** Import errors  
**Solution:** Ensure you're in the `backend/` directory

**Problem:** No status history found  
**Solution:** Call `create_status_history()` first

**Problem:** Invalid transition error  
**Solution:** Check valid transitions table above

**Problem:** API not responding  
**Solution:** Start Flask server with `python3 app.py`

---

## Next Steps

1. ✅ Run demo script to see all features
2. ✅ Review API endpoints in completion report
3. ✅ Integrate with frontend (Task 8.3)
4. ✅ Customize for your workflow

---

## Quick Reference - Python API

```python
# Create
storage.create_status_history(job_id, initial_status)

# Update
storage.update_job_status_with_history(job_id, new_status, notes, user_id)

# Query
storage.get_job_status_history(job_id)
storage.get_all_status_histories()
storage.get_jobs_by_status_with_history(status)
storage.get_status_timeline(job_id)

# Bulk
storage.bulk_update_statuses(updates_list)

# Analytics
storage.get_enhanced_status_summary()
storage.get_jobs_pending_action(days_threshold)

# Export
storage.export_status_report(filepath)
```

---

## That's it!

You're ready to track job application statuses. For complete documentation, see `TASK_8.2_COMPLETION_REPORT.md`.

**Time to Complete:** 5 minutes ✅
