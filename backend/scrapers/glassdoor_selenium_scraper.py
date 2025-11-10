"""
Glassdoor Job Scraper using Selenium
Handles JavaScript-loaded content and dynamic pagination on Glassdoor.com
"""

from typing import List, Dict
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from .selenium_scraper import SeleniumScraper


class GlassdoorSeleniumScraper(SeleniumScraper):
    """Selenium-based scraper for Glassdoor job board"""
    
    def __init__(self, headless: bool = True, user_agent: str = None):
        """Initialize Glassdoor Selenium scraper"""
        super().__init__(headless, user_agent)
        self.base_url = "https://www.glassdoor.com"
        
    def build_search_url(self, job_title: str, location: str, page: int = 0) -> str:
        """
        Build Glassdoor search URL
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            page: Page number (Glassdoor uses page parameter starting from 1)
            
        Returns:
            Complete Glassdoor search URL
        """
        # URL encode the search parameters
        title_encoded = quote_plus(job_title)
        location_encoded = quote_plus(location)
        
        # Glassdoor pagination starts at 1
        page_num = page + 1
        
        # Simplified Glassdoor URL structure
        url = f"{self.base_url}/Job/jobs.htm?sc.keyword={title_encoded}&locT=C&locId=1147401&locKeyword={location_encoded}&jobType=&fromAge=-1&minSalary=0&includeNoSalaryJobs=true&radius=25&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0&page={page_num}"
        return url
    
    def handle_popup(self):
        """
        Handle common popups that Glassdoor shows (login prompts, etc.)
        """
        try:
            # Try to close any modal/popup that might appear
            close_buttons = [
                (By.CSS_SELECTOR, 'button[aria-label="Close"]'),
                (By.CSS_SELECTOR, 'button.modal_closeIcon'),
                (By.CSS_SELECTOR, '.modal_closeIcon'),
                (By.XPATH, "//button[contains(text(), 'Close')]"),
                (By.CLASS_NAME, 'CloseButton')
            ]
            
            for by, selector in close_buttons:
                try:
                    close_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    close_btn.click()
                    print("Closed popup")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    continue
        except Exception as e:
            pass
        
        return False
    
    def extract_jobs(self, soup) -> List[Dict]:
        """
        Extract job listings from Glassdoor page
        
        Args:
            soup: BeautifulSoup object containing Glassdoor page HTML
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Try multiple selectors for job cards (Glassdoor structure varies)
        job_cards = soup.find_all('li', class_='react-job-listing')
        
        if not job_cards:
            job_cards = soup.find_all('li', attrs={'data-test': 'jobListing'})
        
        if not job_cards:
            job_cards = soup.find_all('article', class_='job-listing')
        
        if not job_cards:
            job_cards = soup.find_all('div', class_='jobContainer')
        
        if not job_cards:
            # Try more generic approach
            job_cards = soup.find_all('li', attrs={'class': lambda x: x and 'job' in x.lower()})
        
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
            'source': 'Glassdoor',
            'title': None,
            'company': None,
            'location': None,
            'salary': None,
            'job_type': None,
            'description': None,
            'link': None
        }
        
        # Extract job title and link
        title_elem = card.find('a', class_='job-title')
        if not title_elem:
            title_elem = card.find('a', attrs={'data-test': 'job-link'})
        if not title_elem:
            title_elem = card.find('a', class_='jobLink')
        if not title_elem:
            # Try finding any link with job-related text
            title_elem = card.find('a', attrs={'class': lambda x: x and ('title' in x.lower() or 'job' in x.lower())})
        
        if title_elem:
            job['title'] = self.clean_text(title_elem.get_text())
            href = title_elem.get('href')
            if href:
                job['link'] = f"{self.base_url}{href}" if href.startswith('/') else href
        
        # Alternative: look for job title in other structures
        if not job['title']:
            title_elem = card.find('span', attrs={'class': lambda x: x and 'job' in x.lower() and 'title' in x.lower()})
            if not title_elem:
                title_elem = card.find('h2')
            if title_elem:
                job['title'] = self.clean_text(title_elem.get_text())
        
        # Extract company name
        company_elem = card.find('div', class_='employer-name')
        if not company_elem:
            company_elem = card.find('span', class_='employer-name')
        if not company_elem:
            company_elem = card.find('div', attrs={'data-test': 'employer-name'})
        if not company_elem:
            company_elem = card.find('span', attrs={'data-test': 'employer-name'})
        
        if company_elem:
            job['company'] = self.clean_text(company_elem.get_text())
        
        # Alternative: look for company in link or other structures
        if not job['company']:
            company_link = card.find('a', class_='employer')
            if not company_link:
                company_link = card.find('a', attrs={'class': lambda x: x and 'employer' in x.lower()})
            if company_link:
                job['company'] = self.clean_text(company_link.get_text())
        
        # Extract location
        location_elem = card.find('div', class_='location')
        if not location_elem:
            location_elem = card.find('span', class_='location')
        if not location_elem:
            location_elem = card.find('div', attrs={'data-test': 'emp-location'})
        if not location_elem:
            location_elem = card.find('span', attrs={'data-test': 'emp-location'})
        if not location_elem:
            location_elem = card.find('div', attrs={'class': lambda x: x and 'location' in x.lower()})
        
        if location_elem:
            job['location'] = self.clean_text(location_elem.get_text())
        
        # Extract salary (if available)
        salary_elem = card.find('div', class_='salary')
        if not salary_elem:
            salary_elem = card.find('span', class_='salary-estimate')
        if not salary_elem:
            salary_elem = card.find('span', attrs={'data-test': 'detailSalary'})
        if not salary_elem:
            salary_elem = card.find('div', attrs={'class': lambda x: x and 'salary' in x.lower()})
        
        if salary_elem:
            salary_text = self.clean_text(salary_elem.get_text())
            # Remove "Glassdoor est." prefix if present
            salary_text = salary_text.replace('(Glassdoor est.)', '').replace('Glassdoor est.', '').replace('(Employer est.)', '')
            job['salary'] = self.extract_salary(salary_text)
        
        # Extract job type (Remote, Full-time, etc.)
        job_type_elem = card.find('div', class_='job-type')
        if not job_type_elem:
            job_type_elem = card.find('span', class_='job-type')
        if not job_type_elem:
            job_type_elem = card.find('div', attrs={'data-test': 'job-type'})
        
        if job_type_elem:
            job['job_type'] = self.clean_text(job_type_elem.get_text())
        
        # Check for remote work indicators in badges
        if not job['job_type']:
            badges = card.find_all('span', class_='badge')
            if not badges:
                badges = card.find_all('span', attrs={'class': lambda x: x and 'badge' in x.lower()})
            
            for badge in badges:
                text = self.clean_text(badge.get_text())
                if any(keyword in text.lower() for keyword in 
                      ['remote', 'hybrid', 'onsite', 'full-time', 'part-time', 'contract', 'temporary']):
                    job['job_type'] = text
                    break
        
        # Check text content for job type indicators
        if not job['job_type']:
            card_text = card.get_text().lower()
            if 'remote' in card_text:
                job['job_type'] = 'Remote'
            elif 'hybrid' in card_text:
                job['job_type'] = 'Hybrid'
        
        # Extract job description snippet
        description_elem = card.find('div', class_='job-description')
        if not description_elem:
            description_elem = card.find('div', class_='desc')
        if not description_elem:
            description_elem = card.find('p', class_='job-description')
        if not description_elem:
            description_elem = card.find('div', attrs={'data-test': 'job-description'})
        
        if description_elem:
            job['description'] = self.clean_text(description_elem.get_text())
        else:
            # Try to get any paragraph text as description
            p_elem = card.find('p')
            if p_elem:
                job['description'] = self.clean_text(p_elem.get_text())
        
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
            print(f"Starting Glassdoor scrape: {url}")
            
            # Wait for job listings to load (be more lenient with timeout)
            if not self.get_page(url):
                print("Failed to load initial page")
                return all_jobs
            
            # Handle any popups
            time.sleep(2)
            self.handle_popup()
            
            for page in range(num_pages):
                try:
                    print(f"Scraping page {page + 1}")
                    
                    # Wait a bit for dynamic content
                    time.sleep(2)
                    
                    # Handle popup again if it reappears
                    self.handle_popup()
                    
                    # Scroll to load lazy content
                    self.scroll_page(scroll_pause_time=1.5, num_scrolls=3)
                    
                    # Extract jobs from current page
                    soup = self.get_soup()
                    jobs = self.extract_jobs(soup)
                    
                    if not jobs:
                        print(f"No jobs found on page {page + 1}")
                        # Don't break immediately, might be a temporary issue
                        if page == 0:
                            # Save page source for debugging
                            print("Saving page source for debugging...")
                            with open('/tmp/glassdoor_debug.html', 'w', encoding='utf-8') as f:
                                f.write(soup.prettify())
                        break
                    
                    all_jobs.extend(jobs)
                    print(f"Extracted {len(jobs)} jobs from page {page + 1}")
                    
                    # Try to navigate to next page
                    if page < num_pages - 1:
                        next_clicked = False
                        
                        # Approach 1: Find next button by various selectors
                        next_selectors = [
                            'button[data-test="pagination-next"]',
                            'a[data-test="pagination-next"]',
                            'button.nextButton',
                            'a.nextButton'
                        ]
                        
                        for selector in next_selectors:
                            if self.click_element(By.CSS_SELECTOR, selector):
                                next_clicked = True
                                break
                        
                        # Approach 2: Find by text
                        if not next_clicked:
                            try:
                                next_link = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'next')]")
                                next_link.click()
                                next_clicked = True
                            except:
                                pass
                        
                        # Approach 3: Navigate to next URL directly
                        if not next_clicked:
                            next_url = self.build_search_url(job_title, location, page + 1)
                            if not self.get_page(next_url):
                                print("Could not navigate to next page")
                                break
                            # Handle popup on new page
                            time.sleep(2)
                            self.handle_popup()
                        else:
                            # Wait for new page to load
                            time.sleep(self.get_random_delay())
                            self.handle_popup()
                    
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
            
            if not self.get_page(job_url):
                return details
            
            # Handle popup
            time.sleep(2)
            self.handle_popup()
            
            soup = self.get_soup()
            
            # Extract full job description
            job_desc_elem = soup.find('div', class_='jobDescriptionContent')
            if not job_desc_elem:
                job_desc_elem = soup.find('div', attrs={'data-test': 'jobDescriptionContent'})
            if not job_desc_elem:
                job_desc_elem = soup.find('div', class_='desc')
            
            if job_desc_elem:
                details['full_description'] = self.clean_text(job_desc_elem.get_text())
            
            # Extract additional metadata
            details_section = soup.find('div', class_='job-details')
            if not details_section:
                details_section = soup.find('div', attrs={'data-test': 'job-details'})
            
            if details_section:
                # Look for job type
                job_type_elem = details_section.find('span', string=lambda text: text and 'job type' in text.lower())
                if job_type_elem and job_type_elem.parent:
                    details['job_type'] = self.clean_text(job_type_elem.parent.get_text())
                
                # Look for salary
                salary_elem = details_section.find('span', class_='salary')
                if not salary_elem:
                    salary_elem = details_section.find('div', class_='salary')
                if salary_elem:
                    salary_text = self.clean_text(salary_elem.get_text())
                    details['salary'] = self.extract_salary(salary_text)
        
        finally:
            self.close_driver()
        
        return details
