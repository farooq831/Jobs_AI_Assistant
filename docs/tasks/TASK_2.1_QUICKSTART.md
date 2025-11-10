# Task 2.1 - Quick Start Guide

## What Was Completed

✅ **Frontend Form Component**
- React-based user details form
- Bootstrap styling for professional look
- Real-time client-side validation
- Responsive design

✅ **Backend API Endpoints**
- POST `/api/user-details` - Submit user details
- GET `/api/user-details` - Get all user details
- GET `/api/user-details/<id>` - Get specific user details
- Comprehensive server-side validation

✅ **Validation System**
- Client-side: Real-time field validation
- Server-side: Data integrity validation
- Clear error messages for users

## Quick Setup & Test

### Option 1: Automated Setup (Recommended)

```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
./setup_task_2.1.sh
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run backend
cd backend
python app.py
```

Backend will run on: **http://localhost:5000**

#### Frontend Setup (in a new terminal)
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant/frontend

# Install dependencies (requires Node.js)
npm install

# Run frontend
npm start
```

Frontend will run on: **http://localhost:3000**

## Quick API Test

Once the backend is running, test it with curl:

```bash
# Test health check
curl http://localhost:5000/health

# Submit user details
curl -X POST http://localhost:5000/api/user-details \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "location": "New York, NY",
    "salary_min": 50000,
    "salary_max": 80000,
    "job_titles": ["Software Engineer", "Developer"]
  }'

# Get all user details
curl http://localhost:5000/api/user-details
```

Or run the automated test suite:

```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
source venv/bin/activate
cd backend
python test_api.py
```

## Form Fields

| Field | Type | Validation |
|-------|------|------------|
| **Name** | Text | Required, 2-100 chars, letters only |
| **Location** | Text | Required, 2-100 chars |
| **Min Salary** | Number | Required, positive, < max salary |
| **Max Salary** | Number | Required, positive, > min salary |
| **Job Titles** | Text Area | Required, comma-separated, 1-20 titles |

## Project Structure

```
Jobs_AI_Assistant/
├── backend/
│   ├── app.py              # Flask API with validation
│   └── test_api.py         # API test suite
├── frontend/
│   ├── UserDetailsForm.jsx # Main form component
│   ├── App.jsx             # App wrapper
│   ├── index.jsx           # Entry point
│   ├── index.html          # HTML template
│   ├── App.css             # Styles
│   ├── package.json        # Dependencies
│   └── TASK_2.1_README.md  # Detailed docs
├── requirements.txt        # Python dependencies
├── setup_task_2.1.sh       # Setup script
└── task.md                 # Updated with completion

```

## Troubleshooting

### Backend Issues

**Problem:** `pip` or `pip3` not found
```bash
sudo apt install python3-pip
```

**Problem:** Import errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** Port 5000 already in use
```bash
# Kill process using port 5000
sudo lsof -ti:5000 | xargs kill -9
```

### Frontend Issues

**Problem:** Node.js not installed
- Install from: https://nodejs.org/ (version 16+)

**Problem:** npm install fails
```bash
rm -rf node_modules package-lock.json
npm install
```

**Problem:** Port 3000 already in use
- React will automatically suggest port 3001

### CORS Issues

If you see CORS errors in the browser console, make sure:
1. Flask-CORS is installed: `pip install Flask-CORS`
2. Backend is running before frontend
3. Proxy is configured in `frontend/package.json`

## Next Steps

After verifying Task 2.1 works:

1. **Task 2.2**: Job Type Selection Component (Remote/Onsite/Hybrid)
2. **Task 2.3**: Resume Upload Functionality

## Additional Resources

- **Full Documentation**: `frontend/TASK_2.1_README.md`
- **API Tests**: `backend/test_api.py`
- **Flask Docs**: https://flask.palletsprojects.com/
- **React Docs**: https://react.dev/
- **Bootstrap Docs**: https://getbootstrap.com/

---

**Task Completed:** November 9, 2025
**Status:** ✅ Ready for Testing
