"""
Quick Test Suite for Storage Manager
Tests core storage functionality without requiring scraper dependencies
"""

import os
import sys
import json
import shutil

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage_manager import JobStorageManager


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


def test_basic_storage():
    """Test basic storage operations"""
    print("\n=== Testing Basic Storage Operations ===\n")
    
    test_dir = "test_storage_data"
    
    try:
        # Initialize storage
        print("1. Initializing storage...")
        storage = JobStorageManager(storage_dir=test_dir)
        print("   ✓ Storage initialized")
        
        # Create test jobs
        print("\n2. Creating test jobs...")
        jobs = [
            create_test_job(1, "Software Engineer", "Google"),
            create_test_job(2, "Data Scientist", "Microsoft"),
            create_test_job(3, "Product Manager", "Amazon"),
            create_test_job(4, "DevOps Engineer", "Meta"),
            create_test_job(5, "UX Designer", "Apple")
        ]
        print(f"   ✓ Created {len(jobs)} test jobs")
        
        # Save jobs
        print("\n3. Saving jobs to storage...")
        result = storage.save_jobs(jobs, source="indeed")
        print(f"   ✓ Added: {result['added']}")
        print(f"   ✓ Skipped: {result['skipped']}")
        print(f"   ✓ Invalid: {result['invalid']}")
        print(f"   ✓ Total: {result['total']}")
        
        # Retrieve jobs
        print("\n4. Retrieving jobs...")
        retrieved = storage.get_all_jobs()
        print(f"   ✓ Retrieved {len(retrieved)} jobs")
        
        # Test duplicate handling
        print("\n5. Testing duplicate detection...")
        dup_result = storage.save_jobs(jobs, source="indeed", skip_duplicates=True)
        print(f"   ✓ Duplicates skipped: {dup_result['skipped']}")
        print(f"   ✓ New jobs added: {dup_result['added']}")
        
        # Test filtering
        print("\n6. Testing job filtering...")
        filtered = storage.get_all_jobs(filters={"source": "indeed"})
        print(f"   ✓ Filtered {len(filtered)} jobs by source='indeed'")
        
        # Test statistics
        print("\n7. Getting storage statistics...")
        stats = storage.get_statistics()
        print(f"   ✓ Total jobs: {stats['total_jobs']}")
        print(f"   ✓ Jobs by source: {stats['jobs_by_source']}")
        
        # Test export
        print("\n8. Testing export...")
        export_file = os.path.join(test_dir, "export_test.json")
        storage.export_to_json(export_file)
        print(f"   ✓ Exported to {export_file}")
        
        # Test deletion
        print("\n9. Testing job deletion...")
        job_to_delete = retrieved[0]['id']
        storage.delete_job(job_to_delete)
        remaining = storage.get_all_jobs()
        print(f"   ✓ Deleted 1 job, {len(remaining)} remaining")
        
        print("\n" + "="*50)
        print("✓ ALL TESTS PASSED")
        print("="*50 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"Cleaned up test directory: {test_dir}")


if __name__ == "__main__":
    success = test_basic_storage()
    sys.exit(0 if success else 1)
