#!/usr/bin/env python3
"""
Test Suite for Task 9.2: Forms and File Upload Controls
Comprehensive tests for all form validation and file upload functionality
"""

import unittest
import requests
import json
import os
import sys
from io import BytesIO
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# API Base URL
BASE_URL = "http://localhost:5000"


class TestUserDetailsForm(unittest.TestCase):
    """Test cases for User Details Form"""
    
    def test_01_valid_user_details_submission(self):
        """Test submitting valid user details"""
        data = {
            "name": "John Doe",
            "location": "New York, NY",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Software Engineer", "Developer"],
            "job_types": ["Remote", "Hybrid"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn('message', result)
    
    def test_02_missing_required_fields(self):
        """Test validation with missing required fields"""
        data = {
            "name": "",
            "location": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('errors', result)
    
    def test_03_invalid_salary_range(self):
        """Test validation with invalid salary range (min > max)"""
        data = {
            "name": "John Doe",
            "location": "New York, NY",
            "salary_min": 120000,
            "salary_max": 70000,
            "job_titles": ["Engineer"],
            "job_types": ["Remote"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_04_name_too_short(self):
        """Test validation with name too short"""
        data = {
            "name": "A",
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Dev"],
            "job_types": ["Remote"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_05_name_too_long(self):
        """Test validation with name too long"""
        data = {
            "name": "A" * 150,
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Dev"],
            "job_types": ["Remote"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_06_negative_salary(self):
        """Test validation with negative salary"""
        data = {
            "name": "John Doe",
            "location": "NYC",
            "salary_min": -5000,
            "salary_max": 100000,
            "job_titles": ["Dev"],
            "job_types": ["Remote"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_07_empty_job_titles(self):
        """Test validation with empty job titles"""
        data = {
            "name": "John Doe",
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": [],
            "job_types": ["Remote"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_08_no_job_types_selected(self):
        """Test validation with no job types selected"""
        data = {
            "name": "John Doe",
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Developer"],
            "job_types": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 400)


class TestJobTypeSelection(unittest.TestCase):
    """Test cases for Job Type Selection"""
    
    def test_01_remote_only(self):
        """Test selecting Remote job type only"""
        data = {
            "name": "Test User",
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Engineer"],
            "job_types": ["Remote"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_02_onsite_only(self):
        """Test selecting Onsite job type only"""
        data = {
            "name": "Test User",
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Engineer"],
            "job_types": ["Onsite"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_03_hybrid_only(self):
        """Test selecting Hybrid job type only"""
        data = {
            "name": "Test User",
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Engineer"],
            "job_types": ["Hybrid"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_04_all_job_types(self):
        """Test selecting all job types"""
        data = {
            "name": "Test User",
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Engineer"],
            "job_types": ["Remote", "Onsite", "Hybrid"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_05_multiple_job_types(self):
        """Test selecting multiple job types"""
        data = {
            "name": "Test User",
            "location": "NYC",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Engineer"],
            "job_types": ["Remote", "Hybrid"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)


class TestResumeUpload(unittest.TestCase):
    """Test cases for Resume Upload"""
    
    def test_01_upload_pdf_resume(self):
        """Test uploading a PDF resume"""
        # Create a minimal PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\nxref\n0 2\ntrailer\n<< /Size 2 /Root 1 0 R >>\nstartxref\n50\n%%EOF"
        
        files = {
            'resume': ('test_resume.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resume-upload",
            files=files
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn('resume_id', result)
        self.assertIn('filename', result)
    
    def test_02_invalid_file_type(self):
        """Test uploading invalid file type"""
        files = {
            'resume': ('test.txt', BytesIO(b"Not a resume"), 'text/plain')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resume-upload",
            files=files
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_03_missing_file(self):
        """Test upload without file"""
        response = requests.post(f"{BASE_URL}/api/resume-upload")
        
        self.assertEqual(response.status_code, 400)


class TestExportFunctionality(unittest.TestCase):
    """Test cases for Export Functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_jobs = [
            {
                "id": "job_001",
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "New York, NY",
                "salary": "$80,000 - $120,000",
                "job_type": "Remote",
                "match_score": 85,
                "highlight": "green"
            }
        ]
    
    def test_01_export_to_excel(self):
        """Test exporting jobs to Excel"""
        data = {
            "jobs": self.sample_jobs,
            "user_id": "test_user",
            "include_tips": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/export/excel",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      response.headers.get('Content-Type', ''))
    
    def test_02_export_to_csv(self):
        """Test exporting jobs to CSV"""
        data = {
            "jobs": self.sample_jobs,
            "user_id": "test_user"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/export/csv",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.headers.get('Content-Type', ''))
    
    def test_03_export_to_pdf(self):
        """Test exporting jobs to PDF"""
        data = {
            "jobs": self.sample_jobs,
            "user_id": "test_user",
            "include_tips": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/export/pdf",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/pdf', response.headers.get('Content-Type', ''))
    
    def test_04_export_empty_jobs_list(self):
        """Test exporting with empty jobs list"""
        data = {
            "jobs": [],
            "user_id": "test_user"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/export/excel",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400])


class TestFileValidation(unittest.TestCase):
    """Test cases for File Validation"""
    
    def test_01_file_size_limit(self):
        """Test file size limit validation"""
        # Note: This is a conceptual test
        # Actual implementation would require creating a large file
        pass
    
    def test_02_file_extension_validation(self):
        """Test file extension validation"""
        invalid_files = [
            ('test.exe', b'invalid', 'application/x-msdownload'),
            ('test.jpg', b'invalid', 'image/jpeg'),
            ('test.mp3', b'invalid', 'audio/mpeg')
        ]
        
        for filename, content, mime_type in invalid_files:
            files = {
                'resume': (filename, BytesIO(content), mime_type)
            }
            
            response = requests.post(
                f"{BASE_URL}/api/resume-upload",
                files=files
            )
            
            self.assertEqual(response.status_code, 400)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestUserDetailsForm))
    suite.addTests(loader.loadTestsFromTestCase(TestJobTypeSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestResumeUpload))
    suite.addTests(loader.loadTestsFromTestCase(TestExportFunctionality))
    suite.addTests(loader.loadTestsFromTestCase(TestFileValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("="*70)
    print("TASK 9.2: FORMS AND FILE UPLOAD CONTROLS - TEST SUITE")
    print("="*70)
    print("\nMake sure the Flask backend is running on http://localhost:5000")
    print("Press Enter to start tests...")
    input()
    
    success = run_tests()
    sys.exit(0 if success else 1)
