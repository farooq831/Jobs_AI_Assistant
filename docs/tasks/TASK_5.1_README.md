# Task 5.1: Keyword Extraction - Complete Documentation

## Overview

Task 5.1 implements intelligent keyword extraction from job postings and resumes using Natural Language Processing (NLP). This module uses spaCy to tokenize text, extract relevant keywords, identify technical and soft skills, and calculate keyword match scores between jobs and resumes.

## Features

### 1. **Job Keyword Extraction**
- Extracts keywords from job titles and descriptions
- Identifies technical skills (Python, React, AWS, etc.)
- Identifies soft skills (leadership, communication, etc.)
- Categorizes keywords by type (technical, soft skill, general)
- Extracts common two-word phrases (bigrams) like "machine learning"

### 2. **Resume Keyword Extraction**
- Extracts keywords from resume text
- Identifies candidate skills and competencies
- Analyzes resume content structure
- Provides comprehensive skill profiles

### 3. **Keyword Matching**
- Calculates match percentage between job and resume
- Identifies matched skills
- Highlights missing skills
- Provides detailed match statistics

### 4. **Batch Processing**
- Process multiple jobs at once
- Efficient keyword extraction pipeline
- Bulk analysis capabilities

## Architecture

```
backend/
├── keyword_extractor.py      # Core NLP module
├── app.py                     # API endpoints
└── test_keyword_extraction.py # Test suite
```

### Core Components

#### `KeywordExtractor` Class
Main class handling all keyword extraction logic:
- **`extract_keywords()`**: Extract keywords from any text
- **`extract_skills()`**: Extract technical and soft skills
- **`extract_job_keywords()`**: Specialized job posting extraction
- **`extract_resume_keywords()`**: Specialized resume extraction
- **`calculate_keyword_match()`**: Match calculation between job and resume

## API Endpoints

### 1. Extract Keywords from Job
```http
POST /api/extract-keywords/job
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "description": "We are looking for an experienced Python developer...",
  "job_id": "optional-id"
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "optional-id",
  "keywords": {
    "all_keywords": [
      {"keyword": "python", "count": 5, "type": "technical"},
      {"keyword": "developer", "count": 3, "type": "general"}
    ],
    "title_keywords": [...],
    "technical_skills": ["python", "django", "aws"],
    "soft_skills": ["leadership", "communication"],
    "keyword_count": 25
  }
}
```

### 2. Extract Keywords from Resume
```http
POST /api/extract-keywords/resume
Content-Type: application/json

{
  "resume_text": "Senior Software Engineer with 5+ years...",
  "resume_id": "optional-id"
}
```

**Response:**
```json
{
  "success": true,
  "resume_id": "optional-id",
  "keywords": {
    "all_keywords": [...],
    "technical_skills": ["python", "react", "docker"],
    "soft_skills": ["teamwork", "problem solving"],
    "keyword_count": 45
  }
}
```

### 3. Extract Keywords from Stored Resume
```http
GET /api/extract-keywords/resume/<resume_id>
```

Extracts keywords from a previously uploaded resume.

### 4. Calculate Keyword Match
```http
POST /api/match-keywords
Content-Type: application/json

{
  "job_keywords": {...},
  "resume_keywords": {...}
}
```

Or use stored job and resume:
```json
{
  "job_id": "job-123",
  "resume_id": "resume-456"
}
```

**Response:**
```json
{
  "success": true,
  "match_result": {
    "technical_match": {
      "matched": ["python", "django"],
      "missing": ["aws", "docker"],
      "match_percentage": 40.0,
      "count": 2
    },
    "soft_skills_match": {
      "matched": ["leadership"],
      "missing": ["communication"],
      "match_percentage": 50.0,
      "count": 1
    },
    "overall_match": {
      "matched_keywords": ["python", "developer", "engineer"],
      "match_percentage": 35.5,
      "count": 3
    }
  }
}
```

### 5. Batch Extract Job Keywords
```http
POST /api/batch-extract-keywords/jobs
Content-Type: application/json

{
  "job_ids": ["job1", "job2"],  // Optional
  "limit": 10                    // Optional
}
```

## Usage Examples

### Python Code Examples

#### 1. Basic Keyword Extraction
```python
from keyword_extractor import KeywordExtractor

extractor = KeywordExtractor()

# Extract from job
job_text = "We need a Python developer with React experience"
keywords = extractor.extract_keywords(job_text)

for kw in keywords[:5]:
    print(f"{kw['keyword']} ({kw['type']}): {kw['count']} occurrences")
```

#### 2. Extract Job Keywords
```python
job_data = {
    'title': 'Senior Full Stack Developer',
    'description': '''
        Looking for an experienced developer...
        Required: Python, React, PostgreSQL
        Nice to have: AWS, Docker
    '''
}

result = extractor.extract_job_keywords(job_data)
print(f"Technical skills: {result['technical_skills']}")
print(f"Soft skills: {result['soft_skills']}")
```

#### 3. Match Job and Resume
```python
# Extract from both
job_keywords = extractor.extract_job_keywords(job_data)
resume_keywords = extractor.extract_resume_keywords(resume_text)

# Calculate match
match = extractor.calculate_keyword_match(job_keywords, resume_keywords)

print(f"Technical match: {match['technical_match']['match_percentage']}%")
print(f"Missing skills: {match['technical_match']['missing']}")
```

### cURL Examples

#### Extract Job Keywords
```bash
curl -X POST http://localhost:5000/api/extract-keywords/job \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer",
    "description": "We need a skilled Python developer with Django experience"
  }'
```

#### Extract Resume Keywords
```bash
curl -X POST http://localhost:5000/api/extract-keywords/resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Software Engineer with 5+ years of Python and React experience. Led teams of 5 developers."
  }'
```

#### Match Keywords
```bash
curl -X POST http://localhost:5000/api/match-keywords \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job-123",
    "resume_id": "resume-456"
  }'
```

## NLP Features

### Text Preprocessing
- Lowercase conversion
- URL removal
- Email address removal
- Special character handling
- Whitespace normalization

### Token Analysis
- Part-of-speech (POS) tagging
- Lemmatization
- Stop word filtering
- Custom domain-specific stop words

### Skill Recognition
**Technical Skills Database:**
- Programming languages (Python, Java, JavaScript, etc.)
- Frameworks (React, Django, Flask, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- Cloud platforms (AWS, Azure, GCP, etc.)
- Tools and technologies (Docker, Kubernetes, Git, etc.)
- Data science (TensorFlow, PyTorch, Pandas, etc.)

**Soft Skills Database:**
- Leadership, communication, teamwork
- Problem solving, analytical thinking
- Creativity, adaptability, organization
- And more...

### Bigram Extraction
Automatically identifies important two-word phrases:
- "machine learning"
- "deep learning"
- "data science"
- "full stack"
- "front end"
- "web development"

## Configuration

### spaCy Model
The module uses the `en_core_web_sm` model. If not installed, it will automatically download on first use.

### Customization
You can extend the skill databases by modifying:
```python
KeywordExtractor.TECH_SKILLS
KeywordExtractor.SOFT_SKILLS
KeywordExtractor.STOPWORDS_CUSTOM
```

## Testing

Run the comprehensive test suite:
```bash
cd backend
python test_keyword_extraction.py
```

### Test Coverage
- ✅ Text preprocessing
- ✅ Keyword extraction
- ✅ Skill identification
- ✅ Keyword categorization
- ✅ Job keyword extraction
- ✅ Resume keyword extraction
- ✅ Keyword matching
- ✅ Empty text handling
- ✅ Bigram extraction
- ✅ API endpoints
- ✅ Error handling

## Performance

- **Single job extraction:** ~0.5-1 second
- **Single resume extraction:** ~1-2 seconds
- **Keyword matching:** ~0.1 seconds
- **Batch processing:** ~1 second per job

## Error Handling

All endpoints include comprehensive error handling:
- Missing or invalid data validation
- Text length validation (minimum 50 characters for resumes)
- Graceful handling of missing resources
- Detailed error messages

## Integration with Other Modules

### With Resume Upload (Task 2.3)
```python
# Upload resume → Extract text → Extract keywords
resume_id = upload_resume(file)
keywords = extract_keywords_from_stored_resume(resume_id)
```

### With Job Scraping (Task 3.x)
```python
# Scrape jobs → Extract keywords → Score matches
jobs = scrape_jobs()
for job in jobs:
    job['keywords'] = extractor.extract_job_keywords(job)
```

### With Job Scoring (Task 5.2 - Next)
```python
# Extract keywords → Calculate scores → Rank jobs
job_kw = extractor.extract_job_keywords(job)
resume_kw = extractor.extract_resume_keywords(resume)
match = extractor.calculate_keyword_match(job_kw, resume_kw)
score = calculate_final_score(match, salary, location, ...)
```

## Deliverables

- ✅ `backend/keyword_extractor.py` - Core NLP module (400+ lines)
- ✅ `backend/app.py` - Updated with 5 new endpoints
- ✅ `backend/test_keyword_extraction.py` - 15+ test cases
- ✅ Complete documentation set
- ✅ API endpoint integration

## Future Enhancements

1. **Custom Skill Training**: Train on company-specific skill requirements
2. **Synonym Matching**: Match "JavaScript" with "JS"
3. **Experience Level Detection**: Identify senior vs junior requirements
4. **Education Requirement Extraction**: Extract degree and certification needs
5. **Multi-language Support**: Extend beyond English

## Dependencies

- `spacy>=3.6.0` - NLP library
- `en_core_web_sm` - English language model

## Troubleshooting

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### Import Errors
Ensure you're in the backend directory and virtual environment is activated.

### Low Match Percentages
This is normal - real-world matches are typically 20-60%. The scoring algorithm in Task 5.2 will normalize these values.

## Support

For issues or questions:
1. Check the test suite for examples
2. Review the QUICKSTART guide
3. Examine the ARCHITECTURE document

---

**Task Status:** ✅ COMPLETED
**Implementation Date:** November 10, 2025
**Next Task:** Task 5.2 - Scoring Algorithm
