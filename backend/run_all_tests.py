#!/usr/bin/env python3
"""
Comprehensive Unit Testing Suite Runner
Runs all unit tests for the AI Job Application Assistant
Task 10.1: Unit Testing
"""

import sys
import unittest
import os
import time
from io import StringIO
from datetime import datetime

# Test modules to run
TEST_MODULES = [
    # Core scraping tests
    ('test_scraper', 'Web Scraping (BeautifulSoup)'),
    ('test_selenium_scraper', 'Dynamic Scraping (Selenium)'),
    
    # Data processing tests
    ('test_data_cleaning', 'Data Cleaning'),
    ('test_filtering', 'Job Filtering'),
    
    # Storage tests
    ('test_storage', 'Data Storage Management'),
    
    # Scoring and matching tests
    ('test_keyword_extraction', 'Keyword Extraction (NLP)'),
    ('test_scoring', 'Job Scoring Algorithm'),
    ('test_score_integration', 'Score Integration'),
    
    # Resume analysis tests
    ('test_resume_analyzer', 'Resume Analysis'),
    ('test_resume_upload', 'Resume Upload'),
    ('test_job_keyword_analysis', 'Job Keyword Analysis'),
    ('test_optimization_tips', 'Resume Optimization Tips'),
    
    # Export/Import tests
    ('test_excel_export', 'Excel Export'),
    ('test_csv_pdf_export', 'CSV/PDF Export'),
    ('test_excel_upload', 'Excel Upload'),
    
    # Application tracking tests
    ('test_application_status', 'Application Status Model'),
    ('test_status_tracking', 'Status Tracking Logic'),
    
    # Integration tests
    ('test_ui_integration', 'UI Integration'),
    ('test_api', 'API Endpoints'),
]

class TestResult:
    """Store test results"""
    def __init__(self, module_name, display_name):
        self.module_name = module_name
        self.display_name = display_name
        self.passed = False
        self.total_tests = 0
        self.failures = 0
        self.errors = 0
        self.skipped = 0
        self.duration = 0
        self.error_messages = []

def run_test_module(module_name, display_name):
    """Run a single test module and return results"""
    result = TestResult(module_name, display_name)
    
    try:
        # Import the test module
        test_module = __import__(module_name)
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Run tests with custom result
        runner = unittest.TextTestRunner(stream=StringIO(), verbosity=2)
        start_time = time.time()
        test_result = runner.run(suite)
        result.duration = time.time() - start_time
        
        # Store results
        result.total_tests = test_result.testsRun
        result.failures = len(test_result.failures)
        result.errors = len(test_result.errors)
        result.skipped = len(test_result.skipped)
        result.passed = test_result.wasSuccessful()
        
        # Collect error messages
        for test, traceback in test_result.failures + test_result.errors:
            result.error_messages.append(f"{test}: {traceback}")
            
    except ImportError as e:
        result.errors = 1
        result.error_messages.append(f"Failed to import module: {e}")
    except Exception as e:
        result.errors = 1
        result.error_messages.append(f"Unexpected error: {e}")
    
    return result

def print_header():
    """Print test suite header"""
    print("=" * 80)
    print("AI JOB APPLICATION ASSISTANT - COMPREHENSIVE UNIT TEST SUITE")
    print("Task 10.1: Unit Testing")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print("=" * 80)
    print()

def print_progress(current, total, module_name):
    """Print progress during test execution"""
    percentage = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\r[{bar}] {percentage:.1f}% - Testing: {module_name:<35}", end='', flush=True)

def print_summary(results):
    """Print comprehensive test summary"""
    print("\n\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    total_modules = len(results)
    passed_modules = sum(1 for r in results if r.passed)
    total_tests = sum(r.total_tests for r in results)
    total_failures = sum(r.failures for r in results)
    total_errors = sum(r.errors for r in results)
    total_skipped = sum(r.skipped for r in results)
    total_duration = sum(r.duration for r in results)
    
    # Module results table
    print("\nModule Test Results:")
    print("-" * 80)
    print(f"{'Module':<40} {'Tests':<8} {'Pass/Fail':<12} {'Time':<10}")
    print("-" * 80)
    
    for result in results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        status_icon = "✓" if result.passed else "✗"
        color = "\033[92m" if result.passed else "\033[91m"
        reset = "\033[0m"
        
        test_info = f"{result.total_tests} tests"
        if result.failures > 0 or result.errors > 0:
            test_info += f" ({result.failures}F, {result.errors}E"
            if result.skipped > 0:
                test_info += f", {result.skipped}S"
            test_info += ")"
        elif result.skipped > 0:
            test_info += f" ({result.skipped}S)"
        
        print(f"{result.display_name:<40} {test_info:<8} {color}{status:<12}{reset} {result.duration:.2f}s")
    
    print("-" * 80)
    
    # Overall statistics
    print(f"\n{'OVERALL STATISTICS':<40}")
    print("-" * 80)
    print(f"{'Total Modules:':<30} {total_modules}")
    print(f"{'Passed Modules:':<30} {passed_modules} ({passed_modules/total_modules*100:.1f}%)")
    print(f"{'Failed Modules:':<30} {total_modules - passed_modules}")
    print(f"{'Total Test Cases:':<30} {total_tests}")
    print(f"{'Passed Tests:':<30} {total_tests - total_failures - total_errors}")
    print(f"{'Failed Tests:':<30} {total_failures}")
    print(f"{'Errors:':<30} {total_errors}")
    print(f"{'Skipped Tests:':<30} {total_skipped}")
    print(f"{'Total Duration:':<30} {total_duration:.2f}s")
    print("-" * 80)
    
    # Coverage by module type
    print(f"\n{'COVERAGE BY MODULE TYPE':<40}")
    print("-" * 80)
    
    module_types = {
        'Scraping': ['Web Scraping (BeautifulSoup)', 'Dynamic Scraping (Selenium)'],
        'Data Processing': ['Data Cleaning', 'Job Filtering', 'Data Storage Management'],
        'Scoring & Matching': ['Keyword Extraction (NLP)', 'Job Scoring Algorithm', 'Score Integration'],
        'Resume Analysis': ['Resume Analysis', 'Resume Upload', 'Job Keyword Analysis', 'Resume Optimization Tips'],
        'Export/Import': ['Excel Export', 'CSV/PDF Export', 'Excel Upload'],
        'Application Tracking': ['Application Status Model', 'Status Tracking Logic'],
        'Integration': ['UI Integration', 'API Endpoints']
    }
    
    for category, module_names in module_types.items():
        category_results = [r for r in results if r.display_name in module_names]
        if category_results:
            total_cat_tests = sum(r.total_tests for r in category_results)
            passed_cat_tests = sum(r.total_tests - r.failures - r.errors for r in category_results)
            coverage = (passed_cat_tests / total_cat_tests * 100) if total_cat_tests > 0 else 0
            status = "✓" if all(r.passed for r in category_results) else "✗"
            print(f"{status} {category:<30} {passed_cat_tests}/{total_cat_tests} tests ({coverage:.1f}%)")
    
    print("-" * 80)
    
    # Failed tests details
    failed_results = [r for r in results if not r.passed and r.error_messages]
    if failed_results:
        print(f"\n{'FAILED TESTS DETAILS':<40}")
        print("-" * 80)
        for result in failed_results:
            print(f"\n{result.display_name} ({result.module_name}):")
            for msg in result.error_messages[:3]:  # Show first 3 errors
                print(f"  • {msg[:200]}...")
            if len(result.error_messages) > 3:
                print(f"  ... and {len(result.error_messages) - 3} more errors")
    
    # Final status
    print("\n" + "=" * 80)
    if passed_modules == total_modules:
        print("✓ ALL TESTS PASSED!")
        print("=" * 80)
        return True
    else:
        print(f"✗ {total_modules - passed_modules} MODULE(S) FAILED")
        print("=" * 80)
        return False

def main():
    """Main test runner"""
    print_header()
    
    results = []
    total = len(TEST_MODULES)
    
    for idx, (module_name, display_name) in enumerate(TEST_MODULES, 1):
        print_progress(idx - 1, total, display_name)
        result = run_test_module(module_name, display_name)
        results.append(result)
    
    print_progress(total, total, "Complete")
    
    # Print summary
    all_passed = print_summary(results)
    
    # Generate report file
    report_path = os.path.join(os.path.dirname(__file__), 'test_results.txt')
    with open(report_path, 'w') as f:
        f.write("AI Job Application Assistant - Test Results\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            f.write(f"{result.display_name}: {status}\n")
            f.write(f"  Tests: {result.total_tests}, Failures: {result.failures}, Errors: {result.errors}\n")
            if result.error_messages:
                f.write("  Errors:\n")
                for msg in result.error_messages:
                    f.write(f"    {msg}\n")
            f.write("\n")
    
    print(f"\nDetailed report saved to: {report_path}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
