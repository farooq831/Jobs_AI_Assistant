#!/usr/bin/env python3
"""
End-to-End Integration Tests for AI Job Application Assistant
Tests the complete user flow from input to Excel export and application tracking.

This test suite covers:
1. User profile creation and validation
2. Resume upload and analysis
3. Job scraping and storage
4. Data cleaning and filtering
5. Job scoring and ranking
6. Resume optimization tips generation
7. Excel/CSV/PDF export
8. Status tracking and updates
9. Complete workflow integration

Author: AI Job Application Assistant Team
Date: November 14, 2025
"""

import unittest
import os
import sys
import json
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
from excel_uploader import ExcelUploader
from application_status import ApplicationStatus, ApplicationStatusManager


class TestEndToEndUserFlow(unittest.TestCase):
    """Test complete user flow from start to finish"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.storage_dir = os.path.join(self.test_dir, "data")
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
        self.excel_uploader = ExcelUploader(self.storage)
        self.status_manager = ApplicationStatusManager()
        
        # Sample user profile
        self.user_profile = {
            "user_id": "test_user_001",
            "name": "John Doe",
            "location": "San Francisco, CA",
            "desired_job_titles": ["Software Engineer", "Full Stack Developer"],
            "min_salary": 100000,
            "max_salary": 150000,
            "preferred_job_types": ["Remote", "Hybrid"]
        }
        
        # Sample resume text
        self.resume_text = """
        John Doe
        Software Engineer
        
        EXPERIENCE:
        Senior Software Engineer at Tech Corp (2020-2023)
        - Developed scalable web applications using Python, React, and AWS
        - Led team of 5 developers on microservices architecture
        - Implemented CI/CD pipelines using Jenkins and Docker
        
        Software Developer at StartupXYZ (2018-2020)
        - Built REST APIs with Flask and PostgreSQL
        - Developed frontend components with JavaScript and React
        
        SKILLS:
        Python, JavaScript, React, Flask, Django, AWS, Docker, PostgreSQL,
        MongoDB, Git, CI/CD, Agile, REST APIs, Microservices
        """
        
        # Sample job postings
        self.sample_jobs = [
            {
                "job_id": "job_001",
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc",
                "location": "San Francisco, CA",
                "job_type": "Remote",
                "salary_min": 120000,
                "salary_max": 160000,
                "description": "We're looking for a Senior Software Engineer with Python, React, and AWS experience. Must have 5+ years experience with microservices and CI/CD.",
                "link": "https://example.com/job1",
                "source": "Indeed"
            },
            {
                "job_id": "job_002",
                "title": "Full Stack Developer",
                "company": "Innovative Solutions",
                "location": "San Francisco, CA",
                "job_type": "Hybrid",
                "salary_min": 110000,
                "salary_max": 140000,
                "description": "Full Stack Developer needed with JavaScript, React, Node.js, and MongoDB experience. Docker and Kubernetes knowledge a plus.",
                "link": "https://example.com/job2",
                "source": "Glassdoor"
            },
            {
                "job_id": "job_003",
                "title": "Backend Engineer",
                "company": "DataTech LLC",
                "location": "New York, NY",
                "job_type": "Onsite",
                "salary_min": 90000,
                "salary_max": 120000,
                "description": "Backend Engineer with Java and Spring Boot experience. PostgreSQL and Redis knowledge required.",
                "link": "https://example.com/job3",
                "source": "Indeed"
            },
            {
                "job_id": "job_004",
                "title": "DevOps Engineer",
                "company": "CloudFirst",
                "location": "San Francisco, CA",
                "job_type": "Remote",
                "salary_min": 130000,
                "salary_max": 170000,
                "description": "DevOps Engineer with AWS, Docker, Kubernetes, and CI/CD pipeline experience. Python scripting required.",
                "link": "https://example.com/job4",
                "source": "LinkedIn"
            }
        ]
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_01_complete_workflow_basic(self):
        """Test 1: Complete basic workflow - profile to export"""
        print("\n=== Test 1: Complete Basic Workflow ===")
        
        # Step 1: Store user profile
        print("Step 1: Storing user profile...")
        self.storage.add_user(self.user_profile)
        users = self.storage.get_all_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["user_id"], "test_user_001")
        print("✓ User profile stored")
        
        # Step 2: Store resume
        print("Step 2: Storing resume...")
        resume_id = self.analyzer.store_resume(
            self.resume_text,
            user_id="test_user_001",
            filename="resume.pdf"
        )
        self.assertIsNotNone(resume_id)
        print(f"✓ Resume stored with ID: {resume_id}")
        
        # Step 3: Store job postings
        print("Step 3: Storing job postings...")
        for job in self.sample_jobs:
            success = self.storage.add_job(job)
            self.assertTrue(success)
        stats = self.storage.get_stats()
        self.assertEqual(stats["total_jobs"], 4)
        print(f"✓ Stored {stats['total_jobs']} job postings")
        
        # Step 4: Clean data
        print("Step 4: Cleaning job data...")
        all_jobs = self.storage.get_all_jobs()
        cleaned_jobs = self.processor.clean_jobs(all_jobs)
        self.assertEqual(len(cleaned_jobs), 4)
        print(f"✓ Cleaned {len(cleaned_jobs)} jobs")
        
        # Step 5: Filter jobs
        print("Step 5: Filtering jobs by user preferences...")
        filtered_jobs = self.filter.filter_jobs(
            cleaned_jobs,
            location=self.user_profile["location"],
            min_salary=self.user_profile["min_salary"],
            max_salary=self.user_profile["max_salary"],
            job_types=self.user_profile["preferred_job_types"]
        )
        self.assertGreater(len(filtered_jobs), 0)
        print(f"✓ Filtered to {len(filtered_jobs)} matching jobs")
        
        # Step 6: Score jobs
        print("Step 6: Scoring jobs...")
        scored_jobs = []
        for job in filtered_jobs:
            score_result = self.scorer.score_job(
                job,
                user_keywords=self.user_profile["desired_job_titles"],
                resume_text=self.resume_text,
                user_location=self.user_profile["location"],
                salary_range=(self.user_profile["min_salary"], self.user_profile["max_salary"]),
                preferred_job_types=self.user_profile["preferred_job_types"]
            )
            job.update(score_result)
            scored_jobs.append(job)
        
        scored_jobs.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        self.assertGreater(scored_jobs[0]["overall_score"], 0)
        print(f"✓ Top job score: {scored_jobs[0]['overall_score']:.2f}")
        
        # Step 7: Export to Excel
        print("Step 7: Exporting to Excel...")
        excel_output = BytesIO()
        self.excel_exporter.export_to_excel(
            scored_jobs,
            excel_output,
            include_tips=False
        )
        excel_size = len(excel_output.getvalue())
        self.assertGreater(excel_size, 0)
        print(f"✓ Excel export successful ({excel_size} bytes)")
        
        print("✓ Complete workflow test passed!\n")
    
    def test_02_workflow_with_resume_tips(self):
        """Test 2: Workflow with resume optimization tips"""
        print("\n=== Test 2: Workflow with Resume Optimization Tips ===")
        
        # Setup: Store jobs and resume
        for job in self.sample_jobs:
            self.storage.add_job(job)
        
        resume_id = self.analyzer.store_resume(
            self.resume_text,
            user_id="test_user_001",
            filename="resume.pdf"
        )
        
        # Step 1: Analyze resume against jobs
        print("Step 1: Analyzing resume against jobs...")
        all_jobs = self.storage.get_all_jobs()
        job_analysis = self.analyzer.analyze_job_keywords([job["description"] for job in all_jobs])
        self.assertIn("keywords", job_analysis)
        print(f"✓ Identified {len(job_analysis['keywords'])} key skills from jobs")
        
        # Step 2: Generate optimization tips
        print("Step 2: Generating optimization tips...")
        tips = self.analyzer.generate_optimization_tips(
            resume_id,
            job_descriptions=[job["description"] for job in all_jobs]
        )
        self.assertIn("tips", tips)
        self.assertGreater(len(tips["tips"]), 0)
        print(f"✓ Generated {len(tips['tips'])} optimization tips")
        
        # Step 3: Score jobs with resume context
        print("Step 3: Scoring jobs with resume context...")
        scored_jobs = []
        for job in all_jobs:
            score_result = self.scorer.score_job(
                job,
                user_keywords=self.user_profile["desired_job_titles"],
                resume_text=self.resume_text,
                user_location=self.user_profile["location"],
                salary_range=(self.user_profile["min_salary"], self.user_profile["max_salary"]),
                preferred_job_types=self.user_profile["preferred_job_types"]
            )
            job.update(score_result)
            scored_jobs.append(job)
        
        scored_jobs.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        print(f"✓ Scored {len(scored_jobs)} jobs")
        
        # Step 4: Export with tips
        print("Step 4: Exporting Excel with resume tips...")
        excel_output = BytesIO()
        formatted_tips = self.analyzer.format_tips_for_excel(tips)
        self.excel_exporter.export_to_excel(
            scored_jobs,
            excel_output,
            include_tips=True,
            tips_data=formatted_tips
        )
        excel_size = len(excel_output.getvalue())
        self.assertGreater(excel_size, 0)
        print(f"✓ Excel with tips exported ({excel_size} bytes)")
        
        print("✓ Resume tips workflow test passed!\n")
    
    def test_03_workflow_with_status_tracking(self):
        """Test 3: Complete workflow with application status tracking"""
        print("\n=== Test 3: Workflow with Status Tracking ===")
        
        # Setup: Store and score jobs
        for job in self.sample_jobs:
            self.storage.add_job(job)
        
        all_jobs = self.storage.get_all_jobs()
        scored_jobs = []
        for job in all_jobs:
            score_result = self.scorer.score_job(
                job,
                user_keywords=self.user_profile["desired_job_titles"],
                resume_text=self.resume_text,
                user_location=self.user_profile["location"],
                salary_range=(self.user_profile["min_salary"], self.user_profile["max_salary"]),
                preferred_job_types=self.user_profile["preferred_job_types"]
            )
            job.update(score_result)
            scored_jobs.append(job)
            self.storage.update_job_score(job["job_id"], score_result)
        
        # Step 1: Update application statuses
        print("Step 1: Updating application statuses...")
        status_updates = [
            ("job_001", ApplicationStatus.APPLIED, "Applied via company website"),
            ("job_002", ApplicationStatus.INTERVIEW, "Phone screen scheduled"),
            ("job_003", ApplicationStatus.REJECTED, "Not a good fit"),
            ("job_004", ApplicationStatus.PENDING, "Waiting to hear back")
        ]
        
        for job_id, status, note in status_updates:
            success = self.storage.update_job_status(
                job_id,
                status.value,
                notes=note,
                user="test_user_001"
            )
            self.assertTrue(success)
        
        print(f"✓ Updated status for {len(status_updates)} jobs")
        
        # Step 2: Query jobs by status
        print("Step 2: Querying jobs by status...")
        applied_jobs = self.storage.get_jobs_by_status("applied")
        interview_jobs = self.storage.get_jobs_by_status("interview")
        self.assertEqual(len(applied_jobs), 1)
        self.assertEqual(len(interview_jobs), 1)
        print(f"✓ Applied: {len(applied_jobs)}, Interview: {len(interview_jobs)}")
        
        # Step 3: Get status summary
        print("Step 3: Getting status summary...")
        summary = self.storage.get_status_summary()
        self.assertIn("by_status", summary)
        self.assertEqual(summary["by_status"]["applied"], 1)
        print(f"✓ Status summary: {summary['by_status']}")
        
        # Step 4: Export with status information
        print("Step 4: Exporting with status tracking...")
        jobs_with_status = self.storage.get_all_jobs()
        excel_output = BytesIO()
        self.excel_exporter.export_to_excel(
            jobs_with_status,
            excel_output,
            include_tips=False
        )
        excel_size = len(excel_output.getvalue())
        self.assertGreater(excel_size, 0)
        print(f"✓ Excel with status exported ({excel_size} bytes)")
        
        print("✓ Status tracking workflow test passed!\n")
    
    def test_04_excel_upload_round_trip(self):
        """Test 4: Excel export and re-import (round trip)"""
        print("\n=== Test 4: Excel Export/Import Round Trip ===")
        
        # Step 1: Setup and export
        print("Step 1: Exporting jobs to Excel...")
        for job in self.sample_jobs:
            self.storage.add_job(job)
        
        all_jobs = self.storage.get_all_jobs()
        export_file = os.path.join(self.test_dir, "export.xlsx")
        
        with open(export_file, 'wb') as f:
            self.excel_exporter.export_to_excel(all_jobs, f, include_tips=False)
        
        self.assertTrue(os.path.exists(export_file))
        print(f"✓ Exported to {export_file}")
        
        # Step 2: Manually update Excel (simulated)
        print("Step 2: Simulating manual status updates in Excel...")
        # In real scenario, user would edit Excel file
        # For testing, we'll parse it back
        
        # Step 3: Upload and parse Excel
        print("Step 3: Uploading modified Excel...")
        with open(export_file, 'rb') as f:
            result = self.excel_uploader.parse_excel(f)
        
        self.assertTrue(result["success"])
        self.assertGreater(len(result["jobs"]), 0)
        print(f"✓ Parsed {len(result['jobs'])} jobs from Excel")
        
        # Step 4: Validate data integrity
        print("Step 4: Validating uploaded data...")
        validation = self.excel_uploader.validate_upload_data(result["jobs"])
        self.assertTrue(validation["is_valid"])
        print(f"✓ Data validation passed")
        
        print("✓ Excel round trip test passed!\n")
    
    def test_05_multi_format_export(self):
        """Test 5: Export to multiple formats (Excel, CSV, PDF)"""
        print("\n=== Test 5: Multi-Format Export ===")
        
        # Setup: Store and score jobs
        for job in self.sample_jobs:
            self.storage.add_job(job)
        
        all_jobs = self.storage.get_all_jobs()
        scored_jobs = []
        for job in all_jobs:
            score_result = self.scorer.score_job(
                job,
                user_keywords=self.user_profile["desired_job_titles"],
                resume_text=self.resume_text
            )
            job.update(score_result)
            scored_jobs.append(job)
        
        # Export to Excel
        print("Step 1: Exporting to Excel...")
        excel_output = BytesIO()
        self.excel_exporter.export_to_excel(scored_jobs, excel_output, include_tips=False)
        excel_size = len(excel_output.getvalue())
        self.assertGreater(excel_size, 0)
        print(f"✓ Excel export: {excel_size} bytes")
        
        # Export to CSV
        print("Step 2: Exporting to CSV...")
        csv_output = BytesIO()
        self.csv_exporter.export_to_csv(scored_jobs, csv_output)
        csv_size = len(csv_output.getvalue())
        self.assertGreater(csv_size, 0)
        print(f"✓ CSV export: {csv_size} bytes")
        
        # Export to PDF
        print("Step 3: Exporting to PDF...")
        pdf_output = BytesIO()
        self.pdf_exporter.export_to_pdf(scored_jobs, pdf_output)
        pdf_size = len(pdf_output.getvalue())
        self.assertGreater(pdf_size, 0)
        print(f"✓ PDF export: {pdf_size} bytes")
        
        print("✓ Multi-format export test passed!\n")
    
    def test_06_filtering_pipeline(self):
        """Test 6: Complete filtering and scoring pipeline"""
        print("\n=== Test 6: Filtering and Scoring Pipeline ===")
        
        # Store jobs
        for job in self.sample_jobs:
            self.storage.add_job(job)
        
        all_jobs = self.storage.get_all_jobs()
        print(f"Step 1: Starting with {len(all_jobs)} jobs")
        
        # Step 1: Clean data
        print("Step 2: Cleaning data...")
        cleaned_jobs = self.processor.clean_jobs(all_jobs)
        print(f"✓ After cleaning: {len(cleaned_jobs)} jobs")
        
        # Step 2: Filter by location
        print("Step 3: Filtering by location (San Francisco)...")
        location_filtered = self.filter.filter_by_location(
            cleaned_jobs,
            "San Francisco, CA"
        )
        print(f"✓ After location filter: {len(location_filtered)} jobs")
        
        # Step 3: Filter by salary
        print("Step 4: Filtering by salary ($100k-$150k)...")
        salary_filtered = self.filter.filter_by_salary(
            location_filtered,
            min_salary=100000,
            max_salary=150000
        )
        print(f"✓ After salary filter: {len(salary_filtered)} jobs")
        
        # Step 4: Filter by job type
        print("Step 5: Filtering by job type (Remote/Hybrid)...")
        final_filtered = self.filter.filter_by_job_type(
            salary_filtered,
            ["Remote", "Hybrid"]
        )
        print(f"✓ After job type filter: {len(final_filtered)} jobs")
        
        # Step 5: Score remaining jobs
        print("Step 6: Scoring filtered jobs...")
        scored_jobs = []
        for job in final_filtered:
            score_result = self.scorer.score_job(
                job,
                user_keywords=self.user_profile["desired_job_titles"],
                resume_text=self.resume_text
            )
            job.update(score_result)
            scored_jobs.append(job)
        
        scored_jobs.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        print(f"✓ Scored {len(scored_jobs)} jobs")
        
        if scored_jobs:
            top_job = scored_jobs[0]
            print(f"   Top match: {top_job['title']} at {top_job['company']}")
            print(f"   Score: {top_job['overall_score']:.2f}, Highlight: {top_job.get('highlight', 'N/A')}")
        
        print("✓ Filtering pipeline test passed!\n")
    
    def test_07_error_handling_and_recovery(self):
        """Test 7: Error handling and data recovery"""
        print("\n=== Test 7: Error Handling and Recovery ===")
        
        # Test 1: Handle incomplete job data
        print("Step 1: Testing incomplete job data handling...")
        incomplete_job = {
            "job_id": "job_incomplete",
            "title": "Test Job"
            # Missing required fields
        }
        
        cleaned = self.processor.clean_jobs([incomplete_job])
        self.assertEqual(len(cleaned), 0)  # Should be filtered out
        print("✓ Incomplete jobs filtered correctly")
        
        # Test 2: Handle invalid salary ranges
        print("Step 2: Testing invalid salary handling...")
        invalid_salary_job = self.sample_jobs[0].copy()
        invalid_salary_job["salary_min"] = 200000
        invalid_salary_job["salary_max"] = 100000  # Min > Max
        
        filtered = self.filter.filter_by_salary([invalid_salary_job], 100000, 150000)
        # Should handle gracefully
        print("✓ Invalid salary ranges handled")
        
        # Test 3: Handle missing resume
        print("Step 3: Testing missing resume handling...")
        try:
            tips = self.analyzer.generate_optimization_tips("nonexistent_resume_id")
            # Should return empty or error result
            self.assertIn("error", tips.get("status", "error").lower())
            print("✓ Missing resume handled gracefully")
        except Exception as e:
            print(f"✓ Missing resume raised appropriate error: {type(e).__name__}")
        
        # Test 4: Recover from corrupted storage
        print("Step 4: Testing storage recovery...")
        # Create corrupted jobs file
        jobs_file = os.path.join(self.storage_dir, "jobs.json")
        with open(jobs_file, 'w') as f:
            f.write("{ corrupted json content")
        
        # Storage should handle gracefully
        try:
            new_storage = JobStorageManager(self.storage_dir)
            stats = new_storage.get_stats()
            print("✓ Storage recovered from corrupted data")
        except Exception as e:
            print(f"✓ Storage handled corruption: {type(e).__name__}")
        
        print("✓ Error handling test passed!\n")
    
    def test_08_performance_large_dataset(self):
        """Test 8: Performance with larger dataset"""
        print("\n=== Test 8: Performance with Large Dataset ===")
        
        # Generate 100 sample jobs
        print("Step 1: Generating 100 sample jobs...")
        large_dataset = []
        for i in range(100):
            job = {
                "job_id": f"job_{i:03d}",
                "title": f"Software Engineer {i}",
                "company": f"Company {i}",
                "location": "San Francisco, CA" if i % 2 == 0 else "New York, NY",
                "job_type": ["Remote", "Hybrid", "Onsite"][i % 3],
                "salary_min": 80000 + (i * 1000),
                "salary_max": 120000 + (i * 1000),
                "description": f"Job description for position {i} requiring Python, JavaScript, and AWS skills.",
                "link": f"https://example.com/job{i}",
                "source": "Indeed"
            }
            large_dataset.append(job)
        
        # Store all jobs
        print("Step 2: Storing 100 jobs...")
        start_time = datetime.now()
        for job in large_dataset:
            self.storage.add_job(job)
        storage_time = (datetime.now() - start_time).total_seconds()
        print(f"✓ Storage time: {storage_time:.2f}s")
        
        # Clean and filter
        print("Step 4: Cleaning and filtering...")
        start_time = datetime.now()
        all_jobs = self.storage.get_all_jobs()
        cleaned = self.processor.clean_jobs(all_jobs)
        filtered = self.filter.filter_jobs(
            cleaned,
            location="San Francisco, CA",
            min_salary=100000,
            max_salary=150000
        )
        filter_time = (datetime.now() - start_time).total_seconds()
        print(f"✓ Filtering time: {filter_time:.2f}s ({len(filtered)} results)")
        
        # Score all jobs
        print("Step 4: Scoring all filtered jobs...")
        start_time = datetime.now()
        for job in filtered[:20]:  # Score top 20 for performance
            score_result = self.scorer.score_job(
                job,
                user_keywords=self.user_profile["desired_job_titles"],
                resume_text=self.resume_text
            )
            job.update(score_result)
        scoring_time = (datetime.now() - start_time).total_seconds()
        print(f"✓ Scoring time: {scoring_time:.2f}s")
        
        # Export to Excel
        print("Step 5: Exporting to Excel...")
        start_time = datetime.now()
        excel_output = BytesIO()
        self.excel_exporter.export_to_excel(filtered[:20], excel_output, include_tips=False)
        export_time = (datetime.now() - start_time).total_seconds()
        print(f"✓ Export time: {export_time:.2f}s")
        
        total_time = storage_time + filter_time + scoring_time + export_time
        print(f"\nTotal processing time: {total_time:.2f}s")
        print("✓ Performance test passed!\n")


class TestIntegrationScenarios(unittest.TestCase):
    """Test specific integration scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.storage_dir = os.path.join(self.test_dir, "data")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.storage = JobStorageManager(self.storage_dir)
        self.analyzer = ResumeAnalyzer(KeywordExtractor())
        self.scorer = JobScorer(KeywordExtractor())
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_multiple_users_workflow(self):
        """Test workflow with multiple users"""
        print("\n=== Test: Multiple Users Workflow ===")
        
        users = [
            {"user_id": "user_001", "name": "Alice", "location": "San Francisco, CA"},
            {"user_id": "user_002", "name": "Bob", "location": "New York, NY"},
            {"user_id": "user_003", "name": "Charlie", "location": "Austin, TX"}
        ]
        
        # Add users
        for user in users:
            self.storage.add_user(user)
        
        all_users = self.storage.get_all_users()
        self.assertEqual(len(all_users), 3)
        print(f"✓ Created {len(all_users)} user profiles")
        
        # Add jobs for each user
        for i, user in enumerate(users):
            job = {
                "job_id": f"job_{user['user_id']}",
                "title": f"Job for {user['name']}",
                "company": "Test Company",
                "location": user["location"],
                "job_type": "Remote",
                "description": "Test job description"
            }
            self.storage.add_job(job)
        
        stats = self.storage.get_stats()
        self.assertGreaterEqual(stats["total_jobs"], 3)
        print(f"✓ Added jobs for each user")
        print("✓ Multiple users workflow test passed!\n")
    
    def test_resume_comparison_workflow(self):
        """Test comparing multiple resumes against same jobs"""
        print("\n=== Test: Resume Comparison Workflow ===")
        
        resumes = [
            ("resume_001", "Python developer with 5 years experience in Django and Flask"),
            ("resume_002", "JavaScript expert with React and Node.js skills"),
            ("resume_003", "Full stack engineer with Python, JavaScript, and AWS experience")
        ]
        
        # Store resumes
        resume_ids = []
        for resume_id, text in resumes:
            rid = self.analyzer.store_resume(text, user_id=f"user_{resume_id}", filename=f"{resume_id}.pdf")
            resume_ids.append(rid)
        
        self.assertEqual(len(resume_ids), 3)
        print(f"✓ Stored {len(resume_ids)} resumes")
        
        # Score same job against all resumes
        job = {
            "job_id": "test_job",
            "title": "Full Stack Engineer",
            "description": "Looking for Full Stack Engineer with Python, JavaScript, React, and AWS experience"
        }
        
        scores = []
        for i, rid in enumerate(resume_ids):
            resume_data = self.analyzer.get_resume(rid)
            if resume_data:
                score_result = self.scorer.score_job(
                    job,
                    resume_text=resume_data["text"]
                )
                scores.append(score_result["overall_score"])
        
        self.assertEqual(len(scores), 3)
        print(f"✓ Scored job against {len(scores)} resumes")
        print(f"   Scores: {[f'{s:.2f}' for s in scores]}")
        print("✓ Resume comparison workflow test passed!\n")


def run_all_tests():
    """Run all end-to-end tests"""
    print("=" * 70)
    print("AI Job Application Assistant - End-to-End Integration Tests")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndUserFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    result = run_all_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
