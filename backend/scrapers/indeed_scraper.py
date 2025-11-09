"""
Indeed Job Scraper
Scrapes job listings from Indeed.com
"""

from typing import List, Dict
from urllib.parse import quote_plus
from .base_scraper import BaseScraper


class IndeedScraper(BaseScraper):
    """Scraper for Indeed job board"""
    
    def __init__(self):
        """Initialize Indeed scraper"""
        super().__init__()
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
        
        # Indeed uses mosaic-provider-jobcards container for job listings
        # The structure can vary, so we'll try multiple selectors
        
        # Try to find job cards (Indeed's main job listing container)
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        if not job_cards:
            # Alternative selector
            job_cards = soup.find_all('div', class_='cardOutline')
        
        if not job_cards:
            # Another alternative - try table-based layout
            job_cards = soup.find_all('td', class_='resultContent')
        
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
        
        if title_elem:
            # The title might be in an anchor tag
            anchor = title_elem.find('a') if title_elem.name != 'a' else title_elem
            if anchor:
                job['title'] = self.clean_text(anchor.get_text())
                job_key = anchor.get('data-jk') or anchor.get('id', '').replace('job_', '')
                if job_key:
                    job['link'] = f"{self.base_url}/viewjob?jk={job_key}"
                elif anchor.get('href'):
                    href = anchor.get('href')
                    job['link'] = f"{self.base_url}{href}" if href.startswith('/') else href
            else:
                job['title'] = self.clean_text(title_elem.get_text())
        
        # Extract company name
        company_elem = card.find('span', class_='companyName')
        if not company_elem:
            company_elem = card.find('span', {'data-testid': 'company-name'})
        if company_elem:
            job['company'] = self.clean_text(company_elem.get_text())
        
        # Extract location
        location_elem = card.find('div', class_='companyLocation')
        if not location_elem:
            location_elem = card.find('div', {'data-testid': 'text-location'})
        if location_elem:
            job['location'] = self.clean_text(location_elem.get_text())
        
        # Extract salary (if available)
        salary_elem = card.find('div', class_='salary-snippet')
        if not salary_elem:
            salary_elem = card.find('div', {'data-testid': 'attribute_snippet_testid'})
        if salary_elem:
            salary_text = self.clean_text(salary_elem.get_text())
            job['salary'] = self.extract_salary(salary_text)
        
        # Extract job type (Remote, Full-time, etc.)
        metadata_elems = card.find_all('div', class_='metadata')
        job_type_parts = []
        
        for elem in metadata_elems:
            text = self.clean_text(elem.get_text())
            if text and any(keyword in text.lower() for keyword in ['remote', 'onsite', 'hybrid', 'full-time', 'part-time', 'contract']):
                job_type_parts.append(text)
        
        if job_type_parts:
            job['job_type'] = ', '.join(job_type_parts)
        
        # Try to find job type in other locations
        if not job['job_type']:
            # Check for remote/onsite indicators
            if card.find(string=lambda text: text and 'remote' in text.lower()):
                job['job_type'] = 'Remote'
            elif card.find(string=lambda text: text and 'hybrid' in text.lower()):
                job['job_type'] = 'Hybrid'
        
        # Extract job description snippet
        description_elem = card.find('div', class_='job-snippet')
        if not description_elem:
            description_elem = card.find('div', {'data-testid': 'job-snippet'})
        if description_elem:
            # Remove any nested li elements (they contain metadata)
            for li in description_elem.find_all('li'):
                li.decompose()
            job['description'] = self.clean_text(description_elem.get_text())
        
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
        
        return details
