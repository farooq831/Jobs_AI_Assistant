"""
Test suite for keyword extraction functionality (Task 5.1)
Tests the KeywordExtractor class and API endpoints.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keyword_extractor import KeywordExtractor, get_keyword_extractor
import unittest
from unittest.mock import patch, MagicMock


class TestKeywordExtractor(unittest.TestCase):
    """Test cases for KeywordExtractor class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are used by all tests."""
        cls.extractor = KeywordExtractor()
    
    def test_initialization(self):
        """Test that KeywordExtractor initializes correctly."""
        self.assertIsNotNone(self.extractor.nlp)
        print("✓ KeywordExtractor initialization successful")
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        text = "Visit https://example.com or email test@example.com for more info!!!"
        cleaned = self.extractor.preprocess_text(text)
        
        self.assertNotIn('https', cleaned)
        self.assertNotIn('@', cleaned)
        self.assertNotIn('!!!', cleaned)
        print(f"✓ Text preprocessing: '{text}' -> '{cleaned}'")
    
    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = """
        We are looking for a Senior Software Engineer with experience in Python, 
        JavaScript, and React. The ideal candidate should have strong problem-solving 
        skills and be proficient in database technologies like PostgreSQL and MongoDB.
        """
        
        keywords = self.extractor.extract_keywords(text, top_n=10)
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        
        # Check structure of keyword objects
        for kw in keywords:
            self.assertIn('keyword', kw)
            self.assertIn('count', kw)
            self.assertIn('type', kw)
        
        print(f"✓ Extracted {len(keywords)} keywords from job description")
        print(f"  Sample keywords: {[kw['keyword'] for kw in keywords[:5]]}")
    
    def test_extract_skills(self):
        """Test skill extraction."""
        text = """
        Required skills: Python, JavaScript, React, Node.js, Docker, Kubernetes, AWS.
        Soft skills: Leadership, communication, teamwork, problem solving.
        """
        
        skills = self.extractor.extract_skills(text)
        
        self.assertIn('technical_skills', skills)
        self.assertIn('soft_skills', skills)
        self.assertIsInstance(skills['technical_skills'], list)
        self.assertIsInstance(skills['soft_skills'], list)
        
        # Check that expected skills are found
        tech_skills_lower = [s.lower() for s in skills['technical_skills']]
        self.assertTrue(any('python' in s for s in tech_skills_lower))
        self.assertTrue(any('javascript' in s for s in tech_skills_lower))
        
        soft_skills_lower = [s.lower() for s in skills['soft_skills']]
        self.assertTrue(any('leadership' in s for s in soft_skills_lower))
        
        print(f"✓ Technical skills found: {skills['technical_skills']}")
        print(f"✓ Soft skills found: {skills['soft_skills']}")
    
    def test_categorize_keyword(self):
        """Test keyword categorization."""
        self.assertEqual(self.extractor._categorize_keyword('python'), 'technical')
        self.assertEqual(self.extractor._categorize_keyword('leadership'), 'soft_skill')
        self.assertEqual(self.extractor._categorize_keyword('company'), 'general')
        print("✓ Keyword categorization working correctly")
    
    def test_extract_job_keywords(self):
        """Test job keyword extraction."""
        job_data = {
            'title': 'Senior Python Developer',
            'description': """
            We are seeking a Senior Python Developer to join our team.
            
            Requirements:
            - 5+ years of Python experience
            - Strong knowledge of Django and Flask
            - Experience with AWS and Docker
            - Excellent problem-solving skills
            
            Responsibilities:
            - Design and develop scalable applications
            - Collaborate with cross-functional teams
            - Mentor junior developers
            """
        }
        
        result = self.extractor.extract_job_keywords(job_data)
        
        self.assertIn('all_keywords', result)
        self.assertIn('title_keywords', result)
        self.assertIn('technical_skills', result)
        self.assertIn('soft_skills', result)
        self.assertIn('keyword_count', result)
        
        self.assertGreater(len(result['all_keywords']), 0)
        self.assertGreater(len(result['technical_skills']), 0)
        
        print(f"✓ Job keywords extracted successfully")
        print(f"  Total keywords: {result['keyword_count']}")
        print(f"  Technical skills: {result['technical_skills']}")
        print(f"  Title keywords: {[kw['keyword'] for kw in result['title_keywords'][:3]]}")
    
    def test_extract_resume_keywords(self):
        """Test resume keyword extraction."""
        resume_text = """
        JOHN DOE
        Senior Software Engineer
        
        SUMMARY
        Experienced software engineer with 7+ years in full-stack development.
        Proficient in Python, JavaScript, React, and Node.js.
        
        TECHNICAL SKILLS
        Languages: Python, JavaScript, TypeScript, Java
        Frameworks: Django, Flask, React, Angular, Node.js
        Databases: PostgreSQL, MongoDB, Redis
        Cloud: AWS, Docker, Kubernetes
        
        EXPERIENCE
        Senior Software Engineer - Tech Company (2020-Present)
        - Led development of microservices architecture
        - Implemented CI/CD pipelines using Jenkins
        - Mentored team of 5 junior developers
        
        Software Engineer - Startup Inc (2017-2020)
        - Built REST APIs using Django and Flask
        - Developed responsive frontend using React
        - Optimized database queries improving performance by 40%
        """
        
        result = self.extractor.extract_resume_keywords(resume_text)
        
        self.assertIn('all_keywords', result)
        self.assertIn('technical_skills', result)
        self.assertIn('soft_skills', result)
        self.assertIn('keyword_count', result)
        
        self.assertGreater(len(result['all_keywords']), 0)
        self.assertGreater(len(result['technical_skills']), 0)
        
        print(f"✓ Resume keywords extracted successfully")
        print(f"  Total keywords: {result['keyword_count']}")
        print(f"  Technical skills: {result['technical_skills'][:10]}")
    
    def test_calculate_keyword_match(self):
        """Test keyword match calculation between job and resume."""
        job_keywords = {
            'technical_skills': ['python', 'django', 'postgresql', 'docker', 'aws'],
            'soft_skills': ['leadership', 'communication'],
            'all_keywords': [
                {'keyword': 'python', 'count': 5},
                {'keyword': 'django', 'count': 3},
                {'keyword': 'developer', 'count': 2}
            ]
        }
        
        resume_keywords = {
            'technical_skills': ['python', 'django', 'react', 'node.js'],
            'soft_skills': ['leadership', 'teamwork'],
            'all_keywords': [
                {'keyword': 'python', 'count': 8},
                {'keyword': 'developer', 'count': 4},
                {'keyword': 'react', 'count': 3}
            ]
        }
        
        result = self.extractor.calculate_keyword_match(job_keywords, resume_keywords)
        
        self.assertIn('technical_match', result)
        self.assertIn('soft_skills_match', result)
        self.assertIn('overall_match', result)
        
        # Check technical match
        tech_match = result['technical_match']
        self.assertIn('matched', tech_match)
        self.assertIn('missing', tech_match)
        self.assertIn('match_percentage', tech_match)
        self.assertIn('python', tech_match['matched'])
        self.assertIn('django', tech_match['matched'])
        self.assertIn('docker', tech_match['missing'])
        
        print(f"✓ Keyword match calculated successfully")
        print(f"  Technical match: {tech_match['match_percentage']}%")
        print(f"  Matched skills: {tech_match['matched']}")
        print(f"  Missing skills: {tech_match['missing']}")
    
    def test_empty_text_handling(self):
        """Test handling of empty or None text."""
        self.assertEqual(self.extractor.extract_keywords(""), [])
        self.assertEqual(self.extractor.extract_keywords(None), [])
        
        skills = self.extractor.extract_skills("")
        self.assertEqual(skills['technical_skills'], [])
        self.assertEqual(skills['soft_skills'], [])
        
        print("✓ Empty text handling works correctly")
    
    def test_bigram_extraction(self):
        """Test extraction of two-word phrases (bigrams)."""
        text = "We need a machine learning engineer with deep learning experience and data science skills."
        
        keywords = self.extractor.extract_keywords(text, include_bigrams=True)
        
        # Check for bigrams in results
        all_keywords = [kw['keyword'] for kw in keywords]
        has_bigram = any(' ' in kw for kw in all_keywords)
        
        self.assertTrue(has_bigram, "Should extract bigrams")
        print(f"✓ Bigram extraction working")
        print(f"  Extracted bigrams: {[kw for kw in all_keywords if ' ' in kw]}")
    
    def test_singleton_instance(self):
        """Test that get_keyword_extractor returns singleton instance."""
        instance1 = get_keyword_extractor()
        instance2 = get_keyword_extractor()
        
        self.assertIs(instance1, instance2)
        print("✓ Singleton pattern working correctly")


class TestKeywordExtractionAPI(unittest.TestCase):
    """Test cases for keyword extraction API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Import app here to avoid issues if spacy not installed
        from app import app as flask_app
        cls.app = flask_app
        cls.client = flask_app.test_client()
        cls.app.config['TESTING'] = True
    
    def test_extract_job_keywords_endpoint(self):
        """Test /api/extract-keywords/job endpoint."""
        data = {
            'title': 'Software Engineer',
            'description': 'Looking for a Python developer with Django experience.',
            'job_id': 'test-job-1'
        }
        
        response = self.client.post('/api/extract-keywords/job',
                                   json=data,
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertIn('keywords', json_data)
        self.assertEqual(json_data['job_id'], 'test-job-1')
        
        print("✓ Job keyword extraction endpoint working")
    
    def test_extract_job_keywords_missing_data(self):
        """Test job keyword endpoint with missing data."""
        response = self.client.post('/api/extract-keywords/job',
                                   json={},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        print("✓ Job keyword endpoint validates missing data")
    
    def test_extract_resume_keywords_endpoint(self):
        """Test /api/extract-keywords/resume endpoint."""
        data = {
            'resume_text': """
            Senior Software Engineer with 5+ years of experience in Python,
            JavaScript, React, and AWS. Strong problem-solving and leadership skills.
            Built scalable microservices and led development teams.
            """,
            'resume_id': 'test-resume-1'
        }
        
        response = self.client.post('/api/extract-keywords/resume',
                                   json=data,
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertIn('keywords', json_data)
        self.assertEqual(json_data['resume_id'], 'test-resume-1')
        
        keywords = json_data['keywords']
        self.assertIn('technical_skills', keywords)
        self.assertIn('soft_skills', keywords)
        
        print("✓ Resume keyword extraction endpoint working")
    
    def test_extract_resume_keywords_insufficient_text(self):
        """Test resume keyword endpoint with insufficient text."""
        data = {
            'resume_text': 'Too short'
        }
        
        response = self.client.post('/api/extract-keywords/resume',
                                   json=data,
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        print("✓ Resume keyword endpoint validates text length")
    
    def test_match_keywords_endpoint(self):
        """Test /api/match-keywords endpoint."""
        data = {
            'job_keywords': {
                'technical_skills': ['python', 'django', 'aws'],
                'soft_skills': ['leadership'],
                'all_keywords': [
                    {'keyword': 'python', 'count': 3},
                    {'keyword': 'developer', 'count': 2}
                ]
            },
            'resume_keywords': {
                'technical_skills': ['python', 'react'],
                'soft_skills': ['leadership', 'teamwork'],
                'all_keywords': [
                    {'keyword': 'python', 'count': 5},
                    {'keyword': 'engineer', 'count': 3}
                ]
            }
        }
        
        response = self.client.post('/api/match-keywords',
                                   json=data,
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertIn('match_result', json_data)
        
        match_result = json_data['match_result']
        self.assertIn('technical_match', match_result)
        self.assertIn('soft_skills_match', match_result)
        self.assertIn('overall_match', match_result)
        
        print("✓ Keyword matching endpoint working")
        print(f"  Technical match: {match_result['technical_match']['match_percentage']}%")


def run_tests():
    """Run all tests and display results."""
    print("=" * 70)
    print("KEYWORD EXTRACTION TEST SUITE (Task 5.1)")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKeywordExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestKeywordExtractionAPI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
