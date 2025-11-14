#!/usr/bin/env python3
"""
End-to-End Integration Demo for AI Job Application Assistant
Interactive demonstration of complete user workflow from input to export.

This demo showcases:
1. User profile creation
2. Resume upload and analysis
3. Job scraping simulation
4. Data cleaning and filtering
5. Job scoring and ranking
6. Resume optimization tips
7. Multi-format export (Excel, CSV, PDF)
8. Application status tracking
9. Complete workflow integration

Author: AI Job Application Assistant Team
Date: November 14, 2025
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime
from io import BytesIO

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage_manager import JobStorageManager
from data_processor import DataProcessor, JobFilter
from keyword_extractor import KeywordExtractor
from job_scorer import JobScorer
from resume_analyzer import ResumeAnalyzer
from excel_exporter import ExcelExporter
from csv_pdf_exporter import CSVExporter, PDFExporter
from application_status import ApplicationStatus


class EndToEndDemo:
    """End-to-end workflow demonstration"""
    
    def __init__(self):
        """Initialize demo environment"""
        self.demo_dir = tempfile.mkdtemp(prefix="e2e_demo_")
        self.storage_dir = os.path.join(self.demo_dir, "data")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize components
        self.storage = JobStorageManager(self.storage_dir)
        self.processor = DataProcessor()
        self.filter = JobFilter()
        self.extractor = KeywordExtractor()
        self.scorer = JobScorer(self.extractor)
        self.analyzer = ResumeAnalyzer(self.extractor)
        self.excel_exporter = ExcelExporter()
        self.csv_exporter = CSVExporter()
        self.pdf_exporter = PDFExporter()
        
        print(f"Demo environment created: {self.demo_dir}")
    
    def cleanup(self):
        """Clean up demo environment"""
        if os.path.exists(self.demo_dir):
            shutil.rmtree(self.demo_dir)
            print(f"Demo environment cleaned up")
    
    def demo_1_complete_basic_workflow(self):
        """Demo 1: Complete basic workflow from start to finish"""
        print("\n" + "=" * 70)
        print("DEMO 1: Complete Basic Workflow")
        print("=" * 70)
        print("This demo shows the complete flow from user input to Excel export.")
        print()
        
        # Step 1: User Profile
        print("Step 1: Creating User Profile")
        print("-" * 70)
        user_profile = {
            "user_id": "demo_user_001",
            "name": "Sarah Johnson",
            "email": "sarah.johnson@example.com",
            "location": "San Francisco, CA",
            "desired_job_titles": ["Software Engineer", "Full Stack Developer", "Backend Engineer"],
            "min_salary": 120000,
            "max_salary": 180000,
            "preferred_job_types": ["Remote", "Hybrid"]
        }
        
        self.storage.add_user(user_profile)
        print(f"✓ User profile created:")
        print(f"  Name: {user_profile['name']}")
        print(f"  Location: {user_profile['location']}")
        print(f"  Desired titles: {', '.join(user_profile['desired_job_titles'])}")
        print(f"  Salary range: ${user_profile['min_salary']:,} - ${user_profile['max_salary']:,}")
        print(f"  Job types: {', '.join(user_profile['preferred_job_types'])}")
        input("\nPress Enter to continue...")
        
        # Step 2: Resume Upload
        print("\nStep 2: Resume Upload and Analysis")
        print("-" * 70)
        resume_text = """
        Sarah Johnson
        Senior Software Engineer
        San Francisco, CA | sarah.johnson@example.com | (555) 123-4567
        
        PROFESSIONAL SUMMARY
        Experienced Full Stack Software Engineer with 7+ years developing scalable web applications.
        Expert in Python, JavaScript, React, and cloud technologies (AWS). Strong background in
        microservices architecture, CI/CD, and agile development.
        
        EXPERIENCE
        Senior Software Engineer | TechCorp Inc | 2020 - Present
        • Led development of microservices-based platform serving 1M+ users
        • Architected and implemented RESTful APIs using Python Flask and FastAPI
        • Built responsive frontend applications with React, Redux, and TypeScript
        • Deployed and managed cloud infrastructure on AWS (EC2, RDS, S3, Lambda)
        • Implemented CI/CD pipelines using Jenkins, Docker, and Kubernetes
        • Mentored team of 5 junior developers
        
        Software Engineer | StartupXYZ | 2017 - 2020
        • Developed full-stack features for SaaS product using Django and React
        • Optimized database queries reducing response time by 60%
        • Integrated third-party APIs (Stripe, Twilio, SendGrid)
        • Wrote comprehensive unit and integration tests (95% coverage)
        
        TECHNICAL SKILLS
        • Languages: Python, JavaScript, TypeScript, SQL, HTML/CSS
        • Frameworks: Flask, Django, FastAPI, React, Redux, Node.js, Express
        • Databases: PostgreSQL, MongoDB, Redis, MySQL
        • Cloud/DevOps: AWS (EC2, RDS, S3, Lambda), Docker, Kubernetes, Jenkins
        • Tools: Git, JIRA, Postman, VS Code
        • Methodologies: Agile, Scrum, TDD, CI/CD
        
        EDUCATION
        Bachelor of Science in Computer Science | Stanford University | 2017
        """
        
        resume_id = self.analyzer.store_resume(
            resume_text,
            user_id=user_profile["user_id"],
            filename="sarah_johnson_resume.pdf"
        )
        
        print(f"✓ Resume uploaded successfully")
        print(f"  Resume ID: {resume_id}")
        
        # Extract keywords from resume
        resume_keywords = self.extractor.extract_keywords(resume_text)
        print(f"✓ Extracted {len(resume_keywords)} keywords from resume")
        print(f"  Top skills: {', '.join(list(resume_keywords)[:10])}")
        input("\nPress Enter to continue...")
        
        # Step 3: Job Scraping (Simulated)
        print("\nStep 3: Job Scraping (Simulated)")
        print("-" * 70)
        sample_jobs = [
            {
                "job_id": "job_001",
                "title": "Senior Software Engineer",
                "company": "Google",
                "location": "San Francisco, CA",
                "job_type": "Hybrid",
                "salary_min": 150000,
                "salary_max": 200000,
                "description": "We're looking for a Senior Software Engineer with expertise in Python, JavaScript, and cloud technologies. You'll work on building scalable microservices using Flask/FastAPI and React. Experience with AWS, Docker, and Kubernetes required. 7+ years experience.",
                "link": "https://careers.google.com/jobs/001",
                "source": "Indeed"
            },
            {
                "job_id": "job_002",
                "title": "Full Stack Developer",
                "company": "Facebook",
                "location": "San Francisco, CA",
                "job_type": "Remote",
                "salary_min": 140000,
                "salary_max": 190000,
                "description": "Full Stack Developer needed with strong React and Node.js skills. Must have experience with TypeScript, Redux, and building RESTful APIs. PostgreSQL and MongoDB experience preferred. 5+ years experience.",
                "link": "https://www.facebook.com/careers/jobs/002",
                "source": "Glassdoor"
            },
            {
                "job_id": "job_003",
                "title": "Backend Engineer",
                "company": "Stripe",
                "location": "San Francisco, CA",
                "job_type": "Hybrid",
                "salary_min": 160000,
                "salary_max": 210000,
                "description": "Backend Engineer with Python expertise. Build and maintain high-performance APIs using Django/Flask. Experience with PostgreSQL, Redis, and distributed systems. CI/CD and Docker experience required.",
                "link": "https://stripe.com/jobs/003",
                "source": "LinkedIn"
            },
            {
                "job_id": "job_004",
                "title": "Lead Software Engineer",
                "company": "Airbnb",
                "location": "San Francisco, CA",
                "job_type": "Hybrid",
                "salary_min": 170000,
                "salary_max": 220000,
                "description": "Lead Software Engineer to architect scalable systems. Expert in Python, microservices, AWS, and Kubernetes. Mentor junior engineers and drive technical decisions. 8+ years experience required.",
                "link": "https://careers.airbnb.com/jobs/004",
                "source": "Indeed"
            },
            {
                "job_id": "job_005",
                "title": "Software Engineer",
                "company": "Amazon",
                "location": "Seattle, WA",
                "job_type": "Onsite",
                "salary_min": 130000,
                "salary_max": 170000,
                "description": "Software Engineer for AWS team. Work on cloud services using Java and Python. Strong CS fundamentals and system design skills required.",
                "link": "https://amazon.jobs/005",
                "source": "Indeed"
            },
            {
                "job_id": "job_006",
                "title": "Frontend Developer",
                "company": "Netflix",
                "location": "Los Gatos, CA",
                "job_type": "Onsite",
                "salary_min": 135000,
                "salary_max": 175000,
                "description": "Frontend Developer with React expertise. Build beautiful, performant UIs. TypeScript, Redux, and testing experience required.",
                "link": "https://jobs.netflix.com/006",
                "source": "Glassdoor"
            }
        ]
        
        for job in sample_jobs:
            self.storage.add_job(job)
        
        stats = self.storage.get_stats()
        print(f"✓ Scraped and stored {stats['total_jobs']} job postings")
        print(f"  Sources: {', '.join(stats['sources'])}")
        input("\nPress Enter to continue...")
        
        # Step 4: Data Cleaning
        print("\nStep 4: Data Cleaning and Validation")
        print("-" * 70)
        all_jobs = self.storage.get_all_jobs()
        cleaned_jobs = self.processor.clean_jobs(all_jobs)
        print(f"✓ Cleaned {len(cleaned_jobs)} job postings")
        print(f"  Removed duplicates and invalid entries")
        input("\nPress Enter to continue...")
        
        # Step 5: Job Filtering
        print("\nStep 5: Filtering Jobs by User Preferences")
        print("-" * 70)
        filtered_jobs = self.filter.filter_jobs(
            cleaned_jobs,
            location=user_profile["location"],
            min_salary=user_profile["min_salary"],
            max_salary=user_profile["max_salary"],
            job_types=user_profile["preferred_job_types"]
        )
        
        print(f"✓ Filtered to {len(filtered_jobs)} matching jobs")
        print(f"  Filters applied:")
        print(f"    - Location: {user_profile['location']}")
        print(f"    - Salary: ${user_profile['min_salary']:,} - ${user_profile['max_salary']:,}")
        print(f"    - Job types: {', '.join(user_profile['preferred_job_types'])}")
        input("\nPress Enter to continue...")
        
        # Step 6: Job Scoring
        print("\nStep 6: Scoring and Ranking Jobs")
        print("-" * 70)
        scored_jobs = []
        for job in filtered_jobs:
            score_result = self.scorer.score_job(
                job,
                user_keywords=user_profile["desired_job_titles"],
                resume_text=resume_text,
                user_location=user_profile["location"],
                salary_range=(user_profile["min_salary"], user_profile["max_salary"]),
                preferred_job_types=user_profile["preferred_job_types"]
            )
            job.update(score_result)
            scored_jobs.append(job)
        
        scored_jobs.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        
        print(f"✓ Scored {len(scored_jobs)} jobs")
        print(f"\nTop 3 Matches:")
        for i, job in enumerate(scored_jobs[:3], 1):
            print(f"\n  {i}. {job['title']} at {job['company']}")
            print(f"     Score: {job['overall_score']:.2f}/100")
            print(f"     Highlight: {job.get('highlight', 'N/A')}")
            print(f"     Salary: ${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}")
            print(f"     Location: {job['location']} ({job['job_type']})")
        
        input("\nPress Enter to continue...")
        
        # Step 7: Resume Optimization Tips
        print("\nStep 7: Generating Resume Optimization Tips")
        print("-" * 70)
        tips = self.analyzer.generate_optimization_tips(
            resume_id,
            job_descriptions=[job["description"] for job in scored_jobs]
        )
        
        print(f"✓ Generated {len(tips['tips'])} optimization tips")
        print(f"  Resume strength score: {tips['strength_score']:.1f}/100")
        print(f"\nTop 3 Tips:")
        for i, tip in enumerate(tips["tips"][:3], 1):
            print(f"\n  {i}. [{tip['category']}] {tip['title']}")
            print(f"     {tip['description']}")
            print(f"     Impact: {tip['impact']}, Priority: {tip['priority']}")
        
        input("\nPress Enter to continue...")
        
        # Step 8: Export to Multiple Formats
        print("\nStep 8: Exporting Results")
        print("-" * 70)
        
        # Excel Export
        excel_file = os.path.join(self.demo_dir, "job_matches.xlsx")
        with open(excel_file, 'wb') as f:
            formatted_tips = self.analyzer.format_tips_for_excel(tips)
            self.excel_exporter.export_to_excel(
                scored_jobs,
                f,
                include_tips=True,
                tips_data=formatted_tips
            )
        print(f"✓ Excel export: {excel_file}")
        
        # CSV Export
        csv_file = os.path.join(self.demo_dir, "job_matches.csv")
        with open(csv_file, 'wb') as f:
            self.csv_exporter.export_to_csv(scored_jobs, f)
        print(f"✓ CSV export: {csv_file}")
        
        # PDF Export
        pdf_file = os.path.join(self.demo_dir, "job_matches.pdf")
        with open(pdf_file, 'wb') as f:
            self.pdf_exporter.export_to_pdf(scored_jobs, f, include_tips=True, tips=tips)
        print(f"✓ PDF export: {pdf_file}")
        
        print(f"\n✓ All files exported successfully to: {self.demo_dir}")
        input("\nPress Enter to continue...")
        
        # Step 9: Application Status Tracking
        print("\nStep 9: Application Status Tracking")
        print("-" * 70)
        
        # Apply to top 3 jobs
        status_updates = [
            (scored_jobs[0]["job_id"], ApplicationStatus.APPLIED, "Applied via company website"),
            (scored_jobs[1]["job_id"], ApplicationStatus.APPLIED, "Applied through referral"),
            (scored_jobs[2]["job_id"], ApplicationStatus.PENDING, "Resume under review")
        ]
        
        for job_id, status, note in status_updates:
            self.storage.update_job_status(
                job_id,
                status.value,
                notes=note,
                user=user_profile["user_id"]
            )
        
        print(f"✓ Updated application status for {len(status_updates)} jobs")
        
        # Show status summary
        summary = self.storage.get_status_summary()
        print(f"\nApplication Status Summary:")
        for status, count in summary["by_status"].items():
            print(f"  {status.title()}: {count}")
        
        print("\n" + "=" * 70)
        print("DEMO 1 COMPLETE!")
        print("=" * 70)
        print(f"\nWorkflow Summary:")
        print(f"  ✓ User profile created")
        print(f"  ✓ Resume uploaded and analyzed")
        print(f"  ✓ {stats['total_jobs']} jobs scraped")
        print(f"  ✓ {len(filtered_jobs)} jobs matched preferences")
        print(f"  ✓ Jobs scored and ranked")
        print(f"  ✓ {len(tips['tips'])} optimization tips generated")
        print(f"  ✓ Exported to Excel, CSV, and PDF")
        print(f"  ✓ Application status tracking initialized")
        print(f"\nAll output files are in: {self.demo_dir}")
        input("\nPress Enter to return to menu...")
    
    def demo_2_status_tracking_workflow(self):
        """Demo 2: Application status tracking workflow"""
        print("\n" + "=" * 70)
        print("DEMO 2: Application Status Tracking Workflow")
        print("=" * 70)
        print("This demo shows how to track application progress over time.")
        print()
        
        # Setup: Add some jobs
        jobs = [
            {"job_id": "track_001", "title": "Software Engineer", "company": "CompanyA"},
            {"job_id": "track_002", "title": "Full Stack Dev", "company": "CompanyB"},
            {"job_id": "track_003", "title": "Backend Engineer", "company": "CompanyC"}
        ]
        
        for job in jobs:
            job.update({
                "location": "San Francisco, CA",
                "job_type": "Remote",
                "description": "Sample job description"
            })
            self.storage.add_job(job)
        
        print("Scenario: Tracking 3 job applications over time\n")
        
        # Day 1: Apply to jobs
        print("Day 1: Applying to jobs")
        print("-" * 70)
        for job in jobs:
            self.storage.update_job_status(
                job["job_id"],
                ApplicationStatus.APPLIED.value,
                notes=f"Applied to {job['company']} via company website",
                user="demo_user"
            )
            print(f"✓ Applied to {job['title']} at {job['company']}")
        input("\nPress Enter to continue...")
        
        # Day 3: Get interview for first job
        print("\nDay 3: Interview Scheduled!")
        print("-" * 70)
        self.storage.update_job_status(
            jobs[0]["job_id"],
            ApplicationStatus.INTERVIEW.value,
            notes="Phone screen scheduled for next week",
            user="demo_user"
        )
        print(f"✓ Interview scheduled with {jobs[0]['company']}")
        input("\nPress Enter to continue...")
        
        # Day 5: Rejected from second job
        print("\nDay 5: Update from CompanyB")
        print("-" * 70)
        self.storage.update_job_status(
            jobs[1]["job_id"],
            ApplicationStatus.REJECTED.value,
            notes="Not moving forward at this time",
            user="demo_user"
        )
        print(f"✗ Rejected by {jobs[1]['company']}")
        input("\nPress Enter to continue...")
        
        # Day 7: Offer from first job!
        print("\nDay 7: Great News!")
        print("-" * 70)
        self.storage.update_job_status(
            jobs[0]["job_id"],
            ApplicationStatus.OFFER.value,
            notes="Received offer: $150k base + equity",
            user="demo_user"
        )
        print(f"🎉 Offer received from {jobs[0]['company']}!")
        input("\nPress Enter to continue...")
        
        # Show final status
        print("\nFinal Application Status")
        print("-" * 70)
        summary = self.storage.get_status_summary()
        print(f"Status Summary:")
        for status, count in summary["by_status"].items():
            print(f"  {status.title()}: {count}")
        
        print(f"\nDetailed Status:")
        for job in jobs:
            job_data = self.storage.get_job(job["job_id"])
            if job_data and "status" in job_data:
                print(f"  {job['company']}: {job_data['status'].upper()}")
        
        print("\n" + "=" * 70)
        print("DEMO 2 COMPLETE!")
        print("=" * 70)
        input("\nPress Enter to return to menu...")
    
    def demo_3_multiple_resume_comparison(self):
        """Demo 3: Compare multiple resumes against same jobs"""
        print("\n" + "=" * 70)
        print("DEMO 3: Multiple Resume Comparison")
        print("=" * 70)
        print("Compare different resume versions to see which scores better.")
        print()
        
        # Resume versions
        resumes = {
            "Original": "Software Engineer with Python and JavaScript experience. Worked on web applications.",
            "Enhanced": "Senior Software Engineer with 5+ years experience in Python, JavaScript, React, and AWS. Led development of scalable microservices. Expert in CI/CD, Docker, and Kubernetes.",
            "Keyword-Optimized": "Full Stack Software Engineer specializing in Python (Flask, Django, FastAPI), JavaScript (React, Node.js, TypeScript), and cloud technologies (AWS, Azure). Proven experience with microservices architecture, containerization (Docker, Kubernetes), CI/CD pipelines, and agile development. Strong background in REST APIs, PostgreSQL, MongoDB, and system design."
        }
        
        # Sample job
        job = {
            "job_id": "comparison_job",
            "title": "Senior Software Engineer",
            "company": "Top Tech Company",
            "description": "Looking for Senior Software Engineer with Python, JavaScript, React, and AWS experience. Must have microservices and CI/CD knowledge. Docker and Kubernetes required."
        }
        
        print(f"Comparing 3 resume versions against:")
        print(f"  Position: {job['title']}")
        print(f"  Company: {job['company']}")
        print()
        
        results = []
        for name, text in resumes.items():
            resume_id = self.analyzer.store_resume(text, user_id=f"user_{name}", filename=f"{name}.pdf")
            score_result = self.scorer.score_job(job, resume_text=text)
            results.append((name, score_result["overall_score"]))
            print(f"✓ Analyzed: {name} Resume")
        
        input("\nPress Enter to see results...")
        
        print("\nScoring Results")
        print("-" * 70)
        results.sort(key=lambda x: x[1], reverse=True)
        
        for i, (name, score) in enumerate(results, 1):
            print(f"\n{i}. {name} Resume")
            print(f"   Score: {score:.2f}/100")
            if i == 1:
                print(f"   🏆 Best Match!")
        
        print(f"\nInsight:")
        print(f"  The {results[0][0]} resume scored {results[0][1] - results[-1][1]:.1f} points higher")
        print(f"  than the {results[-1][0]} version due to better keyword matching")
        print(f"  and more specific technical details.")
        
        print("\n" + "=" * 70)
        print("DEMO 3 COMPLETE!")
        print("=" * 70)
        input("\nPress Enter to return to menu...")


def print_menu():
    """Print main menu"""
    print("\n" + "=" * 70)
    print("AI Job Application Assistant - End-to-End Integration Demo")
    print("=" * 70)
    print("\nAvailable Demos:")
    print("  1. Complete Basic Workflow (User Input → Export)")
    print("  2. Application Status Tracking Workflow")
    print("  3. Multiple Resume Comparison")
    print("  4. Run All Demos")
    print("  0. Exit")
    print()


def main():
    """Main demo program"""
    demo = EndToEndDemo()
    
    try:
        while True:
            print_menu()
            choice = input("Select demo (0-4): ").strip()
            
            if choice == "0":
                print("\nThank you for using the demo!")
                break
            elif choice == "1":
                demo.demo_1_complete_basic_workflow()
            elif choice == "2":
                demo.demo_2_status_tracking_workflow()
            elif choice == "3":
                demo.demo_3_multiple_resume_comparison()
            elif choice == "4":
                demo.demo_1_complete_basic_workflow()
                demo.demo_2_status_tracking_workflow()
                demo.demo_3_multiple_resume_comparison()
                print("\n✓ All demos completed!")
            else:
                print("\nInvalid choice. Please try again.")
    
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main()
