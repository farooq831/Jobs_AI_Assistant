"""
Demo script for Excel Export Module
Demonstrates the Excel export functionality with sample data.
"""

print("=" * 70)
print("Excel Export Module - Demo Script")
print("=" * 70)
print()

# Check if openpyxl is available
try:
    import openpyxl
    print("✓ openpyxl is installed")
    openpyxl_available = True
except ImportError:
    print("✗ openpyxl is NOT installed")
    print("  Install with: pip install openpyxl")
    openpyxl_available = False

print()

if openpyxl_available:
    from excel_exporter import export_jobs_to_file, export_jobs_to_excel
    
    # Sample jobs data
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'location': 'San Francisco, CA',
            'salary': '$120,000 - $150,000',
            'job_type': 'Remote',
            'description': 'Looking for an experienced Python developer with strong backend skills. Must have 5+ years of experience.',
            'link': 'https://example.com/job1',
            'score': {
                'overall_score': 85,
                'highlight': 'green'
            }
        },
        {
            'title': 'Junior Developer',
            'company': 'Startup Inc',
            'location': 'New York, NY',
            'salary': '$60,000 - $80,000',
            'job_type': 'Onsite',
            'description': 'Entry-level position for new graduates with basic programming knowledge.',
            'link': 'https://example.com/job2',
            'score': {
                'overall_score': 45,
                'highlight': 'yellow'
            }
        },
        {
            'title': 'Data Scientist',
            'company': 'Analytics Ltd',
            'location': 'Austin, TX',
            'salary': '$90,000 - $110,000',
            'job_type': 'Hybrid',
            'description': 'Looking for data scientist with ML experience and Python skills.',
            'link': 'https://example.com/job3',
            'score': {
                'overall_score': 30,
                'highlight': 'red'
            }
        }
    ]
    
    # Sample resume tips
    sample_tips = {
        'summary': 'Your resume shows good technical skills but needs improvement in quantifying achievements and adding more relevant keywords.',
        'overall_assessment': {
            'strength_score': 72,
            'completeness': 'Good',
            'ats_compatibility': 'Fair'
        },
        'critical_tips': [
            {
                'category': 'keywords',
                'title': 'Add Missing Technical Keywords',
                'description': 'Your resume is missing important keywords like Python, AWS, Docker',
                'action': 'Add these keywords naturally in your experience section',
                'impact': 'high'
            }
        ],
        'important_tips': [
            {
                'category': 'achievements',
                'title': 'Quantify Your Achievements',
                'description': 'Use numbers and metrics to show impact',
                'action': 'Add specific metrics to at least 3 bullet points',
                'impact': 'medium'
            }
        ],
        'optional_tips': [
            {
                'category': 'content',
                'title': 'Add Certifications',
                'description': 'Industry certifications can strengthen your profile',
                'action': 'Include relevant certifications if you have any',
                'impact': 'low'
            }
        ]
    }
    
    print("Sample Data:")
    print(f"  - {len(sample_jobs)} jobs")
    print(f"  - {len(sample_tips['critical_tips'])} critical tips")
    print(f"  - {len(sample_tips['important_tips'])} important tips")
    print(f"  - {len(sample_tips['optional_tips'])} optional tips")
    print()
    
    # Test 1: Export without tips
    print("Test 1: Exporting jobs without tips...")
    try:
        export_jobs_to_file(sample_jobs, 'demo_jobs_only.xlsx', include_tips_sheet=False)
        print("  ✓ Successfully exported to: demo_jobs_only.xlsx")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    # Test 2: Export with tips
    print("Test 2: Exporting jobs with resume tips...")
    try:
        export_jobs_to_file(sample_jobs, 'demo_jobs_with_tips.xlsx', 
                           resume_tips=sample_tips, include_tips_sheet=True)
        print("  ✓ Successfully exported to: demo_jobs_with_tips.xlsx")
        print("  - Includes 'Jobs' sheet with color-coded highlights")
        print("  - Includes 'Resume Tips' sheet with optimization suggestions")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    # Test 3: Export to BytesIO
    print("Test 3: Exporting to memory (BytesIO)...")
    try:
        output = export_jobs_to_excel(sample_jobs, sample_tips, include_tips_sheet=True)
        print(f"  ✓ Successfully exported to memory: {len(output.getvalue())} bytes")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Color-coded job highlighting (Red/Yellow/Green)")
    print("  ✓ Formatted Excel sheets with proper headers")
    print("  ✓ Resume optimization tips as separate sheet")
    print("  ✓ Cell comments with tip summaries")
    print("  ✓ Auto-filter and frozen header row")
    print("  ✓ Adjustable column widths for readability")
    print()
    print("Files created:")
    import os
    for filename in ['demo_jobs_only.xlsx', 'demo_jobs_with_tips.xlsx']:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  - {filename} ({size:,} bytes)")
    print()

else:
    print("=" * 70)
    print("Cannot run demo - openpyxl not installed")
    print("=" * 70)
    print()
    print("To install openpyxl:")
    print("  pip install openpyxl")
    print()
