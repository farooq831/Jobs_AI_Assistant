# Task 2.1 - Testing & Verification Checklist

Use this checklist to verify that Task 2.1 is working correctly.

## Prerequisites
- [ ] Python 3.x installed
- [ ] Node.js 16+ installed
- [ ] pip/pip3 available
- [ ] npm available

## Setup Verification

### Backend Setup
- [ ] Virtual environment created (`venv/` directory exists)
- [ ] Dependencies installed (`pip install -r requirements.txt` successful)
- [ ] Flask-CORS installed (check with `pip list | grep Flask-CORS`)
- [ ] Backend starts without errors (`python backend/app.py`)
- [ ] Backend runs on port 5000
- [ ] No import errors in terminal

### Frontend Setup
- [ ] npm dependencies installed (`node_modules/` directory exists)
- [ ] React starts without errors (`npm start`)
- [ ] Frontend runs on port 3000 (or 3001 if 3000 is busy)
- [ ] Browser opens automatically
- [ ] No compilation errors in terminal

## Functional Testing

### Form Display
- [ ] Form displays correctly in browser
- [ ] All 5 fields are visible (Name, Location, Salary Min, Salary Max, Job Titles)
- [ ] Bootstrap styling applied (professional appearance)
- [ ] Submit button is visible and enabled
- [ ] Form is responsive (test on different window sizes)

### Client-Side Validation

#### Name Field
- [ ] Empty name shows error "Name is required"
- [ ] Single character shows error "Name must be at least 2 characters"
- [ ] Very long name (>100 chars) shows error
- [ ] Valid name clears any previous error
- [ ] Error message appears in red below field

#### Location Field
- [ ] Empty location shows error
- [ ] Single character shows error
- [ ] Valid location clears error

#### Salary Fields
- [ ] Empty salary min shows error
- [ ] Empty salary max shows error
- [ ] Negative salary shows error
- [ ] Min > Max shows error on both fields
- [ ] Valid range clears errors

#### Job Titles Field
- [ ] Empty job titles shows error
- [ ] Single valid title works
- [ ] Multiple comma-separated titles work
- [ ] Error clears when valid input entered

### Form Submission

#### Valid Submission
- [ ] Fill all fields with valid data
- [ ] Click "Submit Details"
- [ ] Button shows "Submitting..." with spinner
- [ ] Success message appears (green alert)
- [ ] Form clears after successful submission
- [ ] Can submit multiple times

#### Invalid Submission
- [ ] Submit empty form
- [ ] All required field errors appear
- [ ] Submit button re-enables after error
- [ ] No data sent to server (check Network tab)

## Backend API Testing

### Health Check
```bash
curl http://localhost:5000/health
```
- [ ] Returns `{"status": "healthy"}`
- [ ] Status code 200

### Index Route
```bash
curl http://localhost:5000/
```
- [ ] Returns JSON with "AI Job Application Assistant backend"
- [ ] Status code 200

### POST Valid Data
```bash
curl -X POST http://localhost:5000/api/user-details \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "location": "New York, NY",
    "salary_min": 50000,
    "salary_max": 80000,
    "job_titles": ["Software Engineer", "Developer"]
  }'
```
- [ ] Returns success response with user_id
- [ ] Status code 201
- [ ] Response includes submitted data

### POST Invalid Data - Missing Fields
```bash
curl -X POST http://localhost:5000/api/user-details \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith"
  }'
```
- [ ] Returns error response
- [ ] Status code 400
- [ ] Response includes error details

### POST Invalid Data - Bad Salary Range
```bash
curl -X POST http://localhost:5000/api/user-details \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Johnson",
    "location": "Chicago",
    "salary_min": 100000,
    "salary_max": 50000,
    "job_titles": ["Engineer"]
  }'
```
- [ ] Returns validation error
- [ ] Status code 400
- [ ] Error mentions salary range issue

### GET All Users
```bash
curl http://localhost:5000/api/user-details
```
- [ ] Returns all stored users
- [ ] Status code 200
- [ ] Response includes count and data

### GET User by ID
```bash
curl http://localhost:5000/api/user-details/1
```
- [ ] Returns user with ID 1 (if exists)
- [ ] Status code 200 (or 404 if not found)

### GET Non-existent User
```bash
curl http://localhost:5000/api/user-details/9999
```
- [ ] Returns error message
- [ ] Status code 404

## Automated Test Suite

### Run Test Script
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
source venv/bin/activate
cd backend
python test_api.py
```

- [ ] All 8 tests pass
- [ ] No errors or exceptions
- [ ] Summary shows 8/8 tests passed

Test results should show:
```
✓ Health Check: PASS
✓ Valid Submission: PASS
✓ Missing Fields: PASS
✓ Invalid Salary Range: PASS
✓ Empty Name: PASS
✓ Get All Users: PASS
✓ Get User by ID: PASS
✓ Get Non-existent User: PASS

Total: 8/8 tests passed
```

## Integration Testing

### Frontend-Backend Communication
- [ ] Frontend successfully connects to backend
- [ ] No CORS errors in browser console
- [ ] Form submission reaches backend (check backend terminal logs)
- [ ] Success/error responses display correctly in UI
- [ ] Network tab shows POST to http://localhost:5000/api/user-details

### Error Handling
- [ ] Server down: Frontend shows connection error
- [ ] Invalid response: Frontend handles gracefully
- [ ] Network timeout: Appropriate error message

## Browser Testing

### Chrome/Edge
- [ ] Form displays correctly
- [ ] Validation works
- [ ] Submission works
- [ ] No console errors

### Firefox
- [ ] Form displays correctly
- [ ] Validation works
- [ ] Submission works
- [ ] No console errors

### Mobile View (Responsive)
- [ ] Form is readable on mobile screen
- [ ] Fields are easily tappable
- [ ] Keyboard doesn't cover form
- [ ] Submit button accessible

## Data Validation Testing

### Name Field Edge Cases
- [ ] "Jo" → Valid (exactly 2 chars)
- [ ] "J" → Invalid (too short)
- [ ] "Mary-Jane O'Connor" → Valid (hyphens and apostrophes)
- [ ] "John123" → Should be caught by server validation
- [ ] String of 100 chars → Valid (boundary)
- [ ] String of 101 chars → Invalid (over limit)

### Salary Edge Cases
- [ ] 0 → Valid (minimum boundary)
- [ ] -1 → Invalid (negative)
- [ ] 50000 → Valid
- [ ] "fifty thousand" → Invalid (not a number)
- [ ] Min: 50000, Max: 50000 → Valid (equal is okay)
- [ ] Min: 50001, Max: 50000 → Invalid (min > max)

### Job Titles Edge Cases
- [ ] Single title → Valid
- [ ] "Engineer, Developer, Analyst" → Valid (3 titles)
- [ ] 20 titles → Valid (boundary)
- [ ] 21 titles → Invalid (over limit)
- [ ] "  Engineer  ,  Developer  " → Valid (whitespace trimmed)
- [ ] Empty string → Invalid

## Performance Testing

### Response Times
- [ ] Form loads in < 2 seconds
- [ ] Validation feedback appears instantly (<100ms)
- [ ] API response time < 500ms
- [ ] Form submission completes in < 1 second

### Load Testing (Optional)
- [ ] Submit 10 forms rapidly → All succeed
- [ ] Concurrent requests don't cause errors
- [ ] Memory usage stable

## Security Testing

### Server-Side Validation
- [ ] Cannot bypass validation using browser DevTools
- [ ] Sending invalid JSON returns 400 error
- [ ] SQL injection attempts in name field → Rejected
- [ ] XSS attempts in text fields → Escaped
- [ ] Extremely large payloads → Rejected

### CORS Configuration
- [ ] Requests from localhost:3000 → Allowed
- [ ] Requests from other origins → Follow CORS policy

## Documentation Verification

### Files Exist
- [ ] `frontend/TASK_2.1_README.md` exists and is complete
- [ ] `TASK_2.1_QUICKSTART.md` exists
- [ ] `TASK_2.1_SUMMARY.md` exists
- [ ] `TASK_2.1_ARCHITECTURE.md` exists
- [ ] `setup_task_2.1.sh` exists and is executable

### Documentation Quality
- [ ] README has clear setup instructions
- [ ] Quick start guide is easy to follow
- [ ] Architecture diagram is clear
- [ ] All code examples work
- [ ] API endpoints documented correctly

## Code Quality

### Frontend Code
- [ ] No console errors
- [ ] No console warnings
- [ ] Code follows React best practices
- [ ] Components are well-structured
- [ ] Comments explain complex logic

### Backend Code
- [ ] No Python errors
- [ ] PEP 8 compliant (mostly)
- [ ] Validation logic is clear
- [ ] Error messages are helpful
- [ ] Code is maintainable

## Final Checks

### Task Completion
- [ ] All requirements from task.md met
- [ ] task.md updated with completion date
- [ ] Git branch is up to date
- [ ] All new files committed

### Handoff Ready
- [ ] Can be run by another developer
- [ ] Setup instructions work from scratch
- [ ] No hard-coded paths (except in docs)
- [ ] Environment variables documented if needed

---

## Scoring

Count your checkmarks:

- **90-100%**: ✅ Excellent - Task complete and production-ready
- **80-89%**: ✅ Good - Task complete with minor issues
- **70-79%**: ⚠️ Acceptable - Task mostly complete, some fixes needed
- **Below 70%**: ❌ Incomplete - More work required

---

## Common Issues & Solutions

### Issue: Port 5000 already in use
```bash
sudo lsof -ti:5000 | xargs kill -9
```

### Issue: Port 3000 already in use
- React will prompt to use 3001 automatically
- Or kill the process: `sudo lsof -ti:3000 | xargs kill -9`

### Issue: Module not found errors (Backend)
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: npm install fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: CORS errors
- Make sure Flask-CORS is installed
- Check proxy in frontend/package.json
- Restart both servers

### Issue: Form not submitting
- Check browser console for errors
- Verify backend is running
- Check Network tab for API calls
- Verify validation is passing

---

**Use this checklist before marking Task 2.1 as complete!**
