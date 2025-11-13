# Task 6.1: Resume Text Extraction - Quick Start Guide

## 5-Minute Setup and Usage

### Prerequisites
- Python 3.8+
- Flask backend running
- Virtual environment activated
- Required packages installed

### Step 1: Install Dependencies (1 minute)

```bash
cd Jobs_AI_Assistant
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install spacy
python -m spacy download en_core_web_sm
```

### Step 2: Start the Backend (30 seconds)

```bash
cd backend
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### Step 3: Upload and Analyze a Resume (2 minutes)

#### Option A: Upload PDF/DOCX Resume

```bash
curl -X POST http://localhost:5000/api/resume-upload \
  -F "resume=@path/to/your/resume.pdf"
```

Response:
```json
{
  "success": true,
  "resume_id": 1,
  "filename": "resume.pdf",
  "text_preview": "John Doe..."
}
```

#### Analyze the Uploaded Resume

```bash
curl http://localhost:5000/api/analyze-resume/1
```

### Step 4: Direct Skills Input (1 minute)

```bash
curl -X POST http://localhost:5000/api/extract-skills-from-list \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "JavaScript", "React", "AWS", "Leadership", "Docker"]
  }'
```

Response:
```json
{
  "success": true,
  "categorized_skills": {
    "total_skills": 6,
    "technical_skills": ["Python", "JavaScript", "React", "AWS", "Docker"],
    "soft_skills": ["Leadership"],
    "all_skills": [...]
  }
}
```

### Step 5: Compare Resume with Job (1 minute)

```bash
curl -X POST http://localhost:5000/api/compare-resume-with-job \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": 1,
    "job_id": "job-123"
  }'
```

Response shows match score and recommendations:
```json
{
  "success": true,
  "comparison": {
    "weighted_match_score": 75.5,
    "match_level": "good",
    "recommendations": [
      "Your resume is well-matched to this job posting!",
      "Consider adding these technical skills: kubernetes, terraform"
    ]
  }
}
```

## Quick Test

Run the test suite to verify everything is working:

```bash
cd backend
python test_resume_analyzer.py
```

Expected output:
```
test_extract_resume_keywords_success ... ok
test_extract_skills_from_list ... ok
test_compare_resume_with_job ... ok
...
----------------------------------------------------------------------
Ran 17 tests in 5.234s

OK
```

## Common Use Cases

### Use Case 1: Analyze Your Resume

```python
import requests

# Read your resume file
with open('my_resume.pdf', 'rb') as f:
    # Upload
    response = requests.post(
        'http://localhost:5000/api/resume-upload',
        files={'resume': f}
    )
    resume_id = response.json()['resume_id']

# Analyze
response = requests.get(f'http://localhost:5000/api/analyze-resume/{resume_id}')
analysis = response.json()['analysis']

print("Your Technical Skills:")
for skill in analysis['technical_skills']:
    print(f"  - {skill}")

print(f"\nEstimated Experience Level: {analysis['experience_indicators']['estimated_level']}")
```

### Use Case 2: Get Job Match Report

```python
import requests

# Generate match report for all jobs
response = requests.post(
    'http://localhost:5000/api/resume-job-match-report',
    json={
        'resume_id': 1,
        'min_score': 50  # Only show jobs with 50%+ match
    }
)

report = response.json()
print(f"Found {report['matching_jobs']} matching jobs")

# Print top 3 matches
for job in report['match_reports'][:3]:
    print(f"\n{job['job_title']} at {job['company']}")
    print(f"Match: {job['match_score']}% ({job['match_level']})")
    print("Recommendations:")
    for rec in job['recommendations'][:2]:
        print(f"  - {rec}")
```

### Use Case 3: Input Skills Directly

```python
import requests

# Your skills
my_skills = [
    'Python', 'Django', 'React', 'PostgreSQL',
    'AWS', 'Docker', 'Git', 'Machine Learning',
    'Leadership', 'Communication'
]

# Categorize them
response = requests.post(
    'http://localhost:5000/api/extract-skills-from-list',
    json={'skills': my_skills}
)

result = response.json()['categorized_skills']
print(f"Technical Skills ({len(result['technical_skills'])}): {', '.join(result['technical_skills'])}")
print(f"Soft Skills ({len(result['soft_skills'])}): {', '.join(result['soft_skills'])}")
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'spacy'"

**Solution:**
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### Issue: "Resume text must be at least 50 characters"

**Solution:** Ensure your resume file contains actual text content. If uploading a scanned PDF, use OCR first.

### Issue: "Resume not found"

**Solution:** Make sure you've uploaded the resume first using `/api/resume-upload` before analyzing it.

### Issue: Backend not responding

**Solution:**
```bash
# Check if Flask is running
curl http://localhost:5000/health

# Restart the backend
cd backend
python app.py
```

## Next Steps

1. **Explore All Endpoints**: See [TASK_6.1_README.md](./TASK_6.1_README.md) for complete API documentation
2. **Understand Architecture**: Read [TASK_6.1_ARCHITECTURE.md](./TASK_6.1_ARCHITECTURE.md) for technical details
3. **Run Full Tests**: Execute `python test_resume_analyzer.py` for comprehensive testing
4. **Integrate with Frontend**: Use these APIs in your React frontend

## API Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/analyze-resume` | POST | Analyze resume text |
| `/api/analyze-resume/{id}` | GET | Analyze uploaded resume |
| `/api/extract-skills-from-list` | POST | Categorize skills list |
| `/api/compare-resume-with-job` | POST | Compare resume with job |
| `/api/resume-job-match-report` | POST | Generate match report |
| `/api/get-skill-categories` | GET | Get skill examples |
| `/api/batch-analyze-resumes` | POST | Analyze multiple resumes |

## Example Response Times

- Resume upload and text extraction: ~0.5-2 seconds
- Keyword analysis: ~0.3-1 second
- Job comparison: ~0.2-0.5 seconds
- Batch report generation (50 jobs): ~5-10 seconds

## Tips for Best Results

1. **Resume Quality**: Ensure resume is well-formatted with clear sections
2. **Text Content**: Use text-based PDFs, not scanned images
3. **Skills Lists**: Be specific (e.g., "React.js" not just "frontend")
4. **Batch Processing**: Use batch endpoints for multiple operations
5. **Caching**: Store analysis results to avoid re-processing

## Support Resources

- Full Documentation: `docs/tasks/TASK_6.1_README.md`
- Architecture Guide: `docs/tasks/TASK_6.1_ARCHITECTURE.md`
- Test Examples: `backend/test_resume_analyzer.py`
- API Reference: See README for complete endpoint list

---

**Estimated Setup Time:** 5 minutes  
**Difficulty Level:** Beginner  
**Prerequisites:** Basic Python and API knowledge
