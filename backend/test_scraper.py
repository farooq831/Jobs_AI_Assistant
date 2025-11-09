"""
Test script for job scrapers
Tests Indeed and Glassdoor scrapers
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.indeed_scraper import IndeedScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
import json


def test_indeed_scraper():
    """Test Indeed scraper functionality"""
    print("\n" + "="*60)
    print("Testing Indeed Scraper")
    print("="*60)
    
    try:
        scraper = IndeedScraper()
        
        # Test with a common job title and location
        job_title = "Software Engineer"
        location = "New York, NY"
        num_pages = 1
        
        print(f"\nSearching for: {job_title}")
        print(f"Location: {location}")
        print(f"Pages: {num_pages}")
        print("\nScraping...")
        
        jobs = scraper.scrape_jobs(job_title, location, num_pages)
        
        print(f"\n✓ Successfully scraped {len(jobs)} jobs from Indeed")
        
        if jobs:
            print("\n" + "-"*60)
            print("Sample Job (First Result):")
            print("-"*60)
            print(json.dumps(jobs[0], indent=2))
            
            # Validate job data
            print("\n" + "-"*60)
            print("Data Validation:")
            print("-"*60)
            valid_jobs = [job for job in jobs if scraper.validate_job_data(job)]
            print(f"Valid jobs: {len(valid_jobs)}/{len(jobs)}")
            
            # Check fields
            fields_check = {
                'title': 0,
                'company': 0,
                'location': 0,
                'salary': 0,
                'job_type': 0,
                'description': 0,
                'link': 0
            }
            
            for job in jobs:
                for field in fields_check:
                    if job.get(field):
                        fields_check[field] += 1
            
            print("\nField coverage:")
            for field, count in fields_check.items():
                percentage = (count / len(jobs)) * 100 if jobs else 0
                print(f"  {field}: {count}/{len(jobs)} ({percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing Indeed scraper: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_glassdoor_scraper():
    """Test Glassdoor scraper functionality"""
    print("\n" + "="*60)
    print("Testing Glassdoor Scraper")
    print("="*60)
    
    try:
        scraper = GlassdoorScraper()
        
        # Test with a common job title and location
        job_title = "Data Analyst"
        location = "San Francisco, CA"
        num_pages = 1
        
        print(f"\nSearching for: {job_title}")
        print(f"Location: {location}")
        print(f"Pages: {num_pages}")
        print("\nScraping...")
        
        jobs = scraper.scrape_jobs(job_title, location, num_pages)
        
        print(f"\n✓ Successfully scraped {len(jobs)} jobs from Glassdoor")
        
        if jobs:
            print("\n" + "-"*60)
            print("Sample Job (First Result):")
            print("-"*60)
            print(json.dumps(jobs[0], indent=2))
            
            # Validate job data
            print("\n" + "-"*60)
            print("Data Validation:")
            print("-"*60)
            valid_jobs = [job for job in jobs if scraper.validate_job_data(job)]
            print(f"Valid jobs: {len(valid_jobs)}/{len(jobs)}")
            
            # Check fields
            fields_check = {
                'title': 0,
                'company': 0,
                'location': 0,
                'salary': 0,
                'job_type': 0,
                'description': 0,
                'link': 0
            }
            
            for job in jobs:
                for field in fields_check:
                    if job.get(field):
                        fields_check[field] += 1
            
            print("\nField coverage:")
            for field, count in fields_check.items():
                percentage = (count / len(jobs)) * 100 if jobs else 0
                print(f"  {field}: {count}/{len(jobs)} ({percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing Glassdoor scraper: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """Test the Flask API endpoint"""
    print("\n" + "="*60)
    print("Testing API Endpoint")
    print("="*60)
    
    try:
        import requests
        
        # Check if server is running
        try:
            response = requests.get('http://localhost:5000/health', timeout=2)
            print("✓ Server is running")
        except requests.exceptions.RequestException:
            print("✗ Server is not running. Start the server with: python backend/app.py")
            return False
        
        # Test scraping endpoint
        payload = {
            "job_titles": ["Python Developer"],
            "location": "Boston, MA",
            "num_pages": 1,
            "sources": ["indeed"]
        }
        
        print(f"\nTesting POST /api/scrape-jobs")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            'http://localhost:5000/api/scrape-jobs',
            json=payload,
            timeout=60
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✓ API endpoint working")
            print(f"  Scraped {result.get('total_jobs', 0)} jobs")
            print(f"  Scrape ID: {result.get('scrape_id')}")
            
            # Test GET endpoint
            scrape_id = result.get('scrape_id')
            if scrape_id:
                print(f"\nTesting GET /api/scrape-jobs/{scrape_id}")
                get_response = requests.get(f'http://localhost:5000/api/scrape-jobs/{scrape_id}')
                if get_response.status_code == 200:
                    print("✓ GET endpoint working")
                else:
                    print(f"✗ GET endpoint failed: {get_response.status_code}")
            
            return True
        else:
            print(f"✗ API endpoint failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n✗ Error testing API endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("JOB SCRAPER TEST SUITE")
    print("="*60)
    
    results = {
        'indeed': False,
        'glassdoor': False,
        'api': False
    }
    
    # Run tests
    results['indeed'] = test_indeed_scraper()
    results['glassdoor'] = test_glassdoor_scraper()
    results['api'] = test_api_endpoint()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name.capitalize()}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
