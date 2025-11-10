"""
Job Scoring Module
Implements weighted scoring algorithm combining keyword match, salary range, location, and job type.
Provides color-coded thresholds (Red, Yellow, White) for job highlighting.
"""

import logging
from typing import Dict, List, Optional, Tuple
from keyword_extractor import get_keyword_extractor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobScorer:
    """
    Calculate match scores for jobs based on multiple weighted factors.
    """
    
    # Default weights for scoring components (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        'keyword_match': 0.50,      # 50% - Most important factor
        'salary_match': 0.25,        # 25% - Significant factor
        'location_match': 0.15,      # 15% - Moderate factor
        'job_type_match': 0.10       # 10% - Minor factor
    }
    
    # Score thresholds for color highlighting
    THRESHOLD_RED = 40      # < 40% = Poor match (Red)
    THRESHOLD_YELLOW = 70   # 40-70% = Fair match (Yellow)
    # > 70% = Good match (White/Green)
    
    # Job type variations and mappings
    JOB_TYPE_MAPPINGS = {
        'remote': ['remote', 'work from home', 'wfh', 'telecommute', 'virtual'],
        'onsite': ['onsite', 'on-site', 'office', 'in-office', 'on site'],
        'hybrid': ['hybrid', 'flexible', 'mixed']
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the job scorer.
        
        Args:
            weights: Custom weights for scoring components (must sum to 1.0)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()
        self.keyword_extractor = get_keyword_extractor()
        logger.info(f"JobScorer initialized with weights: {self.weights}")
    
    def _validate_weights(self):
        """Validate that weights sum to approximately 1.0"""
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def score_job(self, job: Dict, user_preferences: Dict, 
                  resume_keywords: Optional[Dict] = None) -> Dict[str, any]:
        """
        Calculate comprehensive match score for a job.
        
        Args:
            job: Job data dictionary with title, description, location, salary, job_type
            user_preferences: User preferences with location, salary_min/max, job_titles, job_types
            resume_keywords: Optional pre-extracted keywords from resume
            
        Returns:
            Dictionary with overall score, component scores, and color highlight
        """
        if not job or not user_preferences:
            logger.warning("Missing job or user_preferences data")
            return self._create_empty_score()
        
        # Calculate individual component scores
        keyword_score = self._score_keywords(job, user_preferences, resume_keywords)
        salary_score = self._score_salary(job, user_preferences)
        location_score = self._score_location(job, user_preferences)
        job_type_score = self._score_job_type(job, user_preferences)
        
        # Calculate weighted overall score
        overall_score = (
            keyword_score * self.weights['keyword_match'] +
            salary_score * self.weights['salary_match'] +
            location_score * self.weights['location_match'] +
            job_type_score * self.weights['job_type_match']
        )
        
        # Determine color highlight based on thresholds
        highlight = self._determine_highlight(overall_score)
        
        return {
            'overall_score': round(overall_score, 2),
            'highlight': highlight,
            'component_scores': {
                'keyword_match': round(keyword_score, 2),
                'salary_match': round(salary_score, 2),
                'location_match': round(location_score, 2),
                'job_type_match': round(job_type_score, 2)
            },
            'weights': self.weights.copy(),
            'job_id': job.get('id', job.get('link', 'unknown'))
        }
    
    def _score_keywords(self, job: Dict, user_preferences: Dict, 
                       resume_keywords: Optional[Dict] = None) -> float:
        """
        Score based on keyword match between job and resume/user preferences.
        
        Returns:
            Score from 0-100
        """
        try:
            # Extract job keywords
            job_keywords = self.keyword_extractor.extract_job_keywords(job)
            
            # If resume keywords provided, use them for matching
            if resume_keywords:
                match_result = self.keyword_extractor.calculate_keyword_match(
                    job_keywords, resume_keywords
                )
                
                # Weighted average of different match types
                tech_match = match_result['technical_match']['match_percentage']
                overall_match = match_result['overall_match']['match_percentage']
                
                # Technical skills are more important (70% weight)
                keyword_score = (tech_match * 0.7) + (overall_match * 0.3)
                
            else:
                # Fallback: Match against user job titles
                job_title_lower = job.get('title', '').lower()
                user_titles_lower = [title.lower() for title in user_preferences.get('job_titles', [])]
                
                # Check if any user job title appears in job title
                title_match = any(user_title in job_title_lower or job_title_lower in user_title 
                                 for user_title in user_titles_lower)
                
                # Basic scoring: 80% if title matches, 40% otherwise
                keyword_score = 80.0 if title_match else 40.0
            
            return min(100.0, max(0.0, keyword_score))
            
        except Exception as e:
            logger.error(f"Error scoring keywords: {e}")
            return 50.0  # Default middle score on error
    
    def _score_salary(self, job: Dict, user_preferences: Dict) -> float:
        """
        Score based on salary match with user preferences.
        
        Returns:
            Score from 0-100
        """
        try:
            user_min = user_preferences.get('salary_min', 0)
            user_max = user_preferences.get('salary_max', float('inf'))
            
            job_salary = job.get('salary')
            
            # If no salary info in job, give neutral score
            if not job_salary:
                return 50.0
            
            # Handle salary range or single value
            if isinstance(job_salary, dict):
                job_min = job_salary.get('min', 0)
                job_max = job_salary.get('max', float('inf'))
            elif isinstance(job_salary, str):
                # Try to parse salary string
                job_min, job_max = self._parse_salary_string(job_salary)
            else:
                job_min = job_max = float(job_salary)
            
            # Calculate overlap between ranges
            overlap_start = max(user_min, job_min)
            overlap_end = min(user_max, job_max)
            
            if overlap_end < overlap_start:
                # No overlap
                # Check how far off we are
                if job_max < user_min:
                    # Job pays too little
                    ratio = job_max / user_min if user_min > 0 else 0
                    return max(0, 50 * ratio)  # Scale down from 50
                else:
                    # Job pays more than expected (not necessarily bad)
                    return 70.0
            else:
                # Calculate percentage of overlap
                user_range = user_max - user_min
                overlap = overlap_end - overlap_start
                
                if user_range == 0:
                    overlap_pct = 100.0
                else:
                    overlap_pct = (overlap / user_range) * 100
                
                # Perfect overlap or job range within user range = 100
                # Partial overlap scaled accordingly
                return min(100.0, 70 + (overlap_pct * 0.3))
        
        except Exception as e:
            logger.error(f"Error scoring salary: {e}")
            return 50.0
    
    def _parse_salary_string(self, salary_str: str) -> Tuple[float, float]:
        """
        Parse salary string into min and max values.
        
        Args:
            salary_str: Salary string like "$50k-$70k" or "$80,000/year"
            
        Returns:
            Tuple of (min_salary, max_salary)
        """
        import re
        
        # Remove common words
        cleaned = salary_str.lower().replace(',', '').replace('$', '')
        
        # Try to find range pattern
        range_match = re.search(r'(\d+\.?\d*)k?\s*-\s*(\d+\.?\d*)k?', cleaned)
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            
            # Convert k to thousands
            if 'k' in salary_str.lower():
                min_val *= 1000
                max_val *= 1000
            
            return min_val, max_val
        
        # Try to find single value
        single_match = re.search(r'(\d+\.?\d*)k?', cleaned)
        if single_match:
            value = float(single_match.group(1))
            if 'k' in salary_str.lower():
                value *= 1000
            return value, value
        
        return 0, float('inf')
    
    def _score_location(self, job: Dict, user_preferences: Dict) -> float:
        """
        Score based on location match with user preferences.
        
        Returns:
            Score from 0-100
        """
        try:
            job_location = job.get('location', '').lower().strip()
            user_location = user_preferences.get('location', '').lower().strip()
            
            if not job_location:
                return 50.0  # Neutral if no location specified
            
            if not user_location:
                return 100.0  # User doesn't care about location
            
            # Check for remote/work from home
            remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere', 'telecommute']
            if any(keyword in job_location for keyword in remote_keywords):
                return 100.0  # Remote jobs match everyone
            
            # Exact match
            if user_location in job_location or job_location in user_location:
                return 100.0
            
            # Check for city/state match
            # Extract major components
            job_parts = set(job_location.replace(',', ' ').split())
            user_parts = set(user_location.replace(',', ' ').split())
            
            common_parts = job_parts.intersection(user_parts)
            
            if common_parts:
                # Calculate partial match based on common terms
                match_ratio = len(common_parts) / max(len(job_parts), len(user_parts))
                return 60 + (match_ratio * 40)  # Scale from 60-100
            
            return 30.0  # Different locations
            
        except Exception as e:
            logger.error(f"Error scoring location: {e}")
            return 50.0
    
    def _score_job_type(self, job: Dict, user_preferences: Dict) -> float:
        """
        Score based on job type match (remote/onsite/hybrid).
        
        Returns:
            Score from 0-100
        """
        try:
            user_job_types = user_preferences.get('job_types', [])
            
            # If user doesn't specify, don't penalize
            if not user_job_types:
                return 100.0
            
            job_type = job.get('job_type', '').lower()
            job_description = job.get('description', '').lower()
            job_location = job.get('location', '').lower()
            
            # Combine all text for checking
            combined_text = f"{job_type} {job_description} {job_location}"
            
            # Normalize user preferences
            user_types_normalized = [jt.lower() for jt in user_job_types]
            
            # Check each user preference
            for user_type in user_types_normalized:
                # Get all variations of this job type
                variations = self.JOB_TYPE_MAPPINGS.get(user_type, [user_type])
                
                # Check if any variation appears in job
                if any(variation in combined_text for variation in variations):
                    return 100.0
            
            # No match found
            return 40.0
            
        except Exception as e:
            logger.error(f"Error scoring job type: {e}")
            return 50.0
    
    def _determine_highlight(self, score: float) -> str:
        """
        Determine color highlight based on score thresholds.
        
        Args:
            score: Overall match score (0-100)
            
        Returns:
            Color highlight: 'red', 'yellow', or 'white'
        """
        if score < self.THRESHOLD_RED:
            return 'red'
        elif score < self.THRESHOLD_YELLOW:
            return 'yellow'
        else:
            return 'white'
    
    def _create_empty_score(self) -> Dict[str, any]:
        """Create an empty score response for error cases"""
        return {
            'overall_score': 0.0,
            'highlight': 'red',
            'component_scores': {
                'keyword_match': 0.0,
                'salary_match': 0.0,
                'location_match': 0.0,
                'job_type_match': 0.0
            },
            'weights': self.weights.copy(),
            'job_id': 'unknown'
        }
    
    def score_multiple_jobs(self, jobs: List[Dict], user_preferences: Dict,
                           resume_keywords: Optional[Dict] = None) -> List[Dict]:
        """
        Score multiple jobs and return sorted by score.
        
        Args:
            jobs: List of job dictionaries
            user_preferences: User preferences dictionary
            resume_keywords: Optional pre-extracted resume keywords
            
        Returns:
            List of jobs with added 'score' field, sorted by score descending
        """
        scored_jobs = []
        
        for job in jobs:
            try:
                score_result = self.score_job(job, user_preferences, resume_keywords)
                
                # Add score to job data
                job_with_score = job.copy()
                job_with_score['score'] = score_result
                scored_jobs.append(job_with_score)
                
            except Exception as e:
                logger.error(f"Error scoring job {job.get('title', 'unknown')}: {e}")
                # Add job with empty score
                job_with_score = job.copy()
                job_with_score['score'] = self._create_empty_score()
                scored_jobs.append(job_with_score)
        
        # Sort by overall score (descending)
        scored_jobs.sort(key=lambda x: x['score']['overall_score'], reverse=True)
        
        return scored_jobs
    
    def get_score_statistics(self, scored_jobs: List[Dict]) -> Dict[str, any]:
        """
        Calculate statistics for a list of scored jobs.
        
        Args:
            scored_jobs: List of jobs with score information
            
        Returns:
            Dictionary with statistics
        """
        if not scored_jobs:
            return {
                'total_jobs': 0,
                'average_score': 0.0,
                'highest_score': 0.0,
                'lowest_score': 0.0,
                'red_count': 0,
                'yellow_count': 0,
                'white_count': 0
            }
        
        scores = [job['score']['overall_score'] for job in scored_jobs if 'score' in job]
        highlights = [job['score']['highlight'] for job in scored_jobs if 'score' in job]
        
        return {
            'total_jobs': len(scored_jobs),
            'average_score': round(sum(scores) / len(scores), 2) if scores else 0.0,
            'highest_score': round(max(scores), 2) if scores else 0.0,
            'lowest_score': round(min(scores), 2) if scores else 0.0,
            'red_count': highlights.count('red'),
            'yellow_count': highlights.count('yellow'),
            'white_count': highlights.count('white')
        }


# Singleton instance
_scorer_instance = None

def get_job_scorer(weights: Optional[Dict[str, float]] = None) -> JobScorer:
    """
    Get or create singleton JobScorer instance.
    
    Args:
        weights: Optional custom weights for scoring
        
    Returns:
        JobScorer instance
    """
    global _scorer_instance
    if _scorer_instance is None or weights is not None:
        _scorer_instance = JobScorer(weights=weights)
    return _scorer_instance
