# Task 2.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          TASK 2.1                               │
│              User Detail Input Forms Module                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│                   (React + Bootstrap)                           │
│                   Port: 3000                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │          UserDetailsForm Component                    │    │
│  │                                                       │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │  Name Input                                 │    │    │
│  │  │  [_____________________________]            │    │    │
│  │  │  ✓ Client-side validation                   │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                       │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │  Location Input                             │    │    │
│  │  │  [_____________________________]            │    │    │
│  │  │  ✓ Real-time error feedback                 │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                       │    │
│  │  ┌──────────────────┐  ┌──────────────────┐        │    │
│  │  │  Salary Min ($)  │  │  Salary Max ($)  │        │    │
│  │  │  [___________]   │  │  [___________]   │        │    │
│  │  │  ✓ Range check   │  │  ✓ Range check   │        │    │
│  │  └──────────────────┘  └──────────────────┘        │    │
│  │                                                       │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │  Job Titles (comma-separated)              │    │    │
│  │  │  [                                    ]    │    │
│  │  │  [                                    ]    │    │
│  │  │  ✓ Multiple titles support                 │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                       │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │        [  Submit Details  ]                 │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                       │    │
│  └───────────────────────────────────────────────────────┘    │
│                           │                                    │
│                           │ HTTP POST                          │
│                           ▼                                    │
└───────────────────────────────────────────────────────────────┘

                            │
                            │ JSON Payload
                            │
                            ▼

┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                 │
│                      (Flask + CORS)                             │
│                      Port: 5000                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │         API ENDPOINTS                                 │    │
│  │                                                       │    │
│  │  POST /api/user-details                              │    │
│  │  ├─ Receive user data                                │    │
│  │  ├─ Validate server-side                             │    │
│  │  └─ Return success/error response                    │    │
│  │                                                       │    │
│  │  GET /api/user-details                               │    │
│  │  └─ Return all stored user details                   │    │
│  │                                                       │    │
│  │  GET /api/user-details/<id>                          │    │
│  │  └─ Return specific user by ID                       │    │
│  │                                                       │    │
│  └───────────────────────────────────────────────────────┘    │
│                           │                                    │
│                           ▼                                    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │    VALIDATION LAYER                                   │    │
│  │    validate_user_details()                            │    │
│  │                                                       │    │
│  │  ✓ Name: 2-100 chars, letters only                   │    │
│  │  ✓ Location: 2-100 chars                             │    │
│  │  ✓ Salary Min: number, ≥0, ≤ max                     │    │
│  │  ✓ Salary Max: number, ≥0, ≥ min                     │    │
│  │  ✓ Job Titles: 1-20 items, 2-100 chars each          │    │
│  │  ✓ Type checking                                     │    │
│  │  ✓ Pattern matching                                  │    │
│  │                                                       │    │
│  └───────────────────────────────────────────────────────┘    │
│                           │                                    │
│                           ▼                                    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │      DATA STORAGE (In-Memory)                         │    │
│  │      user_details_store = {}                          │    │
│  │                                                       │    │
│  │  {                                                    │    │
│  │    1: {                                               │    │
│  │      name: "John Doe",                                │    │
│  │      location: "New York, NY",                        │    │
│  │      salary_min: 50000,                               │    │
│  │      salary_max: 80000,                               │    │
│  │      job_titles: ["Engineer", "Developer"]            │    │
│  │    }                                                  │    │
│  │  }                                                    │    │
│  │                                                       │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                       DATA FLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User fills form in browser                                 │
│  2. Client-side validation runs on blur/submit                 │
│  3. If valid, POST to /api/user-details                        │
│  4. Flask receives JSON payload                                │
│  5. Server-side validation executes                            │
│  6. If valid, store in memory and return success               │
│  7. If invalid, return error messages                          │
│  8. Frontend displays success/error to user                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION STRATEGY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CLIENT-SIDE                     SERVER-SIDE                   │
│  ════════════                     ════════════                 │
│  • UX improvement                 • Security enforcement        │
│  • Immediate feedback             • Data integrity              │
│  • Reduce server load             • Type checking               │
│  • Form-level validation          • Business rules              │
│                                   • Final authority             │
│                                                                 │
│  Both layers validate the same rules for defense in depth      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    FILE STRUCTURE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Jobs_AI_Assistant/                                            │
│  ├── backend/                                                  │
│  │   ├── app.py                  (✨ Updated)                 │
│  │   ├── test_api.py             (✨ New)                     │
│  │   └── README.md                                            │
│  ├── frontend/                                                 │
│  │   ├── UserDetailsForm.jsx     (✨ New)                     │
│  │   ├── App.jsx                 (✨ New)                     │
│  │   ├── App.css                 (✨ New)                     │
│  │   ├── index.jsx               (✨ New)                     │
│  │   ├── index.html              (✨ New)                     │
│  │   ├── package.json            (✨ New)                     │
│  │   ├── TASK_2.1_README.md      (✨ New)                     │
│  │   └── README.md                                            │
│  ├── requirements.txt             (✨ Updated)                 │
│  ├── task.md                      (✨ Updated)                 │
│  ├── setup_task_2.1.sh            (✨ New)                     │
│  ├── TASK_2.1_QUICKSTART.md       (✨ New)                     │
│  ├── TASK_2.1_SUMMARY.md          (✨ New)                     │
│  └── TASK_2.1_ARCHITECTURE.md     (✨ New - This file)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Frontend:                        Backend:                      │
│  • React 18.2.0                   • Flask 2.2.5                 │
│  • Bootstrap 5.3.0                • Flask-CORS 4.0.0            │
│  • React Scripts 5.0.1            • Python 3.x                  │
│                                                                 │
│  Communication:                   Storage:                      │
│  • REST API                       • In-Memory Dict              │
│  • JSON format                    • (Future: SQLite/Postgres)   │
│  • CORS enabled                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Request/Response Flow

### Successful Submission:

```
Client                                Server
  │                                     │
  │  POST /api/user-details             │
  │  Content-Type: application/json     │
  ├────────────────────────────────────>│
  │  {                                  │
  │    "name": "John Doe",              │
  │    "location": "NY",                │
  │    "salary_min": 50000,             │
  │    "salary_max": 80000,             │
  │    "job_titles": ["Engineer"]       │
  │  }                                  │
  │                                     │
  │                      [Validate Data]│
  │                      [Store in Dict]│
  │                                     │
  │  201 Created                        │
  │<────────────────────────────────────┤
  │  {                                  │
  │    "success": true,                 │
  │    "user_id": 1,                    │
  │    "message": "Success",            │
  │    "data": {...}                    │
  │  }                                  │
  │                                     │
  │  [Display Success Message]          │
  │  [Clear Form]                       │
  │                                     │
```

### Failed Validation:

```
Client                                Server
  │                                     │
  │  POST /api/user-details             │
  ├────────────────────────────────────>│
  │  {                                  │
  │    "name": "J",     // Too short    │
  │    "salary_min": 100000,            │
  │    "salary_max": 50000  // Invalid  │
  │  }                                  │
  │                                     │
  │                      [Validate Data]│
  │                      [Errors Found] │
  │                                     │
  │  400 Bad Request                    │
  │<────────────────────────────────────┤
  │  {                                  │
  │    "success": false,                │
  │    "message": "Validation failed",  │
  │    "errors": {                      │
  │      "name": "Too short",           │
  │      "salary_min": "Exceeds max",   │
  │      "salary_max": "Less than min"  │
  │    }                                │
  │  }                                  │
  │                                     │
  │  [Display Error Messages]           │
  │  [Highlight Invalid Fields]         │
  │                                     │
```

---

**Visual Guide for Task 2.1 Implementation**
