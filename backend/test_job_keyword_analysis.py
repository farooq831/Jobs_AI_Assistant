"""
Test Suite for Task 6.2: Analyze Job Keywords
Tests the functionality of analyzing high-frequency keywords across job postings
and identifying missing keywords from resumes.
"""

import unittest
from resume_analyzer import get_resume_analyzer


class TestJobKeywordAnalysis(unittest.TestCase):
    """Test cases for job keyword analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = get_resume_analyzer()
        
        # Sample resume text
        self.resume_text = """
        John Doe
        Software Engineer
        john.doe@email.com | 555-0123 | linkedin.com/in/johndoe
        
        SKILLS
        Python, JavaScript, React, Node.js, SQL, Git, Agile, Problem Solving
        
        EXPERIENCE
        Senior Software Engineer | Tech Corp | 2020-Present
        - Developed web applications using React and Node.js
        - Led team of 5 developers in agile environment
        - Implemented REST APIs and microservices
        
        Software Developer | StartupXYZ | 2018-2020
        - Built full-stack applications with Python and JavaScript
        - Collaborated with cross-functional teams
        - Improved application performance by 40%
        
        EDUCATION
        BS in Computer Science | University of Tech | 2018
        """
        
        # Sample job descriptions
        self.job_descriptions = [
            """
            Senior Software Engineer
            We are seeking a skilled Senior Software Engineer with expertise in Python, React, 
            and AWS. Must have experience with Docker, Kubernetes, and CI/CD pipelines.
            Strong communication and leadership skills required.
            Responsibilities include designing microservices architecture and mentoring junior developers.
            """,
            """
            Full Stack Developer
            Looking for a Full Stack Developer proficient in Python, JavaScript, React, and Node.js.
            Experience with AWS, Docker, and PostgreSQL is essential.
            Must have strong problem-solving skills and ability to work in agile teams.
            Knowledge of REST APIs and GraphQL preferred.
            """,
            """
            Backend Engineer
            Backend Engineer needed with strong Python and Node.js skills.
            Experience with AWS, Kubernetes, PostgreSQL, and Redis required.
            Must have experience with CI/CD, Docker, and microservices architecture.
            Excellent communication and teamwork skills necessary.
            """,
            """
            Software Engineer
            We need a Software Engineer with Python, React, and AWS experience.
            Docker, Kubernetes, and agile methodology knowledge required.
            Strong analytical and problem-solving abilities.
            Experience with cloud infrastructure and DevOps practices.
            """
        ]
    
    def test_analyze_job_keywords_basic(self):
        """Test basic job keyword analysis."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text,
            top_n=20
        )
        
        # Check structure
        self.assertIn('analysis_summary', result)
        self.assertIn('high_frequency_keywords', result)
        self.assertIn('missing_keywords', result)
        self.assertIn('recommendations', result)
        
        # Check analysis summary
        summary = result['analysis_summary']
        self.assertEqual(summary['total_jobs_analyzed'], 4)
        self.assertGreater(summary['total_unique_technical_keywords'], 0)
        self.assertGreater(summary['total_unique_soft_keywords'], 0)
    
    def test_high_frequency_keywords_identification(self):
        """Test identification of high-frequency keywords."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text,
            top_n=15
        )
        
        high_freq = result['high_frequency_keywords']
        
        # Check technical skills
        tech_skills = high_freq['technical_skills']
        self.assertIsInstance(tech_skills, list)
        self.assertLessEqual(len(tech_skills), 15)
        
        # Each keyword should have required fields
        for skill in tech_skills:
            self.assertIn('keyword', skill)
            self.assertIn('frequency', skill)
            self.assertIn('percentage', skill)
            self.assertIn('in_resume', skill)
        
        # Python should be high frequency (appears in all 4 jobs)
        python_skills = [s for s in tech_skills if 'python' in s['keyword'].lower()]
        if python_skills:
            self.assertEqual(python_skills[0]['frequency'], 4)
            self.assertEqual(python_skills[0]['percentage'], 100.0)
    
    def test_missing_critical_keywords(self):
        """Test identification of missing critical keywords."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text,
            top_n=20
        )
        
        missing = result['missing_keywords']
        
        # Check structure
        self.assertIn('critical_technical', missing)
        self.assertIn('important_technical', missing)
        self.assertIn('critical_soft_skills', missing)
        self.assertIn('important_soft_skills', missing)
        
        # AWS, Docker, Kubernetes should be critical missing (appear in all jobs)
        critical_tech = missing['critical_technical']
        critical_keywords = [k['keyword'] for k in critical_tech]
        
        # These keywords appear frequently but are not in resume
        common_missing = ['aws', 'docker', 'kubernetes']
        for keyword in common_missing:
            # Check if any critical missing keyword contains these terms
            found = any(keyword in kw.lower() for kw in critical_keywords)
            self.assertTrue(found, f"{keyword} should be in critical missing keywords")
    
    def test_missing_keywords_frequency_threshold(self):
        """Test that missing keywords respect frequency thresholds."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text,
            top_n=30
        )
        
        missing = result['missing_keywords']
        
        # Critical keywords should have >=50% frequency
        for keyword in missing['critical_technical']:
            self.assertGreaterEqual(keyword['percentage'], 50)
            self.assertFalse(keyword['in_resume'])
        
        # Important keywords should have 30-50% frequency
        for keyword in missing['important_technical']:
            self.assertGreaterEqual(keyword['percentage'], 30)
            self.assertLess(keyword['percentage'], 50)
            self.assertFalse(keyword['in_resume'])
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text
        )
        
        recommendations = result['recommendations']
        
        # Should have recommendations
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Each recommendation should be a string
        for rec in recommendations:
            self.assertIsInstance(rec, str)
            self.assertGreater(len(rec), 0)
    
    def test_coverage_calculation(self):
        """Test coverage percentage calculation."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text
        )
        
        summary = result['analysis_summary']
        
        # Check coverage percentages are valid
        self.assertGreaterEqual(summary['technical_coverage_percentage'], 0)
        self.assertLessEqual(summary['technical_coverage_percentage'], 100)
        self.assertGreaterEqual(summary['soft_skills_coverage_percentage'], 0)
        self.assertLessEqual(summary['soft_skills_coverage_percentage'], 100)
    
    def test_single_job_analysis(self):
        """Test analysis with a single job description."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=[self.job_descriptions[0]],
            resume_text=self.resume_text,
            top_n=10
        )
        
        summary = result['analysis_summary']
        self.assertEqual(summary['total_jobs_analyzed'], 1)
        self.assertGreater(len(result['high_frequency_keywords']['technical_skills']), 0)
    
    def test_empty_job_descriptions_error(self):
        """Test that empty job descriptions raise error."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze_job_keywords(
                job_descriptions=[],
                resume_text=self.resume_text
            )
    
    def test_no_resume_error(self):
        """Test that missing resume data raises error."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze_job_keywords(
                job_descriptions=self.job_descriptions,
                resume_text=None,
                resume_keywords=None
            )
    
    def test_top_n_parameter(self):
        """Test that top_n parameter limits results correctly."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text,
            top_n=5
        )
        
        tech_skills = result['high_frequency_keywords']['technical_skills']
        self.assertLessEqual(len(tech_skills), 5)
    
    def test_in_resume_flag_accuracy(self):
        """Test that in_resume flag is accurate."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text,
            top_n=30
        )
        
        high_freq = result['high_frequency_keywords']['technical_skills']
        
        # Python is in resume
        python_skills = [s for s in high_freq if 'python' in s['keyword'].lower()]
        if python_skills:
            self.assertTrue(python_skills[0]['in_resume'])
        
        # React is in resume
        react_skills = [s for s in high_freq if 'react' in s['keyword'].lower()]
        if react_skills:
            self.assertTrue(react_skills[0]['in_resume'])
    
    def test_soft_skills_analysis(self):
        """Test soft skills are analyzed separately."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text,
            top_n=20
        )
        
        soft_skills = result['high_frequency_keywords']['soft_skills']
        
        # Should have soft skills
        self.assertIsInstance(soft_skills, list)
        
        # Common soft skills should appear
        soft_skill_keywords = [s['keyword'] for s in soft_skills]
        
        # Check for common soft skills in job descriptions
        common_soft = ['communication', 'leadership', 'problem solving', 'teamwork']
        found_any = any(
            any(common in keyword.lower() for keyword in soft_skill_keywords)
            for common in common_soft
        )
        self.assertTrue(found_any, "Should find common soft skills")
    
    def test_multiple_job_frequency_aggregation(self):
        """Test that frequencies are correctly aggregated across jobs."""
        # Create jobs where AWS appears in different frequencies
        custom_jobs = [
            "Python and AWS experience required",
            "Python and Docker needed",
            "AWS and Kubernetes essential",
            "Python, AWS, Docker, and Kubernetes required"
        ]
        
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=custom_jobs,
            resume_text="I know Python",
            top_n=10
        )
        
        tech_skills = result['high_frequency_keywords']['technical_skills']
        
        # AWS appears in 3 out of 4 jobs = 75%
        aws_skills = [s for s in tech_skills if 'aws' in s['keyword'].lower()]
        if aws_skills:
            self.assertEqual(aws_skills[0]['frequency'], 3)
            self.assertEqual(aws_skills[0]['percentage'], 75.0)
    
    def test_recommendations_priority_levels(self):
        """Test that recommendations include priority indicators."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text
        )
        
        recommendations = result['recommendations']
        
        # Check for priority indicators in recommendations
        has_priority = any(
            '🔴' in rec or '🟡' in rec or '✅' in rec or '⚠️' in rec or '🎯' in rec
            for rec in recommendations
        )
        self.assertTrue(has_priority, "Recommendations should include priority indicators")
    
    def test_general_keywords_analysis(self):
        """Test general keywords analysis."""
        result = self.analyzer.analyze_job_keywords(
            job_descriptions=self.job_descriptions,
            resume_text=self.resume_text,
            top_n=15
        )
        
        general = result['high_frequency_keywords']['general_keywords']
        
        # Should have general keywords
        self.assertIsInstance(general, list)
        self.assertLessEqual(len(general), 15)
        
        # Each should have required structure
        for keyword in general:
            self.assertIn('keyword', keyword)
            self.assertIn('frequency', keyword)
            self.assertIn('percentage', keyword)
            self.assertIn('in_resume', keyword)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestJobKeywordAnalysis)
    
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
    exit(0 if success else 1)
