# Task 6.2 Quick Start Guide: Job Keyword Analysis

**5-Minute Quick Start** ⚡

---

## What is Task 6.2?

Analyzes multiple job postings to identify high-frequency keywords and determines which critical skills are missing from your resume.

---

## Quick Usage

### Method 1: API (Recommended)

```bash
# 1. Start the Flask server
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant/backend
python3 app.py

# 2. Analyze job keywords (in another terminal)
curl -X POST http://localhost:5000/api/analyze-job-keywords \
  -H "Content-Type: application/json" \
  -d '{
    "job_descriptions": [
      "Senior Engineer with Python, AWS, Docker, Kubernetes",
      "Full Stack Developer - React, Node.js, AWS, PostgreSQL",
      "Backend Engineer - Python, Docker, Kubernetes, Redis"
    ],
    "resume_text": "Software Engineer with Python, React, and SQL experience",
    "top_n": 20
  }'

# 3. Get missing keywords summary for a stored resume
curl http://localhost:5000/api/missing-keywords-summary/1
```

### Method 2: Python Direct

```python
from resume_analyzer import get_resume_analyzer

# Create analyzer
analyzer = get_resume_analyzer()

# Job descriptions to analyze
jobs = [
    "Senior Engineer with Python, AWS, Docker, Kubernetes...",
    "Full Stack Developer - React, Node.js, AWS, PostgreSQL...",
    "Backend Engineer - Python, Docker, Kubernetes, Redis..."
]

# Your resume text
resume = """
Software Engineer
Skills: Python, React, SQL, Git, Agile
Experience: 3 years developing web applications
"""

# Analyze
result = analyzer.analyze_job_keywords(
    job_descriptions=jobs,
    resume_text=resume,
    top_n=20
)

# View results
print(f"Jobs Analyzed: {result['analysis_summary']['total_jobs_analyzed']}")
print(f"Technical Coverage: {result['analysis_summary']['technical_coverage_percentage']}%")
print("\nCritical Missing Skills:")
for skill in result['missing_keywords']['critical_technical'][:5]:
    print(f"  - {skill['keyword']} (appears in {skill['percentage']}% of jobs)")

print("\nRecommendations:")
for rec in result['recommendations']:
    print(f"  {rec}")
```

---

## Understanding the Results

### 1. Analysis Summary
```json
{
  "total_jobs_analyzed": 3,
  "total_unique_technical_keywords": 15,
  "technical_coverage_percentage": 45.5,
  "soft_skills_coverage_percentage": 60.0
}
```
- Shows how many jobs were analyzed
- Coverage % = how many high-frequency keywords are in your resume

### 2. High-Frequency Keywords
```json
{
  "keyword": "aws",
  "frequency": 3,
  "percentage": 100.0,
  "in_resume": false
}
```
- `frequency`: How many jobs mention this keyword
- `percentage`: (frequency / total_jobs) × 100
- `in_resume`: Whether it's in your resume

### 3. Missing Keywords (Priority Levels)

**🔴 Critical** (>50% of jobs):
- Must-have skills for your target positions
- Add these to resume ASAP

**🟡 Important** (30-50% of jobs):
- Commonly requested skills
- Consider adding if you have experience

**✅ Success** (>70% coverage):
- Your resume is well-aligned

**⚠️ Warning** (<40% coverage):
- Need to add more relevant skills

---

## Common Use Cases

### Use Case 1: Targeting Specific Jobs
```python
# Analyze jobs you're interested in
target_jobs = [
    "Job posting 1 full text...",
    "Job posting 2 full text...",
    "Job posting 3 full text..."
]

result = analyzer.analyze_job_keywords(
    job_descriptions=target_jobs,
    resume_text=my_resume,
    top_n=30
)

# Focus on critical missing skills
critical_skills = result['missing_keywords']['critical_technical']
print("Add these skills to your resume:")
for skill in critical_skills[:5]:
    print(f"  - {skill['keyword']}")
```

### Use Case 2: Market Research
```python
# Analyze 20+ jobs in your field
market_jobs = [...]  # Many job descriptions

result = analyzer.analyze_job_keywords(
    job_descriptions=market_jobs,
    resume_text=my_resume,
    top_n=50
)

# See what's most in-demand
print("Top 10 most requested skills:")
for skill in result['high_frequency_keywords']['technical_skills'][:10]:
    print(f"  {skill['keyword']}: {skill['percentage']}% of jobs")
```

### Use Case 3: Resume Optimization
```python
# Before optimization
result_before = analyzer.analyze_job_keywords(jobs, my_resume)
print(f"Coverage before: {result_before['analysis_summary']['technical_coverage_percentage']}%")

# Update resume with missing critical skills
updated_resume = my_resume + "\nSkills: AWS, Docker, Kubernetes"

# After optimization
result_after = analyzer.analyze_job_keywords(jobs, updated_resume)
print(f"Coverage after: {result_after['analysis_summary']['technical_coverage_percentage']}%")
```

---

## API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/analyze-job-keywords` | POST | Analyze provided job descriptions |
| `/api/analyze-job-keywords/stored-jobs` | POST | Analyze stored jobs from database |
| `/api/missing-keywords-summary/<id>` | GET | Quick summary of missing keywords |

---

## Sample Output

```json
{
  "success": true,
  "analysis": {
    "analysis_summary": {
      "total_jobs_analyzed": 4,
      "technical_coverage_percentage": 55.5
    },
    "missing_keywords": {
      "critical_technical": [
        {"keyword": "aws", "percentage": 100.0},
        {"keyword": "docker", "percentage": 100.0},
        {"keyword": "kubernetes", "percentage": 75.0}
      ]
    },
    "recommendations": [
      "🔴 HIGH PRIORITY: Add these critical technical skills appearing in 50%+ of jobs: aws, docker, kubernetes",
      "🟡 MEDIUM PRIORITY: Consider adding these technical skills: postgresql, redis",
      "⚠️ Your technical skills coverage is low (55.5%). Focus on adding the most common technical requirements."
    ]
  }
}
```

---

## Tips for Best Results

### 1. **Quality over Quantity**
- 5-10 relevant job postings > 50 random ones
- Focus on jobs you actually want to apply to

### 2. **Complete Job Descriptions**
- Use full job descriptions, not just titles
- Include requirements, responsibilities, and qualifications sections

### 3. **Keep Resume Current**
- Update resume text before analysis
- Include all your relevant skills

### 4. **Use Priority Levels**
- Start with 🔴 Critical skills (>50% frequency)
- Then add 🟡 Important skills (30-50% frequency)
- Don't add skills you don't actually have!

### 5. **Iterate**
- Analyze → Update Resume → Re-analyze
- Track coverage improvement over time

---

## Troubleshooting

### Issue: Low Coverage Despite Many Skills
**Solution:** Skills might be phrased differently. Example:
- Job says: "AWS" → Resume says: "Amazon Web Services"
- Add common abbreviations to resume

### Issue: Too Many Missing Keywords
**Solution:** This is normal! Focus on:
1. Critical skills (>50% frequency)
2. Skills you actually have
3. Skills you can quickly learn

### Issue: No Technical Skills Detected
**Solution:** Check that:
- Job descriptions include technical requirements
- Resume includes skills section
- Skills are clearly stated (not just implied)

---

## Next Steps

After analyzing keywords:

1. **Update Resume** with critical missing skills you possess
2. **Learn Skills** that appear in 75%+ of target jobs
3. **Tailor Resume** for specific applications
4. **Re-analyze** to track improvement

---

## Integration with Other Tasks

- **Task 5.2 (Scoring)**: Uses keyword match for job scoring
- **Task 6.1 (Extraction)**: Provides resume keywords for comparison
- **Task 6.3 (Tips)**: Will use this for generating optimization tips
- **Task 7.1 (Export)**: Will include missing keywords in Excel export

---

## Support

For issues or questions:
1. Check `TASK_6.2_COMPLETION_REPORT.md` for detailed documentation
2. Run tests: `python3 backend/test_job_keyword_analysis.py`
3. Review API examples in `backend/app.py`

---

**Quick Start Complete! 🎉**

You're now ready to analyze job keywords and optimize your resume based on market demand.
