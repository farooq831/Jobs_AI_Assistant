"""
Data Processing Module for Job Cleaning and Normalization
Handles deduplication, validation, and normalization of scraped job data
"""

import re
import logging
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data cleaning, deduplication, and normalization"""
    
    # Common location abbreviations and variations (ordered by specificity)
    LOCATION_MAPPINGS = {
        'washington dc': 'washington',  # More specific patterns first
        'new york city': 'new york',
        'ny': 'new york',
        'nyc': 'new york',
        'sf': 'san francisco',
        'la': 'los angeles',
        'dc': 'washington',
        'philly': 'philadelphia',
        'vegas': 'las vegas',
        'ksa': 'saudi arabia',
        'uae': 'united arab emirates',
        'uk': 'united kingdom',
        'usa': 'united states',
        'us': 'united states',
    }
    
    # Salary pattern regex (order matters - more specific patterns first)
    SALARY_PATTERNS = [
        r'(\d{1,3})k\s*-\s*(\d{1,3})k',  # "100k-150k" or "50k - 70k"
        r'\$(\d{1,3})k-\$(\d{1,3})k',     # "$50k-$70k"
        r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # "$100,000 - $150,000"
        r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*(?:per\s+)?(?:year|yr|annually|annual|/year|/yr))?',  # "$80,000/year"
    ]
    
    # Required fields for a complete job entry
    REQUIRED_FIELDS = ['title', 'company', 'location']
    
    def __init__(self):
        """Initialize the data processor"""
        self.stats = {
            'total_processed': 0,
            'duplicates_removed': 0,
            'incomplete_removed': 0,
            'locations_normalized': 0,
            'salaries_normalized': 0,
            'errors': 0
        }
    
    def clean_data(self, jobs: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Main cleaning pipeline: removes duplicates, incomplete entries, and normalizes data
        
        Args:
            jobs: List of job dictionaries to clean
            
        Returns:
            Tuple of (cleaned_jobs, statistics)
        """
        logger.info(f"Starting data cleaning for {len(jobs)} jobs")
        self.stats['total_processed'] = len(jobs)
        
        # Step 1: Remove duplicates
        jobs = self._remove_duplicates(jobs)
        
        # Step 2: Remove incomplete entries
        jobs = self._remove_incomplete_entries(jobs)
        
        # Step 3: Normalize locations
        jobs = self._normalize_locations(jobs)
        
        # Step 4: Normalize salaries
        jobs = self._normalize_salaries(jobs)
        
        logger.info(f"Data cleaning complete. {len(jobs)} jobs remaining after cleaning")
        return jobs, self.stats
    
    def _generate_job_hash(self, job: Dict) -> str:
        """
        Generate a unique hash for a job based on key fields
        
        Args:
            job: Job dictionary
            
        Returns:
            Hash string
        """
        # Create a signature from key fields
        signature = f"{job.get('title', '').lower()}|{job.get('company', '').lower()}|{job.get('location', '').lower()}"
        return hashlib.md5(signature.encode()).hexdigest()
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate job entries based on title, company, and location
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of unique jobs
        """
        seen_hashes: Set[str] = set()
        unique_jobs = []
        duplicates = 0
        
        for job in jobs:
            job_hash = self._generate_job_hash(job)
            
            if job_hash not in seen_hashes:
                seen_hashes.add(job_hash)
                unique_jobs.append(job)
            else:
                duplicates += 1
                logger.debug(f"Duplicate found: {job.get('title')} at {job.get('company')}")
        
        self.stats['duplicates_removed'] = duplicates
        logger.info(f"Removed {duplicates} duplicate entries")
        
        return unique_jobs
    
    def _remove_incomplete_entries(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove job entries that are missing required fields
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of complete jobs
        """
        complete_jobs = []
        incomplete = 0
        
        for job in jobs:
            # Check if all required fields are present and not empty
            is_complete = all(
                job.get(field) and str(job.get(field)).strip()
                for field in self.REQUIRED_FIELDS
            )
            
            if is_complete:
                complete_jobs.append(job)
            else:
                incomplete += 1
                missing_fields = [f for f in self.REQUIRED_FIELDS if not job.get(f) or not str(job.get(f)).strip()]
                logger.debug(f"Incomplete entry removed. Missing fields: {missing_fields}")
        
        self.stats['incomplete_removed'] = incomplete
        logger.info(f"Removed {incomplete} incomplete entries")
        
        return complete_jobs
    
    def _normalize_locations(self, jobs: List[Dict]) -> List[Dict]:
        """
        Normalize location names to standard formats
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of jobs with normalized locations
        """
        normalized_count = 0
        
        for job in jobs:
            if 'location' in job and job['location']:
                original_location = job['location']
                normalized_location = self._normalize_single_location(original_location)
                
                if normalized_location != original_location:
                    job['location'] = normalized_location
                    job['original_location'] = original_location  # Keep original for reference
                    normalized_count += 1
                    logger.debug(f"Normalized location: '{original_location}' -> '{normalized_location}'")
        
        self.stats['locations_normalized'] = normalized_count
        logger.info(f"Normalized {normalized_count} location entries")
        
        return jobs
    
    def _normalize_single_location(self, location: str) -> str:
        """
        Normalize a single location string
        
        Args:
            location: Location string to normalize
            
        Returns:
            Normalized location string
        """
        if not location:
            return location
        
        # Convert to lowercase for processing
        location_lower = location.lower().strip()
        
        # Remove extra whitespace
        location_lower = re.sub(r'\s+', ' ', location_lower)
        
        # Check for common abbreviations and variations
        for abbr, full_name in self.LOCATION_MAPPINGS.items():
            # Match whole words only
            pattern = r'\b' + re.escape(abbr) + r'\b'
            if re.search(pattern, location_lower):
                location_lower = re.sub(pattern, full_name, location_lower)
        
        # Capitalize each word (Title Case)
        location_normalized = location_lower.title()
        
        # Handle special cases for abbreviations that should remain uppercase
        location_normalized = re.sub(r'\bUsa\b', 'USA', location_normalized)
        location_normalized = re.sub(r'\bUk\b', 'UK', location_normalized)
        location_normalized = re.sub(r'\bUae\b', 'UAE', location_normalized)
        location_normalized = re.sub(r'\bDc\b', 'DC', location_normalized)
        
        return location_normalized
    
    def _normalize_salaries(self, jobs: List[Dict]) -> List[Dict]:
        """
        Normalize salary information to a consistent format
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of jobs with normalized salaries
        """
        normalized_count = 0
        
        for job in jobs:
            if 'salary' in job and job['salary']:
                original_salary = job['salary']
                
                # Try to parse and normalize salary
                normalized = self._normalize_single_salary(original_salary)
                
                if normalized:
                    job['salary_min'] = normalized.get('min')
                    job['salary_max'] = normalized.get('max')
                    job['salary_currency'] = normalized.get('currency', 'USD')
                    job['salary_period'] = normalized.get('period', 'yearly')
                    job['original_salary'] = original_salary  # Keep original
                    normalized_count += 1
                    logger.debug(f"Normalized salary: '{original_salary}' -> {normalized}")
        
        self.stats['salaries_normalized'] = normalized_count
        logger.info(f"Normalized {normalized_count} salary entries")
        
        return jobs
    
    def _normalize_single_salary(self, salary: str) -> Optional[Dict]:
        """
        Parse and normalize a single salary string
        
        Args:
            salary: Salary string to normalize
            
        Returns:
            Dictionary with min, max, currency, and period or None if parsing fails
        """
        if not salary or not isinstance(salary, str):
            return None
        
        salary = salary.strip()
        
        # Determine if it's hourly first
        is_hourly = bool(re.search(r'per\s+hour|/hour|/hr|hourly', salary, re.IGNORECASE))
        
        # Try each pattern
        for pattern in self.SALARY_PATTERNS:
            match = re.search(pattern, salary, re.IGNORECASE)
            if match:
                try:
                    min_salary = match.group(1).replace(',', '')
                    # Check if group(2) exists and is not None
                    if match.lastindex >= 2 and match.group(2):
                        max_salary = match.group(2).replace(',', '')
                    else:
                        max_salary = min_salary
                    
                    # Convert to float
                    min_val = float(min_salary)
                    max_val = float(max_salary)
                    
                    # Handle 'k' notation (e.g., "50k-70k")
                    if 'k' in salary.lower():
                        min_val *= 1000
                        max_val *= 1000
                    
                    # If values are too small and not hourly, assume they're in thousands
                    if not is_hourly:
                        if min_val < 1000:
                            min_val *= 1000
                        if max_val < 1000:
                            max_val *= 1000
                    
                    # Determine currency (default USD)
                    currency = 'USD'
                    if '£' in salary:
                        currency = 'GBP'
                    elif '€' in salary:
                        currency = 'EUR'
                    elif '₹' in salary:
                        currency = 'INR'
                    
                    # Determine period (default yearly)
                    period = 'yearly'
                    if re.search(r'per\s+hour|/hour|/hr|hourly', salary, re.IGNORECASE):
                        period = 'hourly'
                    elif re.search(r'per\s+month|/month|monthly', salary, re.IGNORECASE):
                        period = 'monthly'
                    
                    return {
                        'min': min_val,
                        'max': max_val,
                        'currency': currency,
                        'period': period
                    }
                except (ValueError, AttributeError) as e:
                    logger.debug(f"Error parsing salary '{salary}': {e}")
                    continue
        
        return None
    
    def get_statistics(self) -> Dict:
        """
        Get cleaning statistics
        
        Returns:
            Dictionary with cleaning statistics
        """
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset statistics counters"""
        self.stats = {
            'total_processed': 0,
            'duplicates_removed': 0,
            'incomplete_removed': 0,
            'locations_normalized': 0,
            'salaries_normalized': 0,
            'errors': 0
        }


# Convenience functions
def clean_job_data(jobs: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Clean job data using the DataProcessor
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        Tuple of (cleaned_jobs, statistics)
    """
    processor = DataProcessor()
    return processor.clean_data(jobs)


def normalize_location(location: str) -> str:
    """
    Normalize a location string
    
    Args:
        location: Location string
        
    Returns:
        Normalized location
    """
    processor = DataProcessor()
    return processor._normalize_single_location(location)


def normalize_salary(salary: str) -> Optional[Dict]:
    """
    Normalize a salary string
    
    Args:
        salary: Salary string
        
    Returns:
        Normalized salary dictionary or None
    """
    processor = DataProcessor()
    return processor._normalize_single_salary(salary)
