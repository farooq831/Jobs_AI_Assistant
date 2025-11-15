"""
Keyword Extraction Module for Job Matching
Uses spaCy for NLP-based tokenization and keyword extraction from job descriptions and resumes.
"""

try:
    import spacy
    SPACY_AVAILABLE = True
except Exception:
    spacy = None
    SPACY_AVAILABLE = False

from typing import List, Dict, Set, Tuple
from collections import Counter
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeywordExtractor:
    """
    Extract and analyze keywords from job descriptions and resumes.
    Uses spaCy if available; otherwise falls back to a lightweight regex-based extractor.
    """
    
    # Technical skills and keywords commonly found in job postings
    TECH_SKILLS = {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
        'machine learning', 'deep learning', 'ai', 'nlp', 'computer vision',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'devops',
        'html', 'css', 'sass', 'webpack', 'babel',
        'linux', 'unix', 'bash', 'powershell',
        'data analysis', 'data science', 'analytics', 'visualization',
        'tableau', 'power bi', 'excel', 'r programming'
    }
    
    # Soft skills
    SOFT_SKILLS = {
        'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
        'creative', 'adaptable', 'organized', 'detail-oriented', 'self-motivated',
        'collaborative', 'innovative', 'strategic', 'customer-focused'
    }
    
    # Common job-related terms to filter out
    STOPWORDS_CUSTOM = {
        'job', 'work', 'company', 'team', 'position', 'role', 'opportunity',
        'candidate', 'applicant', 'employee', 'employer', 'hiring', 'recruitment',
        'experience', 'year', 'years', 'day', 'days', 'week', 'weeks', 'month', 'months'
    }
    
    def __init__(self):
        """Initialize the KeywordExtractor with spaCy model."""
        if SPACY_AVAILABLE:
            try:
                # Load spaCy English model
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except Exception:
                # If model not available, set to None and continue with fallback
                logger.warning("spaCy model not available at runtime; falling back to lightweight extractor")
                self.nlp = None
        else:
            logger.info("spaCy not available; using lightweight keyword extractor")
            self.nlp = None
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text for keyword extraction.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces and hyphens
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str, top_n: int = 20, 
                        include_bigrams: bool = True) -> List[Dict[str, any]]:
        """
        Extract keywords from text using spaCy NLP.
        
        Args:
            text: Text to extract keywords from
            top_n: Number of top keywords to return
            include_bigrams: Whether to include two-word phrases
            
        Returns:
            List of keyword dictionaries with keyword, count, and type
        """
        if not text:
            return []
        
        # Preprocess text
        cleaned_text = self.preprocess_text(text)

        keywords = []

        # Prefer spaCy if available and model loaded
        if self.nlp:
            doc = self.nlp(cleaned_text)
            # Single word keywords (nouns, proper nouns, adjectives)
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                    not token.is_stop and 
                    len(token.text) > 2 and
                    token.text not in self.STOPWORDS_CUSTOM):
                    keywords.append(token.lemma_)

            # Bigrams (two-word phrases)
            if include_bigrams:
                for i in range(len(doc) - 1):
                    token1 = doc[i]
                    token2 = doc[i + 1]
                    if ((token1.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                         token2.pos_ in ['NOUN', 'PROPN', 'ADJ']) or
                        (token1.text in ['machine', 'deep', 'data', 'web', 'full', 'front', 'back'] and
                         token2.pos_ in ['NOUN', 'PROPN'])):
                        bigram = f"{token1.text} {token2.text}"
                        if bigram not in self.STOPWORDS_CUSTOM:
                            keywords.append(bigram)
        else:
            # Lightweight fallback: split words and match against known skill lists
            tokens = re.findall(r"\b[\w\-\.]+\b", cleaned_text)
            for i, tok in enumerate(tokens):
                t = tok.lower()
                if len(t) > 2 and t not in self.STOPWORDS_CUSTOM:
                    # match against known tech/soft skills
                    if any(t == s or t in s for s in self.TECH_SKILLS):
                        keywords.append(t)
                    elif any(t == s or t in s for s in self.SOFT_SKILLS):
                        keywords.append(t)
                # bigram fallback
                if include_bigrams and i < len(tokens) - 1:
                    bigram = f"{tokens[i].lower()} {tokens[i+1].lower()}"
                    if bigram not in self.STOPWORDS_CUSTOM and any(bigram == s for s in self.TECH_SKILLS):
                        keywords.append(bigram)
        
        # Count keyword frequencies
        keyword_counts = Counter(keywords)
        
        # Categorize and format keywords
        result = []
        for keyword, count in keyword_counts.most_common(top_n):
            keyword_type = self._categorize_keyword(keyword)
            result.append({
                'keyword': keyword,
                'count': count,
                'type': keyword_type
            })
        
        return result
    
    def _categorize_keyword(self, keyword: str) -> str:
        """
        Categorize a keyword as technical, soft skill, or general.
        
        Args:
            keyword: The keyword to categorize
            
        Returns:
            Category string
        """
        keyword_lower = keyword.lower()
        
        if keyword_lower in self.TECH_SKILLS:
            return 'technical'
        elif keyword_lower in self.SOFT_SKILLS:
            return 'soft_skill'
        
        # Check if it contains technical terms
        for tech in self.TECH_SKILLS:
            if tech in keyword_lower or keyword_lower in tech:
                return 'technical'
        
        return 'general'
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract technical and soft skills from text.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            Dictionary with technical_skills and soft_skills lists
        """
        if not text:
            return {'technical_skills': [], 'soft_skills': []}
        
        cleaned_text = self.preprocess_text(text)
        doc = self.nlp(cleaned_text)
        
        technical_skills = set()
        soft_skills = set()
        
        # Check for exact matches and partial matches
        text_lower = cleaned_text.lower()
        
        # Technical skills
        for skill in self.TECH_SKILLS:
            if skill in text_lower:
                technical_skills.add(skill)
        
        # Soft skills
        for skill in self.SOFT_SKILLS:
            if skill in text_lower:
                soft_skills.add(skill)
        
        # Also check tokens and bigrams
        tokens = [token.lemma_ for token in doc if not token.is_stop]
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i+1]}"
            if bigram in self.TECH_SKILLS:
                technical_skills.add(bigram)
            if bigram in self.SOFT_SKILLS:
                soft_skills.add(bigram)
        
        return {
            'technical_skills': sorted(list(technical_skills)),
            'soft_skills': sorted(list(soft_skills))
        }
    
    def extract_job_keywords(self, job_data: Dict) -> Dict[str, any]:
        """
        Extract keywords from job posting data.
        
        Args:
            job_data: Dictionary containing job information (title, description, etc.)
            
        Returns:
            Dictionary with extracted keywords and skills
        """
        # Combine title and description
        title = job_data.get('title', '')
        description = job_data.get('description', '')
        combined_text = f"{title} {description}"
        
        # Extract keywords
        keywords = self.extract_keywords(combined_text, top_n=30)
        
        # Extract skills
        skills = self.extract_skills(combined_text)
        
        # Extract title-specific keywords (often most important)
        title_keywords = self.extract_keywords(title, top_n=10, include_bigrams=False)
        
        return {
            'all_keywords': keywords,
            'title_keywords': title_keywords,
            'technical_skills': skills['technical_skills'],
            'soft_skills': skills['soft_skills'],
            'keyword_count': len(keywords)
        }
    
    def extract_resume_keywords(self, resume_text: str) -> Dict[str, any]:
        """
        Extract keywords from resume text.
        
        Args:
            resume_text: Full text of the resume
            
        Returns:
            Dictionary with extracted keywords and skills
        """
        # Extract keywords
        keywords = self.extract_keywords(resume_text, top_n=50)
        
        # Extract skills
        skills = self.extract_skills(resume_text)
        
        return {
            'all_keywords': keywords,
            'technical_skills': skills['technical_skills'],
            'soft_skills': skills['soft_skills'],
            'keyword_count': len(keywords)
        }
    
    def calculate_keyword_match(self, job_keywords: Dict, resume_keywords: Dict) -> Dict[str, any]:
        """
        Calculate keyword match score between job and resume.
        
        Args:
            job_keywords: Keywords extracted from job posting
            resume_keywords: Keywords extracted from resume
            
        Returns:
            Dictionary with match statistics
        """
        # Convert to sets for comparison
        job_tech = set(job_keywords.get('technical_skills', []))
        resume_tech = set(resume_keywords.get('technical_skills', []))
        
        job_soft = set(job_keywords.get('soft_skills', []))
        resume_soft = set(resume_keywords.get('soft_skills', []))
        
        job_all = set([kw['keyword'] for kw in job_keywords.get('all_keywords', [])])
        resume_all = set([kw['keyword'] for kw in resume_keywords.get('all_keywords', [])])
        
        # Calculate matches
        tech_match = job_tech.intersection(resume_tech)
        soft_match = job_soft.intersection(resume_soft)
        keyword_match = job_all.intersection(resume_all)
        
        # Calculate missing skills
        missing_tech = job_tech - resume_tech
        missing_soft = job_soft - resume_soft
        
        # Calculate match percentages
        tech_match_pct = (len(tech_match) / len(job_tech) * 100) if job_tech else 0
        soft_match_pct = (len(soft_match) / len(job_soft) * 100) if job_soft else 0
        overall_match_pct = (len(keyword_match) / len(job_all) * 100) if job_all else 0
        
        return {
            'technical_match': {
                'matched': sorted(list(tech_match)),
                'missing': sorted(list(missing_tech)),
                'match_percentage': round(tech_match_pct, 2),
                'count': len(tech_match)
            },
            'soft_skills_match': {
                'matched': sorted(list(soft_match)),
                'missing': sorted(list(missing_soft)),
                'match_percentage': round(soft_match_pct, 2),
                'count': len(soft_match)
            },
            'overall_match': {
                'matched_keywords': sorted(list(keyword_match)),
                'match_percentage': round(overall_match_pct, 2),
                'count': len(keyword_match)
            }
        }


# Singleton instance
_extractor_instance = None

def get_keyword_extractor() -> KeywordExtractor:
    """Get or create singleton KeywordExtractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = KeywordExtractor()
    return _extractor_instance
