"""
Selenium-based Scraper for Dynamic Content
Handles JavaScript-loaded content, pagination, and anti-blocking mechanisms
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class SeleniumScraper(ABC):
    """Abstract base class for Selenium-based job scrapers"""
    
    # User agents for rotation to avoid detection
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    def __init__(self, headless: bool = True, user_agent: Optional[str] = None):
        """
        Initialize the Selenium scraper
        
        Args:
            headless: Whether to run browser in headless mode
            user_agent: Custom user agent (if None, will rotate from list)
        """
        self.headless = headless
        self.user_agent = user_agent or random.choice(self.USER_AGENTS)
        self.driver = None
        self.min_delay = 2  # Minimum delay between requests (seconds)
        self.max_delay = 5  # Maximum delay between requests (seconds)
        self.page_load_timeout = 30  # Maximum time to wait for page load
        self.element_timeout = 10  # Maximum time to wait for elements
        
    def get_random_delay(self) -> float:
        """Generate a random delay to avoid detection"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def _setup_driver(self) -> webdriver.Chrome:
        """
        Setup and configure Chrome WebDriver with anti-blocking measures
        
        Returns:
            Configured Chrome WebDriver instance
        """
        chrome_options = Options()
        
        # Anti-detection measures
        if self.headless:
            chrome_options.add_argument('--headless=new')  # Use new headless mode
        
        chrome_options.add_argument(f'user-agent={self.user_agent}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Performance and stability options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-popup-blocking')
        
        # Privacy options
        chrome_options.add_argument('--incognito')
        
        # Language preferences
        chrome_options.add_argument('--lang=en-US,en;q=0.9')
        chrome_options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en-US,en'
        })
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            driver.set_page_load_timeout(self.page_load_timeout)
            driver.implicitly_wait(self.element_timeout)
            
            return driver
        except WebDriverException as e:
            raise Exception(f"Failed to initialize Chrome WebDriver: {str(e)}. "
                          "Make sure Chrome/Chromium and chromedriver are installed.")
    
    def start_driver(self):
        """Start the WebDriver"""
        if self.driver is None:
            self.driver = self._setup_driver()
    
    def close_driver(self):
        """Close the WebDriver and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing driver: {str(e)}")
            finally:
                self.driver = None
    
    def get_page(self, url: str, wait_for_element: Optional[tuple] = None, max_retries: int = 3) -> bool:
        """
        Navigate to a URL and optionally wait for an element to load
        
        Args:
            url: The URL to navigate to
            wait_for_element: Tuple of (By.METHOD, 'selector') to wait for
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                
                # Add random delay to simulate human behavior
                time.sleep(random.uniform(1, 3))
                
                # Wait for specific element if provided
                if wait_for_element:
                    WebDriverWait(self.driver, self.element_timeout).until(
                        EC.presence_of_element_located(wait_for_element)
                    )
                
                return True
                
            except TimeoutException:
                print(f"Timeout loading page (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(self.get_random_delay())
            except WebDriverException as e:
                print(f"WebDriver error: {str(e)} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(self.get_random_delay())
        
        return False
    
    def scroll_page(self, scroll_pause_time: float = 1.0, num_scrolls: int = 3):
        """
        Scroll the page to load lazy-loaded content
        
        Args:
            scroll_pause_time: Time to wait between scrolls
            num_scrolls: Number of scroll actions to perform
        """
        for i in range(num_scrolls):
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            
            # Scroll up a bit (more human-like)
            if i < num_scrolls - 1:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
                time.sleep(scroll_pause_time * 0.5)
    
    def click_element(self, by: By, selector: str, timeout: int = 10) -> bool:
        """
        Click an element after waiting for it to be clickable
        
        Args:
            by: Selenium By locator type
            selector: Element selector
            timeout: Maximum time to wait
            
        Returns:
            True if successful, False otherwise
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            element.click()
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error clicking element {selector}: {str(e)}")
            return False
    
    def get_soup(self) -> BeautifulSoup:
        """
        Get BeautifulSoup object from current page source
        
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(self.driver.page_source, 'lxml')
    
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
        cleaned = salary_text.replace('$', '').replace(',', '').replace('K', '000').replace('k', '000')
        
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
    
    def handle_pagination(self, next_button_selector: tuple, max_pages: int = 5) -> List[BeautifulSoup]:
        """
        Handle pagination by clicking next button and collecting page sources
        
        Args:
            next_button_selector: Tuple of (By.METHOD, 'selector') for next button
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of BeautifulSoup objects for each page
        """
        pages = []
        current_page = 1
        
        while current_page <= max_pages:
            # Get current page content
            pages.append(self.get_soup())
            print(f"Scraped page {current_page}")
            
            if current_page >= max_pages:
                break
            
            # Try to click next button
            if not self.click_element(next_button_selector[0], next_button_selector[1]):
                print("No more pages or next button not found")
                break
            
            # Wait for page to load
            time.sleep(self.get_random_delay())
            
            current_page += 1
        
        return pages
    
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
        Main method to scrape jobs from the job board using Selenium
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            num_pages: Number of pages to scrape
            
        Returns:
            List of job dictionaries
        """
        all_jobs = []
        
        try:
            # Start the driver
            self.start_driver()
            
            for page in range(num_pages):
                try:
                    # Build search URL
                    url = self.build_search_url(job_title, location, page)
                    print(f"Scraping page {page + 1}: {url}")
                    
                    # Navigate to page
                    if not self.get_page(url):
                        print(f"Failed to load page {page + 1}")
                        continue
                    
                    # Scroll to load dynamic content
                    self.scroll_page()
                    
                    # Get page content
                    soup = self.get_soup()
                    
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
        
        finally:
            # Always close the driver
            self.close_driver()
        
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
    
    def __enter__(self):
        """Context manager entry"""
        self.start_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_driver()
