# Job Keyword Analysis - Task 6.2 README

This README provides quick reference information for the Job Keyword Analysis feature (Task 6.2).

---

## Quick Links

- **Detailed Documentation:** [TASK_6.2_COMPLETION_REPORT.md](TASK_6.2_COMPLETION_REPORT.md)
- **Quick Start Guide:** [TASK_6.2_QUICKSTART.md](TASK_6.2_QUICKSTART.md)
- **Combined Summary:** [TASK_6.1_6.2_SUMMARY.md](TASK_6.1_6.2_SUMMARY.md)
- **Completion Confirmation:** [COMPLETION_CONFIRMATION.md](COMPLETION_CONFIRMATION.md)

---

## What Does This Feature Do?

Analyzes multiple job postings to:
1. Identify high-frequency keywords (skills appearing in 50%+ of jobs)
2. Compare against your resume
3. Detect critical missing keywords
4. Generate priority-based recommendations

---

## Quick Start

### Start the API Server
```bash
cd backend
python3 app.py
```

### Analyze Job Keywords
```bash
curl -X POST http://localhost:5000/api/analyze-job-keywords \
  -H "Content-Type: application/json" \
  -d '{
    "job_descriptions": [
      "Senior Engineer with Python, AWS, Docker...",
      "Full Stack Developer - React, Node.js, AWS..."
    ],
    "resume_text": "Software Engineer with Python experience",
    "top_n": 20
  }'
```

---

## API Endpoints

### 1. Analyze Job Keywords
**POST** `/api/analyze-job-keywords`

Analyze custom job descriptions.

**Request:**
```json
{
  "job_descriptions": ["job1", "job2"],
  "resume_text": "your resume...",  // or "resume_id": 123
  "top_n": 30
}
```

### 2. Analyze Stored Jobs
**POST** `/api/analyze-job-keywords/stored-jobs`

Analyze jobs from the database.

**Request:**
```json
{
  "resume_id": 123,
  "job_ids": ["job-1", "job-2"],  // optional
  "top_n": 30
}
```

### 3. Missing Keywords Summary
**GET** `/api/missing-keywords-summary/<resume_id>`

Quick summary of critical missing keywords.

---

## Response Structure

```json
{
  "success": true,
  "analysis": {
    "analysis_summary": {
      "total_jobs_analyzed": 3,
      "technical_coverage_percentage": 65.5,
      "soft_skills_coverage_percentage": 42.0
    },
    "high_frequency_keywords": {
      "technical_skills": [
        {
          "keyword": "aws",
          "frequency": 3,
          "percentage": 100.0,
          "in_resume": false
        }
      ]
    },
    "missing_keywords": {
      "critical_technical": [...],
      "important_technical": [...]
    },
    "recommendations": [
      "🔴 HIGH PRIORITY: Add these critical technical skills...",
      "🟡 MEDIUM PRIORITY: Consider adding..."
    ]
  }
}
```

---

## Priority Levels

- **🔴 Critical:** Keywords in ≥50% of jobs, not in resume
- **🟡 Important:** Keywords in 30-49% of jobs, not in resume
- **✅ Success:** Good coverage (>70%)
- **⚠️ Warning:** Low coverage (<40%)

---

## Use Cases

### 1. Resume Optimization
Analyze target jobs → Identify missing skills → Update resume → Re-analyze

### 2. Skill Gap Analysis
Analyze 20+ jobs in your field → See most in-demand skills → Prioritize learning

### 3. Market Research
Compare different job markets → Identify trends → Plan career path

---

## Files

### Implementation
- `backend/resume_analyzer.py` - Core analysis logic
- `backend/app.py` - API endpoints
- `backend/test_job_keyword_analysis.py` - Test suite

### Documentation
- `TASK_6.2_COMPLETION_REPORT.md` - Detailed docs
- `TASK_6.2_QUICKSTART.md` - Quick start guide
- `TASK_6.1_6.2_SUMMARY.md` - Combined summary

---

## Testing

```bash
cd backend
python3 test_job_keyword_analysis.py
```

**Note:** Requires spaCy and other dependencies from `requirements.txt`

---

## Integration

Works with:
- Task 5.1 (Keyword Extraction)
- Task 6.1 (Resume Analysis)
- Job Storage Manager
- Scoring System

---

## Example Python Usage

```python
from resume_analyzer import get_resume_analyzer

analyzer = get_resume_analyzer()

result = analyzer.analyze_job_keywords(
    job_descriptions=["job1...", "job2..."],
    resume_text="my resume...",
    top_n=20
)

print(f"Coverage: {result['analysis_summary']['technical_coverage_percentage']}%")
print(f"Missing: {len(result['missing_keywords']['critical_technical'])} critical skills")
```

---

## Support

- See [TASK_6.2_QUICKSTART.md](TASK_6.2_QUICKSTART.md) for detailed usage
- See [TASK_6.2_COMPLETION_REPORT.md](TASK_6.2_COMPLETION_REPORT.md) for technical details
- Check test file for more examples

---

## Status

✅ **COMPLETED** - November 13, 2025  
✅ Production-ready  
✅ Fully tested  
✅ Comprehensively documented  

---

**Last Updated:** November 13, 2025
