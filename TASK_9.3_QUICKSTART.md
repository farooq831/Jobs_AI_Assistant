# Task 9.3: Application Tracker Interface - Quick Start Guide

Get up and running with the Application Tracker Interface in 5 minutes!

---

## Prerequisites

- Backend server running on `http://localhost:5000`
- Frontend development server running
- Sample jobs loaded in the system

---

## Quick Setup

### 1. Start the Backend (Terminal 1)

```bash
cd backend
python app.py
```

### 2. Start the Frontend (Terminal 2)

```bash
cd frontend
npm start
```

### 3. Load Sample Data

```bash
cd backend
python demo_task_9.3.py
# Select option 1: Store Sample Jobs
```

---

## Using the Dashboard

### Open the Application

Navigate to: `http://localhost:3000`

Click on the **Dashboard** tab.

### View Jobs

You'll see a dashboard with:
- **Statistics Summary** at the top (total jobs, match quality breakdown, status counts)
- **Filter Controls** below statistics
- **Job Cards** displaying all matched jobs

### Filter Jobs

#### By Search Term
```
Type in search box: "engineer"
→ Shows only jobs matching "engineer" in title, company, or location
```

#### By Match Quality
```
Select dropdown: "Excellent"
→ Shows only red-highlighted jobs (score ≥ 80)
```

#### By Application Status
```
Select dropdown: "Applied"
→ Shows only jobs you've applied to
```

### Sort Jobs

```
Select sort dropdown: "Sort by Score"
Click arrow button: "↓ Descending"
→ Shows highest-scored jobs first
```

### Update Application Status

1. **Click** "Update Status" button on any job card
2. **Select** new status from dropdown:
   - Pending
   - Applied
   - Interview
   - Offer
   - Rejected
3. **Add** optional notes (e.g., "Applied on 11/14/2025")
4. **Click** "Update Status" button
5. **See** dashboard refresh with new status

### View Status History

1. **Click** "Update Status" on a job
2. **Click** "Show Status History" link
3. **View** timeline of all status changes with timestamps and notes

---

## Common Workflows

### Workflow 1: Find and Apply to Top Jobs

```
1. Open Dashboard
2. Filter by "Excellent" matches (Red)
3. Sort by "Score" (Descending)
4. Review top 3 jobs
5. Click "View Job" to open posting
6. Click "Update Status" → Select "Applied"
7. Add notes: "Applied via LinkedIn"
8. Submit
```

**Time**: 2-3 minutes per job

### Workflow 2: Track Interview Progress

```
1. Filter by status: "Applied"
2. Find job where interview scheduled
3. Click "Update Status"
4. Select "Interview"
5. Add notes: "Phone screen on 11/20 at 2pm"
6. Submit
7. Click "Show Status History" to verify
```

**Time**: 1 minute

### Workflow 3: Weekly Review

```
1. Open Dashboard
2. View statistics summary
3. Check "Pending" count
4. Filter by "Pending" status
5. Apply to 5-10 jobs
6. Update each to "Applied" with notes
7. Review "Interview" and "Offer" counts
```

**Time**: 15-20 minutes

---

## Quick Reference

### Status Types

| Status     | Icon | Meaning                    |
|------------|------|----------------------------|
| Pending    | ⏳   | Not yet applied            |
| Applied    | ✉️   | Application submitted      |
| Interview  | 📅   | Interview scheduled        |
| Offer      | 🎉   | Job offer received         |
| Rejected   | ❌   | Application declined       |

### Match Quality Colors

| Color  | Score Range | Priority   |
|--------|-------------|------------|
| Red    | 80-100      | Excellent  |
| Yellow | 60-79       | Good       |
| Green  | 40-59       | Fair       |
| White  | 0-39        | Poor       |

### Keyboard Shortcuts

| Key       | Action                    |
|-----------|---------------------------|
| Tab       | Navigate between controls |
| Enter     | Activate button           |
| Esc       | Close modal               |
| Ctrl+F    | Focus search box          |

---

## Testing the Interface

### Run Demo Script

```bash
cd backend
python demo_task_9.3.py
```

Menu options:
1. Store Sample Jobs
2. Fetch Dashboard Data
3. Calculate Statistics
4. Filter by Match Quality
5. Filter by Status
6. Sort Jobs
7. Search Jobs
8. Update Status
9. View Status History
10. Complete Workflow

**Select 0** to run all demos.

### Run Test Suite

```bash
cd backend
pytest test_task_9.3.py -v
```

Expected: **27 tests passing** ✅

---

## Troubleshooting

### Dashboard is Empty

**Problem**: No jobs displayed  
**Solution**: 
```bash
python demo_task_9.3.py
# Select option 1 to load sample data
```

### Can't Update Status

**Problem**: "Failed to update status" error  
**Solution**: 
- Verify backend is running on port 5000
- Check browser console for errors
- Ensure job_id exists in database

### Filter Not Working

**Problem**: Filter doesn't change results  
**Solution**:
- Clear all other filters first
- Refresh the page
- Check if jobs actually match the filter criteria

### Modal Won't Close

**Problem**: Status update modal stuck open  
**Solution**:
- Press `Esc` key
- Click outside the modal
- Refresh the page if needed

---

## API Endpoints Reference

### Get All Jobs
```http
GET /api/jobs/stored/{user_id}
```

### Update Status
```http
PUT /api/jobs/{job_id}/status
Content-Type: application/json

{
  "status": "applied",
  "notes": "Optional notes",
  "user_id": "user_001"
}
```

### Get Status History
```http
GET /api/jobs/{job_id}/status/history
```

---

## Next Steps

1. ✅ **Load Sample Data**: Run demo to populate dashboard
2. ✅ **Explore Filters**: Try different filter combinations
3. ✅ **Update Statuses**: Practice updating job statuses
4. ✅ **View History**: Check status history for jobs
5. ✅ **Review Statistics**: Monitor your job search progress

---

## Support

For detailed documentation:
- **Complete Guide**: See `TASK_9.3_COMPLETION_REPORT.md`
- **Architecture**: See `TASK_9.3_ARCHITECTURE.md`
- **Summary**: See `TASK_9.3_SUMMARY.md`

For issues:
- Check backend logs: Terminal running `app.py`
- Check browser console: F12 → Console tab
- Review test output: `pytest test_task_9.3.py -v`

---

**Happy Job Hunting! 🎯**
