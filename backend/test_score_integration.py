"""
Test Suite for Task 5.3: Score Integration into Data Model
Tests score persistence, filtering with scores, and API endpoints
"""

import unittest
import json
import os
import shutil
from storage_manager import JobStorageManager
from job_scorer import get_job_scorer
from data_processor import DataProcessor, filter_jobs


class TestScoreIntegration(unittest.TestCase):
    """Test score integration into data model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_storage_dir = 'test_score_data'
        self.storage = JobStorageManager(storage_dir=self.test_storage_dir)
        self.scorer = get_job_scorer()
        
        # Sample job data
        self.sample_jobs = [
            {
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "New York",
                "salary": "$120,000 - $150,000",
                "job_type": "Remote",
                "description": "Looking for Python expert with Flask experience",
                "link": "https://example.com/job1"
            },
            {
                "title": "Data Scientist",
                "company": "Analytics Inc",
                "location": "San Francisco",
                "salary": "$100,000 - $130,000",
                "job_type": "Hybrid",
                "description": "Machine learning and data analysis role",
                "link": "https://example.com/job2"
            },
            {
                "title": "Junior Developer",
                "company": "Startup LLC",
                "location": "Austin",
                "salary": "$60,000 - $80,000",
                "job_type": "Onsite",
                "description": "Entry level programming position",
                "link": "https://example.com/job3"
            }
        ]
        
        # Sample user preferences
        self.user_preferences = {
            "location": "New York",
            "salary_min": 100000,
            "salary_max": 150000,
            "job_titles": ["Python Developer", "Software Engineer"],
            "job_types": ["Remote", "Hybrid"]
        }
        
        # Sample resume keywords
        self.resume_keywords = {
            "skills": ["python", "flask", "django", "rest api"],
            "technologies": ["git", "docker", "aws"],
            "domains": ["web development", "backend"]
        }
    
    def tearDown(self):
        """Clean up test data"""
        if os.path.exists(self.test_storage_dir):
            shutil.rmtree(self.test_storage_dir)
    
    # ==================== Storage Score Integration Tests ====================
    
    def test_save_jobs_with_scores(self):
        """Test saving jobs with score data"""
        # Score the jobs
        scored_jobs = self.scorer.score_jobs(
            self.sample_jobs, 
            self.user_preferences, 
            self.resume_keywords
        )
        
        # Save to storage
        result = self.storage.save_jobs(scored_jobs, source="test")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['added'], 3)
        
        # Retrieve and verify scores are preserved
        retrieved_jobs = self.storage.get_all_jobs()
        self.assertEqual(len(retrieved_jobs), 3)
        
        for job in retrieved_jobs:
            self.assertIn('score', job)
            self.assertIn('overall_score', job['score'])
            self.assertIn('highlight', job['score'])
            self.assertIn('component_scores', job['score'])
    
    def test_update_single_job_score(self):
        """Test updating score for a single job"""
        # Save jobs without scores
        result = self.storage.save_jobs(self.sample_jobs, source="test")
        self.assertTrue(result['success'])
        
        # Get first job
        jobs = self.storage.get_all_jobs()
        job_id = jobs[0]['id']
        
        # Create score data
        score_data = {
            "overall_score": 85.5,
            "highlight": "white",
            "component_scores": {
                "keyword_match": 90,
                "salary_match": 85,
                "location_match": 100,
                "job_type_match": 75
            }
        }
        
        # Update score
        success = self.storage.update_job_score(job_id, score_data)
        self.assertTrue(success)
        
        # Verify update
        updated_job = self.storage.get_job_by_id(job_id)
        self.assertIsNotNone(updated_job)
        self.assertEqual(updated_job['score']['overall_score'], 85.5)
        self.assertEqual(updated_job['score']['highlight'], 'white')
        self.assertIn('scored_at', updated_job)
    
    def test_update_multiple_job_scores(self):
        """Test batch updating scores for multiple jobs"""
        # Save jobs
        result = self.storage.save_jobs(self.sample_jobs, source="test")
        self.assertTrue(result['success'])
        
        # Get all jobs
        jobs = self.storage.get_all_jobs()
        
        # Prepare score data for all jobs
        job_scores = {}
        for i, job in enumerate(jobs):
            job_scores[job['id']] = {
                "overall_score": 50 + (i * 20),
                "highlight": "red" if i == 0 else "yellow" if i == 1 else "white",
                "component_scores": {
                    "keyword_match": 60,
                    "salary_match": 70,
                    "location_match": 80,
                    "job_type_match": 50
                }
            }
        
        # Update all scores
        update_result = self.storage.update_jobs_scores(job_scores)
        self.assertTrue(update_result['success'])
        self.assertEqual(update_result['updated'], 3)
        self.assertEqual(update_result['not_found'], 0)
        
        # Verify all updates
        updated_jobs = self.storage.get_all_jobs()
        for job in updated_jobs:
            self.assertIn('score', job)
            self.assertIn('scored_at', job)
    
    def test_get_jobs_by_highlight(self):
        """Test filtering jobs by highlight color"""
        # Score and save jobs
        scored_jobs = self.scorer.score_jobs(
            self.sample_jobs,
            self.user_preferences,
            self.resume_keywords
        )
        self.storage.save_jobs(scored_jobs, source="test")
        
        # Get jobs by each highlight color
        red_jobs = self.storage.get_jobs_by_highlight('red')
        yellow_jobs = self.storage.get_jobs_by_highlight('yellow')
        white_jobs = self.storage.get_jobs_by_highlight('white')
        
        # Verify each list contains only jobs with that highlight
        for job in red_jobs:
            self.assertEqual(job['score']['highlight'], 'red')
        
        for job in yellow_jobs:
            self.assertEqual(job['score']['highlight'], 'yellow')
        
        for job in white_jobs:
            self.assertEqual(job['score']['highlight'], 'white')
        
        # Total should equal all jobs
        total = len(red_jobs) + len(yellow_jobs) + len(white_jobs)
        self.assertEqual(total, 3)
    
    def test_get_jobs_by_score_range(self):
        """Test filtering jobs by score range"""
        # Score and save jobs
        scored_jobs = self.scorer.score_jobs(
            self.sample_jobs,
            self.user_preferences,
            self.resume_keywords
        )
        self.storage.save_jobs(scored_jobs, source="test")
        
        # Get high-scoring jobs (>= 70)
        high_score_jobs = self.storage.get_scored_jobs(min_score=70)
        for job in high_score_jobs:
            self.assertGreaterEqual(job['score']['overall_score'], 70)
        
        # Get low-scoring jobs (< 50)
        low_score_jobs = self.storage.get_scored_jobs(max_score=50)
        for job in low_score_jobs:
            self.assertLessEqual(job['score']['overall_score'], 50)
        
        # Get medium-scoring jobs (50-70)
        medium_score_jobs = self.storage.get_scored_jobs(min_score=50, max_score=70)
        for job in medium_score_jobs:
            self.assertGreaterEqual(job['score']['overall_score'], 50)
            self.assertLessEqual(job['score']['overall_score'], 70)
    
    # ==================== Data Processing with Scores Tests ====================
    
    def test_data_cleaning_preserves_scores(self):
        """Test that data cleaning preserves score information"""
        # Score jobs
        scored_jobs = self.scorer.score_jobs(
            self.sample_jobs,
            self.user_preferences,
            self.resume_keywords
        )
        
        # Add some duplicates
        jobs_with_duplicates = scored_jobs + [scored_jobs[0]]
        
        # Clean data
        processor = DataProcessor()
        cleaned_jobs, stats = processor.clean_data(jobs_with_duplicates)
        
        # Verify scores are preserved
        for job in cleaned_jobs:
            if 'score' in job:
                self.assertIn('overall_score', job['score'])
                self.assertIn('highlight', job['score'])
    
    def test_filtering_preserves_scores(self):
        """Test that job filtering preserves score information"""
        # Score and save jobs
        scored_jobs = self.scorer.score_jobs(
            self.sample_jobs,
            self.user_preferences,
            self.resume_keywords
        )
        self.storage.save_jobs(scored_jobs, source="test")
        
        # Filter jobs
        filtered_jobs = filter_jobs(
            scored_jobs,
            location="New York",
            job_types=["Remote"]
        )
        
        # Verify scores are preserved in filtered results
        for job in filtered_jobs:
            if 'score' in job:
                self.assertIn('overall_score', job['score'])
                self.assertIn('highlight', job['score'])
    
    # ==================== Score Calculation Integration Tests ====================
    
    def test_end_to_end_scoring_workflow(self):
        """Test complete workflow: scrape -> clean -> filter -> score -> save"""
        # Step 1: Save raw jobs
        result = self.storage.save_jobs(self.sample_jobs, source="test")
        self.assertTrue(result['success'])
        
        # Step 2: Clean data
        processor = DataProcessor()
        jobs = self.storage.get_all_jobs()
        cleaned_jobs, stats = processor.clean_data(jobs)
        
        # Step 3: Filter jobs
        filtered_jobs = filter_jobs(
            cleaned_jobs,
            salary_min=80000,
            job_types=["Remote", "Hybrid"]
        )
        
        # Step 4: Score filtered jobs
        scored_jobs = self.scorer.score_jobs(
            filtered_jobs,
            self.user_preferences,
            self.resume_keywords
        )
        
        # Step 5: Update storage with scores
        job_scores = {job['id']: job['score'] for job in scored_jobs if 'id' in job}
        update_result = self.storage.update_jobs_scores(job_scores)
        
        # Verify
        self.assertTrue(update_result['success'])
        self.assertGreater(update_result['updated'], 0)
        
        # Get scored jobs from storage
        final_jobs = self.storage.get_all_jobs()
        scored_count = sum(1 for job in final_jobs if 'score' in job)
        self.assertGreater(scored_count, 0)
    
    def test_score_statistics_calculation(self):
        """Test calculation of scoring statistics"""
        # Score jobs
        scored_jobs = self.scorer.score_jobs(
            self.sample_jobs,
            self.user_preferences,
            self.resume_keywords
        )
        
        # Calculate statistics
        stats = self.scorer.calculate_statistics(scored_jobs)
        
        # Verify statistics structure
        self.assertIn('total_jobs', stats)
        self.assertIn('average_score', stats)
        self.assertIn('highest_score', stats)
        self.assertIn('lowest_score', stats)
        self.assertIn('red_count', stats)
        self.assertIn('yellow_count', stats)
        self.assertIn('white_count', stats)
        
        # Verify values
        self.assertEqual(stats['total_jobs'], 3)
        self.assertGreaterEqual(stats['highest_score'], stats['lowest_score'])
        self.assertEqual(
            stats['red_count'] + stats['yellow_count'] + stats['white_count'],
            3
        )
    
    # ==================== Edge Cases and Error Handling Tests ====================
    
    def test_update_score_for_nonexistent_job(self):
        """Test updating score for a job that doesn't exist"""
        score_data = {"overall_score": 75, "highlight": "white"}
        success = self.storage.update_job_score("nonexistent-id", score_data)
        self.assertFalse(success)
    
    def test_get_jobs_by_invalid_highlight(self):
        """Test getting jobs with invalid highlight color"""
        # Save some jobs
        self.storage.save_jobs(self.sample_jobs, source="test")
        
        # Try to get jobs with invalid highlight
        jobs = self.storage.get_jobs_by_highlight('invalid-color')
        self.assertEqual(len(jobs), 0)
    
    def test_score_integration_with_missing_fields(self):
        """Test score integration when jobs have missing fields"""
        incomplete_job = {
            "title": "Test Job",
            "company": "Test Company",
            "location": "Test Location",
            "link": "https://test.com/job"
            # Missing salary, job_type, description
        }
        
        # Score should still work
        score_result = self.scorer.score_job(
            incomplete_job,
            self.user_preferences,
            self.resume_keywords
        )
        
        self.assertIn('overall_score', score_result)
        self.assertIn('highlight', score_result)
    
    def test_bulk_update_with_partial_failures(self):
        """Test batch score update with some invalid job IDs"""
        # Save jobs
        result = self.storage.save_jobs(self.sample_jobs[:2], source="test")
        jobs = self.storage.get_all_jobs()
        
        # Prepare scores including invalid IDs
        job_scores = {}
        for job in jobs:
            job_scores[job['id']] = {"overall_score": 80, "highlight": "white"}
        
        # Add invalid IDs
        job_scores['invalid-id-1'] = {"overall_score": 70, "highlight": "yellow"}
        job_scores['invalid-id-2'] = {"overall_score": 60, "highlight": "red"}
        
        # Update
        update_result = self.storage.update_jobs_scores(job_scores)
        
        # Verify
        self.assertTrue(update_result['success'])
        self.assertEqual(update_result['updated'], 2)
        self.assertEqual(update_result['not_found'], 2)


class TestScoreDataStructure(unittest.TestCase):
    """Test the score data structure and its components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scorer = get_job_scorer()
        
        self.sample_job = {
            "title": "Python Developer",
            "company": "Tech Co",
            "location": "New York",
            "salary": "$120,000",
            "job_type": "Remote",
            "description": "Python and Flask development",
            "link": "https://example.com/job"
        }
        
        self.user_preferences = {
            "location": "New York",
            "salary_min": 100000,
            "salary_max": 150000,
            "job_titles": ["Python Developer"],
            "job_types": ["Remote"]
        }
    
    def test_score_structure(self):
        """Test that score object has correct structure"""
        score = self.scorer.score_job(
            self.sample_job,
            self.user_preferences
        )
        
        # Verify required fields
        self.assertIn('overall_score', score)
        self.assertIn('highlight', score)
        self.assertIn('component_scores', score)
        self.assertIn('weights_used', score)
        
        # Verify component scores
        components = score['component_scores']
        self.assertIn('keyword_match', components)
        self.assertIn('salary_match', components)
        self.assertIn('location_match', components)
        self.assertIn('job_type_match', components)
    
    def test_highlight_values(self):
        """Test that highlight only contains valid values"""
        score = self.scorer.score_job(
            self.sample_job,
            self.user_preferences
        )
        
        self.assertIn(score['highlight'], ['red', 'yellow', 'white'])
    
    def test_score_ranges(self):
        """Test that all scores are in valid range [0, 100]"""
        score = self.scorer.score_job(
            self.sample_job,
            self.user_preferences
        )
        
        # Overall score
        self.assertGreaterEqual(score['overall_score'], 0)
        self.assertLessEqual(score['overall_score'], 100)
        
        # Component scores
        for component_score in score['component_scores'].values():
            self.assertGreaterEqual(component_score, 0)
            self.assertLessEqual(component_score, 100)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestScoreIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestScoreDataStructure))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TASK 5.3 SCORE INTEGRATION TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
