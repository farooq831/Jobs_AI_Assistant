"""
Indeed Job Scraper using Selenium
Handles JavaScript-loaded content and dynamic pagination on Indeed.com
"""

from typing import List, Dict
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .selenium_scraper import SeleniumScraper


class IndeedSeleniumScraper(SeleniumScraper):
    """Selenium-based scraper for Indeed job board"""
    
    def __init__(self, headless: bool = True, user_agent: str = None):
        """Initialize Indeed Selenium scraper"""
        super().__init__(headless, user_agent)
        self.base_url = "https://www.indeed.com"
        
    def build_search_url(self, job_title: str, location: str, page: int = 0) -> str:
        """
        Build Indeed search URL
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            page: Page number (Indeed uses start parameter, 10 jobs per page)
            
        Returns:
            Complete Indeed search URL
        """
        # URL encode the search parameters
        title_encoded = quote_plus(job_title)
        location_encoded = quote_plus(location)
        
        # Indeed uses 'start' parameter for pagination (0, 10, 20, etc.)
        start = page * 10
        
        url = f"{self.base_url}/jobs?q={title_encoded}&l={location_encoded}&start={start}"
        return url
    
    def extract_jobs(self, soup) -> List[Dict]:
        """
        Extract job listings from Indeed page
        
        Args:
            soup: BeautifulSoup object containing Indeed page HTML
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Try multiple selectors for job cards (Indeed structure can vary)
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        if not job_cards:
            job_cards = soup.find_all('div', class_='cardOutline')
        
        if not job_cards:
            job_cards = soup.find_all('td', class_='resultContent')
        
        if not job_cards:
            # Try with data attributes
            job_cards = soup.find_all('div', attrs={'data-jk': True})
        
        for card in job_cards:
            try:
                job_data = self._extract_job_from_card(card)
                if job_data and self.validate_job_data(job_data):
                    jobs.append(job_data)
            except Exception as e:
                print(f"Error extracting job from card: {str(e)}")
                continue
        
        return jobs
    
    def _extract_job_from_card(self, card) -> Dict:
        """
        Extract job information from a single job card
        
        Args:
            card: BeautifulSoup element containing job card
            
        Returns:
            Dictionary with job information
        """
        job = {
            'source': 'Indeed',
            'title': None,
            'company': None,
            'location': None,
            'salary': None,
            'job_type': None,
            'description': None,
            'link': None
        }
        
        # Extract job title and link
        title_elem = card.find('h2', class_='jobTitle')
        if not title_elem:
            title_elem = card.find('a', class_='jcs-JobTitle')
        if not title_elem:
            title_elem = card.find('h2', attrs={'class': lambda x: x and 'jobTitle' in x})
        
        if title_elem:
            # The title might be in an anchor tag
            anchor = title_elem.find('a') if title_elem.name != 'a' else title_elem
            if anchor:
                job['title'] = self.clean_text(anchor.get_text())
                
                # Try to get job key from data attribute
                job_key = anchor.get('data-jk')
                if not job_key:
                    # Try getting from id
                    job_id = anchor.get('id', '')
                    job_key = job_id.replace('job_', '') if 'job_' in job_id else None
                
                if job_key:
                    job['link'] = f"{self.base_url}/viewjob?jk={job_key}"
                elif anchor.get('href'):
                    href = anchor.get('href')
                    job['link'] = f"{self.base_url}{href}" if href.startswith('/') else href
            else:
                job['title'] = self.clean_text(title_elem.get_text())
        
        # If still no title, try other approaches
        if not job['title']:
            span_title = card.find('span', attrs={'title': True})
            if span_title:
                job['title'] = self.clean_text(span_title.get('title'))
        
        # Extract company name
        company_elem = card.find('span', class_='companyName')
        if not company_elem:
            company_elem = card.find('span', attrs={'data-testid': 'company-name'})
        if not company_elem:
            company_elem = card.find('span', attrs={'class': lambda x: x and 'company' in x.lower()})
        if company_elem:
            job['company'] = self.clean_text(company_elem.get_text())
        
        # Extract location
        location_elem = card.find('div', class_='companyLocation')
        if not location_elem:
            location_elem = card.find('div', attrs={'data-testid': 'text-location'})
        if not location_elem:
            location_elem = card.find('div', attrs={'class': lambda x: x and 'location' in x.lower()})
        if location_elem:
            job['location'] = self.clean_text(location_elem.get_text())
        
        # Extract salary (if available)
        salary_elem = card.find('div', class_='salary-snippet')
        if not salary_elem:
            salary_elem = card.find('div', attrs={'data-testid': 'attribute_snippet_testid'})
        if not salary_elem:
            salary_elem = card.find('div', attrs={'class': lambda x: x and 'salary' in x.lower()})
        
        if salary_elem:
            salary_text = self.clean_text(salary_elem.get_text())
            job['salary'] = self.extract_salary(salary_text)
        
        # Extract job type (Remote, Full-time, etc.)
        metadata_elems = card.find_all('div', class_='metadata')
        if not metadata_elems:
            metadata_elems = card.find_all('div', attrs={'class': lambda x: x and 'metadata' in x.lower()})
        
        job_type_parts = []
        for elem in metadata_elems:
            text = self.clean_text(elem.get_text())
            if text and any(keyword in text.lower() for keyword in 
                          ['remote', 'onsite', 'hybrid', 'full-time', 'part-time', 'contract', 'temporary']):
                job_type_parts.append(text)
        
        if job_type_parts:
            job['job_type'] = ', '.join(job_type_parts)
        
        # Try to find job type in other locations
        if not job['job_type']:
            # Check for remote/onsite indicators in attributes
            attributes = card.find_all('div', attrs={'data-testid': lambda x: x and 'attribute' in x.lower()})
            for attr in attributes:
                text = self.clean_text(attr.get_text()).lower()
                if 'remote' in text:
                    job['job_type'] = 'Remote'
                    break
                elif 'hybrid' in text:
                    job['job_type'] = 'Hybrid'
                    break
        
        # Extract job description snippet
        description_elem = card.find('div', class_='job-snippet')
        if not description_elem:
            description_elem = card.find('div', attrs={'data-testid': 'job-snippet'})
        if not description_elem:
            description_elem = card.find('ul', class_='job-snippet')
        
        if description_elem:
            # Remove any nested li elements that contain metadata
            for li in description_elem.find_all('li'):
                if any(keyword in li.get_text().lower() for keyword in ['posted', 'employer active']):
                    li.decompose()
            job['description'] = self.clean_text(description_elem.get_text())
        
        return job
    
    def scrape_with_pagination(self, job_title: str, location: str, num_pages: int = 1) -> List[Dict]:
        """
        Scrape jobs with dynamic pagination support
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            num_pages: Number of pages to scrape
            
        Returns:
            List of job dictionaries
        """
        all_jobs = []
        
        try:
            self.start_driver()
            
            # Navigate to first page
            url = self.build_search_url(job_title, location, 0)
            print(f"Starting Indeed scrape: {url}")
            
            if not self.get_page(url, wait_for_element=(By.CSS_SELECTOR, 'div.job_seen_beacon, div[data-jk]')):
                print("Failed to load initial page")
                return all_jobs
            
            for page in range(num_pages):
                try:
                    print(f"Scraping page {page + 1}")
                    
                    # Scroll to load lazy content
                    self.scroll_page(scroll_pause_time=1.5, num_scrolls=2)
                    
                    # Extract jobs from current page
                    soup = self.get_soup()
                    jobs = self.extract_jobs(soup)
                    
                    if not jobs:
                        print(f"No jobs found on page {page + 1}")
                        break
                    
                    all_jobs.extend(jobs)
                    print(f"Extracted {len(jobs)} jobs from page {page + 1}")
                    
                    # Try to navigate to next page
                    if page < num_pages - 1:
                        # Indeed uses pagination links at bottom
                        # Try different approaches to find and click next button
                        next_clicked = False
                        
                        # Approach 1: Find by aria-label
                        if self.click_element(By.CSS_SELECTOR, 'a[aria-label="Next Page"], a[data-testid="pagination-page-next"]'):
                            next_clicked = True
                        
                        # Approach 2: Find by text
                        if not next_clicked:
                            try:
                                next_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Next')]")
                                next_link.click()
                                next_clicked = True
                            except:
                                pass
                        
                        # Approach 3: Navigate to next URL directly
                        if not next_clicked:
                            next_url = self.build_search_url(job_title, location, page + 1)
                            if not self.get_page(next_url, wait_for_element=(By.CSS_SELECTOR, 'div.job_seen_beacon, div[data-jk]')):
                                print("Could not navigate to next page")
                                break
                        else:
                            # Wait for new page to load
                            import time
                            time.sleep(self.get_random_delay())
                    
                except Exception as e:
                    print(f"Error on page {page + 1}: {str(e)}")
                    continue
        
        finally:
            self.close_driver()
        
        return all_jobs
    
    def get_job_details(self, job_url: str) -> Dict:
        """
        Fetch full job details from a job posting URL using Selenium
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary with detailed job information
        """
        details = {}
        
        try:
            self.start_driver()
            
            if not self.get_page(job_url, wait_for_element=(By.ID, 'jobDescriptionText')):
                return details
            
            soup = self.get_soup()
            
            # Extract full job description
            job_desc_elem = soup.find('div', id='jobDescriptionText')
            if job_desc_elem:
                details['full_description'] = self.clean_text(job_desc_elem.get_text())
            
            # Extract additional metadata
            job_meta = soup.find('div', id='jobDetailsSection')
            if job_meta:
                meta_items = job_meta.find_all('div')
                for item in meta_items:
                    text = self.clean_text(item.get_text())
                    if 'job type' in text.lower():
                        details['job_type'] = text.split(':', 1)[1].strip() if ':' in text else text
                    elif 'salary' in text.lower():
                        salary_text = text.split(':', 1)[1].strip() if ':' in text else text
                        details['salary'] = self.extract_salary(salary_text)
        
        finally:
            self.close_driver()
        
        return details
