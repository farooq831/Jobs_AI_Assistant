# Task 6.1: Resume Text Extraction - Complete Documentation

## Overview
Task 6.1 implements comprehensive resume text extraction and analysis capabilities. This module enables the extraction of keywords from uploaded resumes or directly input skills, analyzes resume content, and compares resumes with job postings to provide actionable recommendations.

## Features

### 1. Resume Text Extraction
- **Comprehensive Keyword Extraction**: Extracts keywords, technical skills, and soft skills from resume text
- **Section Identification**: Automatically identifies resume sections (education, experience, skills, etc.)
- **Contact Information Extraction**: Extracts email, phone, LinkedIn, and GitHub URLs
- **Experience Level Analysis**: Analyzes indicators to estimate experience level (junior/mid/senior)

### 2. Direct Skills Input
- **Skills List Processing**: Accepts and categorizes a direct list of skills
- **Automatic Categorization**: Classifies skills as technical, soft, or general
- **Deduplication**: Removes duplicate skills automatically

### 3. Resume-Job Comparison
- **Keyword Matching**: Compares resume keywords with job requirements
- **Match Scoring**: Calculates weighted match scores
- **Gap Analysis**: Identifies missing skills and critical keywords
- **Recommendations**: Generates actionable recommendations for resume improvement

### 4. Batch Processing
- **Multiple Resume Analysis**: Analyze multiple resumes at once
- **Job Match Reports**: Generate comprehensive match reports against multiple jobs
- **Filtering**: Filter match results by minimum score threshold

## API Endpoints

### 1. Analyze Resume Text
```bash
POST /api/analyze-resume
```

**Request Body:**
```json
{
  "resume_text": "Full resume text content...",
  "resume_id": "optional-identifier",
  "top_n": 50
}
```

**Response:**
```json
{
  "success": true,
  "resume_id": "optional-identifier",
  "analysis": {
    "all_keywords": [...],
    "technical_skills": ["python", "javascript", "aws", ...],
    "soft_skills": ["leadership", "communication", ...],
    "keyword_count": 45,
    "sections_found": {
      "education": true,
      "experience": true,
      "skills": true,
      ...
    },
    "contact_info": {
      "email": "john@example.com",
      "phone": "(555) 123-4567",
      "linkedin": "linkedin.com/in/johndoe",
      "github": "github.com/johndoe"
    },
    "experience_indicators": {
      "years_mentioned_count": 3,
      "estimated_level": "senior"
    },
    "resume_length": 2500,
    "word_count": 420
  },
  "message": "Resume analyzed successfully"
}
```

### 2. Analyze Uploaded Resume
```bash
GET /api/analyze-resume/{resume_id}?top_n=50
```

Analyzes a resume that was previously uploaded through the `/api/resume-upload` endpoint.

### 3. Extract Skills from List
```bash
POST /api/extract-skills-from-list
```

**Request Body:**
```json
{
  "skills": ["Python", "JavaScript", "Leadership", "AWS", "Docker", ...]
}
```

**Response:**
```json
{
  "success": true,
  "categorized_skills": {
    "total_skills": 10,
    "technical_skills": ["Python", "JavaScript", "AWS", "Docker"],
    "soft_skills": ["Leadership"],
    "general_skills": [...],
    "all_skills": [...]
  },
  "message": "Skills extracted and categorized successfully"
}
```

### 4. Compare Resume with Job
```bash
POST /api/compare-resume-with-job
```

**Request Body (Option 1 - Direct keywords):**
```json
{
  "resume_keywords": {...},
  "job_keywords": {...}
}
```

**Request Body (Option 2 - By IDs):**
```json
{
  "resume_id": 123,
  "job_id": "job-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "comparison": {
    "match_result": {
      "technical_match": {
        "matched": ["python", "aws", "docker"],
        "missing": ["kubernetes", "terraform"],
        "match_percentage": 75.5,
        "count": 6
      },
      "soft_skills_match": {
        "matched": ["leadership", "communication"],
        "missing": ["teamwork"],
        "match_percentage": 66.7,
        "count": 2
      },
      "overall_match": {
        "matched_keywords": [...],
        "match_percentage": 68.4,
        "count": 15
      }
    },
    "critical_missing_keywords": ["kubernetes", "microservices"],
    "weighted_match_score": 72.3,
    "match_level": "good",
    "recommendations": [
      "Add more technical skills to your resume...",
      "Consider adding these technical skills: kubernetes, terraform",
      ...
    ]
  },
  "message": "Resume and job compared successfully"
}
```

### 5. Get Skill Categories
```bash
GET /api/get-skill-categories
```

Returns examples of technical and soft skills for reference.

### 6. Batch Analyze Resumes
```bash
POST /api/batch-analyze-resumes
```

**Request Body:**
```json
{
  "resume_ids": [1, 2, 3, 4, 5]
}
```

Analyzes multiple resumes at once and returns results for each.

### 7. Generate Resume-Job Match Report
```bash
POST /api/resume-job-match-report
```

**Request Body:**
```json
{
  "resume_id": 123,
  "job_ids": ["job-1", "job-2"],
  "min_score": 40
}
```

**Response:**
```json
{
  "success": true,
  "resume_id": 123,
  "resume_filename": "john_doe_resume.pdf",
  "total_jobs_analyzed": 50,
  "matching_jobs": 12,
  "match_reports": [
    {
      "job_id": "job-1",
      "job_title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "match_score": 85.5,
      "match_level": "excellent",
      "technical_match": 90.0,
      "soft_skills_match": 75.0,
      "recommendations": [...]
    },
    ...
  ],
  "message": "Generated match report for 12 jobs"
}
```

## Module Architecture

### ResumeAnalyzer Class

```python
class ResumeAnalyzer:
    """Analyzes resume text to extract keywords, skills, and provide insights."""
    
    # Main methods
    def extract_resume_keywords(resume_text, top_n=50) -> Dict
    def extract_skills_from_list(skills_list) -> Dict
    def compare_resume_with_job(resume_keywords, job_keywords) -> Dict
    def get_skill_categories() -> Dict
    
    # Helper methods
    def _identify_sections(resume_text) -> Dict
    def _extract_contact_info(resume_text) -> Dict
    def _analyze_experience_level(resume_text) -> Dict
    def _generate_recommendations(match_result, critical_missing) -> List
    def _get_match_level(score) -> str
```

### Integration with Existing Modules

- **keyword_extractor.py**: Leverages KeywordExtractor for NLP-based keyword extraction
- **job_scorer.py**: Compatible with job scoring for end-to-end job matching
- **storage_manager.py**: Integrates with job and resume storage
- **app.py**: Provides RESTful API endpoints for all functionality

## Usage Examples

### Example 1: Upload and Analyze Resume
```python
import requests

# Upload resume
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/resume-upload',
        files={'resume': f}
    )
    resume_id = response.json()['resume_id']

# Analyze resume
response = requests.get(
    f'http://localhost:5000/api/analyze-resume/{resume_id}'
)
analysis = response.json()['analysis']

print(f"Technical Skills: {analysis['technical_skills']}")
print(f"Experience Level: {analysis['experience_indicators']['estimated_level']}")
```

### Example 2: Direct Skills Input
```python
import requests

skills = ['Python', 'React', 'AWS', 'Leadership', 'Docker']

response = requests.post(
    'http://localhost:5000/api/extract-skills-from-list',
    json={'skills': skills}
)

categorized = response.json()['categorized_skills']
print(f"Technical: {categorized['technical_skills']}")
print(f"Soft Skills: {categorized['soft_skills']}")
```

### Example 3: Compare Resume with Job
```python
import requests

response = requests.post(
    'http://localhost:5000/api/compare-resume-with-job',
    json={
        'resume_id': 1,
        'job_id': 'job-123'
    }
)

comparison = response.json()['comparison']
print(f"Match Score: {comparison['weighted_match_score']}%")
print(f"Match Level: {comparison['match_level']}")
print("Recommendations:")
for rec in comparison['recommendations']:
    print(f"  - {rec}")
```

### Example 4: Generate Match Report
```python
import requests

response = requests.post(
    'http://localhost:5000/api/resume-job-match-report',
    json={
        'resume_id': 1,
        'min_score': 50
    }
)

report = response.json()
print(f"Matching Jobs: {report['matching_jobs']} out of {report['total_jobs_analyzed']}")

for match in report['match_reports'][:5]:
    print(f"\nJob: {match['job_title']} at {match['company']}")
    print(f"Match Score: {match['match_score']}%")
```

## Testing

### Run Tests
```bash
cd backend
python test_resume_analyzer.py
```

### Test Coverage
- Resume keyword extraction (17 test cases)
- Skills list processing
- Resume-job comparison
- Contact information extraction
- Experience level analysis
- Recommendation generation
- Integration tests
- Edge cases and error handling

## Dependencies

- **spacy**: NLP processing and keyword extraction
- **keyword_extractor**: Existing keyword extraction module
- **re**: Regular expression for pattern matching
- **collections.Counter**: Frequency counting

## Error Handling

The module includes comprehensive error handling:
- Validates resume text length (minimum 50 characters)
- Validates skills list (non-empty)
- Handles missing resumes/jobs gracefully
- Provides meaningful error messages

## Performance Considerations

- **Singleton Pattern**: Uses singleton for ResumeAnalyzer to reuse spaCy models
- **Efficient Processing**: Batch operations for multiple resumes
- **Caching**: Keyword extraction results can be cached
- **Filtering**: Min score threshold to reduce result set size

## Future Enhancements

- Resume parsing from different formats (HTML, RTF)
- Multi-language support
- Resume quality scoring
- ATS (Applicant Tracking System) optimization suggestions
- Custom keyword dictionaries
- Industry-specific skill categorization

## Related Documentation

- [TASK_6.1_QUICKSTART.md](./TASK_6.1_QUICKSTART.md) - 5-minute quick start guide
- [TASK_6.1_ARCHITECTURE.md](./TASK_6.1_ARCHITECTURE.md) - Technical architecture
- [TASK_6.1_COMPLETION.md](./TASK_6.1_COMPLETION.md) - Implementation summary
- [TASK_6.1_CHECKLIST.md](./TASK_6.1_CHECKLIST.md) - Verification checklist

## Support

For issues or questions:
1. Check the quickstart guide for common setup issues
2. Review test cases for usage examples
3. Check error messages for specific issues
4. Refer to architecture documentation for design details
