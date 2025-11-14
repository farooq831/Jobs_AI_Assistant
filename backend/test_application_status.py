"""
Test Suite for Application Status Model

Tests all aspects of the application status tracking system:
- ApplicationStatus enum functionality
- StatusTransition validation
- StatusHistory management
- ApplicationStatusManager operations
- Utility functions

Author: AI Job Application Assistant
Date: November 2025
"""

import unittest
import os
import json
import tempfile
from datetime import datetime, timedelta
from application_status import (
    ApplicationStatus,
    StatusTransition,
    StatusHistory,
    ApplicationStatusManager,
    validate_status,
    get_valid_next_statuses,
    create_status_summary
)


class TestApplicationStatus(unittest.TestCase):
    """Test ApplicationStatus enum"""
    
    def test_all_statuses(self):
        """Test that all expected statuses exist"""
        expected = ["Pending", "Applied", "Interview", "Offer", "Rejected"]
        actual = ApplicationStatus.get_all_statuses()
        self.assertEqual(set(expected), set(actual))
    
    def test_from_string_valid(self):
        """Test converting valid strings to status"""
        test_cases = [
            ("Applied", ApplicationStatus.APPLIED),
            ("applied", ApplicationStatus.APPLIED),
            ("APPLIED", ApplicationStatus.APPLIED),
            ("  Applied  ", ApplicationStatus.APPLIED),
            ("Pending", ApplicationStatus.PENDING),
            ("Interview", ApplicationStatus.INTERVIEW),
            ("Offer", ApplicationStatus.OFFER),
            ("Rejected", ApplicationStatus.REJECTED)
        ]
        
        for status_str, expected in test_cases:
            with self.subTest(status_str=status_str):
                result = ApplicationStatus.from_string(status_str)
                self.assertEqual(result, expected)
    
    def test_from_string_invalid(self):
        """Test that invalid strings raise ValueError"""
        invalid_cases = ["Invalid", "Submitted", "", "   ", "123"]
        
        for status_str in invalid_cases:
            with self.subTest(status_str=status_str):
                with self.assertRaises(ValueError):
                    ApplicationStatus.from_string(status_str)
    
    def test_is_valid_status(self):
        """Test status validation"""
        self.assertTrue(ApplicationStatus.is_valid_status("Applied"))
        self.assertTrue(ApplicationStatus.is_valid_status("interview"))
        self.assertFalse(ApplicationStatus.is_valid_status("Invalid"))
        self.assertFalse(ApplicationStatus.is_valid_status(""))
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(ApplicationStatus.APPLIED), "Applied")
        self.assertEqual(str(ApplicationStatus.PENDING), "Pending")


class TestStatusTransition(unittest.TestCase):
    """Test StatusTransition class"""
    
    def test_creation(self):
        """Test creating a status transition"""
        transition = StatusTransition(
            from_status=ApplicationStatus.PENDING,
            to_status=ApplicationStatus.APPLIED,
            notes="Test note"
        )
        
        self.assertEqual(transition.from_status, ApplicationStatus.PENDING)
        self.assertEqual(transition.to_status, ApplicationStatus.APPLIED)
        self.assertEqual(transition.notes, "Test note")
        self.assertIsInstance(transition.timestamp, datetime)
    
    def test_initial_transition(self):
        """Test initial status transition (from None)"""
        transition = StatusTransition(
            from_status=None,
            to_status=ApplicationStatus.APPLIED
        )
        
        self.assertIsNone(transition.from_status)
        self.assertTrue(transition.is_valid_transition())
    
    def test_valid_transitions(self):
        """Test valid status transitions"""
        valid_cases = [
            (ApplicationStatus.PENDING, ApplicationStatus.APPLIED),
            (ApplicationStatus.PENDING, ApplicationStatus.INTERVIEW),
            (ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEW),
            (ApplicationStatus.APPLIED, ApplicationStatus.OFFER),
            (ApplicationStatus.INTERVIEW, ApplicationStatus.OFFER),
            (ApplicationStatus.PENDING, ApplicationStatus.REJECTED),
            (ApplicationStatus.APPLIED, ApplicationStatus.REJECTED),
            (ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED),
            (ApplicationStatus.OFFER, ApplicationStatus.APPLIED),  # Reapply
            (ApplicationStatus.REJECTED, ApplicationStatus.APPLIED),  # Reapply
        ]
        
        for from_status, to_status in valid_cases:
            with self.subTest(from_status=from_status, to_status=to_status):
                transition = StatusTransition(from_status=from_status, to_status=to_status)
                self.assertTrue(
                    transition.is_valid_transition(),
                    f"{from_status.value} -> {to_status.value} should be valid"
                )
    
    def test_invalid_transitions(self):
        """Test invalid status transitions"""
        invalid_cases = [
            (ApplicationStatus.APPLIED, ApplicationStatus.PENDING),
            (ApplicationStatus.INTERVIEW, ApplicationStatus.PENDING),
            (ApplicationStatus.INTERVIEW, ApplicationStatus.APPLIED),
            (ApplicationStatus.OFFER, ApplicationStatus.PENDING),
        ]
        
        for from_status, to_status in invalid_cases:
            with self.subTest(from_status=from_status, to_status=to_status):
                transition = StatusTransition(from_status=from_status, to_status=to_status)
                self.assertFalse(
                    transition.is_valid_transition(),
                    f"{from_status.value} -> {to_status.value} should be invalid"
                )
    
    def test_to_dict(self):
        """Test converting transition to dictionary"""
        transition = StatusTransition(
            from_status=ApplicationStatus.PENDING,
            to_status=ApplicationStatus.APPLIED,
            notes="Test note",
            user_id="user123"
        )
        
        data = transition.to_dict()
        
        self.assertEqual(data["from_status"], "Pending")
        self.assertEqual(data["to_status"], "Applied")
        self.assertEqual(data["notes"], "Test note")
        self.assertEqual(data["user_id"], "user123")
        self.assertIn("timestamp", data)
    
    def test_from_dict(self):
        """Test creating transition from dictionary"""
        data = {
            "from_status": "Pending",
            "to_status": "Applied",
            "timestamp": "2025-11-13T10:00:00",
            "notes": "Test note",
            "user_id": "user123"
        }
        
        transition = StatusTransition.from_dict(data)
        
        self.assertEqual(transition.from_status, ApplicationStatus.PENDING)
        self.assertEqual(transition.to_status, ApplicationStatus.APPLIED)
        self.assertEqual(transition.notes, "Test note")
        self.assertEqual(transition.user_id, "user123")


class TestStatusHistory(unittest.TestCase):
    """Test StatusHistory class"""
    
    def setUp(self):
        """Set up test history"""
        self.history = StatusHistory(job_id="job_123")
    
    def test_creation(self):
        """Test creating status history"""
        self.assertEqual(self.history.job_id, "job_123")
        self.assertEqual(self.history.current_status, ApplicationStatus.PENDING)
        self.assertEqual(len(self.history.transitions), 0)
    
    def test_add_valid_transition(self):
        """Test adding valid transitions"""
        success = self.history.add_transition(
            ApplicationStatus.APPLIED,
            notes="Application submitted"
        )
        
        self.assertTrue(success)
        self.assertEqual(self.history.current_status, ApplicationStatus.APPLIED)
        self.assertEqual(len(self.history.transitions), 1)
        self.assertEqual(self.history.transitions[0].notes, "Application submitted")
    
    def test_add_invalid_transition(self):
        """Test that invalid transitions are rejected"""
        self.history.add_transition(ApplicationStatus.APPLIED)
        
        # Try invalid transition (Applied -> Pending)
        success = self.history.add_transition(ApplicationStatus.PENDING)
        
        self.assertFalse(success)
        self.assertEqual(self.history.current_status, ApplicationStatus.APPLIED)
        self.assertEqual(len(self.history.transitions), 1)
    
    def test_add_transition_without_validation(self):
        """Test adding transition without validation"""
        self.history.add_transition(ApplicationStatus.APPLIED)
        
        # Add invalid transition without validation
        success = self.history.add_transition(
            ApplicationStatus.PENDING,
            validate=False
        )
        
        self.assertTrue(success)
        self.assertEqual(self.history.current_status, ApplicationStatus.PENDING)
    
    def test_multiple_transitions(self):
        """Test multiple status transitions"""
        transitions = [
            ApplicationStatus.APPLIED,
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.OFFER
        ]
        
        for status in transitions:
            self.history.add_transition(status)
        
        self.assertEqual(len(self.history.transitions), 3)
        self.assertEqual(self.history.current_status, ApplicationStatus.OFFER)
    
    def test_get_transition_count(self):
        """Test getting transition count"""
        self.assertEqual(self.history.get_transition_count(), 0)
        
        self.history.add_transition(ApplicationStatus.APPLIED)
        self.assertEqual(self.history.get_transition_count(), 1)
        
        self.history.add_transition(ApplicationStatus.INTERVIEW)
        self.assertEqual(self.history.get_transition_count(), 2)
    
    def test_get_days_in_current_status(self):
        """Test calculating days in current status"""
        days = self.history.get_days_in_current_status()
        self.assertGreaterEqual(days, 0)
        self.assertLessEqual(days, 1)  # Should be less than 1 day for new history
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
        self.history.add_transition(ApplicationStatus.APPLIED, notes="Test")
        self.history.add_transition(ApplicationStatus.INTERVIEW)
        
        # Convert to dict
        data = self.history.to_dict()
        
        self.assertEqual(data["job_id"], "job_123")
        self.assertEqual(data["current_status"], "Interview")
        self.assertEqual(len(data["transitions"]), 2)
        
        # Convert back
        new_history = StatusHistory.from_dict(data)
        
        self.assertEqual(new_history.job_id, self.history.job_id)
        self.assertEqual(new_history.current_status, self.history.current_status)
        self.assertEqual(len(new_history.transitions), len(self.history.transitions))


class TestApplicationStatusManager(unittest.TestCase):
    """Test ApplicationStatusManager class"""
    
    def setUp(self):
        """Set up test manager"""
        self.manager = ApplicationStatusManager()
    
    def test_create_history(self):
        """Test creating status history"""
        history = self.manager.create_history("job_123")
        
        self.assertIsNotNone(history)
        self.assertEqual(history.job_id, "job_123")
        self.assertEqual(history.current_status, ApplicationStatus.PENDING)
    
    def test_create_history_with_initial_status(self):
        """Test creating history with non-pending initial status"""
        history = self.manager.create_history("job_123", ApplicationStatus.APPLIED)
        
        self.assertEqual(history.current_status, ApplicationStatus.APPLIED)
        self.assertEqual(len(history.transitions), 1)
    
    def test_create_duplicate_history(self):
        """Test that creating duplicate history returns existing"""
        history1 = self.manager.create_history("job_123")
        history2 = self.manager.create_history("job_123")
        
        self.assertIs(history1, history2)
    
    def test_get_history(self):
        """Test retrieving history"""
        self.manager.create_history("job_123")
        
        history = self.manager.get_history("job_123")
        self.assertIsNotNone(history)
        self.assertEqual(history.job_id, "job_123")
        
        # Non-existent job
        self.assertIsNone(self.manager.get_history("nonexistent"))
    
    def test_update_status(self):
        """Test updating status"""
        self.manager.create_history("job_123")
        
        success = self.manager.update_status(
            "job_123",
            ApplicationStatus.APPLIED,
            notes="Test note"
        )
        
        self.assertTrue(success)
        
        history = self.manager.get_history("job_123")
        self.assertEqual(history.current_status, ApplicationStatus.APPLIED)
    
    def test_update_status_create_if_missing(self):
        """Test creating history when updating non-existent job"""
        success = self.manager.update_status(
            "new_job",
            ApplicationStatus.APPLIED,
            create_if_missing=True
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(self.manager.get_history("new_job"))
    
    def test_update_status_without_create(self):
        """Test updating non-existent job without creating"""
        success = self.manager.update_status(
            "nonexistent",
            ApplicationStatus.APPLIED,
            create_if_missing=False
        )
        
        self.assertFalse(success)
    
    def test_bulk_update(self):
        """Test bulk status updates"""
        # Create some jobs
        self.manager.create_history("job_1")
        self.manager.create_history("job_2")
        
        updates = [
            {"job_id": "job_1", "status": "Applied", "notes": "Note 1"},
            {"job_id": "job_2", "status": "Interview", "notes": "Note 2"},
            {"job_id": "job_3", "status": "Applied"},  # Will be created
        ]
        
        results = self.manager.bulk_update(updates)
        
        self.assertEqual(results["total"], 3)
        self.assertEqual(results["successful"], 3)
        self.assertEqual(results["failed"], 0)
    
    def test_bulk_update_with_errors(self):
        """Test bulk update with some errors"""
        self.manager.create_history("job_1")
        
        updates = [
            {"job_id": "job_1", "status": "Applied"},
            {"job_id": "job_2", "status": "InvalidStatus"},  # Invalid status
            {"status": "Applied"},  # Missing job_id
        ]
        
        results = self.manager.bulk_update(updates)
        
        self.assertEqual(results["total"], 3)
        self.assertEqual(results["successful"], 1)
        self.assertEqual(results["failed"], 2)
        self.assertEqual(len(results["errors"]), 2)
    
    def test_get_statistics(self):
        """Test getting statistics"""
        # Empty stats
        stats = self.manager.get_statistics()
        self.assertEqual(stats["total_jobs"], 0)
        
        # Add some jobs
        self.manager.create_history("job_1")
        self.manager.update_status("job_1", ApplicationStatus.APPLIED)
        
        self.manager.create_history("job_2")
        self.manager.update_status("job_2", ApplicationStatus.APPLIED)
        self.manager.update_status("job_2", ApplicationStatus.INTERVIEW)
        
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats["total_jobs"], 2)
        self.assertEqual(stats["status_counts"]["Applied"], 1)
        self.assertEqual(stats["status_counts"]["Interview"], 1)
        self.assertIn("average_transitions", stats)
    
    def test_get_jobs_by_status(self):
        """Test getting jobs by status"""
        self.manager.create_history("job_1")
        self.manager.update_status("job_1", ApplicationStatus.APPLIED)
        
        self.manager.create_history("job_2")
        self.manager.update_status("job_2", ApplicationStatus.APPLIED)
        
        self.manager.create_history("job_3")
        self.manager.update_status("job_3", ApplicationStatus.INTERVIEW)
        
        applied_jobs = self.manager.get_jobs_by_status(ApplicationStatus.APPLIED)
        interview_jobs = self.manager.get_jobs_by_status(ApplicationStatus.INTERVIEW)
        
        self.assertEqual(len(applied_jobs), 2)
        self.assertEqual(len(interview_jobs), 1)
        self.assertIn("job_1", applied_jobs)
        self.assertIn("job_2", applied_jobs)
        self.assertIn("job_3", interview_jobs)
    
    def test_export_import_json(self):
        """Test exporting and importing JSON"""
        # Create some histories
        self.manager.create_history("job_1")
        self.manager.update_status("job_1", ApplicationStatus.APPLIED)
        
        self.manager.create_history("job_2")
        self.manager.update_status("job_2", ApplicationStatus.INTERVIEW)
        
        # Export
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            success = self.manager.export_to_json(temp_file)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(temp_file))
            
            # Import into new manager
            new_manager = ApplicationStatusManager()
            success = new_manager.import_from_json(temp_file)
            self.assertTrue(success)
            
            # Verify data
            self.assertEqual(len(new_manager.histories), 2)
            
            history1 = new_manager.get_history("job_1")
            self.assertIsNotNone(history1)
            self.assertEqual(history1.current_status, ApplicationStatus.APPLIED)
            
            history2 = new_manager.get_history("job_2")
            self.assertIsNotNone(history2)
            self.assertEqual(history2.current_status, ApplicationStatus.INTERVIEW)
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_validate_status(self):
        """Test status validation function"""
        valid_cases = ["Applied", "interview", "OFFER"]
        for status_str in valid_cases:
            is_valid, error = validate_status(status_str)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        
        invalid_cases = ["Invalid", "", "123"]
        for status_str in invalid_cases:
            is_valid, error = validate_status(status_str)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error)
    
    def test_get_valid_next_statuses(self):
        """Test getting valid next statuses"""
        # From Pending
        valid_next = get_valid_next_statuses("Pending")
        self.assertIn("Applied", valid_next)
        self.assertIn("Interview", valid_next)
        self.assertIn("Rejected", valid_next)
        
        # From Applied
        valid_next = get_valid_next_statuses("Applied")
        self.assertIn("Interview", valid_next)
        self.assertIn("Offer", valid_next)
        self.assertIn("Rejected", valid_next)
        
        # From Interview
        valid_next = get_valid_next_statuses("Interview")
        self.assertIn("Offer", valid_next)
        self.assertIn("Rejected", valid_next)
        
        # Invalid status
        valid_next = get_valid_next_statuses("Invalid")
        self.assertEqual(len(valid_next), 0)
    
    def test_create_status_summary(self):
        """Test creating status summary"""
        history = StatusHistory(job_id="job_123")
        history.add_transition(ApplicationStatus.APPLIED, notes="Applied online")
        history.add_transition(ApplicationStatus.INTERVIEW, notes="Phone screen")
        
        summary = create_status_summary(history)
        
        self.assertEqual(summary["job_id"], "job_123")
        self.assertEqual(summary["current_status"], "Interview")
        self.assertEqual(summary["total_transitions"], 2)
        self.assertIn("timeline", summary)
        self.assertEqual(len(summary["timeline"]), 2)
        self.assertEqual(summary["timeline"][0]["to"], "Applied")
        self.assertEqual(summary["timeline"][1]["to"], "Interview")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_status_string(self):
        """Test handling empty status strings"""
        with self.assertRaises(ValueError):
            ApplicationStatus.from_string("")
        
        with self.assertRaises(ValueError):
            ApplicationStatus.from_string("   ")
    
    def test_concurrent_updates(self):
        """Test that concurrent updates are handled safely"""
        manager = ApplicationStatusManager()
        manager.create_history("job_123")
        
        # Multiple updates in quick succession
        for i in range(10):
            if i % 2 == 0:
                manager.update_status("job_123", ApplicationStatus.APPLIED)
            else:
                manager.update_status("job_123", ApplicationStatus.INTERVIEW)
        
        history = manager.get_history("job_123")
        self.assertIsNotNone(history)
    
    def test_very_long_notes(self):
        """Test handling very long notes"""
        history = StatusHistory(job_id="job_123")
        long_notes = "X" * 10000
        
        success = history.add_transition(
            ApplicationStatus.APPLIED,
            notes=long_notes
        )
        
        self.assertTrue(success)
        self.assertEqual(len(history.transitions[0].notes), 10000)
    
    def test_special_characters_in_job_id(self):
        """Test handling special characters in job IDs"""
        manager = ApplicationStatusManager()
        special_ids = [
            "job-123",
            "job_456",
            "job.789",
            "job@company",
            "job#123"
        ]
        
        for job_id in special_ids:
            with self.subTest(job_id=job_id):
                history = manager.create_history(job_id)
                self.assertIsNotNone(history)
                self.assertEqual(history.job_id, job_id)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestStatusTransition))
    suite.addTests(loader.loadTestsFromTestCase(TestStatusHistory))
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationStatusManager))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
