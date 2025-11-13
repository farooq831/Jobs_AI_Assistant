"""
Demo script for CSV and PDF export functionality.
Demonstrates all export features with sample data.
"""

import os
from csv_pdf_exporter import CSVExporter, PDFExporter


# Sample jobs data
SAMPLE_JOBS = [
    {
        'title': 'Senior Python Developer',
        'company': 'Tech Innovators Inc.',
        'location': 'San Francisco, CA',
        'salary': '$120,000 - $150,000',
        'job_type': 'Remote',
        'description': 'We are seeking an experienced Python developer to join our backend team. Must have 5+ years of experience with Python, Django, Flask, and REST APIs. Experience with AWS, Docker, and Kubernetes is a plus. Strong problem-solving skills and ability to work in a fast-paced environment required.',
        'link': 'https://example.com/jobs/senior-python-dev',
        'score': {
            'overall_score': 87.5,
            'highlight': 'green',
            'keyword_match_score': 85.0,
            'salary_match_score': 90.0,
            'location_match_score': 85.0
        }
    },
    {
        'title': 'Full Stack Developer',
        'company': 'Digital Solutions LLC',
        'location': 'New York, NY',
        'salary': '$90,000 - $120,000',
        'job_type': 'Hybrid',
        'description': 'Looking for a full stack developer proficient in React, Node.js, and PostgreSQL. 3+ years of experience required. Great opportunity to work on cutting-edge web applications.',
        'link': 'https://example.com/jobs/fullstack-dev',
        'score': {
            'overall_score': 72.0,
            'highlight': 'white',
            'keyword_match_score': 70.0,
            'salary_match_score': 75.0,
            'location_match_score': 71.0
        }
    },
    {
        'title': 'Data Scientist',
        'company': 'Analytics Pro',
        'location': 'Remote',
        'salary': '$100,000 - $140,000',
        'job_type': 'Remote',
        'description': 'Data scientist position requiring strong Python skills, machine learning expertise, and statistical analysis. Experience with TensorFlow, PyTorch, and big data technologies preferred.',
        'link': 'https://example.com/jobs/data-scientist',
        'score': {
            'overall_score': 78.5,
            'highlight': 'white',
            'keyword_match_score': 80.0,
            'salary_match_score': 77.0,
            'location_match_score': 78.5
        }
    },
    {
        'title': 'Junior Web Developer',
        'company': 'StartUp Ventures',
        'location': 'Austin, TX',
        'salary': '$55,000 - $70,000',
        'job_type': 'Onsite',
        'description': 'Entry-level position for motivated developers. Great learning opportunity with mentorship from senior developers. HTML, CSS, JavaScript knowledge required.',
        'link': 'https://example.com/jobs/junior-web-dev',
        'score': {
            'overall_score': 42.0,
            'highlight': 'yellow',
            'keyword_match_score': 35.0,
            'salary_match_score': 50.0,
            'location_match_score': 40.0
        }
    },
    {
        'title': 'DevOps Engineer',
        'company': 'Cloud Systems Corp',
        'location': 'Seattle, WA',
        'salary': '$110,000 - $145,000',
        'job_type': 'Remote',
        'description': 'Experienced DevOps engineer needed for infrastructure automation. Strong AWS/Azure knowledge, CI/CD pipeline experience, and Terraform/Ansible skills required.',
        'link': 'https://example.com/jobs/devops-engineer',
        'score': {
            'overall_score': 65.0,
            'highlight': 'yellow',
            'keyword_match_score': 60.0,
            'salary_match_score': 70.0,
            'location_match_score': 65.0
        }
    }
]


SAMPLE_RESUME_TIPS = {
    'summary': 'Your resume demonstrates solid technical skills and relevant experience. However, there are opportunities to improve keyword optimization, quantify achievements, and enhance ATS compatibility to increase your match rates with target jobs.',
    'overall_assessment': {
        'strength_score': 72,
        'completeness': 'Good',
        'ats_compatibility': 'Fair'
    },
    'critical_tips': [
        {
            'category': 'keywords',
            'title': 'Add Missing Technical Keywords',
            'description': 'Your resume is missing several high-frequency keywords found in target job postings: AWS, Docker, Kubernetes, CI/CD, microservices, and REST APIs.',
            'action': 'Add these keywords naturally in your experience section, particularly in bullet points describing your technical accomplishments.',
            'impact': 'high'
        },
        {
            'category': 'format',
            'title': 'Improve ATS Compatibility',
            'description': 'Current resume format may not be fully ATS-compatible. Using tables or complex formatting can cause parsing issues.',
            'action': 'Use standard section headings (Experience, Education, Skills), avoid tables, and use simple bullet points. Save as .docx or .pdf format.',
            'impact': 'high'
        },
        {
            'category': 'achievements',
            'title': 'Quantify Technical Achievements',
            'description': 'Most bullet points describe responsibilities rather than quantifiable achievements and impact.',
            'action': 'Add metrics to at least 5 bullet points. Examples: "Reduced API response time by 40%", "Managed deployment of 20+ microservices", "Improved test coverage from 60% to 95%".',
            'impact': 'high'
        }
    ],
    'important_tips': [
        {
            'category': 'skills',
            'title': 'Organize Skills Section by Category',
            'description': 'Current skills section is a simple list. Categorization helps both ATS and recruiters.',
            'action': 'Group skills into categories: Programming Languages, Frameworks, Cloud/DevOps, Databases, Tools.',
            'impact': 'medium'
        },
        {
            'category': 'experience',
            'title': 'Add Project Details',
            'description': 'Limited information about project scope, team size, and technologies used.',
            'action': 'For each role, add 1-2 bullet points describing major projects, technologies used, and your specific contributions.',
            'impact': 'medium'
        },
        {
            'category': 'keywords',
            'title': 'Include Soft Skills',
            'description': 'Resume focuses heavily on technical skills but lacks mention of leadership, collaboration, or communication abilities.',
            'action': 'Add 2-3 achievements that demonstrate leadership, cross-functional collaboration, or mentorship.',
            'impact': 'medium'
        }
    ],
    'optional_tips': [
        {
            'category': 'format',
            'title': 'Add a Professional Summary',
            'description': 'A brief professional summary at the top can help ATS and recruiters quickly understand your value proposition.',
            'action': 'Write a 2-3 sentence summary highlighting years of experience, key technical skills, and primary expertise.',
            'impact': 'low'
        },
        {
            'category': 'certifications',
            'title': 'Highlight Relevant Certifications',
            'description': 'If you have technical certifications (AWS, Azure, etc.), they should be prominently displayed.',
            'action': 'Add a "Certifications" section and list relevant credentials with dates.',
            'impact': 'low'
        }
    ]
}


def demo_csv_export():
    """Demonstrate CSV export functionality."""
    print("\n" + "="*60)
    print("CSV EXPORT DEMONSTRATION")
    print("="*60)
    
    exporter = CSVExporter()
    
    # 1. Export with all features
    print("\n1. Exporting with scores and descriptions...")
    exporter.export_jobs_to_file(
        SAMPLE_JOBS,
        'demo_jobs_full.csv',
        include_scores=True,
        include_description=True
    )
    print("   ✓ Created: demo_jobs_full.csv")
    
    # 2. Export without descriptions (smaller file)
    print("\n2. Exporting without descriptions (compact)...")
    exporter.export_jobs_to_file(
        SAMPLE_JOBS,
        'demo_jobs_compact.csv',
        include_scores=True,
        include_description=False
    )
    print("   ✓ Created: demo_jobs_compact.csv")
    
    # 3. Export minimal (for spreadsheet import)
    print("\n3. Exporting minimal data (no scores, no descriptions)...")
    exporter.export_jobs_to_file(
        SAMPLE_JOBS,
        'demo_jobs_minimal.csv',
        include_scores=False,
        include_description=False
    )
    print("   ✓ Created: demo_jobs_minimal.csv")
    
    print("\n✓ CSV export demos complete!")


def demo_pdf_export():
    """Demonstrate PDF export functionality."""
    print("\n" + "="*60)
    print("PDF EXPORT DEMONSTRATION")
    print("="*60)
    
    exporter = PDFExporter()
    
    # 1. Export with resume tips
    print("\n1. Exporting with resume optimization tips...")
    exporter.export_jobs_to_file(
        SAMPLE_JOBS,
        'demo_jobs_with_tips.pdf',
        resume_tips=SAMPLE_RESUME_TIPS,
        include_tips=True
    )
    print("   ✓ Created: demo_jobs_with_tips.pdf")
    
    # 2. Export without tips
    print("\n2. Exporting without tips (jobs only)...")
    exporter.export_jobs_to_file(
        SAMPLE_JOBS,
        'demo_jobs_only.pdf',
        resume_tips=None,
        include_tips=False
    )
    print("   ✓ Created: demo_jobs_only.pdf")
    
    print("\n✓ PDF export demos complete!")


def demo_statistics():
    """Show export statistics."""
    print("\n" + "="*60)
    print("EXPORT STATISTICS")
    print("="*60)
    
    # Calculate statistics
    total_jobs = len(SAMPLE_JOBS)
    highlights = {'green': 0, 'yellow': 0, 'white': 0, 'red': 0}
    total_score = 0
    
    for job in SAMPLE_JOBS:
        score_data = job.get('score', {})
        highlight = score_data.get('highlight', 'white').lower()
        highlights[highlight] = highlights.get(highlight, 0) + 1
        total_score += score_data.get('overall_score', 0)
    
    avg_score = total_score / total_jobs if total_jobs > 0 else 0
    
    print(f"\nTotal Jobs: {total_jobs}")
    print(f"Average Match Score: {avg_score:.1f}%")
    print(f"\nMatch Quality Distribution:")
    print(f"  🟢 Excellent (Green): {highlights['green']} jobs")
    print(f"  ⚪ Good (White): {highlights['white']} jobs")
    print(f"  🟡 Fair (Yellow): {highlights['yellow']} jobs")
    print(f"  🔴 Poor (Red): {highlights['red']} jobs")
    
    print(f"\nResume Tips Summary:")
    print(f"  🔴 Critical Tips: {len(SAMPLE_RESUME_TIPS['critical_tips'])}")
    print(f"  🟡 Important Tips: {len(SAMPLE_RESUME_TIPS['important_tips'])}")
    print(f"  ⚪ Optional Tips: {len(SAMPLE_RESUME_TIPS['optional_tips'])}")
    print(f"  Overall Strength Score: {SAMPLE_RESUME_TIPS['overall_assessment']['strength_score']}/100")


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("CSV AND PDF EXPORT - INTERACTIVE DEMO")
    print("="*60)
    print("\nThis demo will create sample export files to showcase")
    print("the CSV and PDF export functionality.")
    
    # Show statistics
    demo_statistics()
    
    # Run demos
    demo_csv_export()
    demo_pdf_export()
    
    # Summary
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("\nGenerated Files:")
    print("  CSV Files:")
    print("    - demo_jobs_full.csv (with scores & descriptions)")
    print("    - demo_jobs_compact.csv (with scores, no descriptions)")
    print("    - demo_jobs_minimal.csv (basic data only)")
    print("\n  PDF Files:")
    print("    - demo_jobs_with_tips.pdf (jobs + resume tips)")
    print("    - demo_jobs_only.pdf (jobs only)")
    
    print("\nKey Features Demonstrated:")
    print("  ✓ CSV export with customizable columns")
    print("  ✓ PDF export with professional formatting")
    print("  ✓ Color-coded job matching (Green/White/Yellow/Red)")
    print("  ✓ Resume optimization tips integration")
    print("  ✓ Summary statistics and metrics")
    print("  ✓ Multiple export configurations")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
