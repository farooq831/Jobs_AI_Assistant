# Task 5.1: Keyword Extraction - 5-Minute Quickstart

Get up and running with keyword extraction in 5 minutes!

## Prerequisites

```bash
cd backend
pip install spacy
python -m spacy download en_core_web_sm
```

## Quick Start

### 1. Start the Flask Server

```bash
cd backend
python app.py
```

Server runs on `http://localhost:5000`

### 2. Test Job Keyword Extraction

**Python:**
```python
import requests

response = requests.post('http://localhost:5000/api/extract-keywords/job', json={
    'title': 'Senior Python Developer',
    'description': 'Looking for a Python developer with Django and AWS experience. Must have strong problem-solving skills.'
})

result = response.json()
print(f"Technical skills: {result['keywords']['technical_skills']}")
print(f"Soft skills: {result['keywords']['soft_skills']}")
```

**cURL:**
```bash
curl -X POST http://localhost:5000/api/extract-keywords/job \
  -H "Content-Type: application/json" \
  -d '{"title": "Python Developer", "description": "Need Python, Django, AWS skills"}'
```

### 3. Test Resume Keyword Extraction

```python
resume_text = """
Senior Software Engineer with 5 years of experience.
Skills: Python, JavaScript, React, Node.js, Docker, AWS
Led teams and mentored junior developers.
"""

response = requests.post('http://localhost:5000/api/extract-keywords/resume', json={
    'resume_text': resume_text
})

result = response.json()
print(f"Found {result['keywords']['keyword_count']} keywords")
print(f"Technical: {result['keywords']['technical_skills']}")
```

### 4. Calculate Match Score

```python
# First extract keywords from both
job_response = requests.post('http://localhost:5000/api/extract-keywords/job', json={
    'title': 'Python Developer',
    'description': 'Python, Django, AWS required'
})

resume_response = requests.post('http://localhost:5000/api/extract-keywords/resume', json={
    'resume_text': 'Senior Python Developer. Skills: Python, React, Docker'
})

# Then match them
match_response = requests.post('http://localhost:5000/api/match-keywords', json={
    'job_keywords': job_response.json()['keywords'],
    'resume_keywords': resume_response.json()['keywords']
})

match = match_response.json()['match_result']
print(f"Technical match: {match['technical_match']['match_percentage']}%")
print(f"Matched: {match['technical_match']['matched']}")
print(f"Missing: {match['technical_match']['missing']}")
```

## Run Tests

```bash
cd backend
python test_keyword_extraction.py
```

Expected output:
```
✓ KeywordExtractor initialization successful
✓ Text preprocessing working
✓ Extracted keywords from job description
✓ Technical skills found: ['python', 'javascript', 'react', ...]
✓ Soft skills found: ['leadership', 'communication', ...]
...
Tests run: 15
Successes: 15
```

## Quick Examples

### Extract from Existing Resume

If you uploaded a resume using Task 2.3:

```python
# Get keywords from stored resume
resume_id = "your-resume-id"
response = requests.get(f'http://localhost:5000/api/extract-keywords/resume/{resume_id}')

keywords = response.json()['keywords']
print(keywords['technical_skills'])
```

### Batch Process Jobs

```python
# Extract keywords from all stored jobs
response = requests.post('http://localhost:5000/api/batch-extract-keywords/jobs', json={
    'limit': 10  # Process first 10 jobs
})

results = response.json()
print(f"Processed {results['successful']} jobs successfully")
```

### Direct Python Usage

```python
from keyword_extractor import KeywordExtractor

extractor = KeywordExtractor()

# Extract keywords
keywords = extractor.extract_keywords("Python developer with AWS experience")

# Extract skills
skills = extractor.extract_skills("Need Python, React, leadership skills")

print(f"Technical: {skills['technical_skills']}")
print(f"Soft: {skills['soft_skills']}")
```

## Common Use Cases

### 1. Analyze Job Requirements
```python
job_keywords = extractor.extract_job_keywords({
    'title': 'Full Stack Developer',
    'description': 'React, Node.js, Python, PostgreSQL required'
})

print(f"This job requires {len(job_keywords['technical_skills'])} technical skills")
```

### 2. Resume Gap Analysis
```python
match = extractor.calculate_keyword_match(job_keywords, resume_keywords)
missing = match['technical_match']['missing']

print(f"Add these skills to your resume: {missing}")
```

### 3. Skill Frequency Analysis
```python
keywords = extractor.extract_keywords(job_description, top_n=20)

for kw in keywords:
    print(f"{kw['keyword']}: mentioned {kw['count']} times")
```

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/extract-keywords/job` | POST | Extract from job posting |
| `/api/extract-keywords/resume` | POST | Extract from resume text |
| `/api/extract-keywords/resume/<id>` | GET | Extract from stored resume |
| `/api/match-keywords` | POST | Calculate match score |
| `/api/batch-extract-keywords/jobs` | POST | Batch process jobs |

## Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'spacy'`
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

**Problem:** `OSError: [E050] Can't find model 'en_core_web_sm'`
```bash
python -m spacy download en_core_web_sm
```

**Problem:** Low match percentages
- This is normal! Real matches are typically 20-60%
- The scoring algorithm (Task 5.2) will normalize these

## Next Steps

1. ✅ Extract keywords from your resume
2. ✅ Extract keywords from job postings
3. ✅ Calculate match scores
4. ➡️ Proceed to Task 5.2: Implement scoring algorithm
5. ➡️ Integrate with job filtering (Task 4.2)

## Full Documentation

- **Complete Guide:** `TASK_5.1_README.md`
- **Architecture:** `TASK_5.1_ARCHITECTURE.md`
- **Implementation:** `TASK_5.1_COMPLETION.md`

---

**Ready to go! Start extracting keywords now! 🚀**
