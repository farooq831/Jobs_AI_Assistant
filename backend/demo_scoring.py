"""
Quick Demo of Job Scoring System
Shows scoring in action with sample data
"""

from job_scorer import get_job_scorer
from keyword_extractor import get_keyword_extractor

print("="*70)
print("JOB SCORING SYSTEM - DEMO")
print("="*70)

# Sample data
sample_jobs = [
    {
        'id': 'job1',
        'title': 'Senior Python Developer',
        'description': 'Looking for Python expert with Django, Flask, AWS, and Docker experience. Remote work available.',
        'location': 'Remote',
        'salary': {'min': 90000, 'max': 130000},
        'job_type': 'Remote',
        'company': 'Tech Corp'
    },
    {
        'id': 'job2',
        'title': 'Backend Engineer',
        'description': 'Node.js and MongoDB experience required. Some Python knowledge helpful.',
        'location': 'San Francisco, CA',
        'salary': {'min': 80000, 'max': 120000},
        'job_type': 'Hybrid',
        'company': 'Startup Inc'
    },
    {
        'id': 'job3',
        'title': 'Java Developer',
        'description': 'Java, Spring Boot, Oracle database. Must work in office.',
        'location': 'New York, NY',
        'salary': {'min': 60000, 'max': 80000},
        'job_type': 'Onsite',
        'company': 'Enterprise Co'
    }
]

user_preferences = {
    'name': 'Test User',
    'location': 'San Francisco',
    'salary_min': 85000,
    'salary_max': 125000,
    'job_titles': ['Python Developer', 'Backend Developer'],
    'job_types': ['Remote', 'Hybrid']
}

resume_text = """
Senior Software Engineer
Skills: Python, Django, Flask, JavaScript, AWS, Docker, PostgreSQL
5 years of experience in web development and cloud infrastructure
"""

print("\n📋 User Preferences:")
print(f"   Location: {user_preferences['location']}")
print(f"   Salary: ${user_preferences['salary_min']:,} - ${user_preferences['salary_max']:,}")
print(f"   Job Titles: {', '.join(user_preferences['job_titles'])}")
print(f"   Job Types: {', '.join(user_preferences['job_types'])}")

print("\n📄 Resume Summary:")
print("   Skills: Python, Django, Flask, JavaScript, AWS, Docker, PostgreSQL")
print("   Experience: 5 years")

# Extract resume keywords
print("\n🔍 Extracting resume keywords...")
extractor = get_keyword_extractor()
resume_keywords = extractor.extract_resume_keywords(resume_text)
print(f"   Found {len(resume_keywords['technical_skills'])} technical skills")

# Score jobs
print("\n⚡ Scoring jobs...")
scorer = get_job_scorer()
scored_jobs = scorer.score_multiple_jobs(sample_jobs, user_preferences, resume_keywords)

# Display results
print("\n" + "="*70)
print("SCORING RESULTS")
print("="*70)

for i, job in enumerate(scored_jobs, 1):
    score_data = job['score']
    
    # Determine emoji for highlight
    emoji = {'red': '🔴', 'yellow': '🟡', 'white': '⚪'}[score_data['highlight']]
    
    print(f"\n#{i}. {job['title']} - {job['company']}")
    print(f"   {emoji} Overall Score: {score_data['overall_score']}/100 ({score_data['highlight'].upper()})")
    print(f"   📊 Component Scores:")
    print(f"      • Keyword Match:  {score_data['component_scores']['keyword_match']}/100")
    print(f"      • Salary Match:   {score_data['component_scores']['salary_match']}/100")
    print(f"      • Location Match: {score_data['component_scores']['location_match']}/100")
    print(f"      • Job Type Match: {score_data['component_scores']['job_type_match']}/100")
    print(f"   📍 {job['location']}")
    print(f"   💰 ${job['salary']['min']:,} - ${job['salary']['max']:,}")
    print(f"   🏢 {job['job_type']}")

# Statistics
print("\n" + "="*70)
print("STATISTICS")
print("="*70)
stats = scorer.get_score_statistics(scored_jobs)
print(f"Total Jobs: {stats['total_jobs']}")
print(f"Average Score: {stats['average_score']}/100")
print(f"Highest Score: {stats['highest_score']}/100")
print(f"Lowest Score: {stats['lowest_score']}/100")
print(f"\nDistribution:")
print(f"  ⚪ White (Good):  {stats['white_count']} jobs")
print(f"  🟡 Yellow (Fair): {stats['yellow_count']} jobs")
print(f"  🔴 Red (Poor):    {stats['red_count']} jobs")

print("\n" + "="*70)
print("✅ DEMO COMPLETE - Task 5.2 Working Successfully!")
print("="*70)
