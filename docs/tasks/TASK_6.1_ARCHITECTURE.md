# Task 6.1: Resume Text Extraction - Technical Architecture

## System Overview

Task 6.1 implements a comprehensive resume analysis system that extracts, categorizes, and analyzes skills and keywords from resumes, comparing them with job postings to provide actionable insights.

```
┌─────────────────────────────────────────────────────────────┐
│                     Resume Analysis System                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │   Resume     │      │   Skills     │      │   Job    │ │
│  │   Upload     │──────│  Extraction  │──────│Comparison│ │
│  │   (PDF/DOCX) │      │  & Analysis  │      │& Scoring │ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│         │                      │                    │      │
│         ▼                      ▼                    ▼      │
│  ┌──────────────────────────────────────────────────────┐ │
│  │          Resume Analyzer (Core Module)               │ │
│  │  - Keyword Extraction  - Section Identification      │ │
│  │  - Contact Extraction  - Experience Analysis         │ │
│  │  - Skill Categorization                              │ │
│  └──────────────────────────────────────────────────────┘ │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Keyword Extractor (NLP Engine)               │ │
│  │  - spaCy NLP Processing                              │ │
│  │  - Technical/Soft Skill Detection                    │ │
│  │  - Keyword Matching & Scoring                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Resume Analyzer Module (`resume_analyzer.py`)

The core module responsible for resume analysis and job comparison.

```python
class ResumeAnalyzer:
    """
    Main class for resume analysis.
    Coordinates keyword extraction, skill categorization, and job matching.
    """
    
    RESUME_SECTIONS = {
        'education': [...],
        'experience': [...],
        'skills': [...],
        'projects': [...],
        'certifications': [...],
        'achievements': [...]
    }
```

#### Key Components:

**A. Keyword Extraction**
```python
def extract_resume_keywords(resume_text, top_n=50) -> Dict:
    """
    Extracts comprehensive keyword data from resume.
    
    Returns:
    - all_keywords: Top N keywords with frequency
    - technical_skills: Identified technical skills
    - soft_skills: Identified soft skills
    - sections_found: Detected resume sections
    - contact_info: Extracted contact details
    - experience_indicators: Experience level analysis
    """
```

**B. Skills Categorization**
```python
def extract_skills_from_list(skills_list) -> Dict:
    """
    Categorizes skills into technical, soft, and general.
    
    Process:
    1. Parse skill list
    2. Categorize each skill using keyword extractor
    3. Deduplicate and sort
    4. Return categorized results
    """
```

**C. Resume-Job Comparison**
```python
def compare_resume_with_job(resume_keywords, job_keywords) -> Dict:
    """
    Compares resume with job and generates recommendations.
    
    Calculation:
    weighted_score = (tech_match * 0.6) + 
                    (soft_match * 0.2) + 
                    (overall_match * 0.2)
    
    Returns:
    - match_result: Detailed matching statistics
    - critical_missing_keywords: Top missing keywords
    - weighted_match_score: Overall score (0-100)
    - match_level: excellent/good/fair/poor
    - recommendations: Actionable suggestions
    """
```

### 2. Keyword Extractor Integration (`keyword_extractor.py`)

Leverages existing NLP infrastructure:

```python
class KeywordExtractor:
    """
    NLP-based keyword extraction using spaCy.
    Shared between resume analysis and job analysis.
    """
    
    # Skill databases
    TECH_SKILLS = {'python', 'java', 'aws', ...}  # 50+ skills
    SOFT_SKILLS = {'leadership', 'communication', ...}  # 15+ skills
    
    def extract_keywords(text, top_n, include_bigrams) -> List[Dict]
    def extract_skills(text) -> Dict
    def calculate_keyword_match(job_kw, resume_kw) -> Dict
```

### 3. API Layer (`app.py`)

RESTful endpoints for resume analysis:

```python
# Core endpoints
POST   /api/analyze-resume              # Analyze resume text
GET    /api/analyze-resume/{id}         # Analyze uploaded resume
POST   /api/extract-skills-from-list    # Categorize skills list
POST   /api/compare-resume-with-job     # Compare resume with job
GET    /api/get-skill-categories        # Get skill examples

# Advanced endpoints
POST   /api/batch-analyze-resumes       # Batch analysis
POST   /api/resume-job-match-report     # Generate match report
```

## Data Flow

### Flow 1: Resume Upload and Analysis

```
User uploads PDF/DOCX
       ↓
app.py: /api/resume-upload
       ↓
Extract text (PyPDF2/python-docx)
       ↓
Store in resume_store {id → data}
       ↓
User calls /api/analyze-resume/{id}
       ↓
ResumeAnalyzer.extract_resume_keywords()
       ↓
KeywordExtractor.extract_keywords()
       ↓
spaCy NLP processing
       ↓
Categorize & analyze
       ↓
Return comprehensive analysis
```

### Flow 2: Direct Skills Input

```
User provides skills list
       ↓
app.py: /api/extract-skills-from-list
       ↓
ResumeAnalyzer.extract_skills_from_list()
       ↓
For each skill:
  - KeywordExtractor._categorize_keyword()
  - Classify as technical/soft/general
       ↓
Deduplicate and sort
       ↓
Return categorized skills
```

### Flow 3: Resume-Job Comparison

```
User provides resume_id + job_id
       ↓
Retrieve resume from resume_store
Retrieve job from JobStorageManager
       ↓
Extract keywords from both:
  - ResumeAnalyzer.extract_resume_keywords()
  - KeywordExtractor.extract_job_keywords()
       ↓
ResumeAnalyzer.compare_resume_with_job()
       ↓
Calculate matches:
  - Technical skills match
  - Soft skills match
  - Overall keyword match
       ↓
Compute weighted score
       ↓
Generate recommendations
       ↓
Return comparison results
```

## Algorithm Details

### Keyword Extraction Algorithm

```python
# Step 1: Preprocess text
text = preprocess_text(resume_text)
  - Convert to lowercase
  - Remove URLs, emails
  - Remove special characters
  - Normalize whitespace

# Step 2: NLP processing
doc = spacy_nlp(text)

# Step 3: Extract tokens
for token in doc:
    if token.pos_ in ['NOUN', 'PROPN', 'ADJ']:
        if not token.is_stop and len(token) > 2:
            keywords.append(token.lemma_)

# Step 4: Extract bigrams
for i in range(len(doc) - 1):
    if match_bigram_pattern(doc[i], doc[i+1]):
        bigrams.append(f"{doc[i].text} {doc[i+1].text}")

# Step 5: Count and categorize
keyword_counts = Counter(keywords + bigrams)
categorized = [
    {
        'keyword': kw,
        'count': count,
        'type': categorize_keyword(kw)
    }
    for kw, count in keyword_counts.most_common(top_n)
]
```

### Match Score Calculation

```python
# Technical skills match
tech_matched = job_tech_skills ∩ resume_tech_skills
tech_match_pct = |tech_matched| / |job_tech_skills| × 100

# Soft skills match
soft_matched = job_soft_skills ∩ resume_soft_skills
soft_match_pct = |soft_matched| / |job_soft_skills| × 100

# Overall keyword match
kw_matched = job_keywords ∩ resume_keywords
overall_match_pct = |kw_matched| / |job_keywords| × 100

# Weighted score (technical skills weighted more)
weighted_score = (tech_match_pct × 0.6) + 
                (soft_match_pct × 0.2) + 
                (overall_match_pct × 0.2)

# Match level classification
if weighted_score >= 75: return 'excellent'
elif weighted_score >= 60: return 'good'
elif weighted_score >= 40: return 'fair'
else: return 'poor'
```

### Section Identification Algorithm

```python
RESUME_SECTIONS = {
    'education': ['education', 'academic', 'degree', ...],
    'experience': ['experience', 'work history', ...],
    ...
}

def identify_sections(resume_text):
    text_lower = resume_text.lower()
    sections_found = {}
    
    for section_name, keywords in RESUME_SECTIONS.items():
        # Section found if any keyword present
        found = any(keyword in text_lower for keyword in keywords)
        sections_found[section_name] = found
    
    return sections_found
```

### Contact Information Extraction

```python
# Email pattern
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Phone pattern (various formats)
phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

# LinkedIn pattern
linkedin_pattern = r'linkedin\.com/in/[\w-]+'

# GitHub pattern
github_pattern = r'github\.com/[\w-]+'

# Extract using regex
contact_info = {
    'email': re.search(email_pattern, text),
    'phone': re.search(phone_pattern, text),
    'linkedin': re.search(linkedin_pattern, text, re.IGNORECASE),
    'github': re.search(github_pattern, text, re.IGNORECASE)
}
```

## Design Patterns

### 1. Singleton Pattern
```python
_analyzer_instance = None

def get_resume_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ResumeAnalyzer()
    return _analyzer_instance
```

**Rationale:** Reuse expensive spaCy model loading across requests.

### 2. Strategy Pattern
```python
# Different extraction strategies based on input type
if isinstance(input, str):
    # Text-based extraction
    result = extract_resume_keywords(input)
elif isinstance(input, list):
    # List-based extraction
    result = extract_skills_from_list(input)
```

### 3. Template Method Pattern
```python
def compare_resume_with_job(resume_kw, job_kw):
    # Template steps
    match_result = calculate_keyword_match(job_kw, resume_kw)
    critical_missing = identify_critical_missing(...)
    weighted_score = calculate_weighted_score(...)
    recommendations = generate_recommendations(...)
    return compile_results(...)
```

## Performance Optimizations

### 1. Model Caching
- spaCy model loaded once and reused
- Singleton pattern prevents repeated initialization
- ~2-3 second improvement per request

### 2. Batch Processing
- `batch_analyze_resumes`: Process multiple resumes in one request
- `resume_job_match_report`: Generate reports for multiple jobs efficiently
- Reduces HTTP overhead

### 3. Preprocessing Efficiency
- Text cleaning done once before NLP processing
- Compiled regex patterns reused
- Keyword categorization cached

### 4. Filtering
- `min_score` parameter filters low-match jobs early
- Reduces result set size
- Improves response time

## Data Structures

### Resume Analysis Result
```python
{
    'all_keywords': [
        {'keyword': 'python', 'count': 5, 'type': 'technical'},
        ...
    ],
    'technical_skills': ['python', 'aws', ...],
    'soft_skills': ['leadership', ...],
    'sections_found': {'education': True, ...},
    'contact_info': {'email': '...', ...},
    'experience_indicators': {
        'estimated_level': 'senior',
        'years_mentioned_count': 3,
        ...
    }
}
```

### Comparison Result
```python
{
    'match_result': {
        'technical_match': {
            'matched': ['python', 'aws'],
            'missing': ['kubernetes'],
            'match_percentage': 75.0,
            'count': 6
        },
        'soft_skills_match': {...},
        'overall_match': {...}
    },
    'critical_missing_keywords': ['kubernetes', 'terraform'],
    'weighted_match_score': 72.5,
    'match_level': 'good',
    'recommendations': [...]
}
```

## Integration Points

### With Existing Modules

1. **keyword_extractor.py**: Shared NLP infrastructure
2. **job_scorer.py**: Compatible scoring mechanisms
3. **storage_manager.py**: Job data retrieval
4. **app.py**: Resume upload and storage

### External Dependencies

- **spaCy**: NLP processing (`en_core_web_sm` model)
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX text extraction
- **re**: Regular expressions for pattern matching

## Security Considerations

1. **File Upload Validation**: Only PDF/DOCX allowed
2. **File Size Limits**: Max 10MB
3. **Secure Filenames**: Uses `secure_filename()` from werkzeug
4. **Input Validation**: Text length and format validation
5. **Error Handling**: Graceful error messages without exposing internals

## Scalability Considerations

1. **Stateless Design**: No session state, supports horizontal scaling
2. **Database Ready**: Can migrate from in-memory to database storage
3. **Async Processing**: Background jobs for batch operations (future)
4. **Caching Layer**: Redis for frequently accessed analyses (future)

## Testing Strategy

- **Unit Tests**: 17 test cases covering all methods
- **Integration Tests**: End-to-end workflows
- **Edge Cases**: Empty inputs, special characters, malformed data
- **Performance Tests**: Response time validation

## Error Handling Strategy

```python
try:
    result = analyzer.extract_resume_keywords(text)
except ValueError as e:
    return {"success": False, "message": str(e)}, 400
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    return {"success": False, "message": "Internal error"}, 500
```

## Monitoring and Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.info("ResumeAnalyzer initialized")
logger.error(f"Error comparing resume {resume_id}: {str(e)}")
```

## Future Architecture Enhancements

1. **Microservices**: Separate resume analysis service
2. **Message Queue**: RabbitMQ for async processing
3. **Caching**: Redis for analysis results
4. **Database**: PostgreSQL for persistent storage
5. **Machine Learning**: Custom skill classification model
6. **API Gateway**: Rate limiting and authentication

---

**Architecture Version:** 1.0  
**Last Updated:** November 13, 2025  
**Authors:** AI Job Application Assistant Team
