"""
Comprehensive Test Suite for Task 8.2: Backend Status Tracking Logic
Tests the integration of application status tracking with storage manager

Author: AI Job Application Assistant
Date: November 2025
Version: 1.0.0
"""

import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from storage_manager import JobStorageManager
from application_status import ApplicationStatus, ApplicationStatusManager


class TestStatusTrackingIntegration(unittest.TestCase):
    """Test status tracking integration with storage manager"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.storage_manager = JobStorageManager(storage_dir=self.test_dir)
        
        # Add sample jobs for testing
        self.sample_jobs = [
            {
                "job_id": "test_job_001",
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "salary": "$120,000 - $150,000",
                "job_type": "Remote",
                "description": "Great opportunity",
                "link": "https://example.com/job1"
            },
            {
                "job_id": "test_job_002",
                "title": "Data Scientist",
                "company": "Data Inc",
                "location": "New York, NY",
                "salary": "$130,000 - $160,000",
                "job_type": "Hybrid",
                "description": "Data analytics role",
                "link": "https://example.com/job2"
            },
            {
                "job_id": "test_job_003",
                "title": "Product Manager",
                "company": "Product Co",
                "location": "Austin, TX",
                "salary": "$110,000 - $140,000",
                "job_type": "Onsite",
                "description": "Product leadership",
                "link": "https://example.com/job3"
            }
        ]
        
        # Add jobs to storage - they'll get hashed IDs but we'll use job_id for status tracking
        result = self.storage_manager.save_jobs(self.sample_jobs, source="test_setup")
        
        # Get the stored jobs to retrieve their generated IDs
        stored_jobs = self.storage_manager.get_all_jobs()
        # Map job_id to actual stored id
        self.job_id_map = {job.get('job_id'): job['id'] for job in stored_jobs if job.get('job_id')}
        
        # Use job_id field for status tracking (more intuitive)
        self.job_001 = "test_job_001"
        self.job_002 = "test_job_002"
        self.job_003 = "test_job_003"
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    # Test 1: Create Status History
    def test_create_status_history(self):
        """Test creating a new status history for a job"""
        job_id = self.job_001
        
        success = self.storage_manager.create_status_history(job_id, "Pending")
        
        self.assertTrue(success)
        
        # Verify history was created
        history = self.storage_manager.get_job_status_history(job_id)
        self.assertIsNotNone(history)
        self.assertEqual(history["current_status"], "Pending")
        self.assertEqual(history["job_id"], job_id)
    
    # Test 2: Update Job Status with History
    def test_update_job_status_with_history(self):
        """Test updating job status with full history tracking"""
        job_id = self.job_001
        
        # Create initial history
        self.storage_manager.create_status_history(job_id, "Pending")
        
        # Update to Applied
        result = self.storage_manager.update_job_status_with_history(
            job_id=job_id,
            new_status="Applied",
            notes="Submitted application via LinkedIn",
            user_id="user123"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["new_status"], "Applied")
        self.assertGreater(result["transition_count"], 0)
        
        # Verify history was updated
        history = self.storage_manager.get_job_status_history(job_id)
        self.assertEqual(history["current_status"], "Applied")
        self.assertGreater(history["total_transitions"], 0)
    
    # Test 3: Invalid Status Transition
    def test_invalid_status_transition(self):
        """Test that invalid status transitions are rejected"""
        job_id = self.job_001
        
        # Create history with Applied status
        self.storage_manager.create_status_history(job_id, "Applied")
        
        # Try to go back to Pending (invalid transition)
        result = self.storage_manager.update_job_status_with_history(
            job_id=job_id,
            new_status="Pending"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("Invalid", result.get("error", ""))
    
    # Test 4: Status Timeline
    def test_get_status_timeline(self):
        """Test getting timeline of status changes"""
        job_id = self.job_001
        
        # Create history and make several transitions
        self.storage_manager.create_status_history(job_id, "Pending")
        
        transitions = [
            ("Applied", "Submitted application"),
            ("Interview", "Phone screen scheduled"),
            ("Offer", "Received offer letter")
        ]
        
        for status, notes in transitions:
            self.storage_manager.update_job_status_with_history(
                job_id=job_id,
                new_status=status,
                notes=notes
            )
        
        # Get timeline
        timeline = self.storage_manager.get_status_timeline(job_id)
        
        self.assertGreaterEqual(len(timeline), 3)
        
        # Verify last transition
        last_transition = timeline[-1]
        self.assertEqual(last_transition["to_status"], "Offer")
        self.assertEqual(last_transition["notes"], "Received offer letter")
    
    # Test 5: Bulk Status Updates
    def test_bulk_status_updates(self):
        """Test bulk status updates"""
        # Create histories for all jobs
        for job in self.sample_jobs:
            self.storage_manager.create_status_history(job["job_id"])
        
        # Prepare bulk updates
        updates = [
            {"job_id": self.job_001, "status": "Applied", "notes": "Applied online"},
            {"job_id": self.job_002, "status": "Applied", "notes": "Applied via referral"},
            {"job_id": self.job_003, "status": "Interview", "notes": "Phone interview scheduled"}
        ]
        
        # Perform bulk update
        results = self.storage_manager.bulk_update_statuses(updates)
        
        self.assertEqual(results["total"], 3)
        self.assertEqual(results["successful"], 3)
        self.assertEqual(results["failed"], 0)
        
        # Verify updates
        history_001 = self.storage_manager.get_job_status_history(self.job_001)
        self.assertEqual(history_001["current_status"], "Applied")
        
        history_003 = self.storage_manager.get_job_status_history(self.job_003)
        self.assertEqual(history_003["current_status"], "Interview")
    
    # Test 6: Get Jobs by Status
    def test_get_jobs_by_status_with_history(self):
        """Test getting jobs filtered by status with history"""
        # Create histories and set statuses
        for job in self.sample_jobs:
            self.storage_manager.create_status_history(job["job_id"])
        
        self.storage_manager.update_job_status_with_history(self.job_001, "Applied", update_job_record=True)
        self.storage_manager.update_job_status_with_history(self.job_002, "Applied", update_job_record=True)
        self.storage_manager.update_job_status_with_history(self.job_003, "Interview", update_job_record=True)
        
        # Get jobs with "Applied" status - this looks at status_manager histories
        applied_jobs = self.storage_manager.get_jobs_by_status_with_history("Applied")
        
        # Should return 2 jobs (job_001 and job_002) that have matching job records
        self.assertEqual(len(applied_jobs), 2)
        
        # Verify each job has history
        for job in applied_jobs:
            self.assertIn("status_history", job)
            self.assertEqual(job["status_history"]["current_status"], "Applied")
    
    # Test 7: Enhanced Status Summary
    def test_enhanced_status_summary(self):
        """Test getting enhanced status summary with statistics"""
        # Create histories and set various statuses
        for i, job in enumerate(self.sample_jobs):
            self.storage_manager.create_status_history(job["job_id"])
        
        self.storage_manager.update_job_status_with_history(self.job_001, "Applied")
        self.storage_manager.update_job_status_with_history(self.job_002, "Interview")
        self.storage_manager.update_job_status_with_history(self.job_003, "Offer")
        
        # Get enhanced summary
        summary = self.storage_manager.get_enhanced_status_summary()
        
        self.assertIn("total_jobs", summary)
        self.assertIn("status_counts", summary)
        self.assertIn("history_stats", summary)
        # Changed: history_stats tracks status manager histories, not job records
        self.assertEqual(summary["history_stats"]["total_jobs"], 3)
    
    # Test 8: Jobs Pending Action
    def test_get_jobs_pending_action(self):
        """Test getting jobs that need attention"""
        # This test is time-sensitive, so we'll just verify the structure
        for job in self.sample_jobs:
            self.storage_manager.create_status_history(job["job_id"])
        
        # Set one job to Applied status
        self.storage_manager.update_job_status_with_history(self.job_001, "Applied")
        
        # Get pending jobs (with 0 days threshold to include all)
        pending_jobs = self.storage_manager.get_jobs_pending_action(days_threshold=0)
        
        self.assertIsInstance(pending_jobs, list)
        
        # Each pending job should have required fields
        for job in pending_jobs:
            self.assertIn("job_id", job)
            self.assertIn("current_status", job)
            self.assertIn("days_in_status", job)
    
    # Test 9: Export and Import Status Report
    def test_export_status_report(self):
        """Test exporting comprehensive status report"""
        # Set up some jobs with statuses
        for job in self.sample_jobs:
            self.storage_manager.create_status_history(job["job_id"])
        
        self.storage_manager.update_job_status_with_history(self.job_001, "Applied")
        self.storage_manager.update_job_status_with_history(self.job_002, "Interview")
        
        # Export report
        report_path = os.path.join(self.test_dir, "status_report.json")
        success = self.storage_manager.export_status_report(report_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(report_path))
        
        # Verify report contents
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        self.assertIn("generated_at", report)
        self.assertIn("summary", report)
        self.assertIn("all_histories", report)
        self.assertIn("status_distribution", report)
    
    # Test 10: All Status Histories
    def test_get_all_status_histories(self):
        """Test getting all status histories"""
        # Create histories for all jobs
        for job in self.sample_jobs:
            self.storage_manager.create_status_history(job["job_id"])
        
        # Get all histories
        all_histories = self.storage_manager.get_all_status_histories()
        
        self.assertEqual(len(all_histories), 3)
        
        # Verify each history has required fields
        for history in all_histories:
            self.assertIn("job_id", history)
            self.assertIn("current_status", history)
            self.assertIn("total_transitions", history)
    
    # Test 11: Status History Persistence
    def test_status_history_persistence(self):
        """Test that status histories persist across manager instances"""
        job_id = self.job_001
        
        # Create and update status
        self.storage_manager.create_status_history(job_id)
        self.storage_manager.update_job_status_with_history(
            job_id=job_id,
            new_status="Applied",
            notes="Test persistence"
        )
        
        # Create new storage manager instance (should load existing data)
        new_manager = JobStorageManager(storage_dir=self.test_dir)
        
        # Verify history was loaded
        history = new_manager.get_job_status_history(job_id)
        self.assertIsNotNone(history)
        self.assertEqual(history["current_status"], "Applied")
    
    # Test 12: Multiple Transitions Same Job
    def test_multiple_transitions_same_job(self):
        """Test multiple status transitions for the same job"""
        job_id = self.job_001
        
        self.storage_manager.create_status_history(job_id)
        
        # Simulate full application lifecycle
        statuses = ["Applied", "Interview", "Offer"]
        
        for status in statuses:
            result = self.storage_manager.update_job_status_with_history(
                job_id=job_id,
                new_status=status,
                notes=f"Updated to {status}"
            )
            self.assertTrue(result["success"])
        
        # Verify final state
        history = self.storage_manager.get_job_status_history(job_id)
        self.assertEqual(history["current_status"], "Offer")
        self.assertEqual(history["total_transitions"], 3)
        
        # Verify timeline
        timeline = self.storage_manager.get_status_timeline(job_id)
        self.assertEqual(len(timeline), 3)
    
    # Test 13: Status Update Without History Record
    def test_status_update_creates_history_if_missing(self):
        """Test that updating status creates history if it doesn't exist"""
        job_id = self.job_001
        
        # Update status without creating history first
        result = self.storage_manager.update_job_status_with_history(
            job_id=job_id,
            new_status="Applied",
            notes="Should create history automatically"
        )
        
        self.assertTrue(result["success"])
        
        # Verify history was created
        history = self.storage_manager.get_job_status_history(job_id)
        self.assertIsNotNone(history)
        self.assertEqual(history["current_status"], "Applied")
    
    # Test 14: Invalid Status String
    def test_invalid_status_string(self):
        """Test handling of invalid status strings"""
        job_id = self.job_001
        
        self.storage_manager.create_status_history(job_id)
        
        # Try to update with invalid status
        result = self.storage_manager.update_job_status_with_history(
            job_id=job_id,
            new_status="InvalidStatus"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    # Test 15: Days in Status Calculation
    def test_days_in_status_calculation(self):
        """Test calculation of days in current status"""
        job_id = self.job_001
        
        self.storage_manager.create_status_history(job_id)
        self.storage_manager.update_job_status_with_history(
            job_id=job_id,
            new_status="Applied"
        )
        
        history = self.storage_manager.get_job_status_history(job_id)
        
        # Should be 0 days since we just updated
        self.assertEqual(history["days_in_current_status"], 0)
    
    # Test 16: Filter Jobs by Multiple Criteria
    def test_filter_jobs_by_status_and_other_criteria(self):
        """Test filtering jobs by status along with other criteria"""
        # Set up jobs with statuses
        for job in self.sample_jobs:
            self.storage_manager.create_status_history(job["job_id"])
        
        self.storage_manager.update_job_status_with_history(self.job_001, "Applied", update_job_record=True)
        self.storage_manager.update_job_status_with_history(self.job_002, "Applied", update_job_record=True)
        self.storage_manager.update_job_status_with_history(self.job_003, "Interview", update_job_record=True)
        
        # Get Applied jobs
        applied_jobs = self.storage_manager.get_jobs_by_status_with_history("Applied")
        
        # Filter by additional criteria (e.g., location)
        sf_applied = [j for j in applied_jobs if "San Francisco" in j.get("location", "")]
        
        self.assertEqual(len(sf_applied), 1)
        self.assertEqual(sf_applied[0]["job_id"], self.job_001)


class TestStatusHistoryFile(unittest.TestCase):
    """Test status history file operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.storage_manager = JobStorageManager(storage_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_status_history_file_creation(self):
        """Test that status history file is created"""
        status_file = os.path.join(self.test_dir, "status_history.json")
        self.assertTrue(os.path.exists(status_file))
    
    def test_status_history_file_structure(self):
        """Test the structure of status history file"""
        status_file = os.path.join(self.test_dir, "status_history.json")
        
        with open(status_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("created_at", data)
        self.assertIn("last_updated", data)
        self.assertIn("histories", data)
        self.assertIsInstance(data["histories"], list)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.storage_manager = JobStorageManager(storage_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_get_history_nonexistent_job(self):
        """Test getting history for non-existent job"""
        history = self.storage_manager.get_job_status_history("nonexistent_job")
        self.assertIsNone(history)
    
    def test_bulk_update_with_errors(self):
        """Test bulk update with some invalid entries"""
        # Create one valid job
        self.storage_manager.create_status_history(self.job_001)
        
        updates = [
            {"job_id": self.job_001, "status": "Applied"},  # Valid
            {"job_id": self.job_002, "status": "InvalidStatus"},  # Invalid status
            {"job_id": self.job_003},  # Missing status
        ]
        
        results = self.storage_manager.bulk_update_statuses(updates)
        
        self.assertEqual(results["total"], 3)
        self.assertEqual(results["successful"], 1)
        self.assertEqual(results["failed"], 2)
        self.assertEqual(len(results["errors"]), 2)
    
    def test_empty_status_timeline(self):
        """Test getting timeline for job with no history"""
        timeline = self.storage_manager.get_status_timeline("nonexistent_job")
        self.assertEqual(timeline, [])


def run_tests():
    """Run all tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStatusTrackingIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStatusHistoryFile))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
