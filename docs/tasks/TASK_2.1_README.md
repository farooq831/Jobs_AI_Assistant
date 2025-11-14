# User Details Input Module

## Overview
This module implements Task 2.1 of the AI Job Application Assistant project. It provides a complete user details input form with both client-side and server-side validation.

## Components

### Frontend Components
- **UserDetailsForm.jsx**: Main React component with form inputs and validation
- **App.jsx**: Application wrapper component
- **index.jsx**: React entry point
- **index.html**: HTML template
- **App.css**: Styling for the application
- **package.json**: Frontend dependencies and scripts

### Backend Components
- **app.py**: Flask backend with API endpoints and validation logic

## Features

### Form Fields
1. **Name** (Required)
   - Text input
   - Minimum 2 characters
   - Maximum 100 characters
   - Only letters, spaces, hyphens, and apostrophes allowed

2. **Location** (Required)
   - Text input
   - Minimum 2 characters
   - Maximum 100 characters

3. **Salary Range** (Required)
   - Minimum salary input (number)
   - Maximum salary input (number)
   - Must be positive values
   - Minimum cannot exceed maximum

4. **Job Titles** (Required)
   - Textarea for comma-separated titles
   - At least one title required
   - Maximum 20 titles
   - Each title 2-100 characters

### Validation

#### Client-Side Validation
- Real-time validation as user types
- Immediate error feedback
- Field-level error messages
- Form submission prevention if invalid

#### Server-Side Validation
- Comprehensive data validation
- Type checking
- Range validation
- Pattern matching (e.g., name format)
- Returns detailed error messages

## API Endpoints

### POST /api/user-details
Submit user details for storage.

**Request Body:**
```json
{
  "name": "John Doe",
  "location": "New York, NY",
  "salary_min": 50000,
  "salary_max": 80000,
  "job_titles": ["Software Engineer", "Full Stack Developer"]
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "User details saved successfully",
  "user_id": 1,
  "data": {
    "name": "John Doe",
    "location": "New York, NY",
    "salary_min": 50000,
    "salary_max": 80000,
    "job_titles": ["Software Engineer", "Full Stack Developer"]
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "name": "Name is required",
    "salary_min": "Minimum salary cannot exceed maximum salary"
  }
}
```

### GET /api/user-details
Retrieve all stored user details.

**Success Response (200):**
```json
{
  "success": true,
  "count": 2,
  "data": {
    "1": {...},
    "2": {...}
  }
}
```

### GET /api/user-details/<user_id>
Retrieve specific user details by ID.

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
pip install -r requirements.txt
```

2. Run the Flask backend:
```bash
cd backend
python app.py
```

The backend will run on http://localhost:5000

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant/frontend
npm install
```

2. Run the React development server:
```bash
npm start
```

The frontend will run on http://localhost:3000

## Testing

### Manual Testing Steps

1. **Start both servers** (backend and frontend)

2. **Test valid submission:**
   - Fill all fields with valid data
   - Submit the form
   - Verify success message appears
   - Check backend console for received data

3. **Test client-side validation:**
   - Submit empty form → should show all required field errors
   - Enter name with 1 character → should show error
   - Enter min salary > max salary → should show error
   - Enter job titles without commas → should work as single title

4. **Test server-side validation:**
   - Use browser DevTools to bypass client validation
   - Send invalid data via API
   - Verify server returns appropriate error messages

5. **Test API endpoints:**
```bash
# Test POST endpoint
curl -X POST http://localhost:5000/api/user-details \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "location": "San Francisco, CA",
    "salary_min": 70000,
    "salary_max": 120000,
    "job_titles": ["Data Scientist", "ML Engineer"]
  }'

# Test GET all
curl http://localhost:5000/api/user-details

# Test GET by ID
curl http://localhost:5000/api/user-details/1
```

## Validation Rules Summary

| Field | Validation Rules |
|-------|-----------------|
| Name | Required, 2-100 chars, letters/spaces/hyphens/apostrophes only |
| Location | Required, 2-100 chars |
| Salary Min | Required, number, >= 0, < 10,000,000 |
| Salary Max | Required, number, >= 0, < 10,000,000, >= salary_min |
| Job Titles | Required, 1-20 titles, each 2-100 chars |

## Future Enhancements

1. **Database Integration**: Replace in-memory storage with SQLite/PostgreSQL
2. **User Authentication**: Add user accounts and authentication
3. **Data Persistence**: Save user preferences across sessions
4. **Auto-complete**: Add location auto-complete
5. **Salary Suggestions**: Show salary ranges based on job titles
6. **Form State Persistence**: Save draft forms in browser storage
7. **Advanced Validation**: Email validation, phone number validation

## Files Created/Modified

### Frontend Files Created:
- `frontend/UserDetailsForm.jsx`
- `frontend/App.jsx`
- `frontend/App.css`
- `frontend/index.jsx`
- `frontend/index.html`
- `frontend/package.json`

### Backend Files Modified:
- `backend/app.py` - Added API endpoints and validation
- `requirements.txt` - Added Flask-CORS dependency

### Documentation:
- `frontend/TASK_2.1_README.md` - This file

## Task Completion Status

✅ Task 2.1: Develop User Detail Input Forms
- ✅ Build frontend form to collect name, location, salary range, job titles
- ✅ Implement client-side validations
- ✅ Implement server-side validations
- ✅ Create API endpoints
- ✅ Test functionality

## Next Steps

Proceed to **Task 2.2: Job Type Selection Component** to add multi-select interface for Remote/Onsite/Hybrid job types.
