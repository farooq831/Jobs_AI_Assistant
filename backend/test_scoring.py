"""
Comprehensive Test Suite for Job Scoring Module
Tests scoring algorithm, thresholds, weights, and API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import unittest
from job_scorer import JobScorer, get_job_scorer
from keyword_extractor import get_keyword_extractor


class TestJobScorer(unittest.TestCase):
    """Test JobScorer class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scorer = JobScorer()
        
        self.sample_job = {
            'id': 'job123',
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'location': 'New York, NY',
            'salary': {'min': 80000, 'max': 120000},
            'job_type': 'Remote',
            'description': 'Looking for a Python developer with Django and Flask experience. Must know AWS and Docker.'
        }
        
        self.user_preferences = {
            'name': 'John Doe',
            'location': 'New York',
            'salary_min': 70000,
            'salary_max': 100000,
            'job_titles': ['Python Developer', 'Software Engineer'],
            'job_types': ['Remote', 'Hybrid']
        }
        
        self.resume_text = """
        John Doe - Software Engineer
        Skills: Python, Django, Flask, JavaScript, React, AWS, Docker, Git
        Experience: 5 years in web development
        """
    
    def test_scorer_initialization(self):
        """Test scorer initializes with correct default weights"""
        self.assertAlmostEqual(sum(self.scorer.weights.values()), 1.0, places=2)
        self.assertEqual(self.scorer.weights['keyword_match'], 0.50)
        self.assertEqual(self.scorer.weights['salary_match'], 0.25)
        self.assertEqual(self.scorer.weights['location_match'], 0.15)
        self.assertEqual(self.scorer.weights['job_type_match'], 0.10)
    
    def test_custom_weights(self):
        """Test scorer with custom weights"""
        custom_weights = {
            'keyword_match': 0.40,
            'salary_match': 0.30,
            'location_match': 0.20,
            'job_type_match': 0.10
        }
        scorer = JobScorer(weights=custom_weights)
        self.assertEqual(scorer.weights['keyword_match'], 0.40)
        self.assertAlmostEqual(sum(scorer.weights.values()), 1.0, places=2)
    
    def test_invalid_weights(self):
        """Test that invalid weights raise error"""
        invalid_weights = {
            'keyword_match': 0.30,
            'salary_match': 0.30,
            'location_match': 0.20,
            'job_type_match': 0.10
        }
        with self.assertRaises(ValueError):
            JobScorer(weights=invalid_weights)
    
    def test_score_job_basic(self):
        """Test basic job scoring"""
        result = self.scorer.score_job(self.sample_job, self.user_preferences)
        
        self.assertIn('overall_score', result)
        self.assertIn('highlight', result)
        self.assertIn('component_scores', result)
        self.assertIn('weights', result)
        
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)
        self.assertIn(result['highlight'], ['red', 'yellow', 'white'])
    
    def test_score_job_with_resume(self):
        """Test job scoring with resume keywords"""
        extractor = get_keyword_extractor()
        resume_keywords = extractor.extract_resume_keywords(self.resume_text)
        
        result = self.scorer.score_job(
            self.sample_job, 
            self.user_preferences,
            resume_keywords
        )
        
        self.assertGreater(result['overall_score'], 0)
        self.assertIn(result['highlight'], ['red', 'yellow', 'white'])
    
    def test_salary_scoring_perfect_overlap(self):
        """Test salary scoring with perfect overlap"""
        job = self.sample_job.copy()
        job['salary'] = {'min': 70000, 'max': 100000}
        
        score = self.scorer._score_salary(job, self.user_preferences)
        self.assertGreaterEqual(score, 90)
    
    def test_salary_scoring_no_overlap(self):
        """Test salary scoring with no overlap"""
        job = self.sample_job.copy()
        job['salary'] = {'min': 30000, 'max': 40000}
        
        score = self.scorer._score_salary(job, self.user_preferences)
        self.assertLess(score, 50)
    
    def test_salary_scoring_partial_overlap(self):
        """Test salary scoring with partial overlap"""
        job = self.sample_job.copy()
        job['salary'] = {'min': 60000, 'max': 80000}
        
        score = self.scorer._score_salary(job, self.user_preferences)
        self.assertGreater(score, 50)
        self.assertLess(score, 100)
    
    def test_salary_scoring_no_salary_info(self):
        """Test salary scoring when job has no salary"""
        job = self.sample_job.copy()
        job['salary'] = None
        
        score = self.scorer._score_salary(job, self.user_preferences)
        self.assertEqual(score, 50.0)  # Neutral score
    
    def test_location_scoring_exact_match(self):
        """Test location scoring with exact match"""
        job = self.sample_job.copy()
        job['location'] = 'New York, NY'
        
        score = self.scorer._score_location(job, self.user_preferences)
        self.assertEqual(score, 100.0)
    
    def test_location_scoring_remote(self):
        """Test location scoring for remote jobs"""
        job = self.sample_job.copy()
        job['location'] = 'Remote'
        
        score = self.scorer._score_location(job, self.user_preferences)
        self.assertEqual(score, 100.0)
    
    def test_location_scoring_different_location(self):
        """Test location scoring for different location"""
        job = self.sample_job.copy()
        job['location'] = 'Los Angeles, CA'
        prefs = self.user_preferences.copy()
        prefs['location'] = 'New York, NY'
        
        score = self.scorer._score_location(job, prefs)
        self.assertLess(score, 50)
    
    def test_job_type_scoring_match(self):
        """Test job type scoring with match"""
        job = self.sample_job.copy()
        job['job_type'] = 'Remote'
        
        score = self.scorer._score_job_type(job, self.user_preferences)
        self.assertEqual(score, 100.0)
    
    def test_job_type_scoring_no_match(self):
        """Test job type scoring with no match"""
        job = self.sample_job.copy()
        job['job_type'] = 'Onsite'
        prefs = self.user_preferences.copy()
        prefs['job_types'] = ['Remote']
        
        score = self.scorer._score_job_type(job, prefs)
        self.assertEqual(score, 40.0)
    
    def test_job_type_scoring_no_preference(self):
        """Test job type scoring when user has no preference"""
        job = self.sample_job.copy()
        prefs = self.user_preferences.copy()
        prefs['job_types'] = []
        
        score = self.scorer._score_job_type(job, prefs)
        self.assertEqual(score, 100.0)
    
    def test_highlight_red(self):
        """Test red highlight threshold"""
        highlight = self.scorer._determine_highlight(30)
        self.assertEqual(highlight, 'red')
    
    def test_highlight_yellow(self):
        """Test yellow highlight threshold"""
        highlight = self.scorer._determine_highlight(55)
        self.assertEqual(highlight, 'yellow')
    
    def test_highlight_white(self):
        """Test white highlight threshold"""
        highlight = self.scorer._determine_highlight(80)
        self.assertEqual(highlight, 'white')
    
    def test_highlight_boundary_red_yellow(self):
        """Test boundary between red and yellow"""
        highlight = self.scorer._determine_highlight(40)
        self.assertEqual(highlight, 'yellow')
    
    def test_highlight_boundary_yellow_white(self):
        """Test boundary between yellow and white"""
        highlight = self.scorer._determine_highlight(70)
        self.assertEqual(highlight, 'white')
    
    def test_score_multiple_jobs(self):
        """Test scoring multiple jobs"""
        jobs = [
            self.sample_job.copy(),
            {
                'id': 'job456',
                'title': 'Java Developer',
                'company': 'Other Corp',
                'location': 'Boston, MA',
                'salary': {'min': 60000, 'max': 80000},
                'job_type': 'Onsite',
                'description': 'Java and Spring experience required'
            }
        ]
        
        scored_jobs = self.scorer.score_multiple_jobs(jobs, self.user_preferences)
        
        self.assertEqual(len(scored_jobs), 2)
        self.assertIn('score', scored_jobs[0])
        
        # Check that jobs are sorted by score (descending)
        self.assertGreaterEqual(
            scored_jobs[0]['score']['overall_score'],
            scored_jobs[1]['score']['overall_score']
        )
    
    def test_score_statistics(self):
        """Test score statistics calculation"""
        scored_jobs = [
            {'score': {'overall_score': 80, 'highlight': 'white'}},
            {'score': {'overall_score': 60, 'highlight': 'yellow'}},
            {'score': {'overall_score': 30, 'highlight': 'red'}},
            {'score': {'overall_score': 90, 'highlight': 'white'}},
        ]
        
        stats = self.scorer.get_score_statistics(scored_jobs)
        
        self.assertEqual(stats['total_jobs'], 4)
        self.assertEqual(stats['average_score'], 65.0)
        self.assertEqual(stats['highest_score'], 90.0)
        self.assertEqual(stats['lowest_score'], 30.0)
        self.assertEqual(stats['red_count'], 1)
        self.assertEqual(stats['yellow_count'], 1)
        self.assertEqual(stats['white_count'], 2)
    
    def test_empty_job_handling(self):
        """Test handling of empty job data"""
        result = self.scorer.score_job({}, self.user_preferences)
        
        self.assertEqual(result['overall_score'], 0.0)
        self.assertEqual(result['highlight'], 'red')
    
    def test_empty_preferences_handling(self):
        """Test handling of empty preferences"""
        result = self.scorer.score_job(self.sample_job, {})
        
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)
    
    def test_parse_salary_string_range(self):
        """Test parsing salary range string"""
        min_sal, max_sal = self.scorer._parse_salary_string("$50k-$70k")
        self.assertEqual(min_sal, 50000)
        self.assertEqual(max_sal, 70000)
    
    def test_parse_salary_string_single(self):
        """Test parsing single salary value"""
        min_sal, max_sal = self.scorer._parse_salary_string("$80,000")
        self.assertEqual(min_sal, 80000)
        self.assertEqual(max_sal, 80000)
    
    def test_parse_salary_string_with_text(self):
        """Test parsing salary with text"""
        min_sal, max_sal = self.scorer._parse_salary_string("80k per year")
        self.assertEqual(min_sal, 80000)
    
    def test_singleton_instance(self):
        """Test that get_job_scorer returns singleton"""
        scorer1 = get_job_scorer()
        scorer2 = get_job_scorer()
        self.assertEqual(id(scorer1), id(scorer2))


class TestScoringEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scorer = JobScorer()
    
    def test_very_high_salary(self):
        """Test job with very high salary"""
        job = {
            'title': 'CEO',
            'salary': {'min': 500000, 'max': 1000000}
        }
        prefs = {
            'salary_min': 50000,
            'salary_max': 100000
        }
        
        score = self.scorer._score_salary(job, prefs)
        self.assertGreater(score, 0)
    
    def test_zero_salary_range(self):
        """Test when user has zero salary range"""
        job = {
            'title': 'Test',
            'salary': {'min': 70000, 'max': 90000}
        }
        prefs = {
            'salary_min': 80000,
            'salary_max': 80000
        }
        
        score = self.scorer._score_salary(job, prefs)
        self.assertGreater(score, 0)
    
    def test_location_with_special_characters(self):
        """Test location with special characters"""
        job = {
            'title': 'Test',
            'location': 'São Paulo, Brazil'
        }
        prefs = {
            'location': 'São Paulo'
        }
        
        score = self.scorer._score_location(job, prefs)
        self.assertGreater(score, 50)
    
    def test_empty_job_description(self):
        """Test job with empty description"""
        job = {
            'title': 'Developer',
            'description': ''
        }
        prefs = {
            'job_titles': ['Developer']
        }
        
        result = self.scorer.score_job(job, prefs)
        self.assertGreater(result['overall_score'], 0)
    
    def test_unicode_in_job_title(self):
        """Test job with unicode characters"""
        job = {
            'title': 'Développeur Python',
            'description': 'French company'
        }
        prefs = {
            'job_titles': ['Python Developer']
        }
        
        result = self.scorer.score_job(job, prefs)
        self.assertGreaterEqual(result['overall_score'], 0)


class TestScoringIntegration(unittest.TestCase):
    """Integration tests for complete scoring workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scorer = JobScorer()
        self.extractor = get_keyword_extractor()
        
        self.resume_text = """
        Senior Software Engineer with 8 years of experience
        Technical Skills: Python, Django, Flask, JavaScript, React, Node.js
        Cloud: AWS, Docker, Kubernetes, CI/CD
        Databases: PostgreSQL, MongoDB, Redis
        """
        
        self.jobs = [
            {
                'id': 'excellent_match',
                'title': 'Senior Python Developer',
                'company': 'Tech Corp',
                'location': 'Remote',
                'salary': {'min': 90000, 'max': 130000},
                'job_type': 'Remote',
                'description': 'Senior role using Python, Django, AWS, Docker. PostgreSQL experience required.'
            },
            {
                'id': 'good_match',
                'title': 'Backend Developer',
                'company': 'Startup Inc',
                'location': 'San Francisco, CA',
                'salary': {'min': 80000, 'max': 120000},
                'job_type': 'Hybrid',
                'description': 'Backend development with Python and Node.js. AWS experience preferred.'
            },
            {
                'id': 'poor_match',
                'title': 'Java Developer',
                'company': 'Enterprise Co',
                'location': 'New York, NY',
                'salary': {'min': 60000, 'max': 80000},
                'job_type': 'Onsite',
                'description': 'Java, Spring Boot, and Oracle database experience required.'
            }
        ]
        
        self.user_prefs = {
            'name': 'Test User',
            'location': 'San Francisco',
            'salary_min': 85000,
            'salary_max': 125000,
            'job_titles': ['Python Developer', 'Backend Developer'],
            'job_types': ['Remote', 'Hybrid']
        }
    
    def test_full_scoring_workflow(self):
        """Test complete scoring workflow with resume"""
        resume_keywords = self.extractor.extract_resume_keywords(self.resume_text)
        scored_jobs = self.scorer.score_multiple_jobs(
            self.jobs, 
            self.user_prefs,
            resume_keywords
        )
        
        self.assertEqual(len(scored_jobs), 3)
        
        # Verify jobs are sorted by score
        scores = [job['score']['overall_score'] for job in scored_jobs]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Verify the excellent match has high score
        excellent = next(j for j in scored_jobs if j['id'] == 'excellent_match')
        self.assertGreater(excellent['score']['overall_score'], 70)
        self.assertEqual(excellent['score']['highlight'], 'white')
        
        # Verify the poor match has low score
        poor = next(j for j in scored_jobs if j['id'] == 'poor_match')
        self.assertLess(poor['score']['overall_score'], 60)
    
    def test_scoring_without_resume(self):
        """Test scoring workflow without resume"""
        scored_jobs = self.scorer.score_multiple_jobs(
            self.jobs,
            self.user_prefs
        )
        
        self.assertEqual(len(scored_jobs), 3)
        
        # All jobs should have scores
        for job in scored_jobs:
            self.assertIn('score', job)
            self.assertGreaterEqual(job['score']['overall_score'], 0)
            self.assertLessEqual(job['score']['overall_score'], 100)
    
    def test_statistics_calculation(self):
        """Test statistics for scored jobs"""
        resume_keywords = self.extractor.extract_resume_keywords(self.resume_text)
        scored_jobs = self.scorer.score_multiple_jobs(
            self.jobs,
            self.user_prefs,
            resume_keywords
        )
        
        stats = self.scorer.get_score_statistics(scored_jobs)
        
        self.assertEqual(stats['total_jobs'], 3)
        self.assertGreater(stats['average_score'], 0)
        self.assertGreater(stats['highest_score'], stats['lowest_score'])
        self.assertEqual(
            stats['red_count'] + stats['yellow_count'] + stats['white_count'],
            3
        )


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestJobScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestScoringEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestScoringIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
