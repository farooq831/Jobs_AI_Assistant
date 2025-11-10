# Task 5.1: Keyword Extraction - Technical Architecture

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend / Client                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask API Layer                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ /api/extract-keywords/job                            │   │
│  │ /api/extract-keywords/resume                         │   │
│  │ /api/extract-keywords/resume/<id>                    │   │
│  │ /api/match-keywords                                  │   │
│  │ /api/batch-extract-keywords/jobs                     │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Keyword Extractor Module                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  KeywordExtractor Class                              │   │
│  │  ├─ preprocess_text()                                │   │
│  │  ├─ extract_keywords()                               │   │
│  │  ├─ extract_skills()                                 │   │
│  │  ├─ extract_job_keywords()                           │   │
│  │  ├─ extract_resume_keywords()                        │   │
│  │  └─ calculate_keyword_match()                        │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    spaCy NLP Engine                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  English Language Model (en_core_web_sm)             │   │
│  │  ├─ Tokenization                                     │   │
│  │  ├─ Part-of-Speech Tagging                           │   │
│  │  ├─ Lemmatization                                    │   │
│  │  ├─ Named Entity Recognition                         │   │
│  │  └─ Dependency Parsing                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Module Architecture

### Core Components

#### 1. KeywordExtractor Class

**Purpose:** Central NLP processing unit for all keyword extraction operations.

**Design Pattern:** Singleton
- Single instance shared across application
- Loads spaCy model once
- Reduces memory footprint and initialization time

**Responsibilities:**
- Text preprocessing and normalization
- Keyword extraction using NLP
- Skill identification and categorization
- Match calculation between documents

**Key Attributes:**
```python
self.nlp                    # spaCy language model
self.TECH_SKILLS           # Set of technical skills
self.SOFT_SKILLS           # Set of soft skills
self.STOPWORDS_CUSTOM      # Domain-specific stop words
```

#### 2. Text Preprocessing Pipeline

```
Raw Text
    │
    ├─► Lowercase conversion
    │
    ├─► URL removal (http://, www.)
    │
    ├─► Email removal (user@domain.com)
    │
    ├─► Special character filtering
    │
    ├─► Whitespace normalization
    │
    └─► Cleaned Text
```

#### 3. Keyword Extraction Pipeline

```
Cleaned Text
    │
    ├─► spaCy NLP Processing
    │   ├─► Tokenization
    │   ├─► POS Tagging
    │   └─► Lemmatization
    │
    ├─► Token Filtering
    │   ├─► Keep: NOUN, PROPN, ADJ
    │   ├─► Remove: Stop words
    │   └─► Remove: Custom stop words
    │
    ├─► Bigram Extraction
    │   └─► Pattern matching (NOUN+NOUN, ADJ+NOUN)
    │
    ├─► Frequency Counting
    │
    ├─► Categorization
    │   ├─► Technical skills
    │   ├─► Soft skills
    │   └─► General keywords
    │
    └─► Top-N Selection
```

## Data Flow

### Job Keyword Extraction Flow

```
1. API Request
   ↓
2. Validate Input (title, description)
   ↓
3. Combine title + description
   ↓
4. Preprocess text
   ↓
5. Extract keywords (all)
   ↓
6. Extract title keywords (separate)
   ↓
7. Extract skills (technical + soft)
   ↓
8. Categorize and format results
   ↓
9. Return structured response
```

### Resume Keyword Extraction Flow

```
1. API Request (text or resume_id)
   ↓
2. Get resume text (direct or from storage)
   ↓
3. Validate text length (min 50 chars)
   ↓
4. Preprocess text
   ↓
5. Extract keywords
   ↓
6. Extract skills
   ↓
7. Format results
   ↓
8. Return structured response
```

### Keyword Matching Flow

```
1. API Request (keywords or IDs)
   ↓
2. Get job and resume keywords
   │   ├─► From request (direct)
   │   └─► From storage (IDs)
   ↓
3. Convert to sets for comparison
   │   ├─► job_tech_skills
   │   ├─► resume_tech_skills
   │   ├─► job_soft_skills
   │   └─► resume_soft_skills
   ↓
4. Calculate intersections (matches)
   ↓
5. Calculate differences (missing)
   ↓
6. Calculate percentages
   ↓
7. Format match results
   ↓
8. Return structured response
```

## Algorithm Details

### 1. Keyword Extraction Algorithm

```python
def extract_keywords(text, top_n=20, include_bigrams=True):
    # Step 1: Preprocess
    cleaned = preprocess_text(text)
    
    # Step 2: spaCy processing
    doc = nlp(cleaned)
    
    # Step 3: Extract single-word keywords
    keywords = []
    for token in doc:
        if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and
            not token.is_stop and
            len(token.text) > 2 and
            token.text not in STOPWORDS_CUSTOM):
            keywords.append(token.lemma_)
    
    # Step 4: Extract bigrams (optional)
    if include_bigrams:
        for i in range(len(doc) - 1):
            if meets_bigram_criteria(doc[i], doc[i+1]):
                keywords.append(f"{doc[i].text} {doc[i+1].text}")
    
    # Step 5: Count frequencies
    keyword_counts = Counter(keywords)
    
    # Step 6: Categorize and format
    result = []
    for keyword, count in keyword_counts.most_common(top_n):
        result.append({
            'keyword': keyword,
            'count': count,
            'type': categorize_keyword(keyword)
        })
    
    return result
```

### 2. Skill Extraction Algorithm

```python
def extract_skills(text):
    technical_skills = set()
    soft_skills = set()
    
    # Exact and partial matching
    text_lower = text.lower()
    
    # Check each known skill
    for skill in TECH_SKILLS:
        if skill in text_lower:
            technical_skills.add(skill)
    
    for skill in SOFT_SKILLS:
        if skill in text_lower:
            soft_skills.add(skill)
    
    # Check tokens and bigrams
    doc = nlp(text_lower)
    tokens = [token.lemma_ for token in doc if not token.is_stop]
    
    for i in range(len(tokens) - 1):
        bigram = f"{tokens[i]} {tokens[i+1]}"
        if bigram in TECH_SKILLS:
            technical_skills.add(bigram)
        if bigram in SOFT_SKILLS:
            soft_skills.add(bigram)
    
    return {
        'technical_skills': sorted(list(technical_skills)),
        'soft_skills': sorted(list(soft_skills))
    }
```

### 3. Match Calculation Algorithm

```python
def calculate_keyword_match(job_keywords, resume_keywords):
    # Convert to sets
    job_tech = set(job_keywords['technical_skills'])
    resume_tech = set(resume_keywords['technical_skills'])
    
    # Calculate intersections
    tech_match = job_tech & resume_tech
    tech_missing = job_tech - resume_tech
    
    # Calculate percentages
    tech_match_pct = (len(tech_match) / len(job_tech)) * 100 if job_tech else 0
    
    # Same for soft skills and overall
    # ...
    
    return {
        'technical_match': {
            'matched': sorted(list(tech_match)),
            'missing': sorted(list(tech_missing)),
            'match_percentage': round(tech_match_pct, 2),
            'count': len(tech_match)
        },
        # ... soft skills and overall
    }
```

## NLP Processing Details

### spaCy Pipeline

```
Text → Tokenizer → Tagger → Parser → NER → Lemmatizer
         ↓          ↓        ↓       ↓        ↓
      Tokens     POS Tags  Deps   Entities  Lemmas
```

**What Each Component Does:**

1. **Tokenizer**: Splits text into words, punctuation
2. **Tagger**: Assigns part-of-speech tags (NOUN, VERB, ADJ, etc.)
3. **Parser**: Analyzes grammatical structure
4. **NER**: Identifies named entities (companies, locations, etc.)
5. **Lemmatizer**: Converts words to base form (running → run)

### Part-of-Speech (POS) Tags Used

- **NOUN**: Common nouns (developer, experience, skill)
- **PROPN**: Proper nouns (Python, AWS, React)
- **ADJ**: Adjectives (senior, strong, excellent)

### Why These Tags?
- Nouns represent concrete concepts and skills
- Proper nouns capture specific technologies and tools
- Adjectives capture qualifications and attributes

## Data Structures

### Keyword Object
```python
{
    "keyword": str,        # The actual keyword
    "count": int,          # Frequency in text
    "type": str           # "technical" | "soft_skill" | "general"
}
```

### Job Keywords Object
```python
{
    "all_keywords": [Keyword],      # All extracted keywords
    "title_keywords": [Keyword],    # Title-specific keywords
    "technical_skills": [str],      # List of technical skills
    "soft_skills": [str],           # List of soft skills
    "keyword_count": int            # Total unique keywords
}
```

### Resume Keywords Object
```python
{
    "all_keywords": [Keyword],      # All extracted keywords
    "technical_skills": [str],      # List of technical skills
    "soft_skills": [str],           # List of soft skills
    "keyword_count": int            # Total unique keywords
}
```

### Match Result Object
```python
{
    "technical_match": {
        "matched": [str],              # Matched technical skills
        "missing": [str],              # Missing technical skills
        "match_percentage": float,     # Match %
        "count": int                   # Number matched
    },
    "soft_skills_match": { ... },     # Same structure
    "overall_match": { ... }          # Same structure
}
```

## Performance Considerations

### Optimization Strategies

1. **Singleton Pattern**
   - Load spaCy model once
   - Reuse across requests
   - Memory: ~100MB (one-time)

2. **Caching Opportunities**
   - Cache frequently accessed job keywords
   - Cache resume keywords after upload
   - Use Redis for distributed caching

3. **Batch Processing**
   - Process multiple jobs in one pass
   - Reduces overhead of repeated model access

4. **Text Preprocessing**
   - Regex operations before heavy NLP
   - Reduces tokens to process

### Performance Metrics

| Operation | Time | Memory |
|-----------|------|--------|
| Model Load | 2-3s | 100MB |
| Single Job | 0.5-1s | +10MB |
| Single Resume | 1-2s | +15MB |
| Match Calc | 0.1s | +1MB |
| Batch (10 jobs) | 8-10s | +50MB |

## Scalability

### Horizontal Scaling
- Each API instance loads own spaCy model
- Stateless design allows load balancing
- No shared state between requests

### Vertical Scaling
- More RAM = More concurrent processing
- CPU-bound for text processing
- GPU acceleration possible (spaCy Transformers)

## Error Handling

### Exception Hierarchy
```
Exception
├─ ValueError (invalid input)
├─ OSError (spaCy model not found)
├─ KeyError (missing required fields)
└─ RuntimeError (processing errors)
```

### Error Recovery
1. **Missing Model**: Auto-download on first run
2. **Invalid Text**: Validate before processing
3. **Empty Results**: Return empty structures (not errors)
4. **API Errors**: Return 400/500 with clear messages

## Security Considerations

### Input Validation
- Text length limits (max 100KB)
- Character encoding validation (UTF-8)
- Malicious pattern detection

### Rate Limiting
- Recommended: 60 requests/minute per user
- Batch endpoint: 10 requests/minute

### Data Privacy
- No storage of extracted keywords (stateless)
- Resume text processed in memory only
- No logging of sensitive content

## Integration Points

### Input Sources
- Direct API calls (frontend)
- Resume upload module (Task 2.3)
- Job scraper module (Task 3.x)
- Job storage (Task 3.3)

### Output Consumers
- Scoring algorithm (Task 5.2)
- Resume optimization (Task 6.x)
- Job matching dashboard
- Export module (Task 7.x)

## Testing Strategy

### Unit Tests
- Individual methods (extract_keywords, extract_skills)
- Edge cases (empty text, special characters)
- Categorization logic

### Integration Tests
- API endpoints
- Full extraction pipelines
- Match calculations

### Performance Tests
- Large text processing
- Batch operations
- Memory usage monitoring

## Dependencies

### Direct Dependencies
```
spacy==3.6.0
en_core_web_sm (spaCy model)
```

### Transitive Dependencies
- numpy (spaCy dependency)
- cymem, murmurhash (spaCy internals)
- srsly, thinc (spaCy dependencies)

## Future Enhancements

1. **Custom Skill Training**
   - Company-specific skill dictionaries
   - Industry-specific taxonomies

2. **Synonym Matching**
   - "JavaScript" ↔ "JS"
   - "React.js" ↔ "React"

3. **Contextual Analysis**
   - Years of experience extraction
   - Proficiency levels (beginner, expert)

4. **Multi-Language Support**
   - Spanish, French, German models
   - Language detection

5. **Advanced NLP**
   - Transformer models (BERT, RoBERTa)
   - Fine-tuning on job descriptions
   - Semantic similarity scoring

---

**Architecture Version:** 1.0
**Last Updated:** November 10, 2025
**Status:** Production-Ready
