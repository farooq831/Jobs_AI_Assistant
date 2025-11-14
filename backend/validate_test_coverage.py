#!/usr/bin/env python3
"""
Test Coverage Validation Script
Validates that all core modules have corresponding unit tests
Task 10.1: Unit Testing
"""

import os
import glob

def get_module_files():
    """Get all Python module files (excluding tests and demos)"""
    backend_dir = os.path.dirname(__file__)
    all_files = glob.glob(os.path.join(backend_dir, '*.py'))
    
    modules = []
    for f in all_files:
        basename = os.path.basename(f)
        # Exclude test files, demo files, and special files
        if not (basename.startswith('test_') or 
                basename.startswith('demo_') or
                basename in ['app.py', 'run_all_tests.py', 'validate_test_coverage.py', '__init__.py']):
            modules.append(basename.replace('.py', ''))
    
    return sorted(modules)

def get_test_files():
    """Get all test files"""
    backend_dir = os.path.dirname(__file__)
    test_files = glob.glob(os.path.join(backend_dir, 'test_*.py'))
    return [os.path.basename(f).replace('.py', '') for f in sorted(test_files)]

def check_test_coverage():
    """Check which modules have test coverage"""
    modules = get_module_files()
    tests = get_test_files()
    
    print("=" * 80)
    print("TEST COVERAGE VALIDATION")
    print("=" * 80)
    print()
    
    # Define explicit test mappings
    test_mappings = {
        'csv_pdf_exporter': ['test_csv_pdf_export'],
        'data_processor': ['test_data_cleaning', 'test_filtering'],
        'excel_exporter': ['test_excel_export'],
        'excel_uploader': ['test_excel_upload'],
        'job_scorer': ['test_scoring', 'test_score_integration'],
        'keyword_extractor': ['test_keyword_extraction'],
        'storage_manager': ['test_storage', 'test_storage_simple'],
        'application_status': ['test_application_status'],
        'resume_analyzer': ['test_resume_analyzer', 'test_resume_upload', 'test_job_keyword_analysis', 'test_optimization_tips']
    }
    
    # Check coverage
    covered = []
    not_covered = []
    
    for module in modules:
        # Check explicit mapping first
        if module in test_mappings:
            test_files = [t for t in test_mappings[module] if t in tests]
            if test_files:
                covered.append((module, ', '.join(test_files)))
                continue
        
        # Check if there's a direct test file
        test_file = f'test_{module}'
        has_test = test_file in tests
        
        if has_test:
            covered.append((module, test_file))
        else:
            # Check if module might be tested indirectly
            indirect = []
            for test in tests:
                if module.replace('_', '') in test.replace('_', ''):
                    indirect.append(test)
            
            if indirect:
                covered.append((module, ', '.join(indirect)))
            else:
                not_covered.append(module)
    
    # Print results
    print(f"Core Modules Found: {len(modules)}")
    print(f"Test Files Found: {len(tests)}")
    print(f"Coverage: {len(covered)}/{len(modules)} ({len(covered)/len(modules)*100:.1f}%)")
    print()
    
    print("MODULES WITH TEST COVERAGE:")
    print("-" * 80)
    for module, test in covered:
        print(f"✓ {module:<30} -> {test}")
    
    if not_covered:
        print("\nMODULES WITHOUT DIRECT TEST COVERAGE:")
        print("-" * 80)
        for module in not_covered:
            print(f"✗ {module}")
        print("\nNote: Some modules may be tested indirectly through integration tests")
    
    print("\n" + "=" * 80)
    print("ALL TEST FILES:")
    print("-" * 80)
    for test in tests:
        print(f"  • {test}.py")
    
    print("\n" + "=" * 80)
    
    # Test quality indicators
    print("\nTEST QUALITY INDICATORS:")
    print("-" * 80)
    
    test_categories = {
        'Scraping': ['test_scraper', 'test_selenium_scraper'],
        'Data Processing': ['test_data_cleaning', 'test_filtering'],
        'Storage': ['test_storage', 'test_storage_simple'],
        'Scoring': ['test_keyword_extraction', 'test_scoring', 'test_score_integration'],
        'Resume Analysis': ['test_resume_analyzer', 'test_resume_upload', 'test_job_keyword_analysis', 'test_optimization_tips'],
        'Export/Import': ['test_excel_export', 'test_csv_pdf_export', 'test_excel_upload'],
        'Application Tracking': ['test_application_status', 'test_status_tracking'],
        'Integration': ['test_ui_integration', 'test_api', 'test_task_9.2', 'test_task_9.3']
    }
    
    for category, test_list in test_categories.items():
        found = [t for t in test_list if t in tests]
        status = "✓" if found else "✗"
        print(f"{status} {category:<30} {len(found)}/{len(test_list)} tests")
    
    print("=" * 80)
    
    return len(not_covered) == 0

if __name__ == '__main__':
    all_covered = check_test_coverage()
    exit(0 if all_covered else 1)
