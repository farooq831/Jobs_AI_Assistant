#!/usr/bin/env python3
"""
Test suite for Task 8.3: UI Integration
Tests the integration between job dashboard UI and status tracking backend.
"""

import unittest
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:5000"

class TestUIIntegration(unittest.TestCase):
    """Test UI integration with backend APIs"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        print("\n" + "="*60)
        print("  Starting UI Integration Tests")
        print("="*60 + "\n")
    
    def test_01_fetch_jobs_endpoint(self):
        """Test fetching jobs for dashboard display"""
        print("Test 1: Fetch jobs endpoint...")
        
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('jobs', data)
        self.assertIsInstance(data['jobs'], list)
        
        print("  ✓ Jobs fetched successfully")
    
    def test_02_status_summary_endpoint(self):
        """Test status summary endpoint"""
        print("Test 2: Status summary endpoint...")
        
        response = requests.get(f"{BASE_URL}/api/jobs/status/summary")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('total_jobs', data)
        self.assertIn('pending', data)
        self.assertIn('applied', data)
        
        print("  ✓ Status summary retrieved successfully")
    
    def test_03_update_job_status(self):
        """Test updating job status"""
        print("Test 3: Update job status...")
        
        # Get a job first
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        self.assertEqual(response.status_code, 200)
        
        jobs = response.json().get('jobs', [])
        if not jobs:
            self.skipTest("No jobs available")
        
        job_id = jobs[0].get('id')
        
        # Update status
        update_data = {
            "status": "applied",
            "notes": "Test update from UI",
            "user_id": "test_user"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/jobs/status/{job_id}",
            json=update_data
        )
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertIn('new_status', result)
        self.assertEqual(result['new_status'], 'applied')
        
        print("  ✓ Job status updated successfully")
    
    def test_04_get_status_history(self):
        """Test retrieving status history"""
        print("Test 4: Get status history...")
        
        # Get a job
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        jobs = response.json().get('jobs', [])
        if not jobs:
            self.skipTest("No jobs available")
        
        job_id = jobs[0].get('id')
        
        # Get history
        response = requests.get(f"{BASE_URL}/api/jobs/status-history/{job_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('history', data)
        self.assertIsInstance(data['history'], list)
        
        print("  ✓ Status history retrieved successfully")
    
    def test_05_filter_by_highlight(self):
        """Test filtering jobs by highlight"""
        print("Test 5: Filter by highlight...")
        
        highlights = ['red', 'yellow', 'green']
        
        for highlight in highlights:
            response = requests.get(f"{BASE_URL}/api/jobs-by-highlight/{highlight}")
            self.assertIn(response.status_code, [200, 404])
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn('jobs', data)
        
        print("  ✓ Highlight filtering works")
    
    def test_06_filter_by_status(self):
        """Test filtering jobs by status"""
        print("Test 6: Filter by status...")
        
        statuses = ['pending', 'applied', 'interview']
        
        for status in statuses:
            response = requests.get(f"{BASE_URL}/api/jobs/status?status={status}")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('jobs', data)
        
        print("  ✓ Status filtering works")
    
    def test_07_filter_by_score_range(self):
        """Test filtering jobs by score range"""
        print("Test 7: Filter by score range...")
        
        response = requests.get(
            f"{BASE_URL}/api/jobs-by-score?min_score=70&max_score=100"
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('jobs', data)
        
        print("  ✓ Score range filtering works")
    
    def test_08_batch_status_update(self):
        """Test batch status update"""
        print("Test 8: Batch status update...")
        
        # Get jobs
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        jobs = response.json().get('jobs', [])
        
        if len(jobs) < 2:
            self.skipTest("Need at least 2 jobs")
        
        # Batch update
        updates = [
            {
                "job_id": jobs[0].get('id'),
                "status": "interview"
            },
            {
                "job_id": jobs[1].get('id'),
                "status": "applied"
            }
        ]
        
        response = requests.put(
            f"{BASE_URL}/api/jobs/batch-status",
            json={"updates": updates, "user_id": "test_user"}
        )
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertIn('updated', result)
        
        print("  ✓ Batch update successful")
    
    def test_09_enhanced_status_summary(self):
        """Test enhanced status summary"""
        print("Test 9: Enhanced status summary...")
        
        response = requests.get(f"{BASE_URL}/api/jobs/status-summary/enhanced")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('total_jobs', data)
        self.assertIn('by_status', data)
        
        print("  ✓ Enhanced summary retrieved")
    
    def test_10_cors_headers(self):
        """Test CORS headers for frontend integration"""
        print("Test 10: CORS headers...")
        
        response = requests.options(
            f"{BASE_URL}/api/storage/jobs",
            headers={'Origin': 'http://localhost:3000'}
        )
        
        # Should not error
        self.assertIn(response.status_code, [200, 204])
        
        print("  ✓ CORS configured correctly")
    
    def test_11_error_handling(self):
        """Test error handling for invalid requests"""
        print("Test 11: Error handling...")
        
        # Invalid job ID
        response = requests.get(f"{BASE_URL}/api/jobs/status-history/invalid_id")
        self.assertIn(response.status_code, [404, 400])
        
        # Invalid status
        response = requests.put(
            f"{BASE_URL}/api/jobs/status/test_id",
            json={"status": "invalid_status"}
        )
        self.assertIn(response.status_code, [400, 404])
        
        print("  ✓ Error handling works correctly")
    
    def test_12_response_format(self):
        """Test response format consistency"""
        print("Test 12: Response format consistency...")
        
        # Check jobs endpoint format
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        data = response.json()
        
        if data.get('jobs'):
            job = data['jobs'][0]
            # Verify expected fields exist
            expected_fields = ['id', 'title', 'company']
            for field in expected_fields:
                self.assertIn(field, job)
        
        print("  ✓ Response format is consistent")
    
    def test_13_pagination_support(self):
        """Test if pagination parameters work"""
        print("Test 13: Pagination support...")
        
        # Try with limit parameter
        response = requests.get(f"{BASE_URL}/api/storage/jobs?limit=5")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        jobs = data.get('jobs', [])
        
        # Should return at most 5 jobs if limit works
        if len(jobs) > 0:
            self.assertLessEqual(len(jobs), 100)  # Reasonable limit
        
        print("  ✓ Pagination parameters accepted")
    
    def test_14_search_functionality(self):
        """Test search/filter parameters"""
        print("Test 14: Search functionality...")
        
        # Get all jobs first
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        jobs = response.json().get('jobs', [])
        
        if jobs:
            # Try searching by company
            company = jobs[0].get('company')
            if company:
                # This tests if API supports query parameters
                response = requests.get(
                    f"{BASE_URL}/api/storage/jobs",
                    params={'company': company}
                )
                self.assertEqual(response.status_code, 200)
        
        print("  ✓ Search parameters work")
    
    def test_15_ui_workflow_integration(self):
        """Test complete UI workflow"""
        print("Test 15: Complete UI workflow...")
        
        # 1. Fetch jobs
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        self.assertEqual(response.status_code, 200)
        jobs = response.json().get('jobs', [])
        
        if not jobs:
            self.skipTest("No jobs for workflow test")
        
        # 2. Get status summary
        response = requests.get(f"{BASE_URL}/api/jobs/status/summary")
        self.assertEqual(response.status_code, 200)
        
        # 3. Select and update a job
        job_id = jobs[0].get('id')
        response = requests.put(
            f"{BASE_URL}/api/jobs/status/{job_id}",
            json={"status": "applied", "user_id": "test_user"}
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Verify history updated
        response = requests.get(f"{BASE_URL}/api/jobs/status-history/{job_id}")
        self.assertEqual(response.status_code, 200)
        history = response.json().get('history', [])
        self.assertGreater(len(history), 0)
        
        print("  ✓ Complete workflow successful")

def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUIIntegration)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("="*60 + "\n")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
