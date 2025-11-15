# 🚀 Quick Start Guide - AI Job Application Assistant

## ⚡ Fast Installation (5 Minutes)

### Step 1: Install pip
```bash
sudo apt update
sudo apt install python3-pip -y
```

### Step 2: Install Python Dependencies
```bash
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
pip3 install -r requirements.txt
```

### Step 3: Download NLP Model
```bash
python3 -m spacy download en_core_web_sm
```

### Step 4: Install Frontend Dependencies (if Node.js installed)
```bash
# Check Node.js
node --version

# If installed, run:
cd frontend
npm install
cd ..

# If NOT installed:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
cd frontend && npm install && cd ..
```

### Step 5: Start the Application
```bash
./quick_start.sh
```

**That's it!** Your application should open at http://localhost:3000

---

## 🎯 First Time Usage

### 1. Setup Your Profile (30 seconds)

When you first open the app, you'll see a form:

```
┌────────────────────────────────────────┐
│   Setup Your Job Search Profile        │
├────────────────────────────────────────┤
│                                         │
│   Name: [Your Name________________]    │
│                                         │
│   Location: [New York, NY________]     │
│                                         │
│   Salary Range:                        │
│   Min: [$80,000__] Max: [$120,000_]    │
│                                         │
│   Job Titles (one per line):           │
│   [Software Engineer______________]    │
│   [Full Stack Developer___________]    │
│   [+] Add more                          │
│                                         │
│   Upload Resume:                        │
│   [📄 Choose File] resume.pdf          │
│                                         │
│   [💾 Save Profile]                     │
│                                         │
└────────────────────────────────────────┘
```

**Fill in:**
- ✏️ Your full name
- 📍 Your preferred location
- 💰 Your salary expectations
- 📋 Job titles you're interested in
- 📄 Your resume (PDF or DOCX)

Click **Save Profile** ✓

---

### 2. Jobs Are Automatically Scraped

After saving your profile, the system will automatically:
- 🔍 Search Indeed for matching jobs
- 🔍 Search Glassdoor for matching jobs
- 🧹 Clean and filter the results
- 🎯 Score each job against your profile
- 🎨 Color-code them by match quality

This takes about 30-60 seconds depending on the number of job titles.

---

### 3. View Your Matched Jobs

You'll see a dashboard like this:

```
┌───────────────────────────────────────────────────────────────┐
│  AI Job Application Assistant                    [📤 Export]   │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  📊 Dashboard Stats:                                           │
│  Total Jobs: 156  |  Applied: 0  |  Interviews: 0             │
│                                                                │
│  🔍 Filters: [All Scores ▼] [All Status ▼] [🔄 Refresh]       │
│                                                                │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ⚪ Senior Software Engineer                         89%  ▓▓▓ │
│  🏢 Google  📍 New York, NY  💰 $120k-$180k                   │
│  Status: ⭕ Not Applied                                        │
│  We're looking for an experienced engineer with Python...     │
│  [📝 Update Status] [🔗 View Full Details]                    │
│                                                                │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ⚪ Full Stack Developer (Remote)                    76%  ▓▓▓ │
│  🏢 Amazon  📍 Remote  💰 $100k-$150k                         │
│  Status: ⭕ Not Applied                                        │
│  Join our cloud team building microservices with React...     │
│  [📝 Update Status] [🔗 View Full Details]                    │
│                                                                │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  🟡 Software Engineer II                             54%  ▓▓  │
│  🏢 Microsoft  📍 Seattle, WA  💰 $95k-$135k                  │
│  Status: ⭕ Not Applied                                        │
│  Looking for mid-level engineer to join our Azure team...     │
│  [📝 Update Status] [🔗 View Full Details]                    │
│                                                                │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  🔴 Junior Developer                                 22%  ▓    │
│  🏢 Startup Inc  📍 Austin, TX  💰 $50k-$70k                  │
│  Status: ⭕ Not Applied                                        │
│  Entry level position for recent graduates...                 │
│  [📝 Update Status] [🔗 View Full Details]                    │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

**Color Meanings:**
- ⚪ **WHITE** (70-100%): Excellent match! Apply immediately
- 🟡 **YELLOW** (30-70%): Fair match, worth considering
- 🔴 **RED** (0-30%): Poor match, probably skip

---

### 4. Update Application Status

When you apply to a job, click **Update Status**:

```
┌────────────────────────────────────────┐
│   Update Application Status             │
├────────────────────────────────────────┤
│                                         │
│   Job: Senior Software Engineer         │
│   Company: Google                       │
│                                         │
│   Status: [Applied ▼]                   │
│   • Not Applied                         │
│   • Applied                             │
│   • Interview Scheduled                 │
│   • Offer Received                      │
│   • Rejected                            │
│   • Withdrawn                           │
│                                         │
│   Application Date: [2025-11-15____]   │
│                                         │
│   Notes:                                │
│   [Applied via LinkedIn____________]    │
│   [Interview scheduled for Monday__]    │
│   [________________________________]    │
│                                         │
│   [💾 Save]  [❌ Cancel]                │
│                                         │
└────────────────────────────────────────┘
```

The job card will update to show:

```
│  ⚪ Senior Software Engineer                         89%  ▓▓▓ │
│  🏢 Google  📍 New York, NY  💰 $120k-$180k                   │
│  Status: 🟢 Applied (2025-11-15)                              │
│  Note: Applied via LinkedIn, Interview scheduled for Monday   │
```

---

### 5. Export Your Job List

Click **Export** to download your job list:

```
┌────────────────────────────────────────┐
│   Export Job Listings                   │
├────────────────────────────────────────┤
│                                         │
│   Choose Format:                        │
│   ⚪ Excel (.xlsx) - Best for analysis  │
│   ⚪ CSV (.csv) - For other tools       │
│   ⚪ PDF (.pdf) - For printing          │
│                                         │
│   Filter Options:                       │
│   ☑ Include all jobs                   │
│   ☐ Only white/yellow jobs              │
│   ☐ Only applied jobs                   │
│   ☐ Custom filter...                    │
│                                         │
│   Columns to Include:                   │
│   ☑ Job Title                           │
│   ☑ Company                             │
│   ☑ Location                            │
│   ☑ Salary                              │
│   ☑ Score                               │
│   ☑ Status                              │
│   ☑ Application Date                    │
│   ☑ Notes                               │
│                                         │
│   [📥 Download]  [❌ Cancel]            │
│                                         │
└────────────────────────────────────────┘
```

This creates a file like:
- `jobs_export_2025-11-15.xlsx`
- `jobs_export_2025-11-15.csv`
- `jobs_export_2025-11-15.pdf`

You can share this with career counselors or keep for your records!

---

## 🔧 Advanced Features

### Bulk Upload Jobs from Excel

If you already have a list of jobs in Excel:

```bash
# Your Excel file should have columns:
# Title | Company | Location | Salary | Description | URL
```

Click **Import** → Choose your Excel file → Jobs are added automatically!

### Custom Filters

Filter jobs by:
- Score range (e.g., only 70%+)
- Location (e.g., only Remote)
- Salary range (e.g., $100k+)
- Application status
- Company name

### Refresh Job Data

Click **🔄 Refresh** to scrape new jobs with your current preferences.

---

## 📊 Understanding Your Score

### How Jobs Are Scored

Each job gets a score from 0-100% based on:

**1. Keyword Match (50% of score)**
- How many skills from your resume match the job description
- Example: You have Python, React, AWS → Job needs Python, React, Docker
- Match: 2/3 = 67% → Contributes 33.5 points

**2. Salary Match (25% of score)**
- How well the job salary fits your range
- Example: You want $80k-$120k → Job offers $100k-$140k
- Overlap: $100k-$120k = good match → Contributes 20 points

**3. Location Match (15% of score)**
- Does the location match your preference
- Example: You want "New York, NY" → Job is in "New York, NY"
- Exact match → Contributes 15 points

**4. Job Type Match (10% of score)**
- Remote/Hybrid/Onsite preference
- Example: You prefer Remote → Job is Remote
- Perfect match → Contributes 10 points

**Total Example: 33.5 + 20 + 15 + 10 = 78.5% → WHITE ⚪**

---

## 🎨 UI Features

### Responsive Design

The app works on:
- 🖥️ **Desktop** (1920x1080+) - Full features
- 💻 **Laptop** (1366x768+) - Optimized layout
- 📱 **Tablet** (768px+) - Touch-friendly
- 📱 **Mobile** (320px+) - Essential features

### Dark Mode Support

The UI automatically adapts to your system theme preference.

### Keyboard Shortcuts

- `Ctrl + R` - Refresh jobs
- `Ctrl + E` - Export
- `Ctrl + F` - Focus filter
- `Esc` - Close modals

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
**Problem:** Frontend shows "Backend unavailable"
**Solution:**
```bash
# Check if backend is running
curl http://localhost:5000/health

# If not, start it:
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
python3 backend/app.py
```

### "No jobs found"
**Problem:** Dashboard shows "No jobs found"
**Solution:**
1. Check your internet connection
2. Try refreshing (🔄 button)
3. Adjust your search preferences (broader job titles)
4. Check backend logs: `cat backend.log`

### "Resume upload failed"
**Problem:** Can't upload resume
**Solution:**
1. Ensure file is PDF or DOCX (not .doc or .txt)
2. File size must be < 10MB
3. File must contain readable text (not scanned image)
4. Try re-saving your resume as PDF

### "Slow performance"
**Problem:** App is slow
**Solution:**
1. Clear old jobs: Settings → Clear Data
2. Reduce number of scraped pages (1-2 pages max)
3. Close other applications
4. Check system resources: `htop`

### "Port already in use"
**Problem:** "Address already in use" error
**Solution:**
```bash
# Kill processes on ports 5000 and 3000
lsof -ti:5000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Then restart
./quick_start.sh
```

---

## 📞 Getting Help

### Check Logs
```bash
# Backend logs
tail -f backend.log

# Frontend logs
tail -f frontend.log

# Error logs
cat data/errors.log
```

### Run Tests
```bash
cd backend
python3 run_all_tests.py
```

### Verify Installation
```bash
# Check Python packages
pip3 list | grep -i flask

# Check Node packages
cd frontend && npm list
```

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Flask not installed | `pip3 install flask` |
| `ModuleNotFoundError: No module named 'en_core_web_sm'` | spaCy model missing | `python3 -m spacy download en_core_web_sm` |
| `npm: command not found` | Node.js not installed | Install Node.js |
| `Port 5000 already in use` | Backend already running | Kill existing process |
| `CORS error` | Backend not running | Start backend server |

---

## 🎓 Best Practices

### For Job Hunting

1. **Keep Resume Updated**
   - Upload latest version regularly
   - Include all relevant skills
   - Use industry keywords

2. **Check Daily**
   - New jobs are added frequently
   - Set aside 30 minutes daily
   - Apply to white-coded jobs first

3. **Track Everything**
   - Update status immediately after applying
   - Add notes (contact person, how you applied)
   - Set reminders for follow-ups

4. **Use Exports**
   - Export weekly to track progress
   - Share with mentors/career coaches
   - Keep records for interviews

### For Best Results

1. **Be Specific with Job Titles**
   - Use exact titles from job postings
   - Include variations (e.g., "Software Engineer", "SWE", "Software Developer")

2. **Set Realistic Salary Range**
   - Research market rates for your role
   - Consider location cost of living
   - Don't filter too narrowly

3. **Review Yellow Jobs**
   - Don't ignore fair matches
   - Read full descriptions
   - You might qualify with learning

4. **Update Status Religiously**
   - Helps avoid duplicate applications
   - Track response rates
   - Identify patterns

---

## 🎉 Success Tips

### Week 1: Setup
- ✅ Install application
- ✅ Create profile
- ✅ Upload resume
- ✅ Review first 50 jobs
- ✅ Apply to 5 white-coded jobs

### Week 2-4: Active Hunting
- 📅 Check dashboard daily
- 📧 Apply to 10-15 jobs/week
- 📝 Follow up on applications
- 📊 Track interview invites
- 🔄 Refresh job list twice/week

### Week 4+: Optimization
- 📈 Review success rate
- 🎯 Focus on high-scoring jobs
- 💼 Network with companies
- 📚 Learn missing skills
- 🎨 Update resume for better matches

---

## 📈 Metrics to Track

The app automatically tracks:
- Total jobs found
- Jobs applied to
- Interview invitations
- Offers received
- Rejection rate
- Average match score
- Response time

Use these to:
- Identify which job titles work best
- See which locations have more opportunities
- Understand your competitive position
- Adjust your search strategy

---

## 🚀 Next Steps

Now that you've set up the application:

1. **✅ Complete your profile**
2. **✅ Upload your resume**
3. **✅ Review matched jobs**
4. **✅ Start applying!**

**Your AI-powered job search assistant is ready to help you land your dream job!** 🎯

---

**Need Help?** Check:
- 📖 Full Documentation: `README.md`
- 🏗️ Architecture: `ARCHITECTURE_DIAGRAM.md`
- 📊 Status Report: `APPLICATION_STATUS_REPORT.md`
- 🔧 Complete Guide: `COMPLETE_OVERVIEW.md`

**Ready to start?** Run: `./quick_start.sh` 🚀
