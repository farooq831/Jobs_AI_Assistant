"""
Job Storage Manager
Manages persistent storage of scraped job data with error handling and retry mechanisms
"""

import json
import os
import time
import hashlib
from typing import List, Dict, Optional, Set
from datetime import datetime
from threading import Lock
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobStorageManager:
    """Manages storage of scraped job data in JSON format"""
    
    def __init__(self, storage_dir: str = 'data'):
        """
        Initialize the storage manager
        
        Args:
            storage_dir: Directory to store JSON files
        """
        self.storage_dir = storage_dir
        self.jobs_file = os.path.join(storage_dir, 'jobs.json')
        self.metadata_file = os.path.join(storage_dir, 'metadata.json')
        self.errors_file = os.path.join(storage_dir, 'scraping_errors.json')
        self.lock = Lock()  # Thread safety for concurrent access
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize storage files if they don't exist
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage files with empty structures"""
        if not os.path.exists(self.jobs_file):
            self._write_json(self.jobs_file, {"jobs": [], "count": 0})
        
        if not os.path.exists(self.metadata_file):
            self._write_json(self.metadata_file, {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_scrapes": 0,
                "successful_scrapes": 0,
                "failed_scrapes": 0
            })
        
        if not os.path.exists(self.errors_file):
            self._write_json(self.errors_file, {"errors": []})
    
    def _read_json(self, filepath: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Read JSON file with retry mechanism
        
        Args:
            filepath: Path to JSON file
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary from JSON or None if failed
        """
        for attempt in range(max_retries):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Failed to read {filepath} after {max_retries} attempts")
                    return None
            except FileNotFoundError:
                logger.warning(f"File not found: {filepath}")
                return None
            except Exception as e:
                logger.error(f"Error reading {filepath}: {e}")
                return None
        
        return None
    
    def _write_json(self, filepath: str, data: Dict, max_retries: int = 3) -> bool:
        """
        Write JSON file with retry mechanism
        
        Args:
            filepath: Path to JSON file
            data: Dictionary to write
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                # Write to temporary file first
                temp_filepath = f"{filepath}.tmp"
                with open(temp_filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Rename to actual file (atomic operation)
                os.replace(temp_filepath, filepath)
                return True
                
            except Exception as e:
                logger.error(f"Error writing {filepath} on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Failed to write {filepath} after {max_retries} attempts")
                    return False
        
        return False
    
    def _generate_job_hash(self, job: Dict) -> str:
        """
        Generate a unique hash for a job to detect duplicates
        
        Args:
            job: Job dictionary
            
        Returns:
            Hash string
        """
        # Use link as primary identifier, fallback to title+company+location
        if job.get('link'):
            key = job['link']
        else:
            key = f"{job.get('title', '')}|{job.get('company', '')}|{job.get('location', '')}"
        
        return hashlib.md5(key.encode('utf-8')).hexdigest()
    
    def _validate_job(self, job: Dict) -> tuple[bool, str]:
        """
        Validate job data structure
        
        Args:
            job: Job dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['title', 'company', 'location', 'link']
        
        for field in required_fields:
            if field not in job or not job[field]:
                return False, f"Missing required field: {field}"
        
        # Validate data types
        if not isinstance(job['title'], str):
            return False, "Job title must be a string"
        if not isinstance(job['company'], str):
            return False, "Company must be a string"
        if not isinstance(job['location'], str):
            return False, "Location must be a string"
        if not isinstance(job['link'], str):
            return False, "Link must be a string"
        
        return True, ""
    
    def save_jobs(self, jobs: List[Dict], source: str = "unknown", 
                  skip_duplicates: bool = True) -> Dict:
        """
        Save scraped jobs to storage with duplicate detection
        
        Args:
            jobs: List of job dictionaries
            source: Source of the jobs (e.g., 'indeed', 'glassdoor')
            skip_duplicates: Whether to skip duplicate jobs
            
        Returns:
            Dictionary with save results
        """
        with self.lock:
            try:
                # Read existing data
                data = self._read_json(self.jobs_file)
                if data is None:
                    data = {"jobs": [], "count": 0}
                
                existing_jobs = data.get('jobs', [])
                
                # Build hash set of existing jobs
                existing_hashes: Set[str] = set()
                if skip_duplicates:
                    existing_hashes = {self._generate_job_hash(job) for job in existing_jobs}
                
                # Process new jobs
                added_count = 0
                skipped_count = 0
                invalid_count = 0
                
                for job in jobs:
                    # Validate job
                    is_valid, error_msg = self._validate_job(job)
                    if not is_valid:
                        invalid_count += 1
                        logger.warning(f"Invalid job data: {error_msg}")
                        continue
                    
                    # Check for duplicates
                    job_hash = self._generate_job_hash(job)
                    if skip_duplicates and job_hash in existing_hashes:
                        skipped_count += 1
                        continue
                    
                    # Add metadata
                    job['source'] = source
                    job['scraped_at'] = datetime.now().isoformat()
                    job['id'] = job_hash
                    
                    # Add to list
                    existing_jobs.append(job)
                    existing_hashes.add(job_hash)
                    added_count += 1
                
                # Update data
                data['jobs'] = existing_jobs
                data['count'] = len(existing_jobs)
                
                # Write to file
                if not self._write_json(self.jobs_file, data):
                    return {
                        "success": False,
                        "error": "Failed to write jobs to storage",
                        "added": 0,
                        "skipped": 0,
                        "invalid": invalid_count
                    }
                
                # Update metadata
                self._update_metadata(success=True)
                
                logger.info(f"Saved jobs: {added_count} added, {skipped_count} skipped, {invalid_count} invalid")
                
                return {
                    "success": True,
                    "added": added_count,
                    "skipped": skipped_count,
                    "invalid": invalid_count,
                    "total": data['count']
                }
                
            except Exception as e:
                logger.error(f"Error saving jobs: {e}")
                self._update_metadata(success=False)
                self._log_error("save_jobs", str(e))
                return {
                    "success": False,
                    "error": str(e),
                    "added": 0,
                    "skipped": 0,
                    "invalid": 0
                }
    
    def get_all_jobs(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve all stored jobs with optional filtering
        
        Args:
            filters: Optional dictionary with filter criteria
                     (e.g., {'source': 'indeed', 'location': 'New York'})
        
        Returns:
            List of job dictionaries
        """
        with self.lock:
            try:
                data = self._read_json(self.jobs_file)
                if data is None:
                    return []
                
                jobs = data.get('jobs', [])
                
                # Apply filters if provided
                if filters:
                    filtered_jobs = []
                    for job in jobs:
                        match = True
                        for key, value in filters.items():
                            if key not in job or job[key] != value:
                                match = False
                                break
                        if match:
                            filtered_jobs.append(job)
                    return filtered_jobs
                
                return jobs
                
            except Exception as e:
                logger.error(f"Error retrieving jobs: {e}")
                return []
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """
        Retrieve a specific job by ID
        
        Args:
            job_id: Job ID (hash)
            
        Returns:
            Job dictionary or None if not found
        """
        jobs = self.get_all_jobs()
        for job in jobs:
            if job.get('id') == job_id:
                return job
        return None
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job by ID
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                data = self._read_json(self.jobs_file)
                if data is None:
                    return False
                
                jobs = data.get('jobs', [])
                initial_count = len(jobs)
                
                # Filter out the job to delete
                jobs = [job for job in jobs if job.get('id') != job_id]
                
                if len(jobs) == initial_count:
                    logger.warning(f"Job {job_id} not found")
                    return False
                
                data['jobs'] = jobs
                data['count'] = len(jobs)
                
                return self._write_json(self.jobs_file, data)
                
            except Exception as e:
                logger.error(f"Error deleting job: {e}")
                return False
    
    def clear_all_jobs(self) -> bool:
        """
        Clear all stored jobs
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                data = {"jobs": [], "count": 0}
                return self._write_json(self.jobs_file, data)
            except Exception as e:
                logger.error(f"Error clearing jobs: {e}")
                return False
    
    def get_statistics(self) -> Dict:
        """
        Get storage statistics
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            try:
                data = self._read_json(self.jobs_file)
                metadata = self._read_json(self.metadata_file)
                errors = self._read_json(self.errors_file)
                
                jobs = data.get('jobs', []) if data else []
                
                # Calculate statistics
                sources = {}
                for job in jobs:
                    source = job.get('source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1
                
                return {
                    "total_jobs": len(jobs),
                    "jobs_by_source": sources,
                    "metadata": metadata,
                    "error_count": len(errors.get('errors', [])) if errors else 0,
                    "storage_size_bytes": os.path.getsize(self.jobs_file) if os.path.exists(self.jobs_file) else 0
                }
                
            except Exception as e:
                logger.error(f"Error getting statistics: {e}")
                return {}
    
    def _update_metadata(self, success: bool = True):
        """
        Update metadata after scraping operation
        
        Args:
            success: Whether the operation was successful
        """
        try:
            metadata = self._read_json(self.metadata_file)
            if metadata is None:
                metadata = {}
            
            metadata['last_updated'] = datetime.now().isoformat()
            metadata['total_scrapes'] = metadata.get('total_scrapes', 0) + 1
            
            if success:
                metadata['successful_scrapes'] = metadata.get('successful_scrapes', 0) + 1
            else:
                metadata['failed_scrapes'] = metadata.get('failed_scrapes', 0) + 1
            
            self._write_json(self.metadata_file, metadata)
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
    
    def _log_error(self, operation: str, error_message: str):
        """
        Log scraping errors
        
        Args:
            operation: Operation that failed
            error_message: Error message
        """
        try:
            errors = self._read_json(self.errors_file)
            if errors is None:
                errors = {"errors": []}
            
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "error": error_message
            }
            
            errors['errors'].append(error_entry)
            
            # Keep only last 100 errors
            if len(errors['errors']) > 100:
                errors['errors'] = errors['errors'][-100:]
            
            self._write_json(self.errors_file, errors)
            
        except Exception as e:
            logger.error(f"Error logging error: {e}")
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """
        Get recent scraping errors
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of error dictionaries
        """
        try:
            errors = self._read_json(self.errors_file)
            if errors is None:
                return []
            
            error_list = errors.get('errors', [])
            return error_list[-limit:] if error_list else []
            
        except Exception as e:
            logger.error(f"Error retrieving errors: {e}")
            return []
    
    def export_to_json(self, output_file: str, filters: Optional[Dict] = None) -> bool:
        """
        Export jobs to a separate JSON file
        
        Args:
            output_file: Path to output file
            filters: Optional filters to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            jobs = self.get_all_jobs(filters)
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_jobs": len(jobs),
                "filters": filters,
                "jobs": jobs
            }
            
            return self._write_json(output_file, export_data)
            
        except Exception as e:
            logger.error(f"Error exporting jobs: {e}")
            return False
