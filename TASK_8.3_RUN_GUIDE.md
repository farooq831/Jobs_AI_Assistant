# Task 8.3: UI Integration - Quick Run Guide

## Running the Complete Application

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm

### Step 1: Start Backend
```bash
cd backend
python app.py
```

Backend will start on http://localhost:5000

### Step 2: Start Frontend (New Terminal)
```bash
cd frontend

# First time only
npm install

# Start dev server
npm start
```

Frontend will open automatically at http://localhost:3000

### Step 3: Use the Dashboard

#### View Jobs
- Dashboard opens automatically
- Jobs displayed with scores and status

#### Filter Jobs
- **Search**: Type in search box
- **Highlight**: Select Red/Yellow/White/Green
- **Status**: Select Pending/Applied/Interview/Offer/Rejected

#### Update Status
1. Click "Update Status" on any job
2. Select new status
3. Add notes (optional)
4. Click "Update Status"
5. View status history

#### Sort Jobs
- Sort by: Score, Title, Company, Date
- Order: Ascending/Descending

### Running Tests
```bash
cd backend
python test_ui_integration.py
```

### Running Demo
```bash
cd backend
python demo_ui_integration.py
# Select option 0 to run all demos
```

### Features Available

✅ **Job Dashboard**
- View all jobs with match scores
- Color-coded highlights (Red/Yellow/White/Green)
- Status badges (Pending/Applied/Interview/Offer/Rejected)
- Real-time status summary

✅ **Filtering & Search**
- Search by title, company, location
- Filter by highlight color
- Filter by application status
- Combine multiple filters

✅ **Sorting**
- Sort by score, title, company, date
- Ascending or descending order

✅ **Status Management**
- Update job application status
- Add notes for context
- View complete status history
- Timeline visualization

✅ **Tabs**
- Dashboard: Job listings and management
- Profile: User details form
- Resume: Resume upload

### Troubleshooting

**Backend not starting?**
```bash
pip install -r requirements.txt
```

**Frontend not loading?**
```bash
cd frontend
rm -rf node_modules
npm install
```

**No jobs showing?**
- Run scrapers first (Task 3.x)
- Or load sample data

**CORS errors?**
```bash
pip install flask-cors
```

### Sample Data (Optional)

If you need sample jobs for testing:
```bash
cd backend
python demo_ui_integration.py
# This will help test with existing data
```

### Next Steps

1. ✅ View jobs on dashboard
2. ✅ Try filtering and sorting
3. ✅ Update some job statuses
4. ✅ Check status history
5. ✅ View status summary

### Documentation

- **README**: `docs/tasks/TASK_8.3_README.md`
- **Quickstart**: `docs/tasks/TASK_8.3_QUICKSTART.md`
- **Architecture**: `docs/tasks/TASK_8.3_ARCHITECTURE.md`

---

**Enjoy your new job dashboard!** 🎉
