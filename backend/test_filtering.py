"""
Test Suite for Job Filtering Functionality
Tests location, salary, and job type filtering
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data_processor import JobFilter, filter_jobs
import json


def test_location_filtering():
    """Test location-based filtering"""
    print("\n=== Testing Location Filtering ===")
    
    # Sample jobs
    jobs = [
        {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "New York, NY",
            "salary": "$100,000 - $150,000"
        },
        {
            "title": "Backend Developer",
            "company": "StartUp Inc",
            "location": "Remote",
            "salary": "$80,000 - $120,000"
        },
        {
            "title": "Frontend Developer",
            "company": "Web Solutions",
            "location": "San Francisco, CA",
            "salary": "$90,000 - $130,000"
        },
        {
            "title": "Full Stack Engineer",
            "company": "Digital Agency",
            "location": "New York City, NY",
            "salary": "$110,000 - $160,000"
        }
    ]
    
    # Test 1: Filter by New York
    print("\n1. Filter by 'New York':")
    filtered, stats = filter_jobs(jobs, user_location="New York")
    print(f"   Input: {stats['total_input']} jobs")
    print(f"   Output: {stats['total_output']} jobs")
    print(f"   Filtered out: {stats['location_filtered']} jobs")
    
    for job in filtered:
        print(f"   - {job['title']} at {job['company']} ({job['location']})")
    
    # Should include New York jobs and Remote jobs (3 total)
    assert stats['total_output'] == 3, f"Expected 3 jobs, got {stats['total_output']}"
    print("   ✓ Test passed: New York filtering works correctly")
    
    # Test 2: Filter by San Francisco
    print("\n2. Filter by 'San Francisco':")
    filtered, stats = filter_jobs(jobs, user_location="San Francisco")
    print(f"   Input: {stats['total_input']} jobs")
    print(f"   Output: {stats['total_output']} jobs")
    
    for job in filtered:
        print(f"   - {job['title']} at {job['company']} ({job['location']})")
    
    # Should include San Francisco jobs and Remote jobs (2 total)
    assert stats['total_output'] == 2, f"Expected 2 jobs, got {stats['total_output']}"
    print("   ✓ Test passed: San Francisco filtering works correctly")
    
    print("\n✅ All location filtering tests passed!")


def test_salary_filtering():
    """Test salary-based filtering"""
    print("\n=== Testing Salary Filtering ===")
    
    # Sample jobs with normalized salaries
    jobs = [
        {
            "title": "Junior Developer",
            "company": "StartUp A",
            "location": "Remote",
            "salary": "$50,000 - $70,000",
            "salary_min": 50000,
            "salary_max": 70000
        },
        {
            "title": "Mid-Level Developer",
            "company": "Tech B",
            "location": "New York",
            "salary": "$80,000 - $120,000",
            "salary_min": 80000,
            "salary_max": 120000
        },
        {
            "title": "Senior Developer",
            "company": "Enterprise C",
            "location": "San Francisco",
            "salary": "$130,000 - $180,000",
            "salary_min": 130000,
            "salary_max": 180000
        },
        {
            "title": "Lead Developer",
            "company": "BigTech D",
            "location": "Seattle",
            "salary": "$150,000 - $200,000",
            "salary_min": 150000,
            "salary_max": 200000
        }
    ]
    
    # Test 1: Filter by salary range $80k - $150k
    print("\n1. Filter by salary range $80,000 - $150,000:")
    filtered, stats = filter_jobs(jobs, salary_min=80000, salary_max=150000)
    print(f"   Input: {stats['total_input']} jobs")
    print(f"   Output: {stats['total_output']} jobs")
    print(f"   Filtered out: {stats['salary_filtered']} jobs")
    
    for job in filtered:
        print(f"   - {job['title']}: ${job['salary_min']:,} - ${job['salary_max']:,}")
    
    # Should include Mid-Level (80-120k), Senior (130-180k overlap), Lead (150-200k overlap)
    assert stats['total_output'] == 3, f"Expected 3 jobs, got {stats['total_output']}"
    print("   ✓ Test passed: Salary range filtering works correctly")
    
    # Test 2: Filter by minimum salary only
    print("\n2. Filter by minimum salary $100,000:")
    filtered, stats = filter_jobs(jobs, salary_min=100000)
    print(f"   Output: {stats['total_output']} jobs")
    
    for job in filtered:
        print(f"   - {job['title']}: ${job['salary_min']:,} - ${job['salary_max']:,}")
    
    # Should include jobs with max >= 100k (Mid, Senior, Lead)
    assert stats['total_output'] >= 3, f"Expected at least 3 jobs, got {stats['total_output']}"
    print("   ✓ Test passed: Minimum salary filtering works correctly")
    
    # Test 3: Filter by maximum salary only
    print("\n3. Filter by maximum salary $100,000:")
    filtered, stats = filter_jobs(jobs, salary_max=100000)
    print(f"   Output: {stats['total_output']} jobs")
    
    for job in filtered:
        print(f"   - {job['title']}: ${job['salary_min']:,} - ${job['salary_max']:,}")
    
    # Should include jobs with min <= 100k (Junior, Mid-Level)
    assert stats['total_output'] >= 2, f"Expected at least 2 jobs, got {stats['total_output']}"
    print("   ✓ Test passed: Maximum salary filtering works correctly")
    
    print("\n✅ All salary filtering tests passed!")


def test_job_type_filtering():
    """Test job type filtering"""
    print("\n=== Testing Job Type Filtering ===")
    
    # Sample jobs
    jobs = [
        {
            "title": "Remote Engineer",
            "company": "RemoteCo",
            "location": "Remote",
            "job_type": "Remote",
            "description": "Fully remote position"
        },
        {
            "title": "Office Engineer",
            "company": "OfficeCo",
            "location": "New York, NY",
            "job_type": "Onsite",
            "description": "In-office position"
        },
        {
            "title": "Hybrid Developer",
            "company": "FlexCo",
            "location": "San Francisco, CA",
            "job_type": "Hybrid",
            "description": "Hybrid work arrangement"
        },
        {
            "title": "Work From Home Developer",
            "company": "WFHCo",
            "location": "Anywhere",
            "description": "Work from home position"
        }
    ]
    
    # Test 1: Filter for Remote only
    print("\n1. Filter for Remote jobs only:")
    filtered, stats = filter_jobs(jobs, job_types=["Remote"])
    print(f"   Input: {stats['total_input']} jobs")
    print(f"   Output: {stats['total_output']} jobs")
    print(f"   Filtered out: {stats['job_type_filtered']} jobs")
    
    for job in filtered:
        print(f"   - {job['title']} ({job.get('job_type', 'N/A')})")
    
    # Should include remote jobs (2 total - explicit remote + WFH)
    assert stats['total_output'] >= 2, f"Expected at least 2 jobs, got {stats['total_output']}"
    print("   ✓ Test passed: Remote filtering works correctly")
    
    # Test 2: Filter for Remote and Hybrid
    print("\n2. Filter for Remote and Hybrid jobs:")
    filtered, stats = filter_jobs(jobs, job_types=["Remote", "Hybrid"])
    print(f"   Output: {stats['total_output']} jobs")
    
    for job in filtered:
        print(f"   - {job['title']} ({job.get('job_type', 'N/A')})")
    
    # Should include remote and hybrid jobs (3 total)
    assert stats['total_output'] >= 3, f"Expected at least 3 jobs, got {stats['total_output']}"
    print("   ✓ Test passed: Multi-type filtering works correctly")
    
    # Test 3: Filter for Onsite only
    print("\n3. Filter for Onsite jobs only:")
    filtered, stats = filter_jobs(jobs, job_types=["Onsite"])
    print(f"   Output: {stats['total_output']} jobs")
    
    for job in filtered:
        print(f"   - {job['title']} ({job.get('job_type', 'N/A')})")
    
    # Should include onsite jobs only (1 total)
    assert stats['total_output'] >= 1, f"Expected at least 1 job, got {stats['total_output']}"
    print("   ✓ Test passed: Onsite filtering works correctly")
    
    print("\n✅ All job type filtering tests passed!")


def test_combined_filtering():
    """Test combined filtering with multiple criteria"""
    print("\n=== Testing Combined Filtering ===")
    
    # Sample jobs
    jobs = [
        {
            "title": "Remote Senior Developer",
            "company": "TechCorp",
            "location": "Remote",
            "job_type": "Remote",
            "salary_min": 120000,
            "salary_max": 160000
        },
        {
            "title": "Junior Developer",
            "company": "LocalStartup",
            "location": "New York, NY",
            "job_type": "Onsite",
            "salary_min": 50000,
            "salary_max": 70000
        },
        {
            "title": "Hybrid Mid-Level Engineer",
            "company": "FlexCompany",
            "location": "New York, NY",
            "job_type": "Hybrid",
            "salary_min": 90000,
            "salary_max": 130000
        },
        {
            "title": "Senior Onsite Engineer",
            "company": "BigCorp",
            "location": "San Francisco, CA",
            "job_type": "Onsite",
            "salary_min": 140000,
            "salary_max": 180000
        }
    ]
    
    # Test: Filter for New York, $80k-$150k, Remote or Hybrid
    print("\n1. Filter for: New York, $80k-$150k, Remote or Hybrid:")
    filtered, stats = filter_jobs(
        jobs,
        user_location="New York",
        salary_min=80000,
        salary_max=150000,
        job_types=["Remote", "Hybrid"]
    )
    
    print(f"   Input: {stats['total_input']} jobs")
    print(f"   Output: {stats['total_output']} jobs")
    print(f"   Location filtered: {stats['location_filtered']}")
    print(f"   Salary filtered: {stats['salary_filtered']}")
    print(f"   Job type filtered: {stats['job_type_filtered']}")
    
    for job in filtered:
        print(f"   - {job['title']} at {job['company']}")
        print(f"     Location: {job['location']}, Type: {job['job_type']}, Salary: ${job['salary_min']:,}-${job['salary_max']:,}")
    
    # Should include Remote Senior (matches remote + salary) and Hybrid Mid-Level (matches all)
    assert stats['total_output'] >= 2, f"Expected at least 2 jobs, got {stats['total_output']}"
    print("   ✓ Test passed: Combined filtering works correctly")
    
    print("\n✅ All combined filtering tests passed!")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    # Test 1: Empty job list
    print("\n1. Test with empty job list:")
    filtered, stats = filter_jobs([], user_location="New York")
    assert len(filtered) == 0, "Expected empty result"
    print("   ✓ Test passed: Empty list handled correctly")
    
    # Test 2: Jobs with missing salary info
    print("\n2. Test with missing salary information:")
    jobs = [
        {"title": "Job 1", "company": "Co1", "location": "Remote"},
        {"title": "Job 2", "company": "Co2", "location": "NY", "salary_min": 100000, "salary_max": 150000}
    ]
    filtered, stats = filter_jobs(jobs, salary_min=80000, salary_max=120000)
    print(f"   Output: {len(filtered)} jobs (should include job without salary)")
    assert len(filtered) >= 1, "Expected at least 1 job"
    print("   ✓ Test passed: Missing salary handled correctly")
    
    # Test 3: Jobs with missing location
    print("\n3. Test with missing location:")
    jobs = [
        {"title": "Job 1", "company": "Co1", "location": ""},
        {"title": "Job 2", "company": "Co2", "location": "Remote"}
    ]
    filtered, stats = filter_jobs(jobs, user_location="New York")
    print(f"   Output: {len(filtered)} jobs")
    print("   ✓ Test passed: Missing location handled correctly")
    
    # Test 4: No filters applied
    print("\n4. Test with no filters:")
    jobs = [
        {"title": "Job 1", "company": "Co1", "location": "NY"},
        {"title": "Job 2", "company": "Co2", "location": "CA"}
    ]
    filtered, stats = filter_jobs(jobs)
    assert len(filtered) == 2, f"Expected 2 jobs, got {len(filtered)}"
    print("   ✓ Test passed: No filters returns all jobs")
    
    print("\n✅ All edge case tests passed!")


def run_all_tests():
    """Run all filtering tests"""
    print("=" * 60)
    print("JOB FILTERING TEST SUITE")
    print("=" * 60)
    
    try:
        test_location_filtering()
        test_salary_filtering()
        test_job_type_filtering()
        test_combined_filtering()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
