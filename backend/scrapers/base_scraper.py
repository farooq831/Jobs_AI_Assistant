"""
Base Scraper Class
Provides common functionality for all job board scrapers
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Abstract base class for job scrapers"""
    
    def __init__(self):
        """Initialize the scraper with common settings"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.min_delay = 2  # Minimum delay between requests (seconds)
        self.max_delay = 5  # Maximum delay between requests (seconds)
        
    def get_random_delay(self) -> float:
        """Generate a random delay to avoid detection"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """
        Make an HTTP request with retries and error handling
        
        Args:
            url: The URL to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response object or None if failed
        """
        for attempt in range(max_retries):
            try:
                # Add random delay between requests
                if attempt > 0:
                    time.sleep(self.get_random_delay())
                
                response = self.session.get(url, headers=self.headers, timeout=10)
                
                # Check if request was successful
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limited, wait longer
                    wait_time = (attempt + 1) * 10
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Request failed with status code: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"Request timeout (attempt {attempt + 1}/{max_retries})")
            except requests.exceptions.RequestException as e:
                print(f"Request error: {str(e)} (attempt {attempt + 1}/{max_retries})")
            
            # Wait before retry
            if attempt < max_retries - 1:
                time.sleep(self.get_random_delay())
        
        return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html_content, 'lxml')
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text data
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        return text.strip()
    
    def extract_salary(self, salary_text: str) -> Dict[str, Optional[int]]:
        """
        Extract salary information from text
        
        Args:
            salary_text: Text containing salary information
            
        Returns:
            Dictionary with min and max salary values
        """
        import re
        
        if not salary_text:
            return {"min": None, "max": None, "raw": None}
        
        # Remove common currency symbols and text
        cleaned = salary_text.replace('$', '').replace(',', '').replace('K', '000')
        
        # Try to find salary ranges (e.g., "50000-80000" or "50-80K")
        range_pattern = r'(\d+)\s*[-–to]\s*(\d+)'
        range_match = re.search(range_pattern, cleaned, re.IGNORECASE)
        
        if range_match:
            min_sal = int(range_match.group(1))
            max_sal = int(range_match.group(2))
            return {"min": min_sal, "max": max_sal, "raw": salary_text}
        
        # Try to find single salary value
        single_pattern = r'(\d{4,})'
        single_match = re.search(single_pattern, cleaned)
        
        if single_match:
            salary = int(single_match.group(1))
            return {"min": salary, "max": salary, "raw": salary_text}
        
        return {"min": None, "max": None, "raw": salary_text}
    
    @abstractmethod
    def build_search_url(self, job_title: str, location: str, page: int = 0) -> str:
        """
        Build the search URL for the job board
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            page: Page number for pagination
            
        Returns:
            Complete search URL
        """
        pass
    
    @abstractmethod
    def extract_jobs(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract job listings from parsed HTML
        
        Args:
            soup: BeautifulSoup object containing page HTML
            
        Returns:
            List of job dictionaries with extracted information
        """
        pass
    
    def scrape_jobs(self, job_title: str, location: str, num_pages: int = 1) -> List[Dict]:
        """
        Main method to scrape jobs from the job board
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            num_pages: Number of pages to scrape
            
        Returns:
            List of job dictionaries
        """
        all_jobs = []
        
        for page in range(num_pages):
            try:
                # Build search URL
                url = self.build_search_url(job_title, location, page)
                print(f"Scraping page {page + 1}: {url}")
                
                # Make request
                response = self.make_request(url)
                
                if response is None:
                    print(f"Failed to fetch page {page + 1}")
                    continue
                
                # Parse HTML
                soup = self.parse_html(response.text)
                
                # Extract jobs
                jobs = self.extract_jobs(soup)
                
                if not jobs:
                    print(f"No jobs found on page {page + 1}")
                    break
                
                all_jobs.extend(jobs)
                print(f"Extracted {len(jobs)} jobs from page {page + 1}")
                
                # Add delay between pages
                if page < num_pages - 1:
                    time.sleep(self.get_random_delay())
                    
            except Exception as e:
                print(f"Error scraping page {page + 1}: {str(e)}")
                continue
        
        return all_jobs
    
    def validate_job_data(self, job: Dict) -> bool:
        """
        Validate that a job dictionary has required fields
        
        Args:
            job: Job dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['title', 'company', 'location', 'link']
        return all(field in job and job[field] for field in required_fields)
