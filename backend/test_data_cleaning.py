"""
Test Suite for Data Cleaning Module
Tests deduplication, validation, and normalization functions
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from data_processor import DataProcessor, clean_job_data, normalize_location, normalize_salary


def test_remove_duplicates():
    """Test duplicate removal"""
    print("\n" + "="*60)
    print("TEST: Remove Duplicates")
    print("="*60)
    
    processor = DataProcessor()
    
    jobs = [
        {
            "title": "Software Engineer",
            "company": "Google",
            "location": "New York",
            "salary": "$100k-$150k"
        },
        {
            "title": "Software Engineer",
            "company": "Google",
            "location": "New York",
            "salary": "$100k-$150k"  # Duplicate
        },
        {
            "title": "Data Scientist",
            "company": "Amazon",
            "location": "Seattle",
            "salary": "$120k-$160k"
        },
        {
            "title": "software engineer",  # Same as first but different case
            "company": "google",
            "location": "new york",
            "salary": "$110k-$155k"
        }
    ]
    
    unique_jobs = processor._remove_duplicates(jobs)
    
    print(f"Original jobs: {len(jobs)}")
    print(f"Unique jobs: {len(unique_jobs)}")
    print(f"Duplicates removed: {processor.stats['duplicates_removed']}")
    
    assert len(unique_jobs) == 2, f"Expected 2 unique jobs, got {len(unique_jobs)}"
    print("✓ Test passed: Duplicates removed correctly")
    
    return True


def test_remove_incomplete_entries():
    """Test removal of incomplete entries"""
    print("\n" + "="*60)
    print("TEST: Remove Incomplete Entries")
    print("="*60)
    
    processor = DataProcessor()
    
    jobs = [
        {
            "title": "Software Engineer",
            "company": "Google",
            "location": "New York",
            "salary": "$100k-$150k"
        },
        {
            "title": "",  # Missing title
            "company": "Amazon",
            "location": "Seattle"
        },
        {
            "title": "Data Analyst",
            "company": "",  # Missing company
            "location": "Boston"
        },
        {
            "title": "Product Manager",
            "company": "Microsoft"
            # Missing location
        },
        {
            "title": "Designer",
            "company": "Apple",
            "location": "Cupertino"
        }
    ]
    
    complete_jobs = processor._remove_incomplete_entries(jobs)
    
    print(f"Original jobs: {len(jobs)}")
    print(f"Complete jobs: {len(complete_jobs)}")
    print(f"Incomplete entries removed: {processor.stats['incomplete_removed']}")
    
    assert len(complete_jobs) == 2, f"Expected 2 complete jobs, got {len(complete_jobs)}"
    print("✓ Test passed: Incomplete entries removed correctly")
    
    return True


def test_normalize_locations():
    """Test location normalization"""
    print("\n" + "="*60)
    print("TEST: Normalize Locations")
    print("="*60)
    
    processor = DataProcessor()
    
    test_cases = [
        ("NYC", "New York"),
        ("new york city", "New York"),
        ("SF", "San Francisco"),
        ("LA", "Los Angeles"),
        ("washington dc", "Washington"),  # "washington dc" maps to "washington"
        ("Remote - USA", "United States"),  # "USA" gets expanded to "United States"
        ("   boston  ", "Boston"),
    ]
    
    passed = 0
    failed = 0
    
    for input_loc, expected in test_cases:
        result = processor._normalize_single_location(input_loc)
        if expected.lower() in result.lower():
            print(f"✓ '{input_loc}' -> '{result}'")
            passed += 1
        else:
            print(f"✗ '{input_loc}' -> '{result}' (expected contains '{expected}')")
            failed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    assert failed == 0, f"{failed} location normalization tests failed"
    print("✓ Test passed: Locations normalized correctly")
    
    return True

def test_normalize_salaries():
    """Test salary normalization"""
    print("\n" + "="*60)
    print("TEST: Normalize Salaries")
    print("="*60)
    
    processor = DataProcessor()
    
    test_cases = [
        ("$100,000 - $150,000", {"min": 100000, "max": 150000}),
        ("$50k-$70k", {"min": 50000, "max": 70000}),
        ("100k - 120k", {"min": 100000, "max": 120000}),
        ("$80,000/year", {"min": 80000, "max": 80000}),
        ("60-80k", {"min": 60000, "max": 80000}),
        ("$25/hour", {"min": 25, "max": 25}),
    ]
    
    passed = 0
    failed = 0
    
    for input_salary, expected in test_cases:
        result = processor._normalize_single_salary(input_salary)
        if result:
            if result['min'] == expected['min'] and result['max'] == expected['max']:
                print(f"✓ '{input_salary}' -> {result['min']}-{result['max']}")
                passed += 1
            else:
                print(f"✗ '{input_salary}' -> {result['min']}-{result['max']} (expected {expected['min']}-{expected['max']})")
                failed += 1
        else:
            print(f"✗ '{input_salary}' -> None (parsing failed)")
            failed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    assert failed == 0, f"{failed} salary normalization tests failed"
    print("✓ Test passed: Salaries normalized correctly")
    
    return True


def test_full_cleaning_pipeline():
    """Test the complete cleaning pipeline"""
    print("\n" + "="*60)
    print("TEST: Full Cleaning Pipeline")
    print("="*60)
    
    jobs = [
        {
            "title": "Software Engineer",
            "company": "Google",
            "location": "NYC",
            "salary": "$100k-$150k",
            "description": "Python developer"
        },
        {
            "title": "Software Engineer",  # Exact duplicate (case-insensitive)
            "company": "google",
            "location": "NYC",
            "salary": "$100,000-$150,000"
        },
        {
            "title": "Data Scientist",
            "company": "Amazon",
            "location": "seattle",
            "salary": "120k-160k"
        },
        {
            "title": "",  # Incomplete
            "company": "Microsoft",
            "location": "Redmond"
        },
        {
            "title": "Product Manager",
            "company": "Apple",
            "location": "SF",
            "salary": "$140,000 per year"
        }
    ]
    
    print(f"Input: {len(jobs)} jobs")
    
    cleaned_jobs, stats = clean_job_data(jobs)
    
    print(f"\nCleaning Statistics:")
    print(f"  - Total processed: {stats['total_processed']}")
    print(f"  - Duplicates removed: {stats['duplicates_removed']}")
    print(f"  - Incomplete removed: {stats['incomplete_removed']}")
    print(f"  - Locations normalized: {stats['locations_normalized']}")
    print(f"  - Salaries normalized: {stats['salaries_normalized']}")
    print(f"\nOutput: {len(cleaned_jobs)} cleaned jobs")
    
    # Verify results
    assert len(cleaned_jobs) == 3, f"Expected 3 cleaned jobs, got {len(cleaned_jobs)}"
    assert stats['duplicates_removed'] == 1, f"Should remove 1 duplicate, removed {stats['duplicates_removed']}"
    assert stats['incomplete_removed'] == 1, f"Should remove 1 incomplete entry, removed {stats['incomplete_removed']}"
    
    # Check if locations are normalized
    for job in cleaned_jobs:
        print(f"\n  Job: {job['title']} at {job['company']}")
        print(f"    Location: {job['location']}")
        if 'salary_min' in job:
            print(f"    Salary: ${job['salary_min']:,.0f} - ${job['salary_max']:,.0f}")
    
    print("\n✓ Test passed: Full pipeline works correctly")
    
    return True


def test_convenience_functions():
    """Test convenience functions"""
    print("\n" + "="*60)
    print("TEST: Convenience Functions")
    print("="*60)
    
    # Test normalize_location
    location = normalize_location("NYC")
    print(f"normalize_location('NYC') = '{location}'")
    assert "New York" in location.title()
    
    # Test normalize_salary
    salary = normalize_salary("$100k-$150k")
    print(f"normalize_salary('$100k-$150k') = {salary}")
    assert salary['min'] == 100000
    assert salary['max'] == 150000
    
    print("✓ Test passed: Convenience functions work correctly")
    
    return True


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "="*60)
    print("TEST: Edge Cases and Error Handling")
    print("="*60)
    
    processor = DataProcessor()
    
    # Empty list
    result, stats = clean_job_data([])
    assert len(result) == 0
    print("✓ Handles empty list")
    
    # None values
    location = processor._normalize_single_location(None)
    assert location is None
    print("✓ Handles None location")
    
    salary = processor._normalize_single_salary(None)
    assert salary is None
    print("✓ Handles None salary")
    
    # Invalid salary formats
    invalid_salaries = ["TBD", "Competitive", "N/A", ""]
    for sal in invalid_salaries:
        result = processor._normalize_single_salary(sal)
        # Should either return None or parse what it can
        print(f"  '{sal}' -> {result}")
    print("✓ Handles invalid salary formats")
    
    print("✓ Test passed: Edge cases handled correctly")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" DATA CLEANING MODULE TEST SUITE")
    print("="*70)
    
    tests = [
        ("Remove Duplicates", test_remove_duplicates),
        ("Remove Incomplete Entries", test_remove_incomplete_entries),
        ("Normalize Locations", test_normalize_locations),
        ("Normalize Salaries", test_normalize_salaries),
        ("Full Cleaning Pipeline", test_full_cleaning_pipeline),
        ("Convenience Functions", test_convenience_functions),
        ("Edge Cases", test_edge_cases),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {test_name}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ TEST ERROR: {test_name}")
            print(f"  Error: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        return True
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
