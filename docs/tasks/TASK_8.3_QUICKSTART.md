# Task 8.3: UI Integration - Quick Start Guide

Get the job dashboard UI up and running in 5 minutes!

## Prerequisites
- ✅ Backend running on http://localhost:5000
- ✅ Node.js 14+ and npm installed
- ✅ Some jobs in the database (from Task 3.x scraping)

## Step 1: Start Backend (30 seconds)

```bash
# Navigate to backend directory
cd backend

# Start Flask server
python app.py
```

You should see:
```
 * Running on http://localhost:5000
```

## Step 2: Install Frontend Dependencies (2 minutes)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Step 3: Start Frontend (30 seconds)

```bash
# Start React development server
npm start
```

Browser should automatically open to http://localhost:3000

## Step 4: View Your Dashboard (10 seconds)

The dashboard will load automatically showing:
- All scraped jobs with match scores
- Status summary at the top
- Filters and sorting options

## Quick Feature Tour (2 minutes)

### View Jobs
✅ Jobs are displayed in a grid with color-coded highlights  
✅ Each job shows: title, company, location, salary, score, status

### Filter Jobs
1. **Search**: Type in search box (e.g., "Software Engineer")
2. **By Highlight**: Select "Red", "Yellow", "White", or "Green"
3. **By Status**: Select "Pending", "Applied", "Interview", etc.

### Sort Jobs
1. **Sort By**: Choose Score, Title, Company, or Date
2. **Order**: Select Ascending or Descending

### Update Status
1. Click "Update Status" on any job card
2. Select new status from dropdown
3. Add notes (optional)
4. Click "Update Status" button
5. View status history in the modal

### View Summary
- Status summary card shows at top
- Total jobs and breakdown by status
- Updates automatically

## Test It Works

### Run Quick Test
```bash
cd backend
python test_ui_integration.py
```

### Run Interactive Demo
```bash
cd backend
python demo_ui_integration.py
# Select option 9 for full workflow simulation
```

## Common Quick Fixes

### Backend Not Running?
```bash
cd backend
python app.py
```

### No Jobs Showing?
```bash
# Add some test jobs
cd backend
python -c "from storage_manager import JobStorageManager; sm = JobStorageManager(); print(f'Jobs: {sm.get_jobs_count()}')"

# If 0, run a scraper first (Task 3.x)
```

### Port Already in Use?
```bash
# Frontend (3000)
lsof -ti:3000 | xargs kill -9

# Backend (5000)
lsof -ti:5000 | xargs kill -9
```

### CORS Errors?
Verify `flask-cors` is installed:
```bash
pip install flask-cors
```

## Quick Navigation

Once running:
- **Dashboard Tab**: View and manage jobs (default)
- **User Profile Tab**: Update user preferences
- **Resume Upload Tab**: Upload and analyze resume

## Next Steps

✅ **Filter Jobs**: Try different filter combinations  
✅ **Update Statuses**: Mark jobs as Applied, Interview, etc.  
✅ **View History**: Click "Update Status" to see timeline  
✅ **Export Data**: Use backend export endpoints  

## Quick Reference

### Key Endpoints
```
GET  /api/storage/jobs              # Get all jobs
GET  /api/jobs/status/summary       # Get status summary
PUT  /api/jobs/status/<id>          # Update job status
GET  /api/jobs/status-history/<id>  # Get status history
GET  /api/jobs-by-highlight/<color> # Filter by highlight
GET  /api/jobs/status?status=<val>  # Filter by status
```

### Frontend URLs
```
http://localhost:3000              # Main app
http://localhost:3000#dashboard    # Dashboard tab
http://localhost:3000#profile      # Profile tab
http://localhost:3000#resume       # Resume tab
```

### Status Values
- `pending` - Initial state
- `applied` - Application submitted
- `interview` - Interview scheduled
- `offer` - Job offer received
- `rejected` - Application rejected

### Highlight Colors
- `red` - Low match (0-60%)
- `yellow` - Medium match (60-80%)
- `white` - Good match (80-90%)
- `green` - Excellent match (90-100%)

## Troubleshooting (< 1 minute each)

### Issue: Blank Dashboard
**Fix**: Check backend has jobs
```bash
curl http://localhost:5000/api/storage/jobs
```

### Issue: Status Update Fails
**Fix**: Check job ID exists
```bash
curl http://localhost:5000/api/storage/jobs/<job_id>
```

### Issue: Modal Won't Open
**Fix**: Check browser console for errors (F12)

### Issue: Filters Don't Work
**Fix**: Ensure jobs have highlight/status fields set

## You're Ready! 🚀

Your dashboard is now running and integrated with status tracking!

**Next**: Update some job statuses and watch the summary update in real-time.

---

Need more details? See [Full README](./TASK_8.3_README.md)
