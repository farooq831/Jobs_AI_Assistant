"""
Test Suite for Storage Manager and Retry Logic
Tests job storage, data validation, deduplication, and retry mechanisms
"""

import os
import sys
import json
import time
import shutil
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage_manager import JobStorageManager
from scrapers.retry_scraper import RetryScraper, RetryConfig, retry_with_backoff


# ==================== Test Data ====================

def create_test_job(job_id=1, title="Software Engineer", company="Test Corp"):
    """Create a test job dictionary"""
    return {
        "title": title,
        "company": company,
        "location": "New York, NY",
        "link": f"https://example.com/job/{job_id}",
        "description": "Test job description",
        "job_type": "Full-time",
        "salary": {"min": 80000, "max": 120000, "raw": "$80,000 - $120,000"}
    }


# ==================== Storage Manager Tests ====================

def test_storage_initialization():
    """Test storage manager initialization"""
    print("\n=== Test: Storage Initialization ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Check that directory and files were created
    assert os.path.exists(test_dir), "Storage directory not created"
    assert os.path.exists(storage.jobs_file), "Jobs file not created"
    assert os.path.exists(storage.metadata_file), "Metadata file not created"
    assert os.path.exists(storage.errors_file), "Errors file not created"
    
    print("✓ Storage initialized successfully")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


def test_save_and_retrieve_jobs():
    """Test saving and retrieving jobs"""
    print("\n=== Test: Save and Retrieve Jobs ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Create test jobs
    jobs = [
        create_test_job(1, "Software Engineer", "Company A"),
        create_test_job(2, "Data Scientist", "Company B"),
        create_test_job(3, "Product Manager", "Company C")
    ]
    
    # Save jobs
    result = storage.save_jobs(jobs, source="test")
    
    assert result["success"], f"Failed to save jobs: {result.get('error')}"
    assert result["added"] == 3, f"Expected 3 jobs added, got {result['added']}"
    assert result["total"] == 3, f"Expected total 3, got {result['total']}"
    
    print(f"✓ Saved {result['added']} jobs")
    
    # Retrieve jobs
    retrieved_jobs = storage.get_all_jobs()
    
    assert len(retrieved_jobs) == 3, f"Expected 3 jobs, got {len(retrieved_jobs)}"
    assert all(job.get('source') == 'test' for job in retrieved_jobs), "Source not set correctly"
    
    print(f"✓ Retrieved {len(retrieved_jobs)} jobs")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


def test_duplicate_detection():
    """Test duplicate job detection"""
    print("\n=== Test: Duplicate Detection ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Create test jobs
    job1 = create_test_job(1, "Software Engineer", "Company A")
    job2 = create_test_job(1, "Software Engineer", "Company A")  # Duplicate
    job3 = create_test_job(2, "Data Scientist", "Company B")
    
    # Save first batch
    result1 = storage.save_jobs([job1, job3], source="test")
    assert result1["added"] == 2, f"Expected 2 jobs added, got {result1['added']}"
    
    print(f"✓ First batch: {result1['added']} added")
    
    # Save second batch with duplicate
    result2 = storage.save_jobs([job1, job2, job3], source="test", skip_duplicates=True)
    assert result2["skipped"] == 3, f"Expected 3 duplicates skipped, got {result2['skipped']}"
    assert result2["added"] == 0, f"Expected 0 new jobs, got {result2['added']}"
    
    print(f"✓ Second batch: {result2['skipped']} duplicates skipped")
    
    # Verify total
    jobs = storage.get_all_jobs()
    assert len(jobs) == 2, f"Expected 2 unique jobs, got {len(jobs)}"
    
    print(f"✓ Total unique jobs: {len(jobs)}")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


def test_data_validation():
    """Test job data validation"""
    print("\n=== Test: Data Validation ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Create invalid jobs
    invalid_jobs = [
        {"title": "Engineer"},  # Missing required fields
        {"title": "Engineer", "company": "Corp"},  # Missing location and link
        create_test_job(1),  # Valid job
        {"title": "", "company": "Corp", "location": "NY", "link": "http://test.com"}  # Empty title
    ]
    
    # Try to save
    result = storage.save_jobs(invalid_jobs, source="test")
    
    assert result["added"] == 1, f"Expected 1 valid job, got {result['added']}"
    assert result["invalid"] == 3, f"Expected 3 invalid jobs, got {result['invalid']}"
    
    print(f"✓ Validation: {result['added']} valid, {result['invalid']} invalid")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


def test_job_filtering():
    """Test job filtering"""
    print("\n=== Test: Job Filtering ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Create jobs from different sources
    indeed_jobs = [
        create_test_job(1, "Software Engineer", "Company A"),
        create_test_job(2, "Data Scientist", "Company B")
    ]
    glassdoor_jobs = [
        create_test_job(3, "Product Manager", "Company C"),
        create_test_job(4, "Designer", "Company D")
    ]
    
    storage.save_jobs(indeed_jobs, source="indeed")
    storage.save_jobs(glassdoor_jobs, source="glassdoor")
    
    # Test filtering by source
    indeed_filtered = storage.get_all_jobs(filters={"source": "indeed"})
    assert len(indeed_filtered) == 2, f"Expected 2 Indeed jobs, got {len(indeed_filtered)}"
    
    glassdoor_filtered = storage.get_all_jobs(filters={"source": "glassdoor"})
    assert len(glassdoor_filtered) == 2, f"Expected 2 Glassdoor jobs, got {len(glassdoor_filtered)}"
    
    print(f"✓ Filtered: {len(indeed_filtered)} Indeed jobs, {len(glassdoor_filtered)} Glassdoor jobs")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


def test_job_deletion():
    """Test job deletion"""
    print("\n=== Test: Job Deletion ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Create and save jobs
    jobs = [create_test_job(i) for i in range(5)]
    storage.save_jobs(jobs, source="test")
    
    # Get all jobs
    all_jobs = storage.get_all_jobs()
    assert len(all_jobs) == 5, "Initial jobs not saved correctly"
    
    # Delete one job
    job_id = all_jobs[0]['id']
    success = storage.delete_job(job_id)
    assert success, "Failed to delete job"
    
    # Verify deletion
    remaining_jobs = storage.get_all_jobs()
    assert len(remaining_jobs) == 4, f"Expected 4 jobs after deletion, got {len(remaining_jobs)}"
    
    print(f"✓ Deleted 1 job, {len(remaining_jobs)} remaining")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


def test_clear_all_jobs():
    """Test clearing all jobs"""
    print("\n=== Test: Clear All Jobs ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Create and save jobs
    jobs = [create_test_job(i) for i in range(10)]
    storage.save_jobs(jobs, source="test")
    
    # Verify jobs exist
    assert len(storage.get_all_jobs()) == 10, "Jobs not saved"
    
    # Clear all
    success = storage.clear_all_jobs()
    assert success, "Failed to clear jobs"
    
    # Verify empty
    remaining = storage.get_all_jobs()
    assert len(remaining) == 0, f"Expected 0 jobs, got {len(remaining)}"
    
    print("✓ All jobs cleared successfully")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


def test_statistics():
    """Test storage statistics"""
    print("\n=== Test: Storage Statistics ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Save jobs from different sources
    storage.save_jobs([create_test_job(i) for i in range(3)], source="indeed")
    storage.save_jobs([create_test_job(i+3) for i in range(2)], source="glassdoor")
    
    # Get statistics
    stats = storage.get_statistics()
    
    assert stats["total_jobs"] == 5, f"Expected 5 total jobs, got {stats['total_jobs']}"
    assert stats["jobs_by_source"]["indeed"] == 3, "Incorrect Indeed count"
    assert stats["jobs_by_source"]["glassdoor"] == 2, "Incorrect Glassdoor count"
    
    print(f"✓ Statistics: {stats['total_jobs']} total jobs")
    print(f"  - Indeed: {stats['jobs_by_source']['indeed']}")
    print(f"  - Glassdoor: {stats['jobs_by_source']['glassdoor']}")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


def test_export_jobs():
    """Test exporting jobs to JSON"""
    print("\n=== Test: Export Jobs ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Save jobs
    jobs = [create_test_job(i) for i in range(5)]
    storage.save_jobs(jobs, source="test")
    
    # Export
    export_file = os.path.join(test_dir, "exported_jobs.json")
    success = storage.export_to_json(export_file)
    assert success, "Export failed"
    assert os.path.exists(export_file), "Export file not created"
    
    # Verify export content
    with open(export_file, 'r') as f:
        export_data = json.load(f)
    
    assert export_data["total_jobs"] == 5, "Incorrect job count in export"
    assert len(export_data["jobs"]) == 5, "Incorrect jobs in export"
    
    print(f"✓ Exported {export_data['total_jobs']} jobs to {export_file}")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


# ==================== Retry Logic Tests ====================

class MockScraper:
    """Mock scraper for testing retry logic"""
    
    def __init__(self, fail_times=0):
        self.fail_times = fail_times
        self.call_count = 0
    
    def scrape_jobs(self, job_title, location, num_pages=1):
        self.call_count += 1
        if self.call_count <= self.fail_times:
            raise Exception(f"Mock scraper failure (attempt {self.call_count})")
        return [create_test_job(i, job_title) for i in range(3)]


def test_retry_decorator():
    """Test retry decorator"""
    print("\n=== Test: Retry Decorator ===")
    
    call_count = [0]
    
    @retry_with_backoff(max_retries=3, initial_delay=0.1, exponential_base=2.0)
    def flaky_function():
        call_count[0] += 1
        if call_count[0] < 3:
            raise Exception("Temporary failure")
        return "Success"
    
    # Should succeed after 3 attempts
    result = flaky_function()
    assert result == "Success", "Function did not succeed"
    assert call_count[0] == 3, f"Expected 3 calls, got {call_count[0]}"
    
    print(f"✓ Retry decorator worked: {call_count[0]} attempts")
    
    return True


def test_retry_scraper_success():
    """Test retry scraper with successful scraping"""
    print("\n=== Test: Retry Scraper Success ===")
    
    # Create mock scraper that succeeds immediately
    mock_scraper = MockScraper(fail_times=0)
    config = RetryConfig(max_retries=3, initial_delay=0.1)
    retry_scraper = RetryScraper(mock_scraper, config)
    
    # Scrape
    result = retry_scraper.scrape_jobs_with_retry("Software Engineer", "New York", 1)
    
    assert result["success"], "Scraping should succeed"
    assert len(result["jobs"]) == 3, "Should get 3 jobs"
    assert result["total_attempts"] == 1, "Should succeed on first attempt"
    
    print(f"✓ Scraping succeeded on attempt {result['total_attempts']}")
    
    return True


def test_retry_scraper_with_retries():
    """Test retry scraper with failures then success"""
    print("\n=== Test: Retry Scraper With Retries ===")
    
    # Create mock scraper that fails 2 times then succeeds
    mock_scraper = MockScraper(fail_times=2)
    config = RetryConfig(max_retries=3, initial_delay=0.1)
    retry_scraper = RetryScraper(mock_scraper, config)
    
    # Scrape
    result = retry_scraper.scrape_jobs_with_retry("Software Engineer", "New York", 1)
    
    assert result["success"], "Scraping should eventually succeed"
    assert len(result["jobs"]) == 3, "Should get 3 jobs"
    assert result["total_attempts"] == 3, f"Should succeed on 3rd attempt, got {result['total_attempts']}"
    
    print(f"✓ Scraping succeeded after {result['total_attempts']} attempts")
    
    return True


def test_retry_scraper_exhausted():
    """Test retry scraper when all retries are exhausted"""
    print("\n=== Test: Retry Scraper Exhausted ===")
    
    # Create mock scraper that always fails
    mock_scraper = MockScraper(fail_times=10)
    config = RetryConfig(max_retries=3, initial_delay=0.1)
    retry_scraper = RetryScraper(mock_scraper, config)
    
    # Scrape
    result = retry_scraper.scrape_jobs_with_retry("Software Engineer", "New York", 1)
    
    assert not result["success"], "Scraping should fail"
    assert len(result["jobs"]) == 0, "Should get no jobs"
    assert result["total_attempts"] == 4, f"Should attempt 4 times (1 + 3 retries), got {result['total_attempts']}"
    assert "final_error" in result, "Should have final error"
    
    print(f"✓ Scraping failed after {result['total_attempts']} attempts (as expected)")
    
    return True


def test_retry_scraper_statistics():
    """Test retry scraper statistics"""
    print("\n=== Test: Retry Scraper Statistics ===")
    
    mock_scraper = MockScraper(fail_times=0)
    config = RetryConfig(max_retries=3, initial_delay=0.1)
    retry_scraper = RetryScraper(mock_scraper, config)
    
    # Perform multiple scrapes
    retry_scraper.scrape_jobs_with_retry("Software Engineer", "New York", 1)
    retry_scraper.scrape_jobs_with_retry("Data Scientist", "Boston", 1)
    retry_scraper.scrape_jobs_with_retry("Product Manager", "Seattle", 1)
    
    # Get statistics
    stats = retry_scraper.get_attempt_statistics()
    
    assert stats["total_attempts"] == 3, "Should have 3 total attempts"
    assert stats["successful"] == 3, "All should succeed"
    assert stats["failed"] == 0, "None should fail"
    assert stats["success_rate"] == 100.0, "Success rate should be 100%"
    
    print(f"✓ Statistics: {stats['successful']}/{stats['total_attempts']} successful ({stats['success_rate']:.1f}%)")
    
    return True


# ==================== Integration Tests ====================

def test_storage_with_retry_integration():
    """Test integration of storage manager with retry scraper"""
    print("\n=== Test: Storage + Retry Integration ===")
    
    test_dir = "test_data"
    storage = JobStorageManager(storage_dir=test_dir)
    
    # Create retry scraper
    mock_scraper = MockScraper(fail_times=1)  # Fail once, then succeed
    config = RetryConfig(max_retries=3, initial_delay=0.1)
    retry_scraper = RetryScraper(mock_scraper, config)
    
    # Scrape with retry
    result = retry_scraper.scrape_jobs_with_retry("Software Engineer", "New York", 1)
    
    assert result["success"], "Scraping should succeed"
    
    # Save to storage
    storage_result = storage.save_jobs(result["jobs"], source="test_integration")
    
    assert storage_result["success"], "Storage should succeed"
    assert storage_result["added"] == 3, "Should save 3 jobs"
    
    # Verify retrieval
    jobs = storage.get_all_jobs()
    assert len(jobs) == 3, "Should retrieve 3 jobs"
    
    print(f"✓ Integration test passed: scraped with retry and saved {len(jobs)} jobs")
    
    # Cleanup
    shutil.rmtree(test_dir)
    return True


# ==================== Test Runner ====================

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running Storage Manager and Retry Logic Test Suite")
    print("="*60)
    
    tests = [
        # Storage tests
        ("Storage Initialization", test_storage_initialization),
        ("Save and Retrieve Jobs", test_save_and_retrieve_jobs),
        ("Duplicate Detection", test_duplicate_detection),
        ("Data Validation", test_data_validation),
        ("Job Filtering", test_job_filtering),
        ("Job Deletion", test_job_deletion),
        ("Clear All Jobs", test_clear_all_jobs),
        ("Storage Statistics", test_statistics),
        ("Export Jobs", test_export_jobs),
        
        # Retry logic tests
        ("Retry Decorator", test_retry_decorator),
        ("Retry Scraper Success", test_retry_scraper_success),
        ("Retry Scraper With Retries", test_retry_scraper_with_retries),
        ("Retry Scraper Exhausted", test_retry_scraper_exhausted),
        ("Retry Scraper Statistics", test_retry_scraper_statistics),
        
        # Integration tests
        ("Storage + Retry Integration", test_storage_with_retry_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ FAILED: {test_name}")
            print(f"  Error: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {test_name}")
            print(f"  Error: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
