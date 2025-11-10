#!/usr/bin/env python3
"""
Test script for Selenium-based job scrapers
Tests dynamic scraping functionality with Indeed and Glassdoor
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from scrapers.indeed_selenium_scraper import IndeedSeleniumScraper
from scrapers.glassdoor_selenium_scraper import GlassdoorSeleniumScraper
import json


def test_indeed_selenium():
    """Test Indeed scraper with Selenium"""
    print("\n" + "="*60)
    print("Testing Indeed Selenium Scraper")
    print("="*60)
    
    try:
        scraper = IndeedSeleniumScraper(headless=True)
        
        print("\nTest 1: Scraping 'Software Engineer' jobs in 'New York'")
        jobs = scraper.scrape_jobs("Software Engineer", "New York", num_pages=1)
        
        print(f"\nResults: Found {len(jobs)} jobs")
        
        if jobs:
            print("\nSample job (first result):")
            print(json.dumps(jobs[0], indent=2, default=str))
            
            # Validate job structure
            required_fields = ['title', 'company', 'location', 'link', 'source']
            missing_fields = [field for field in required_fields if field not in jobs[0]]
            
            if missing_fields:
                print(f"\n⚠️  Warning: Missing fields in job data: {missing_fields}")
            else:
                print("\n✓ All required fields present")
        else:
            print("\n⚠️  Warning: No jobs found. This could be due to:")
            print("   - Rate limiting")
            print("   - Website structure changes")
            print("   - ChromeDriver not installed/configured properly")
        
        return len(jobs) > 0
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_glassdoor_selenium():
    """Test Glassdoor scraper with Selenium"""
    print("\n" + "="*60)
    print("Testing Glassdoor Selenium Scraper")
    print("="*60)
    
    try:
        scraper = GlassdoorSeleniumScraper(headless=True)
        
        print("\nTest 1: Scraping 'Data Scientist' jobs in 'San Francisco'")
        jobs = scraper.scrape_jobs("Data Scientist", "San Francisco", num_pages=1)
        
        print(f"\nResults: Found {len(jobs)} jobs")
        
        if jobs:
            print("\nSample job (first result):")
            print(json.dumps(jobs[0], indent=2, default=str))
            
            # Validate job structure
            required_fields = ['title', 'company', 'location', 'link', 'source']
            missing_fields = [field for field in required_fields if field not in jobs[0]]
            
            if missing_fields:
                print(f"\n⚠️  Warning: Missing fields in job data: {missing_fields}")
            else:
                print("\n✓ All required fields present")
        else:
            print("\n⚠️  Warning: No jobs found. This could be due to:")
            print("   - Rate limiting")
            print("   - Website structure changes")
            print("   - ChromeDriver not installed/configured properly")
            print("   - Glassdoor popup/login prompts")
        
        return len(jobs) > 0
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_pagination():
    """Test pagination functionality"""
    print("\n" + "="*60)
    print("Testing Pagination with Indeed")
    print("="*60)
    
    try:
        scraper = IndeedSeleniumScraper(headless=True)
        
        print("\nScraping 2 pages of 'Python Developer' jobs in 'Boston'")
        jobs = scraper.scrape_jobs("Python Developer", "Boston", num_pages=2)
        
        print(f"\nResults: Found {len(jobs)} jobs across 2 pages")
        
        if len(jobs) > 10:
            print("✓ Pagination appears to be working (found > 10 jobs)")
            return True
        else:
            print("⚠️  Warning: Pagination might not be working correctly")
            return False
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_anti_blocking():
    """Test anti-blocking mechanisms"""
    print("\n" + "="*60)
    print("Testing Anti-Blocking Mechanisms")
    print("="*60)
    
    try:
        print("\nTesting user agent rotation...")
        scraper1 = IndeedSeleniumScraper(headless=True)
        scraper2 = IndeedSeleniumScraper(headless=True)
        
        if scraper1.user_agent != scraper2.user_agent:
            print("✓ User agents are being rotated")
            print(f"  UA1: {scraper1.user_agent[:50]}...")
            print(f"  UA2: {scraper2.user_agent[:50]}...")
        else:
            print("⚠️  User agents might not be rotating")
        
        print("\nTesting random delays...")
        import time
        delays = []
        for i in range(5):
            start = time.time()
            delay = scraper1.get_random_delay()
            delays.append(delay)
        
        if len(set(delays)) > 1:
            print(f"✓ Delays are random: {delays}")
        else:
            print("⚠️  Delays might not be randomized properly")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_api_endpoint():
    """Test the Flask API endpoint for Selenium scraping"""
    print("\n" + "="*60)
    print("Testing Flask API Endpoint")
    print("="*60)
    
    try:
        import requests
        
        print("\nTesting /api/scrape-jobs-dynamic endpoint...")
        
        payload = {
            "job_titles": ["Frontend Developer"],
            "location": "Austin, TX",
            "num_pages": 1,
            "sources": ["indeed"],
            "headless": True
        }
        
        # Note: This assumes Flask server is running on port 5000
        response = requests.post("http://localhost:5000/api/scrape-jobs-dynamic", json=payload)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ API endpoint working!")
            print(f"  Total jobs: {data.get('total_jobs', 0)}")
            print(f"  Scrape ID: {data.get('scrape_id', 'N/A')}")
            return True
        else:
            print(f"⚠️  API returned status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("⚠️  Flask server not running. Start it with: python backend/app.py")
        return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*15 + "SELENIUM SCRAPER TEST SUITE")
    print("="*70)
    
    print("\nThis test suite will:")
    print("1. Test Indeed Selenium scraper")
    print("2. Test Glassdoor Selenium scraper")
    print("3. Test pagination functionality")
    print("4. Test anti-blocking mechanisms")
    print("5. Test Flask API endpoint (if server is running)")
    
    print("\n⚠️  Note: These tests require:")
    print("   - Chrome/Chromium browser installed")
    print("   - ChromeDriver installed and in PATH")
    print("   - Internet connection")
    print("   - Tests may be slow (respecting rate limits)")
    
    input("\nPress Enter to continue...")
    
    results = {
        "Indeed Selenium": test_indeed_selenium(),
        "Glassdoor Selenium": test_glassdoor_selenium(),
        "Pagination": test_pagination(),
        "Anti-Blocking": test_anti_blocking(),
        "API Endpoint": test_api_endpoint()
    }
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<50} {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print("\n" + "="*70)
    print(f"Tests Passed: {passed_count}/{total_count}")
    print("="*70)
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        print("\nCommon issues:")
        print("- ChromeDriver not installed: Install with 'sudo apt install chromium-chromedriver'")
        print("- Rate limiting: Wait a few minutes and try again")
        print("- Website changes: Scrapers may need updating")
        return 1


if __name__ == "__main__":
    sys.exit(main())
