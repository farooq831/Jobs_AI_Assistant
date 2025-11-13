"""
Test Suite for Resume Analyzer Module (Task 6.1)
Tests resume text extraction, skill extraction, and job matching functionality.
"""

import unittest
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resume_analyzer import ResumeAnalyzer, get_resume_analyzer
from keyword_extractor import get_keyword_extractor


class TestResumeAnalyzer(unittest.TestCase):
    """Test cases for ResumeAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = get_resume_analyzer()
        self.extractor = get_keyword_extractor()
        
        # Sample resume text
        self.sample_resume = """
        John Doe
        Email: john.doe@email.com
        Phone: (555) 123-4567
        LinkedIn: linkedin.com/in/johndoe
        GitHub: github.com/johndoe
        
        PROFESSIONAL SUMMARY
        Experienced Software Engineer with 5+ years of expertise in Python, JavaScript, 
        and cloud technologies. Strong leadership and problem-solving skills.
        
        TECHNICAL SKILLS
        - Programming Languages: Python, JavaScript, TypeScript, Java
        - Web Frameworks: React, Angular, Django, Flask, Node.js
        - Databases: PostgreSQL, MongoDB, Redis
        - Cloud Platforms: AWS, Docker, Kubernetes
        - Tools: Git, Jenkins, CI/CD
        - Machine Learning: TensorFlow, scikit-learn, pandas
        
        PROFESSIONAL EXPERIENCE
        
        Senior Software Engineer - Tech Corp (2020-Present)
        - Led development of microservices architecture using Python and Docker
        - Implemented CI/CD pipelines with Jenkins
        - Mentored junior developers and conducted code reviews
        - Improved system performance by 40%
        
        Software Engineer - StartupXYZ (2018-2020)
        - Developed full-stack web applications using React and Node.js
        - Designed and implemented RESTful APIs
        - Worked in agile environment with scrum methodology
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2018
        
        CERTIFICATIONS
        - AWS Certified Solutions Architect
        - Certified Kubernetes Administrator
        
        ACHIEVEMENTS
        - Won Best Innovation Award 2021
        - Published research paper on machine learning optimization
        """
        
        # Sample job posting
        self.sample_job = {
            'id': 'job-123',
            'title': 'Senior Python Developer',
            'company': 'Tech Innovations Inc',
            'location': 'San Francisco, CA',
            'description': """
            We are seeking a Senior Python Developer to join our growing team.
            
            Requirements:
            - 5+ years of Python development experience
            - Strong experience with Django or Flask
            - Knowledge of AWS cloud services
            - Experience with Docker and Kubernetes
            - PostgreSQL database skills
            - Git version control
            - CI/CD pipeline experience
            - Machine learning experience is a plus
            - Excellent problem-solving and communication skills
            - Team leadership experience preferred
            """
        }
        
        # Sample skills list
        self.sample_skills = [
            'Python', 'JavaScript', 'React', 'Django', 'PostgreSQL',
            'AWS', 'Docker', 'Git', 'Machine Learning', 'Leadership',
            'Communication', 'Problem Solving', 'TensorFlow'
        ]
    
    def test_extract_resume_keywords_success(self):
        """Test successful resume keyword extraction."""
        result = self.analyzer.extract_resume_keywords(self.sample_resume)
        
        # Check structure
        self.assertIn('all_keywords', result)
        self.assertIn('technical_skills', result)
        self.assertIn('soft_skills', result)
        self.assertIn('sections_found', result)
        self.assertIn('contact_info', result)
        self.assertIn('experience_indicators', result)
        
        # Check keywords were extracted
        self.assertGreater(len(result['all_keywords']), 0)
        self.assertGreater(len(result['technical_skills']), 0)
        
        # Check specific technical skills
        self.assertIn('python', result['technical_skills'])
        self.assertIn('javascript', result['technical_skills'])
        
        # Check word count
        self.assertGreater(result['word_count'], 100)
    
    def test_extract_resume_keywords_short_text(self):
        """Test that short resume text raises error."""
        with self.assertRaises(ValueError):
            self.analyzer.extract_resume_keywords("Too short")
    
    def test_extract_skills_from_list(self):
        """Test extracting skills from a direct list."""
        result = self.analyzer.extract_skills_from_list(self.sample_skills)
        
        # Check structure
        self.assertIn('total_skills', result)
        self.assertIn('technical_skills', result)
        self.assertIn('soft_skills', result)
        self.assertIn('general_skills', result)
        self.assertIn('all_skills', result)
        
        # Check counts
        self.assertEqual(result['total_skills'], len(self.sample_skills))
        
        # Check categorization
        self.assertIn('Python', result['technical_skills'])
        self.assertIn('Leadership', result['soft_skills'])
        
        # Check all skills are present
        self.assertEqual(len(result['all_skills']), len(set(self.sample_skills)))
    
    def test_extract_skills_from_empty_list(self):
        """Test that empty skills list raises error."""
        with self.assertRaises(ValueError):
            self.analyzer.extract_skills_from_list([])
    
    def test_identify_sections(self):
        """Test resume section identification."""
        result = self.analyzer.extract_resume_keywords(self.sample_resume)
        sections = result['sections_found']
        
        # Check that key sections are found
        self.assertTrue(sections['education'])
        self.assertTrue(sections['experience'])
        self.assertTrue(sections['skills'])
        self.assertTrue(sections['certifications'])
        self.assertTrue(sections['achievements'])
    
    def test_extract_contact_info(self):
        """Test contact information extraction."""
        result = self.analyzer.extract_resume_keywords(self.sample_resume)
        contact = result['contact_info']
        
        # Check email
        self.assertIsNotNone(contact['email'])
        self.assertEqual(contact['email'], 'john.doe@email.com')
        
        # Check phone
        self.assertIsNotNone(contact['phone'])
        
        # Check LinkedIn
        self.assertIsNotNone(contact['linkedin'])
        self.assertIn('linkedin.com/in/johndoe', contact['linkedin'])
        
        # Check GitHub
        self.assertIsNotNone(contact['github'])
        self.assertIn('github.com/johndoe', contact['github'])
    
    def test_analyze_experience_level(self):
        """Test experience level analysis."""
        result = self.analyzer.extract_resume_keywords(self.sample_resume)
        experience = result['experience_indicators']
        
        # Check structure
        self.assertIn('years_mentioned_count', experience)
        self.assertIn('senior_indicators', experience)
        self.assertIn('mid_indicators', experience)
        self.assertIn('junior_indicators', experience)
        self.assertIn('estimated_level', experience)
        
        # Check that senior level is detected (has "Senior" in title)
        self.assertGreater(experience['senior_indicators'], 0)
        self.assertEqual(experience['estimated_level'], 'senior')
    
    def test_compare_resume_with_job(self):
        """Test comparing resume with job posting."""
        # Extract keywords from resume and job
        resume_keywords = self.analyzer.extract_resume_keywords(self.sample_resume)
        job_keywords = self.extractor.extract_job_keywords(self.sample_job)
        
        # Compare
        comparison = self.analyzer.compare_resume_with_job(resume_keywords, job_keywords)
        
        # Check structure
        self.assertIn('match_result', comparison)
        self.assertIn('critical_missing_keywords', comparison)
        self.assertIn('weighted_match_score', comparison)
        self.assertIn('match_level', comparison)
        self.assertIn('recommendations', comparison)
        
        # Check score is reasonable
        self.assertGreaterEqual(comparison['weighted_match_score'], 0)
        self.assertLessEqual(comparison['weighted_match_score'], 100)
        
        # Check match level
        self.assertIn(comparison['match_level'], ['poor', 'fair', 'good', 'excellent'])
        
        # Check recommendations are provided
        self.assertIsInstance(comparison['recommendations'], list)
    
    def test_match_level_calculation(self):
        """Test match level calculation for different scores."""
        # Excellent match
        self.assertEqual(self.analyzer._get_match_level(80), 'excellent')
        
        # Good match
        self.assertEqual(self.analyzer._get_match_level(65), 'good')
        
        # Fair match
        self.assertEqual(self.analyzer._get_match_level(50), 'fair')
        
        # Poor match
        self.assertEqual(self.analyzer._get_match_level(30), 'poor')
    
    def test_get_skill_categories(self):
        """Test getting skill categories."""
        categories = self.analyzer.get_skill_categories()
        
        # Check structure
        self.assertIn('technical_skills_examples', categories)
        self.assertIn('soft_skills_examples', categories)
        
        # Check we have examples
        self.assertGreater(len(categories['technical_skills_examples']), 0)
        self.assertGreater(len(categories['soft_skills_examples']), 0)
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated appropriately."""
        # Create a job with skills not in resume
        job_with_missing_skills = {
            'title': 'Rust Developer',
            'description': 'Looking for expert in Rust programming and blockchain technology.'
        }
        
        resume_keywords = self.analyzer.extract_resume_keywords(self.sample_resume)
        job_keywords = self.extractor.extract_job_keywords(job_with_missing_skills)
        
        comparison = self.analyzer.compare_resume_with_job(resume_keywords, job_keywords)
        
        # Should have recommendations due to low match
        self.assertGreater(len(comparison['recommendations']), 0)
    
    def test_high_match_scenario(self):
        """Test scenario with high resume-job match."""
        # Create a job that matches resume well
        matching_job = {
            'title': 'Senior Python Engineer',
            'description': """
            Looking for Senior Python Engineer with React, Django, AWS, Docker,
            Kubernetes, PostgreSQL, machine learning, leadership, and problem-solving skills.
            """
        }
        
        resume_keywords = self.analyzer.extract_resume_keywords(self.sample_resume)
        job_keywords = self.extractor.extract_job_keywords(matching_job)
        
        comparison = self.analyzer.compare_resume_with_job(resume_keywords, job_keywords)
        
        # Should have high match score
        self.assertGreater(comparison['weighted_match_score'], 50)
    
    def test_singleton_pattern(self):
        """Test that get_resume_analyzer returns singleton."""
        analyzer1 = get_resume_analyzer()
        analyzer2 = get_resume_analyzer()
        
        self.assertIs(analyzer1, analyzer2)
    
    def test_multiple_resume_analysis(self):
        """Test analyzing multiple different resumes."""
        resumes = [
            "Software developer with Python and Java experience. 5 years in web development.",
            "Data scientist with expertise in machine learning, TensorFlow, and Python. PhD in Computer Science.",
            "Junior developer fresh graduate with knowledge of JavaScript, React, and Node.js."
        ]
        
        # Pad resumes to meet minimum length
        resumes = [r + " " * (50 - len(r)) if len(r) < 50 else r for r in resumes]
        
        for resume in resumes:
            result = self.analyzer.extract_resume_keywords(resume)
            
            # All should extract successfully
            self.assertIn('all_keywords', result)
            self.assertIn('technical_skills', result)
    
    def test_special_characters_handling(self):
        """Test handling of special characters in resume."""
        resume_with_special = """
        Developer with C++, C#, .NET experience.
        Email: test@example.com
        Skills: node.js, vue.js, react.js
        """ + " " * 200  # Pad to meet minimum length
        
        result = self.analyzer.extract_resume_keywords(resume_with_special)
        
        # Should extract successfully without errors
        self.assertIsNotNone(result)
        self.assertIn('all_keywords', result)


class TestResumeAnalyzerIntegration(unittest.TestCase):
    """Integration tests for resume analyzer with other modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = get_resume_analyzer()
        self.extractor = get_keyword_extractor()
    
    def test_end_to_end_workflow(self):
        """Test complete workflow: upload -> analyze -> compare -> recommendations."""
        # Sample resume
        resume = """
        Software Engineer
        john@example.com
        
        SKILLS
        Python, Django, PostgreSQL, AWS, Docker, Git
        
        EXPERIENCE
        Software Engineer at TechCo (2019-2023)
        - Developed web applications using Django
        - Deployed applications on AWS
        - Used Docker for containerization
        """ + " " * 200
        
        # Sample job
        job = {
            'title': 'Python Developer',
            'description': 'Looking for Python developer with Django, AWS, and Docker experience.'
        }
        
        # Step 1: Extract resume keywords
        resume_keywords = self.analyzer.extract_resume_keywords(resume)
        self.assertIsNotNone(resume_keywords)
        
        # Step 2: Extract job keywords
        job_keywords = self.extractor.extract_job_keywords(job)
        self.assertIsNotNone(job_keywords)
        
        # Step 3: Compare and get recommendations
        comparison = self.analyzer.compare_resume_with_job(resume_keywords, job_keywords)
        self.assertIsNotNone(comparison)
        self.assertIn('recommendations', comparison)
        
        # Should have good match
        self.assertGreater(comparison['weighted_match_score'], 40)
    
    def test_skills_list_integration(self):
        """Test skills list extraction integrated with job matching."""
        skills = ['Python', 'Django', 'React', 'AWS', 'Leadership']
        
        # Extract and categorize
        categorized = self.analyzer.extract_skills_from_list(skills)
        
        # Should have technical and soft skills
        self.assertGreater(len(categorized['technical_skills']), 0)
        self.assertGreater(len(categorized['soft_skills']), 0)


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestResumeAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestResumeAnalyzerIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
