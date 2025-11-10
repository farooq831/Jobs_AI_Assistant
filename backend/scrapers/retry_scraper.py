"""
Retry Scraper Wrapper
Provides retry logic with exponential backoff for scraping operations
"""

import time
import logging
from typing import List, Dict, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retry_on_exceptions: tuple = (Exception,)
    ):
        """
        Initialize retry configuration
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff calculation
            retry_on_exceptions: Tuple of exception types to retry on
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retry_on_exceptions = retry_on_exceptions


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on_exceptions: tuple = (Exception,)
):
    """
    Decorator to add retry logic with exponential backoff to a function
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        retry_on_exceptions: Tuple of exception types to retry on
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {str(e)}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        initial_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


class RetryScraper:
    """Wrapper class that adds retry logic to scraper operations"""
    
    def __init__(self, scraper, config: Optional[RetryConfig] = None):
        """
        Initialize retry scraper wrapper
        
        Args:
            scraper: The scraper instance to wrap
            config: Retry configuration (uses defaults if not provided)
        """
        self.scraper = scraper
        self.config = config or RetryConfig()
        self.scrape_attempts = []  # Track scraping attempts for analysis
    
    def scrape_jobs_with_retry(
        self,
        job_title: str,
        location: str,
        num_pages: int = 1
    ) -> Dict:
        """
        Scrape jobs with retry logic and detailed result tracking
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            num_pages: Number of pages to scrape
            
        Returns:
            Dictionary with scraping results including retry information
        """
        attempt_info = {
            "job_title": job_title,
            "location": location,
            "num_pages": num_pages,
            "attempts": [],
            "success": False,
            "jobs": [],
            "total_attempts": 0,
            "total_time": 0
        }
        
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            attempt_start = time.time()
            attempt_data = {
                "attempt_number": attempt + 1,
                "timestamp": time.time(),
                "success": False,
                "jobs_count": 0,
                "error": None,
                "duration": 0
            }
            
            try:
                # Attempt to scrape
                jobs = self.scraper.scrape_jobs(job_title, location, num_pages)
                
                attempt_data["success"] = True
                attempt_data["jobs_count"] = len(jobs)
                attempt_data["duration"] = time.time() - attempt_start
                
                attempt_info["attempts"].append(attempt_data)
                attempt_info["success"] = True
                attempt_info["jobs"] = jobs
                attempt_info["total_attempts"] = attempt + 1
                attempt_info["total_time"] = time.time() - start_time
                
                logger.info(
                    f"Successfully scraped {len(jobs)} jobs for '{job_title}' "
                    f"in {location} on attempt {attempt + 1}"
                )
                
                self.scrape_attempts.append(attempt_info)
                return attempt_info
                
            except self.config.retry_on_exceptions as e:
                last_exception = e
                attempt_data["error"] = str(e)
                attempt_data["duration"] = time.time() - attempt_start
                attempt_info["attempts"].append(attempt_data)
                
                if attempt == self.config.max_retries:
                    logger.error(
                        f"Failed to scrape jobs for '{job_title}' in {location} "
                        f"after {self.config.max_retries} retries: {str(e)}"
                    )
                    attempt_info["total_attempts"] = attempt + 1
                    attempt_info["total_time"] = time.time() - start_time
                    attempt_info["final_error"] = str(e)
                    
                    self.scrape_attempts.append(attempt_info)
                    return attempt_info
                
                # Calculate delay with exponential backoff
                delay = min(
                    self.config.initial_delay * (self.config.exponential_base ** attempt),
                    self.config.max_delay
                )
                
                logger.warning(
                    f"Attempt {attempt + 1}/{self.config.max_retries} failed for "
                    f"'{job_title}' in {location}: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                time.sleep(delay)
        
        # Should not reach here, but handle just in case
        attempt_info["total_attempts"] = self.config.max_retries + 1
        attempt_info["total_time"] = time.time() - start_time
        attempt_info["final_error"] = str(last_exception) if last_exception else "Unknown error"
        
        self.scrape_attempts.append(attempt_info)
        return attempt_info
    
    def scrape_multiple_with_retry(
        self,
        job_titles: List[str],
        location: str,
        num_pages: int = 1
    ) -> Dict:
        """
        Scrape multiple job titles with retry logic
        
        Args:
            job_titles: List of job titles to search for
            location: Location to search in
            num_pages: Number of pages to scrape per job title
            
        Returns:
            Dictionary with aggregated results
        """
        results = {
            "job_titles": job_titles,
            "location": location,
            "num_pages": num_pages,
            "results": [],
            "total_jobs": 0,
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "total_time": 0
        }
        
        start_time = time.time()
        
        for job_title in job_titles:
            result = self.scrape_jobs_with_retry(job_title, location, num_pages)
            results["results"].append(result)
            
            if result["success"]:
                results["total_jobs"] += len(result["jobs"])
                results["successful_scrapes"] += 1
            else:
                results["failed_scrapes"] += 1
        
        results["total_time"] = time.time() - start_time
        
        return results
    
    def get_attempt_statistics(self) -> Dict:
        """
        Get statistics about scraping attempts
        
        Returns:
            Dictionary with statistics
        """
        if not self.scrape_attempts:
            return {
                "total_attempts": 0,
                "successful": 0,
                "failed": 0,
                "average_retries": 0,
                "average_time": 0
            }
        
        total = len(self.scrape_attempts)
        successful = sum(1 for a in self.scrape_attempts if a["success"])
        failed = total - successful
        
        total_retries = sum(a["total_attempts"] for a in self.scrape_attempts)
        total_time = sum(a["total_time"] for a in self.scrape_attempts)
        
        return {
            "total_attempts": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "average_retries": total_retries / total if total > 0 else 0,
            "average_time": total_time / total if total > 0 else 0,
            "total_time": total_time
        }
    
    def clear_attempt_history(self):
        """Clear the attempt history"""
        self.scrape_attempts = []


# Convenience function to create retry-enabled scraper
def create_retry_scraper(scraper_class, *args, **kwargs):
    """
    Create a scraper instance with retry capabilities
    
    Args:
        scraper_class: The scraper class to instantiate
        *args, **kwargs: Arguments to pass to the scraper constructor
        
    Returns:
        RetryScraper instance wrapping the scraper
    """
    # Extract retry config if provided
    retry_config = kwargs.pop('retry_config', None)
    
    # Create scraper instance
    scraper = scraper_class(*args, **kwargs)
    
    # Wrap with retry logic
    return RetryScraper(scraper, retry_config)
