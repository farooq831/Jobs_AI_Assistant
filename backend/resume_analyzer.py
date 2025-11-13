"""
Resume Analyzer Module for Task 6.1: Resume Text Extraction
Extracts keywords from uploaded resumes or directly input skills.
"""

import logging
from typing import Dict, List, Optional, Set
from keyword_extractor import get_keyword_extractor
import re
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """
    Analyzes resume text to extract keywords, skills, and provide insights.
    """
    
    # Common resume sections
    RESUME_SECTIONS = {
        'education': ['education', 'academic', 'degree', 'university', 'college', 'bachelor', 'master', 'phd'],
        'experience': ['experience', 'work history', 'employment', 'professional experience'],
        'skills': ['skills', 'technical skills', 'core competencies', 'expertise'],
        'projects': ['projects', 'portfolio', 'work samples'],
        'certifications': ['certification', 'certificate', 'licensed', 'accredited'],
        'achievements': ['achievement', 'award', 'recognition', 'accomplishment']
    }
    
    def __init__(self):
        """Initialize the ResumeAnalyzer."""
        self.extractor = get_keyword_extractor()
        logger.info("ResumeAnalyzer initialized")
    
    def extract_resume_keywords(self, resume_text: str, top_n: int = 50) -> Dict[str, any]:
        """
        Extract keywords from resume text.
        
        Args:
            resume_text: Full text of the resume
            top_n: Number of top keywords to extract
            
        Returns:
            Dictionary with comprehensive keyword analysis
        """
        if not resume_text or len(resume_text.strip()) < 50:
            raise ValueError("Resume text must be at least 50 characters")
        
        # Use keyword extractor for basic extraction
        keywords = self.extractor.extract_resume_keywords(resume_text)
        
        # Extract sections
        sections = self._identify_sections(resume_text)
        
        # Extract contact information
        contact_info = self._extract_contact_info(resume_text)
        
        # Calculate experience level indicators
        experience_indicators = self._analyze_experience_level(resume_text)
        
        return {
            'all_keywords': keywords['all_keywords'][:top_n],
            'technical_skills': keywords['technical_skills'],
            'soft_skills': keywords['soft_skills'],
            'keyword_count': keywords['keyword_count'],
            'sections_found': sections,
            'contact_info': contact_info,
            'experience_indicators': experience_indicators,
            'resume_length': len(resume_text),
            'word_count': len(resume_text.split())
        }
    
    def extract_skills_from_list(self, skills_list: List[str]) -> Dict[str, any]:
        """
        Extract and categorize skills from a direct list input.
        
        Args:
            skills_list: List of skill strings
            
        Returns:
            Dictionary with categorized skills
        """
        if not skills_list:
            raise ValueError("Skills list cannot be empty")
        
        # Combine skills into text for processing
        skills_text = ", ".join(skills_list)
        
        # Extract skills using keyword extractor
        skills_data = self.extractor.extract_skills(skills_text)
        
        # Categorize each skill
        categorized_skills = {
            'technical_skills': [],
            'soft_skills': [],
            'general_skills': []
        }
        
        for skill in skills_list:
            skill_lower = skill.lower().strip()
            skill_type = self.extractor._categorize_keyword(skill_lower)
            
            if skill_type == 'technical':
                categorized_skills['technical_skills'].append(skill)
            elif skill_type == 'soft_skill':
                categorized_skills['soft_skills'].append(skill)
            else:
                categorized_skills['general_skills'].append(skill)
        
        return {
            'total_skills': len(skills_list),
            'technical_skills': sorted(set(categorized_skills['technical_skills'])),
            'soft_skills': sorted(set(categorized_skills['soft_skills'])),
            'general_skills': sorted(set(categorized_skills['general_skills'])),
            'all_skills': sorted(set([s.strip() for s in skills_list]))
        }
    
    def compare_resume_with_job(self, resume_keywords: Dict, job_keywords: Dict) -> Dict[str, any]:
        """
        Compare resume keywords with job requirements.
        
        Args:
            resume_keywords: Keywords extracted from resume
            job_keywords: Keywords extracted from job posting
            
        Returns:
            Detailed comparison and recommendations
        """
        # Calculate keyword match
        match_result = self.extractor.calculate_keyword_match(job_keywords, resume_keywords)
        
        # Identify critical missing skills (top job keywords not in resume)
        job_top_keywords = set([kw['keyword'] for kw in job_keywords.get('all_keywords', [])[:10]])
        resume_all_keywords = set([kw['keyword'] for kw in resume_keywords.get('all_keywords', [])])
        critical_missing = job_top_keywords - resume_all_keywords
        
        # Calculate overall match score
        tech_match_pct = match_result['technical_match']['match_percentage']
        soft_match_pct = match_result['soft_skills_match']['match_percentage']
        overall_match_pct = match_result['overall_match']['match_percentage']
        
        # Weighted score (technical skills are more important)
        weighted_score = (tech_match_pct * 0.6) + (soft_match_pct * 0.2) + (overall_match_pct * 0.2)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(match_result, critical_missing)
        
        return {
            'match_result': match_result,
            'critical_missing_keywords': sorted(list(critical_missing)),
            'weighted_match_score': round(weighted_score, 2),
            'match_level': self._get_match_level(weighted_score),
            'recommendations': recommendations
        }
    
    def _identify_sections(self, resume_text: str) -> Dict[str, bool]:
        """
        Identify which common resume sections are present.
        
        Args:
            resume_text: Resume text to analyze
            
        Returns:
            Dictionary mapping section names to presence (bool)
        """
        text_lower = resume_text.lower()
        sections_found = {}
        
        for section_name, keywords in self.RESUME_SECTIONS.items():
            found = any(keyword in text_lower for keyword in keywords)
            sections_found[section_name] = found
        
        return sections_found
    
    def _extract_contact_info(self, resume_text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from resume.
        
        Args:
            resume_text: Resume text to analyze
            
        Returns:
            Dictionary with contact information (if found)
        """
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone pattern (various formats)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, resume_text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, resume_text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, resume_text, re.IGNORECASE)
        if github_match:
            contact_info['github'] = github_match.group()
        
        return contact_info
    
    def _analyze_experience_level(self, resume_text: str) -> Dict[str, any]:
        """
        Analyze indicators of experience level in resume.
        
        Args:
            resume_text: Resume text to analyze
            
        Returns:
            Dictionary with experience level indicators
        """
        text_lower = resume_text.lower()
        
        # Count year mentions
        year_pattern = r'\b(19|20)\d{2}\b'
        years_mentioned = len(re.findall(year_pattern, resume_text))
        
        # Experience level indicators
        senior_indicators = ['senior', 'lead', 'principal', 'architect', 'manager', 'director']
        mid_indicators = ['mid-level', 'intermediate', 'experienced']
        junior_indicators = ['junior', 'entry-level', 'associate', 'intern']
        
        senior_count = sum(text_lower.count(indicator) for indicator in senior_indicators)
        mid_count = sum(text_lower.count(indicator) for indicator in mid_indicators)
        junior_count = sum(text_lower.count(indicator) for indicator in junior_indicators)
        
        # Estimate experience level
        if senior_count > mid_count and senior_count > junior_count:
            estimated_level = 'senior'
        elif junior_count > mid_count and junior_count > senior_count:
            estimated_level = 'junior'
        else:
            estimated_level = 'mid-level'
        
        return {
            'years_mentioned_count': years_mentioned,
            'senior_indicators': senior_count,
            'mid_indicators': mid_count,
            'junior_indicators': junior_count,
            'estimated_level': estimated_level
        }
    
    def _generate_recommendations(self, match_result: Dict, critical_missing: Set[str]) -> List[str]:
        """
        Generate recommendations for resume improvement.
        
        Args:
            match_result: Results from keyword matching
            critical_missing: Critical keywords missing from resume
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Technical skills recommendations
        tech_match = match_result['technical_match']
        if tech_match['match_percentage'] < 50:
            recommendations.append(
                f"Add more technical skills to your resume. Only {tech_match['match_percentage']:.0f}% "
                f"of required technical skills are present."
            )
            if tech_match['missing']:
                top_missing = tech_match['missing'][:5]
                recommendations.append(
                    f"Consider adding these technical skills: {', '.join(top_missing)}"
                )
        
        # Soft skills recommendations
        soft_match = match_result['soft_skills_match']
        if soft_match['match_percentage'] < 40:
            recommendations.append(
                f"Highlight more soft skills. Only {soft_match['match_percentage']:.0f}% "
                f"of desired soft skills are mentioned."
            )
            if soft_match['missing']:
                recommendations.append(
                    f"Include these soft skills: {', '.join(soft_match['missing'][:3])}"
                )
        
        # Critical missing keywords
        if critical_missing:
            recommendations.append(
                f"Add these important keywords from the job posting: {', '.join(list(critical_missing)[:5])}"
            )
        
        # Overall match recommendations
        overall_pct = match_result['overall_match']['match_percentage']
        if overall_pct < 30:
            recommendations.append(
                "Consider tailoring your resume more closely to this job posting. "
                "The overall keyword match is low."
            )
        elif overall_pct >= 70:
            recommendations.append(
                "Your resume is well-matched to this job posting! Make sure to highlight "
                "your matching skills prominently."
            )
        
        return recommendations
    
    def _get_match_level(self, score: float) -> str:
        """
        Determine match level based on score.
        
        Args:
            score: Match score (0-100)
            
        Returns:
            Match level string
        """
        if score >= 75:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """
        Get available skill categories for reference.
        
        Returns:
            Dictionary of skill categories
        """
        return {
            'technical_skills_examples': sorted(list(self.extractor.TECH_SKILLS))[:20],
            'soft_skills_examples': sorted(list(self.extractor.SOFT_SKILLS))
        }
    
    def analyze_job_keywords(self, job_descriptions: List[str], 
                            resume_text: str = None,
                            resume_keywords: Dict = None,
                            top_n: int = 30) -> Dict[str, any]:
        """
        Task 6.2: Analyze Job Keywords
        Identify high-frequency keywords missing from the resume across multiple job postings.
        
        Args:
            job_descriptions: List of job description texts
            resume_text: Resume text (optional, if resume_keywords not provided)
            resume_keywords: Pre-extracted resume keywords (optional)
            top_n: Number of top keywords to return
            
        Returns:
            Dictionary with high-frequency keywords analysis and missing keywords
        """
        if not job_descriptions:
            raise ValueError("At least one job description is required")
        
        if resume_text is None and resume_keywords is None:
            raise ValueError("Either resume_text or resume_keywords must be provided")
        
        # Extract resume keywords if not provided
        if resume_keywords is None:
            resume_keywords = self.extract_resume_keywords(resume_text)
        
        # Get resume keyword set for comparison
        resume_kw_set = set([kw['keyword'] for kw in resume_keywords.get('all_keywords', [])])
        resume_tech_set = set(resume_keywords.get('technical_skills', []))
        resume_soft_set = set(resume_keywords.get('soft_skills', []))
        
        # Aggregate keywords from all job descriptions
        all_job_keywords = []
        tech_keywords_counter = Counter()
        soft_keywords_counter = Counter()
        general_keywords_counter = Counter()
        
        for job_desc in job_descriptions:
            # Extract keywords from this job description
            job_kw = self.extractor.extract_job_keywords(job_desc)
            all_job_keywords.append(job_kw)
            
            # Count technical skills
            for skill in job_kw.get('technical_skills', []):
                tech_keywords_counter[skill.lower()] += 1
            
            # Count soft skills
            for skill in job_kw.get('soft_skills', []):
                soft_keywords_counter[skill.lower()] += 1
            
            # Count all keywords
            for kw_dict in job_kw.get('all_keywords', []):
                keyword = kw_dict['keyword'].lower()
                general_keywords_counter[keyword] += 1
        
        # Calculate frequencies (as percentage of total jobs)
        total_jobs = len(job_descriptions)
        
        # Get top high-frequency keywords
        high_freq_technical = [
            {
                'keyword': kw,
                'frequency': count,
                'percentage': round((count / total_jobs) * 100, 1),
                'in_resume': kw in resume_tech_set or kw in resume_kw_set
            }
            for kw, count in tech_keywords_counter.most_common(top_n)
        ]
        
        high_freq_soft = [
            {
                'keyword': kw,
                'frequency': count,
                'percentage': round((count / total_jobs) * 100, 1),
                'in_resume': kw in resume_soft_set or kw in resume_kw_set
            }
            for kw, count in soft_keywords_counter.most_common(top_n)
        ]
        
        high_freq_general = [
            {
                'keyword': kw,
                'frequency': count,
                'percentage': round((count / total_jobs) * 100, 1),
                'in_resume': kw in resume_kw_set
            }
            for kw, count in general_keywords_counter.most_common(top_n)
        ]
        
        # Identify missing high-frequency keywords (appearing in >50% of jobs)
        missing_critical_technical = [
            item for item in high_freq_technical 
            if not item['in_resume'] and item['percentage'] >= 50
        ]
        
        missing_important_technical = [
            item for item in high_freq_technical 
            if not item['in_resume'] and 30 <= item['percentage'] < 50
        ]
        
        missing_critical_soft = [
            item for item in high_freq_soft 
            if not item['in_resume'] and item['percentage'] >= 50
        ]
        
        missing_important_soft = [
            item for item in high_freq_soft 
            if not item['in_resume'] and 30 <= item['percentage'] < 50
        ]
        
        # Overall missing keywords from general analysis
        missing_general = [
            item for item in high_freq_general 
            if not item['in_resume'] and item['percentage'] >= 40
        ]
        
        # Calculate coverage statistics
        total_high_freq_tech = len([k for k in high_freq_technical if k['percentage'] >= 30])
        matched_high_freq_tech = len([k for k in high_freq_technical if k['in_resume'] and k['percentage'] >= 30])
        tech_coverage = round((matched_high_freq_tech / total_high_freq_tech * 100) if total_high_freq_tech > 0 else 0, 1)
        
        total_high_freq_soft = len([k for k in high_freq_soft if k['percentage'] >= 30])
        matched_high_freq_soft = len([k for k in high_freq_soft if k['in_resume'] and k['percentage'] >= 30])
        soft_coverage = round((matched_high_freq_soft / total_high_freq_soft * 100) if total_high_freq_soft > 0 else 0, 1)
        
        return {
            'analysis_summary': {
                'total_jobs_analyzed': total_jobs,
                'total_unique_technical_keywords': len(tech_keywords_counter),
                'total_unique_soft_keywords': len(soft_keywords_counter),
                'total_unique_keywords': len(general_keywords_counter),
                'technical_coverage_percentage': tech_coverage,
                'soft_skills_coverage_percentage': soft_coverage
            },
            'high_frequency_keywords': {
                'technical_skills': high_freq_technical[:top_n],
                'soft_skills': high_freq_soft[:top_n],
                'general_keywords': high_freq_general[:top_n]
            },
            'missing_keywords': {
                'critical_technical': missing_critical_technical,  # >50% frequency, not in resume
                'important_technical': missing_important_technical,  # 30-50% frequency, not in resume
                'critical_soft_skills': missing_critical_soft,  # >50% frequency, not in resume
                'important_soft_skills': missing_important_soft,  # 30-50% frequency, not in resume
                'general_missing': missing_general  # >40% frequency, not in resume
            },
            'recommendations': self._generate_keyword_recommendations(
                missing_critical_technical, 
                missing_important_technical,
                missing_critical_soft,
                missing_important_soft,
                tech_coverage,
                soft_coverage
            )
        }
    
    def _generate_keyword_recommendations(self, 
                                         critical_tech: List[Dict],
                                         important_tech: List[Dict],
                                         critical_soft: List[Dict],
                                         important_soft: List[Dict],
                                         tech_coverage: float,
                                         soft_coverage: float) -> List[str]:
        """
        Generate recommendations based on missing high-frequency keywords.
        
        Args:
            critical_tech: Critical missing technical keywords
            important_tech: Important missing technical keywords
            critical_soft: Critical missing soft skills
            important_soft: Important missing soft skills
            tech_coverage: Technical keyword coverage percentage
            soft_coverage: Soft skills coverage percentage
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Critical technical keywords (high priority)
        if critical_tech:
            top_critical = [k['keyword'] for k in critical_tech[:5]]
            recommendations.append(
                f"🔴 HIGH PRIORITY: Add these critical technical skills appearing in 50%+ of jobs: "
                f"{', '.join(top_critical)}"
            )
        
        # Important technical keywords (medium priority)
        if important_tech:
            top_important = [k['keyword'] for k in important_tech[:5]]
            recommendations.append(
                f"🟡 MEDIUM PRIORITY: Consider adding these technical skills appearing in 30-50% of jobs: "
                f"{', '.join(top_important)}"
            )
        
        # Critical soft skills
        if critical_soft:
            top_soft = [k['keyword'] for k in critical_soft[:3]]
            recommendations.append(
                f"🔴 HIGH PRIORITY: Highlight these soft skills appearing in 50%+ of jobs: "
                f"{', '.join(top_soft)}"
            )
        
        # Important soft skills
        if important_soft:
            top_soft = [k['keyword'] for k in important_soft[:3]]
            recommendations.append(
                f"🟡 MEDIUM PRIORITY: Include these soft skills appearing in 30-50% of jobs: "
                f"{', '.join(top_soft)}"
            )
        
        # Coverage-based recommendations
        if tech_coverage < 40:
            recommendations.append(
                f"⚠️ Your technical skills coverage is low ({tech_coverage}%). "
                f"Focus on adding the most common technical requirements from job postings."
            )
        elif tech_coverage >= 70:
            recommendations.append(
                f"✅ Excellent technical skills coverage ({tech_coverage}%)! "
                f"Your resume aligns well with common technical requirements."
            )
        
        if soft_coverage < 40:
            recommendations.append(
                f"⚠️ Your soft skills coverage is low ({soft_coverage}%). "
                f"Add more examples demonstrating the soft skills employers are seeking."
            )
        elif soft_coverage >= 70:
            recommendations.append(
                f"✅ Great soft skills coverage ({soft_coverage}%)! "
                f"You're highlighting the soft skills employers want to see."
            )
        
        # General advice
        if not critical_tech and not critical_soft and tech_coverage >= 60 and soft_coverage >= 60:
            recommendations.append(
                "🎯 Your resume is well-optimized for these job postings! "
                "Continue to tailor it for specific applications."
            )
        
        return recommendations


# Singleton instance
_analyzer_instance = None

def get_resume_analyzer() -> ResumeAnalyzer:
    """Get or create singleton ResumeAnalyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ResumeAnalyzer()
    return _analyzer_instance
