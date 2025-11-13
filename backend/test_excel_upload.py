"""
Test Suite for Excel Upload Module (Task 7.3)

Tests for:
- Excel file parsing
- Status validation
- Data integrity checks
- Error handling
- Integration with storage manager

Run with: python test_excel_upload.py
"""

import unittest
import os
import sys
from datetime import datetime
import openpyxl
from openpyxl.styles import PatternFill
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from excel_uploader import ExcelUploader, ExcelUploadError
from storage_manager import JobStorageManager


class TestExcelUploader(unittest.TestCase):
    """Test cases for ExcelUploader class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.uploader = ExcelUploader()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_jobs.xlsx')
        
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_excel(self, filename, data, headers=None):
        """Helper to create test Excel files"""
        if headers is None:
            headers = ['job_id', 'title', 'company', 'status', 'applied_date', 'notes']
        
        wb = openpyxl.Workbook()
        ws = wb.active
        
        # Write headers
        ws.append(headers)
        
        # Write data
        for row in data:
            ws.append(row)
        
        wb.save(filename)
        wb.close()
        
    def test_parse_valid_excel(self):
        """Test parsing a valid Excel file"""
        data = [
            ['job1', 'Software Engineer', 'Tech Corp', 'Applied', '2025-11-10', 'Applied via website'],
            ['job2', 'Data Analyst', 'Data Inc', 'Interview', '2025-11-11', 'Phone screening scheduled'],
            ['job3', 'Product Manager', 'Product Co', 'Offer', '2025-11-12', 'Received offer letter']
        ]
        
        self.create_test_excel(self.test_file, data)
        
        result = self.uploader.parse_excel_file(self.test_file)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_rows'], 3)
        self.assertEqual(result['valid_rows'], 3)
        self.assertEqual(len(result['data']), 3)
        self.assertEqual(len(result['errors']), 0)
        
    def test_parse_invalid_status(self):
        """Test parsing with invalid status values"""
        data = [
            ['job1', 'Software Engineer', 'Tech Corp', 'InvalidStatus', '2025-11-10', 'Test'],
            ['job2', 'Data Analyst', 'Data Inc', 'Applied', '2025-11-11', 'Test']
        ]
        
        self.create_test_excel(self.test_file, data)
        
        result = self.uploader.parse_excel_file(self.test_file)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['warnings']), 1)
        # First job should have None status due to validation
        self.assertIsNone(result['data'][0]['status'])
        # Second job should have valid status
        self.assertEqual(result['data'][1]['status'], 'Applied')
        
    def test_parse_missing_required_fields(self):
        """Test parsing with missing required fields"""
        data = [
            ['job1', 'Software Engineer', '', 'Applied', '2025-11-10', 'Missing company'],
            ['', 'Data Analyst', 'Data Inc', 'Applied', '2025-11-11', 'Missing job_id']
        ]
        
        self.create_test_excel(self.test_file, data)
        
        result = self.uploader.parse_excel_file(self.test_file)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['valid_rows'], 0)
        self.assertEqual(len(result['errors']), 2)
        
    def test_parse_case_insensitive_status(self):
        """Test that status values are case-insensitive"""
        data = [
            ['job1', 'Engineer', 'Corp', 'applied', '2025-11-10', ''],
            ['job2', 'Analyst', 'Inc', 'INTERVIEW', '2025-11-11', ''],
            ['job3', 'Manager', 'Co', 'Offer', '2025-11-12', '']
        ]
        
        self.create_test_excel(self.test_file, data)
        
        result = self.uploader.parse_excel_file(self.test_file)
        
        self.assertTrue(result['success'])
        # All statuses should be normalized
        self.assertEqual(result['data'][0]['status'], 'Applied')
        self.assertEqual(result['data'][1]['status'], 'Interview')
        self.assertEqual(result['data'][2]['status'], 'Offer')
        
    def test_parse_various_date_formats(self):
        """Test parsing different date formats"""
        data = [
            ['job1', 'Engineer', 'Corp', 'Applied', '2025-11-10', ''],
            ['job2', 'Analyst', 'Inc', 'Applied', '11/11/2025', ''],
            ['job3', 'Manager', 'Co', 'Applied', '12-11-2025', '']
        ]
        
        self.create_test_excel(self.test_file, data)
        
        result = self.uploader.parse_excel_file(self.test_file)
        
        self.assertTrue(result['success'])
        # First date should parse correctly
        self.assertEqual(result['data'][0]['applied_date'], '2025-11-10')
        # Other dates might parse or generate warnings
        
    def test_parse_empty_rows(self):
        """Test that empty rows are skipped"""
        data = [
            ['job1', 'Engineer', 'Corp', 'Applied', '2025-11-10', ''],
            ['', '', '', '', '', ''],  # Empty row
            ['job2', 'Analyst', 'Inc', 'Applied', '2025-11-11', '']
        ]
        
        self.create_test_excel(self.test_file, data)
        
        result = self.uploader.parse_excel_file(self.test_file)
        
        # Should only have 2 rows (empty row skipped)
        self.assertEqual(len(result['data']), 2)
        
    def test_parse_alternative_column_names(self):
        """Test parsing with alternative column names"""
        headers = ['id', 'job_title', 'company_name', 'app_status', 'date_applied', 'comments']
        data = [
            ['job1', 'Software Engineer', 'Tech Corp', 'Applied', '2025-11-10', 'Test']
        ]
        
        self.create_test_excel(self.test_file, data, headers=headers)
        
        result = self.uploader.parse_excel_file(self.test_file)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_rows'], 1)
        self.assertEqual(result['data'][0]['job_id'], 'job1')
        self.assertEqual(result['data'][0]['title'], 'Software Engineer')
        
    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        with self.assertRaises(ExcelUploadError):
            self.uploader.parse_excel_file('/nonexistent/file.xlsx')
            
    def test_parse_invalid_sheet_name(self):
        """Test parsing with invalid sheet name"""
        data = [['job1', 'Engineer', 'Corp', 'Applied', '2025-11-10', '']]
        self.create_test_excel(self.test_file, data)
        
        with self.assertRaises(ExcelUploadError):
            self.uploader.parse_excel_file(self.test_file, sheet_name='NonexistentSheet')
            
    def test_summary_generation(self):
        """Test that summary statistics are correct"""
        data = [
            ['job1', 'Engineer', 'Corp', 'Applied', '2025-11-10', 'Note 1'],
            ['job2', 'Analyst', 'Inc', 'Applied', '2025-11-11', ''],
            ['job3', 'Manager', 'Co', 'Interview', '2025-11-12', 'Note 2'],
            ['job4', 'Developer', 'Dev Inc', 'Offer', '', 'Note 3']
        ]
        
        self.create_test_excel(self.test_file, data)
        
        result = self.uploader.parse_excel_file(self.test_file)
        
        summary = result['summary']
        self.assertEqual(summary['total_jobs'], 4)
        self.assertEqual(summary['status_counts']['Applied'], 2)
        self.assertEqual(summary['status_counts']['Interview'], 1)
        self.assertEqual(summary['status_counts']['Offer'], 1)
        self.assertEqual(summary['jobs_with_dates'], 3)
        self.assertEqual(summary['jobs_with_notes'], 3)


class TestValidationAgainstStorage(unittest.TestCase):
    """Test validation against stored jobs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.uploader = ExcelUploader()
        self.test_dir = tempfile.mkdtemp()
        self.storage_dir = os.path.join(self.test_dir, 'storage')
        self.storage_manager = JobStorageManager(storage_dir=self.storage_dir)
        
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_validate_matched_jobs(self):
        """Test validation with matching jobs"""
        # Add jobs to storage
        self.storage_manager.add_job({
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'San Francisco'
        })
        
        # Parse data with matching job
        parsed_data = [{
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'status': 'Applied',
            'valid': True
        }]
        
        stored_jobs = self.storage_manager.get_all_jobs()
        result = self.uploader.validate_against_stored_jobs(parsed_data, stored_jobs)
        
        self.assertEqual(len(result['matched_jobs']), 1)
        self.assertEqual(len(result['new_jobs']), 0)
        self.assertEqual(len(result['mismatched_jobs']), 0)
        
    def test_validate_new_jobs(self):
        """Test validation with new jobs not in storage"""
        # Add one job to storage
        self.storage_manager.add_job({
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp'
        })
        
        # Parse data with new job
        parsed_data = [{
            'job_id': 'job2',
            'title': 'Data Analyst',
            'company': 'Data Inc',
            'status': 'Applied',
            'valid': True
        }]
        
        stored_jobs = self.storage_manager.get_all_jobs()
        result = self.uploader.validate_against_stored_jobs(parsed_data, stored_jobs)
        
        self.assertEqual(len(result['matched_jobs']), 0)
        self.assertEqual(len(result['new_jobs']), 1)
        
    def test_validate_mismatched_jobs(self):
        """Test validation with mismatched job details"""
        # Add job to storage
        self.storage_manager.add_job({
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp'
        })
        
        # Parse data with different title
        parsed_data = [{
            'job_id': 'job1',
            'title': 'Senior Software Engineer',  # Different title
            'company': 'Tech Corp',
            'status': 'Applied',
            'valid': True
        }]
        
        stored_jobs = self.storage_manager.get_all_jobs()
        result = self.uploader.validate_against_stored_jobs(parsed_data, stored_jobs)
        
        self.assertEqual(len(result['mismatched_jobs']), 1)
        self.assertEqual(len(result['mismatched_jobs'][0]['discrepancies']), 1)
        self.assertEqual(result['mismatched_jobs'][0]['discrepancies'][0]['field'], 'title')


class TestStatusUpdates(unittest.TestCase):
    """Test status update extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.uploader = ExcelUploader()
        self.test_dir = tempfile.mkdtemp()
        self.storage_dir = os.path.join(self.test_dir, 'storage')
        self.storage_manager = JobStorageManager(storage_dir=self.storage_dir)
        
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_get_status_updates(self):
        """Test extracting status updates"""
        # Add jobs to storage
        self.storage_manager.add_job({
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'application_status': 'Pending'
        })
        
        self.storage_manager.add_job({
            'job_id': 'job2',
            'title': 'Data Analyst',
            'company': 'Data Inc',
            'application_status': 'Applied'
        })
        
        # Parse data with status changes
        parsed_data = [
            {
                'job_id': 'job1',
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'status': 'Applied',  # Changed from Pending
                'applied_date': '2025-11-10',
                'notes': 'Applied via website',
                'valid': True
            },
            {
                'job_id': 'job2',
                'title': 'Data Analyst',
                'company': 'Data Inc',
                'status': 'Applied',  # No change
                'valid': True
            }
        ]
        
        stored_jobs = self.storage_manager.get_all_jobs()
        updates = self.uploader.get_status_updates(parsed_data, stored_jobs)
        
        # Only job1 should have an update (status changed)
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0]['job_id'], 'job1')
        self.assertEqual(updates[0]['old_status'], 'Pending')
        self.assertEqual(updates[0]['new_status'], 'Applied')
        
    def test_get_status_updates_no_changes(self):
        """Test when there are no status changes"""
        self.storage_manager.add_job({
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'application_status': 'Applied'
        })
        
        parsed_data = [{
            'job_id': 'job1',
            'status': 'Applied',  # Same status
            'valid': True
        }]
        
        stored_jobs = self.storage_manager.get_all_jobs()
        updates = self.uploader.get_status_updates(parsed_data, stored_jobs)
        
        self.assertEqual(len(updates), 0)


class TestStorageManagerStatusFeatures(unittest.TestCase):
    """Test storage manager status tracking features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.storage_dir = os.path.join(self.test_dir, 'storage')
        self.storage_manager = JobStorageManager(storage_dir=self.storage_dir)
        
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_update_job_status(self):
        """Test updating status for a single job"""
        # Add a job
        self.storage_manager.add_job({
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp'
        })
        
        # Update status
        result = self.storage_manager.update_job_status(
            job_id='job1',
            status='Applied',
            applied_date='2025-11-10',
            notes='Applied via website'
        )
        
        self.assertTrue(result['success'])
        
        # Verify update
        jobs = self.storage_manager.get_all_jobs()
        self.assertEqual(jobs[0]['application_status'], 'Applied')
        self.assertEqual(jobs[0]['applied_date'], '2025-11-10')
        self.assertIn('status_history', jobs[0])
        self.assertEqual(len(jobs[0]['status_history']), 1)
        
    def test_update_nonexistent_job_status(self):
        """Test updating status for a job that doesn't exist"""
        result = self.storage_manager.update_job_status(
            job_id='nonexistent',
            status='Applied'
        )
        
        self.assertFalse(result['success'])
        
    def test_batch_update_statuses(self):
        """Test batch status updates"""
        # Add jobs
        self.storage_manager.add_job({
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp'
        })
        
        self.storage_manager.add_job({
            'job_id': 'job2',
            'title': 'Data Analyst',
            'company': 'Data Inc'
        })
        
        # Batch update
        updates = [
            {
                'job_id': 'job1',
                'new_status': 'Applied',
                'applied_date': '2025-11-10'
            },
            {
                'job_id': 'job2',
                'new_status': 'Interview',
                'applied_date': '2025-11-11'
            }
        ]
        
        result = self.storage_manager.batch_update_job_statuses(updates)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['updated'], 2)
        self.assertEqual(result['not_found'], 0)
        
    def test_get_jobs_by_status(self):
        """Test filtering jobs by status"""
        # Add jobs with different statuses
        self.storage_manager.add_job({
            'job_id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp'
        })
        
        self.storage_manager.update_job_status('job1', 'Applied')
        
        self.storage_manager.add_job({
            'job_id': 'job2',
            'title': 'Data Analyst',
            'company': 'Data Inc'
        })
        
        self.storage_manager.update_job_status('job2', 'Interview')
        
        # Get jobs by status
        applied_jobs = self.storage_manager.get_jobs_by_status('Applied')
        interview_jobs = self.storage_manager.get_jobs_by_status('Interview')
        
        self.assertEqual(len(applied_jobs), 1)
        self.assertEqual(len(interview_jobs), 1)
        
    def test_get_status_summary(self):
        """Test status summary generation"""
        # Add jobs with various statuses
        jobs_data = [
            ('job1', 'Applied'),
            ('job2', 'Applied'),
            ('job3', 'Interview'),
            ('job4', 'Offer'),
            ('job5', None)  # No status
        ]
        
        for job_id, status in jobs_data:
            self.storage_manager.add_job({
                'job_id': job_id,
                'title': f'Position {job_id}',
                'company': 'Company'
            })
            
            if status:
                self.storage_manager.update_job_status(
                    job_id=job_id,
                    status=status,
                    applied_date='2025-11-10'
                )
        
        summary = self.storage_manager.get_status_summary()
        
        self.assertEqual(summary['total_jobs'], 5)
        self.assertEqual(summary['jobs_with_status'], 4)
        self.assertEqual(summary['jobs_without_status'], 1)
        self.assertEqual(summary['status_counts']['Applied'], 2)
        self.assertEqual(summary['status_counts']['Interview'], 1)
        self.assertEqual(summary['status_counts']['Offer'], 1)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("Excel Upload Module - Test Suite")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExcelUploader))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationAgainstStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestStatusUpdates))
    suite.addTests(loader.loadTestsFromTestCase(TestStorageManagerStatusFeatures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
