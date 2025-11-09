# AI Job Application Assistant

An intelligent job search and application management system that helps users find, match, and track job opportunities.

## 📋 Project Overview

This application assists job seekers by:
- Collecting user preferences (location, salary, job titles, job types)
- Scraping job listings from multiple platforms
- Matching and scoring jobs based on user profile
- Providing resume optimization suggestions
- Tracking application status
- Exporting results to Excel/CSV

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- Node.js 16+
- pip/pip3
- npm

### Setup (Linux/Mac)

```bash
# Clone and navigate to project
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Run the Application

**Terminal 1 - Backend:**
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
source venv/bin/activate
cd backend
python app.py
```
Backend runs at: http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant/frontend
npm start
```
Frontend runs at: http://localhost:3000

### Quick Start (Windows PowerShell)

```powershell
# 1. Create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run backend (development)
$env:FLASK_APP = "backend/app.py"
flask run --host=0.0.0.0 --port=5000

# 4. In another terminal, run frontend
cd frontend
npm install
npm start
```

## 📁 Project Structure

```
Jobs_AI_Assistant/
├── backend/               # Flask backend
│   ├── app.py            # Main Flask app with API endpoints
│   ├── test_api.py       # API test suite
│   └── README.md
├── frontend/              # React frontend
│   ├── UserDetailsForm.jsx  # User input form component
│   ├── App.jsx           # App wrapper
│   ├── index.jsx         # React entry point
│   ├── package.json      # Frontend dependencies
│   └── TASK_2.1_README.md  # Frontend documentation
├── docs/                  # Project documentation
│   └── project_scope_and_requirements.md
├── requirements.txt       # Python dependencies
├── task.md               # Task breakdown and progress
├── design.md             # Design specifications
├── PRD.md                # Product Requirements Document
└── README.md             # This file
```

## 🎯 Current Progress

### ✅ Phase 1: Project Setup (Completed)
- [x] Project scope and requirements defined
- [x] Development environment setup
- [x] Backend scaffold (Flask)
- [x] Frontend scaffold (React)

### ✅ Phase 2: User Input Module (In Progress)
- [x] **Task 2.1: User Detail Input Forms** ✅ (Completed Nov 9, 2025)
  - Professional React form with Bootstrap
  - Client-side and server-side validation
  - RESTful API endpoints
  - [📖 See TASK_2.1_README.md for details](./TASK_2.1_README.md)
- [ ] Task 2.2: Job Type Selection Component
- [ ] Task 2.3: Resume Upload Functionality

### 📝 Next Steps
- Implement job type selection (Remote/Onsite/Hybrid)
- Add resume upload functionality
- Build job scraping module
- Develop matching and scoring algorithm

## 🔌 API Endpoints

### User Details
- `POST /api/user-details` - Submit user preferences
- `GET /api/user-details` - Get all user details
- `GET /api/user-details/<id>` - Get specific user

### Health Check
- `GET /health` - Backend health check
- `GET /` - API status

## 🧪 Testing

### Backend Tests
```bash
source venv/bin/activate
cd backend
python test_api.py
```

### Manual Testing
1. Start both backend and frontend
2. Navigate to http://localhost:3000
3. Fill and submit the user details form
4. Verify data is received and validated

## 📚 Documentation

- **Task Breakdown:** `task.md` - Detailed task list and progress
- **PRD:** `PRD.md` - Product requirements
- **Design:** `design.md` - UI/UX design specifications
- **Task 2.1 Complete Guide:** `TASK_2.1_README.md` - User input forms documentation
- **Quick Start:** `TASK_2.1_QUICKSTART.md` - Setup guide for Task 2.1
- **Architecture:** `TASK_2.1_ARCHITECTURE.md` - System design diagrams

## 🛠️ Technology Stack

**Backend:**
- Flask 2.2.5
- Flask-CORS 4.0.0
- BeautifulSoup4 (for scraping)
- Selenium (for dynamic scraping)
- spaCy (for NLP/matching)
- pandas (for data processing)
- openpyxl (for Excel export)

**Frontend:**
- React 18.2.0
- Bootstrap 5.3.0
- React Scripts 5.0.1

**Development:**
- Python 3.x
- Node.js 16+
- Git for version control

## 🔧 Development

### Adding a New Feature
1. Create a new branch from main
2. Implement the feature
3. Write tests
4. Update documentation
5. Submit for review

### Code Style
- Backend: Follow PEP 8
- Frontend: Follow React best practices
- Use meaningful variable names
- Comment complex logic

## 🐛 Troubleshooting

### Port Conflicts
```bash
# Kill process on port 5000 (backend)
sudo lsof -ti:5000 | xargs kill -9

# Kill process on port 3000 (frontend)
sudo lsof -ti:3000 | xargs kill -9
```

### Dependency Issues
```bash
# Backend
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Errors
- Ensure Flask-CORS is installed
- Restart both backend and frontend
- Check proxy configuration in `frontend/package.json`

## 📈 Roadmap

**Phase 3:** Job Scraping Module  
**Phase 4:** Data Processing and Filtering  
**Phase 5:** Job Matching and Scoring  
**Phase 6:** Resume Optimization  
**Phase 7:** Export and Import  
**Phase 8:** Application Tracker  
**Phase 9:** User Interface  
**Phase 10:** Testing and Documentation  
**Phase 11:** Deployment

See `task.md` for detailed timeline and tasks.

## 🤝 Contributing

This is an active development project. Check `task.md` for current tasks and progress.

## 📄 License

[Add license information]

## 📧 Contact

[Add contact information]

---

**Last Updated:** November 9, 2025  
**Current Phase:** Phase 2 - User Input Module  
**Latest Completion:** Task 2.1 - User Detail Input Forms ✅
