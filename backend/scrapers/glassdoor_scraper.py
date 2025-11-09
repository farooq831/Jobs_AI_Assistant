"""
Glassdoor Job Scraper
Scrapes job listings from Glassdoor.com
"""

from typing import List, Dict
from urllib.parse import quote_plus
from .base_scraper import BaseScraper


class GlassdoorScraper(BaseScraper):
    """Scraper for Glassdoor job board"""
    
    def __init__(self):
        """Initialize Glassdoor scraper"""
        super().__init__()
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
        
        url = f"{self.base_url}/Job/jobs.htm?sc.keyword={title_encoded}&locT=C&locId={location_encoded}&jobType=&fromAge=-1&minSalary=0&includeNoSalaryJobs=true&radius=25&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0&page={page_num}"
        return url
    
    def extract_jobs(self, soup) -> List[Dict]:
        """
        Extract job listings from Glassdoor page
        
        Args:
            soup: BeautifulSoup object containing Glassdoor page HTML
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Glassdoor's structure - trying multiple selectors
        # Glassdoor uses a list structure for job cards
        job_cards = soup.find_all('li', class_='react-job-listing')
        
        if not job_cards:
            # Alternative selector
            job_cards = soup.find_all('li', {'data-test': 'jobListing'})
        
        if not job_cards:
            # Try finding job cards by article tag
            job_cards = soup.find_all('article', class_='job-listing')
        
        if not job_cards:
            # Try finding divs with job-related classes
            job_cards = soup.find_all('div', class_='jobContainer')
        
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
            title_elem = card.find('a', {'data-test': 'job-link'})
        if not title_elem:
            title_elem = card.find('a', class_='jobLink')
        
        if title_elem:
            job['title'] = self.clean_text(title_elem.get_text())
            href = title_elem.get('href')
            if href:
                job['link'] = f"{self.base_url}{href}" if href.startswith('/') else href
        
        # Alternative: look for job title in other structures
        if not job['title']:
            title_elem = card.find('span', class_='job-title')
            if title_elem:
                job['title'] = self.clean_text(title_elem.get_text())
        
        # Extract company name
        company_elem = card.find('div', class_='employer-name')
        if not company_elem:
            company_elem = card.find('span', class_='employer-name')
        if not company_elem:
            company_elem = card.find('div', {'data-test': 'employer-name'})
        if company_elem:
            job['company'] = self.clean_text(company_elem.get_text())
        
        # Alternative: look for company in link or span
        if not job['company']:
            company_link = card.find('a', class_='employer')
            if company_link:
                job['company'] = self.clean_text(company_link.get_text())
        
        # Extract location
        location_elem = card.find('div', class_='location')
        if not location_elem:
            location_elem = card.find('span', class_='location')
        if not location_elem:
            location_elem = card.find('div', {'data-test': 'emp-location'})
        if location_elem:
            job['location'] = self.clean_text(location_elem.get_text())
        
        # Extract salary (if available)
        salary_elem = card.find('div', class_='salary')
        if not salary_elem:
            salary_elem = card.find('span', class_='salary-estimate')
        if not salary_elem:
            salary_elem = card.find('span', {'data-test': 'detailSalary'})
        
        if salary_elem:
            salary_text = self.clean_text(salary_elem.get_text())
            # Remove "Glassdoor est." prefix if present
            salary_text = salary_text.replace('(Glassdoor est.)', '').replace('Glassdoor est.', '')
            job['salary'] = self.extract_salary(salary_text)
        
        # Extract job type (Remote, Full-time, etc.)
        job_type_elem = card.find('div', class_='job-type')
        if not job_type_elem:
            job_type_elem = card.find('span', class_='job-type')
        if job_type_elem:
            job['job_type'] = self.clean_text(job_type_elem.get_text())
        
        # Check for remote work indicators
        if not job['job_type']:
            # Look for badges or tags
            badges = card.find_all('span', class_='badge')
            for badge in badges:
                text = self.clean_text(badge.get_text())
                if any(keyword in text.lower() for keyword in ['remote', 'hybrid', 'onsite', 'full-time', 'part-time', 'contract']):
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
        
        if description_elem:
            job['description'] = self.clean_text(description_elem.get_text())
        else:
            # Try to get any paragraph text as description
            p_elem = card.find('p')
            if p_elem:
                job['description'] = self.clean_text(p_elem.get_text())
        
        return job
    
    def get_job_details(self, job_url: str) -> Dict:
        """
        Fetch full job details from a job posting URL
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary with detailed job information
        """
        response = self.make_request(job_url)
        
        if not response:
            return {}
        
        soup = self.parse_html(response.text)
        
        details = {}
        
        # Extract full job description
        job_desc_elem = soup.find('div', class_='jobDescriptionContent')
        if not job_desc_elem:
            job_desc_elem = soup.find('div', {'data-test': 'jobDescriptionContent'})
        if job_desc_elem:
            details['full_description'] = self.clean_text(job_desc_elem.get_text())
        
        # Extract additional metadata
        # Glassdoor shows job details in various sections
        details_section = soup.find('div', class_='job-details')
        if details_section:
            # Look for job type
            job_type_elem = details_section.find('span', string=lambda text: text and 'job type' in text.lower())
            if job_type_elem and job_type_elem.parent:
                details['job_type'] = self.clean_text(job_type_elem.parent.get_text())
            
            # Look for salary
            salary_elem = details_section.find('span', class_='salary')
            if salary_elem:
                salary_text = self.clean_text(salary_elem.get_text())
                details['salary'] = self.extract_salary(salary_text)
        
        return details
