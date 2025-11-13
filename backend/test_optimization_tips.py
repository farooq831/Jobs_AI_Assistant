"""
Test suite for Task 6.3: Generate Optimization Tips
Tests resume optimization tip generation, formatting, and API endpoints.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import unittest
from resume_analyzer import get_resume_analyzer, ResumeAnalyzer


class TestOptimizationTips(unittest.TestCase):
    """Test optimization tips generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = get_resume_analyzer()
        
        # Sample resume with some issues
        self.weak_resume = """
        John Doe
        johndoe@email.com
        
        I am a software developer with experience in programming.
        I have worked on various projects and know several technologies.
        I am good at solving problems and working in teams.
        """
        
        # Sample complete resume
        self.strong_resume = """
        Jane Smith
        jane.smith@email.com
        (555) 123-4567
        linkedin.com/in/janesmith
        github.com/janesmith
        
        PROFESSIONAL SUMMARY
        Senior Software Engineer with 8+ years of experience in full-stack development,
        specializing in Python, JavaScript, React, and cloud technologies.
        
        EXPERIENCE
        Senior Software Engineer | Tech Corp | 2020 - Present
        - Led development of microservices architecture using Python, Docker, and Kubernetes
        - Managed team of 5 developers, mentoring junior engineers
        - Implemented CI/CD pipelines reducing deployment time by 60%
        - Technologies: Python, Django, React, PostgreSQL, AWS, Docker, Kubernetes
        
        Software Engineer | StartUp Inc | 2016 - 2020
        - Developed RESTful APIs using Flask and FastAPI
        - Built responsive web applications with React and TypeScript
        - Collaborated with product team using Agile methodologies
        - Technologies: Python, Flask, React, TypeScript, MongoDB, Redis
        
        EDUCATION
        Bachelor of Science in Computer Science | University of Technology | 2016
        
        SKILLS
        Programming Languages: Python, JavaScript, TypeScript, Java, SQL
        Frameworks: Django, Flask, FastAPI, React, Node.js, Express
        Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, GitLab CI
        Databases: PostgreSQL, MongoDB, Redis, MySQL
        Soft Skills: Leadership, Team Collaboration, Problem Solving, Communication
        
        CERTIFICATIONS
        - AWS Certified Solutions Architect
        - Certified Kubernetes Administrator
        
        PROJECTS
        E-commerce Platform (2021)
        - Built scalable microservices platform handling 100K+ daily users
        - Technologies: Python, Django, React, PostgreSQL, AWS
        """
        
        # Sample job descriptions
        self.job_descriptions = [
            """
            Senior Python Developer
            
            We are seeking a Senior Python Developer to join our team.
            
            Requirements:
            - 5+ years Python development experience
            - Strong experience with Django or Flask
            - Experience with Docker and Kubernetes
            - Knowledge of AWS cloud services
            - Experience with PostgreSQL or MySQL
            - Strong problem-solving skills
            - Excellent communication and teamwork
            - Agile development experience
            """,
            """
            Full Stack Engineer
            
            Join our team as a Full Stack Engineer!
            
            Requirements:
            - Python backend development (Django/Flask)
            - React and TypeScript frontend experience
            - RESTful API design and development
            - Docker containerization
            - AWS or cloud platform experience
            - Unit testing and test-driven development
            - Git version control
            - Strong leadership and collaboration skills
            """
        ]
    
    def test_generate_basic_tips(self):
        """Test basic tip generation"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume
        )
        
        self.assertIn('overall_assessment', tips)
        self.assertIn('critical_tips', tips)
        self.assertIn('important_tips', tips)
        self.assertIn('optional_tips', tips)
        self.assertIn('summary', tips)
        self.assertIn('action_items', tips)
        
        # Weak resume should have low score
        score = tips['overall_assessment']['strength_score']
        self.assertLess(score, 70)
        
        # Should have some critical tips
        self.assertGreater(len(tips['critical_tips']), 0)
    
    def test_strong_resume_tips(self):
        """Test tips for strong resume"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.strong_resume
        )
        
        score = tips['overall_assessment']['strength_score']
        
        # Strong resume should have higher score
        self.assertGreater(score, 60)
        
        # Should have strengths identified
        self.assertGreater(len(tips['overall_assessment']['key_strengths']), 0)
    
    def test_tips_with_job_descriptions(self):
        """Test tips generation with job descriptions"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume,
            job_descriptions=self.job_descriptions
        )
        
        # Should have job-specific tips
        has_job_tips = any(
            tip.get('category') == 'job_match' 
            for tip in tips['critical_tips'] + tips['important_tips']
        )
        
        self.assertTrue(has_job_tips)
    
    def test_tips_with_user_preferences(self):
        """Test tips with user preferences"""
        user_prefs = {
            'job_titles': ['Python Developer', 'Backend Engineer'],
            'location': 'San Francisco, CA',
            'job_types': ['Remote'],
            'salary_min': 100000,
            'salary_max': 150000
        }
        
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume,
            user_preferences=user_prefs
        )
        
        # Should have tailoring tips
        self.assertGreater(len(tips.get('tailoring_tips', [])), 0)
    
    def test_structural_tips(self):
        """Test structural tips identification"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume
        )
        
        # Weak resume should have structural issues
        structural_tips = [
            tip for tip in tips['critical_tips'] + tips['important_tips']
            if tip.get('category') == 'structure'
        ]
        
        self.assertGreater(len(structural_tips), 0)
    
    def test_contact_info_tips(self):
        """Test contact information tips"""
        resume_no_contact = "I am a developer with Python skills."
        
        tips = self.analyzer.generate_optimization_tips(
            resume_text=resume_no_contact
        )
        
        # Should have critical tip about missing email
        contact_tips = [
            tip for tip in tips['critical_tips']
            if tip.get('category') == 'contact'
        ]
        
        self.assertGreater(len(contact_tips), 0)
    
    def test_keyword_tips(self):
        """Test keyword-related tips"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume
        )
        
        # Should have keyword tips
        keyword_tips = [
            tip for tip in tips['important_tips']
            if tip.get('category') == 'keywords'
        ]
        
        self.assertGreater(len(keyword_tips), 0)
    
    def test_overall_assessment(self):
        """Test overall assessment calculation"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.strong_resume
        )
        
        assessment = tips['overall_assessment']
        
        self.assertIn('strength_score', assessment)
        self.assertIn('key_strengths', assessment)
        self.assertIn('areas_for_improvement', assessment)
        
        # Score should be 0-100
        score = assessment['strength_score']
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_action_items_generation(self):
        """Test action items generation"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume
        )
        
        self.assertGreater(len(tips['action_items']), 0)
        
        # Action items should have required fields
        for action in tips['action_items']:
            self.assertIn('priority', action)
            self.assertIn('action', action)
            self.assertIn('category', action)
    
    def test_summary_generation(self):
        """Test summary generation"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume
        )
        
        summary = tips['summary']
        
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 10)
        
        # Should mention score
        self.assertIn('score', summary.lower())
    
    def test_tip_prioritization(self):
        """Test that tips are properly prioritized"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume,
            job_descriptions=self.job_descriptions
        )
        
        # All critical tips should have high impact
        for tip in tips['critical_tips']:
            self.assertIn(tip.get('priority'), ['critical'])
        
        # All important tips should have priority set
        for tip in tips['important_tips']:
            self.assertIn(tip.get('priority'), ['important'])
    
    def test_format_for_excel(self):
        """Test Excel formatting"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume
        )
        
        excel_rows = self.analyzer.format_tips_for_excel(tips)
        
        # Should have rows
        self.assertGreater(len(excel_rows), 0)
        
        # First row should be summary
        self.assertEqual(excel_rows[0]['Priority'], 'SUMMARY')
        
        # All rows should have required columns
        for row in excel_rows:
            self.assertIn('Priority', row)
            self.assertIn('Category', row)
            self.assertIn('Title', row)
            self.assertIn('Description', row)
            self.assertIn('Action', row)
            self.assertIn('Impact', row)
    
    def test_format_for_frontend(self):
        """Test frontend formatting"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.strong_resume
        )
        
        frontend_data = self.analyzer.format_tips_for_frontend(tips)
        
        # Check structure
        self.assertIn('metadata', frontend_data)
        self.assertIn('score', frontend_data)
        self.assertIn('summary', frontend_data)
        self.assertIn('tips_by_priority', frontend_data)
        self.assertIn('action_plan', frontend_data)
        self.assertIn('statistics', frontend_data)
        
        # Check score object
        score_obj = frontend_data['score']
        self.assertIn('value', score_obj)
        self.assertIn('level', score_obj)
        self.assertIn('color', score_obj)
        
        # Check tips by priority
        tips_by_priority = frontend_data['tips_by_priority']
        self.assertIn('critical', tips_by_priority)
        self.assertIn('important', tips_by_priority)
        self.assertIn('optional', tips_by_priority)
        
        # Each priority should have count and items
        for priority in ['critical', 'important', 'optional']:
            self.assertIn('count', tips_by_priority[priority])
            self.assertIn('items', tips_by_priority[priority])
            self.assertIn('badge_color', tips_by_priority[priority])
            self.assertIn('icon', tips_by_priority[priority])
    
    def test_score_level_mapping(self):
        """Test score level descriptions"""
        test_cases = [
            (85, 'Excellent'),
            (70, 'Good'),
            (50, 'Fair'),
            (30, 'Needs Improvement')
        ]
        
        for score, expected_level in test_cases:
            level = self.analyzer._get_score_level(score)
            self.assertEqual(level, expected_level)
    
    def test_score_color_mapping(self):
        """Test score color codes"""
        test_cases = [
            (85, '#28a745'),  # Green
            (70, '#ffc107'),  # Yellow
            (50, '#fd7e14'),  # Orange
            (30, '#dc3545')   # Red
        ]
        
        for score, expected_color in test_cases:
            color = self.analyzer._get_score_color(score)
            self.assertEqual(color, expected_color)
    
    def test_comprehensive_tips(self):
        """Test comprehensive tip generation with all inputs"""
        user_prefs = {
            'job_titles': ['Python Developer'],
            'location': 'Remote',
            'job_types': ['Remote']
        }
        
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.strong_resume,
            job_descriptions=self.job_descriptions,
            user_preferences=user_prefs
        )
        
        # Should have all sections populated
        self.assertGreater(tips['overall_assessment']['strength_score'], 0)
        
        # Should have various tip categories
        total_tips = (
            len(tips['critical_tips']) +
            len(tips['important_tips']) +
            len(tips['optional_tips'])
        )
        
        # Strong resume with job matching should have some tips
        self.assertGreater(total_tips, 0)
    
    def test_timestamp_formatting(self):
        """Test timestamp formatting"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.strong_resume
        )
        
        # Should have ISO timestamp
        self.assertIn('generated_at', tips)
        
        # Test readable format conversion
        frontend_data = self.analyzer.format_tips_for_frontend(tips)
        readable = frontend_data['metadata']['timestamp_readable']
        
        self.assertIsInstance(readable, str)
        self.assertGreater(len(readable), 10)
    
    def test_empty_resume_handling(self):
        """Test handling of empty/minimal resume"""
        minimal_resume = "John Doe"
        
        tips = self.analyzer.generate_optimization_tips(
            resume_text=minimal_resume
        )
        
        # Should have many critical issues
        self.assertGreater(len(tips['critical_tips']), 3)
        
        # Score should be very low
        self.assertLess(tips['overall_assessment']['strength_score'], 40)
    
    def test_job_coverage_tips(self):
        """Test job coverage-based tips"""
        tips = self.analyzer.generate_optimization_tips(
            resume_text=self.weak_resume,
            job_descriptions=self.job_descriptions
        )
        
        # Should have coverage-related tips
        coverage_tips = [
            tip for tip in tips['critical_tips'] + tips['important_tips']
            if tip.get('category') == 'coverage'
        ]
        
        # Weak resume should have coverage issues
        self.assertGreater(len(coverage_tips), 0)


class TestOptimizationTipsAPI(unittest.TestCase):
    """Test optimization tips API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test Flask app"""
        # Import here to avoid circular imports
        import app as flask_app
        cls.app = flask_app.app
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        
        # Add a test resume
        cls.test_resume_text = """
        John Developer
        john@email.com
        
        Python developer with 3 years experience.
        Skills: Python, JavaScript, SQL
        """
        
        # Store resume
        flask_app.resume_store[1] = {
            'id': 1,
            'filename': 'test_resume.pdf',
            'full_text': cls.test_resume_text,
            'extracted_text': cls.test_resume_text
        }
    
    def test_generate_optimization_tips_endpoint(self):
        """Test POST /api/optimization-tips"""
        response = self.client.post('/api/optimization-tips', json={
            'resume_text': self.test_resume_text
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['success'])
        self.assertIn('tips', data)
        self.assertIn('overall_assessment', data['tips'])
    
    def test_optimization_tips_with_resume_id(self):
        """Test using resume_id"""
        response = self.client.post('/api/optimization-tips', json={
            'resume_id': 1
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['success'])
    
    def test_optimization_tips_frontend_format(self):
        """Test frontend format"""
        response = self.client.post('/api/optimization-tips', json={
            'resume_id': 1,
            'format': 'frontend'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['success'])
        self.assertIn('score', data['tips'])
        self.assertIn('tips_by_priority', data['tips'])
    
    def test_optimization_tips_excel_format(self):
        """Test Excel format"""
        response = self.client.post('/api/optimization-tips', json={
            'resume_id': 1,
            'format': 'excel'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['success'])
        self.assertIsInstance(data['tips'], list)
        
        # Should have rows with required columns
        if len(data['tips']) > 0:
            self.assertIn('Priority', data['tips'][0])
            self.assertIn('Category', data['tips'][0])
    
    def test_get_optimization_tips_for_resume(self):
        """Test GET /api/optimization-tips/<resume_id>"""
        response = self.client.get('/api/optimization-tips/1')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['resume_id'], 1)
    
    def test_quick_optimization_summary(self):
        """Test GET /api/optimization-tips/quick-summary/<resume_id>"""
        response = self.client.get('/api/optimization-tips/quick-summary/1')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['success'])
        self.assertIn('quick_summary', data)
        
        summary = data['quick_summary']
        self.assertIn('score', summary)
        self.assertIn('summary', summary)
        self.assertIn('top_actions', summary)
    
    def test_invalid_resume_id(self):
        """Test with invalid resume ID"""
        response = self.client.get('/api/optimization-tips/999')
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        
        self.assertFalse(data['success'])
    
    def test_missing_required_data(self):
        """Test with missing required data"""
        response = self.client.post('/api/optimization-tips', json={})
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        
        self.assertFalse(data['success'])
    
    def test_batch_optimization_tips(self):
        """Test POST /api/batch-optimization-tips"""
        response = self.client.post('/api/batch-optimization-tips', json={
            'resume_ids': [1],
            'format': 'frontend'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['success'])
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOptimizationTips))
    suite.addTests(loader.loadTestsFromTestCase(TestOptimizationTipsAPI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY - Task 6.3: Generate Optimization Tips")
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
