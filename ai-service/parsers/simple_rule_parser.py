"""
Simple rule-based parser that doesn't require external dependencies.
Extracts basic entities using regex patterns.
"""

import re
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SimpleRuleParser:
    """
    Simple rule-based parser using only Python standard library.
    Fallback when full RuleBasedParser fails to initialize.
    """
    
    def __init__(self):
        """Initialize the parser with compiled regex patterns."""
        self.logger = logging.getLogger(__name__)
        
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone patterns (including Indian formats)
        self.phone_patterns = [
            re.compile(r'\+91[-\s]?(\d{5})[-\s]?(\d{5})'),  # +91 87904 33333
            re.compile(r'(\d{3})[-\s]?(\d{3})[-\s]?(\d{4})'),  # 879-043-3333
            re.compile(r'(\d{10})'),  # 8790433333
        ]
        
        # LinkedIn pattern
        self.linkedin_pattern = re.compile(
            r'linkedin\.com/in/[\w\-]+', re.IGNORECASE
        )
        
        # GitHub pattern
        self.github_pattern = re.compile(
            r'github\.com/[\w\-]+', re.IGNORECASE
        )
        
        # Website pattern (basic)
        self.website_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`[\]]+', re.IGNORECASE
        )
        
        # Date patterns
        self.date_patterns = [
            re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),  # MM/DD/YYYY
            re.compile(r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'),  # YYYY/MM/DD
            re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', re.IGNORECASE),
        ]
        
        # Skills keywords
        self.skill_keywords = {
            'react', 'reactjs', 'react.js', 'vue', 'vuejs', 'angular', 'angularjs',
            'javascript', 'typescript', 'node', 'nodejs', 'node.js', 'express',
            'python', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'database',
            'git', 'github', 'gitlab', 'bitbucket', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'cloud', 'devops', 'ci/cd', 'jenkins',
            'rest', 'restful', 'api', 'graphql', 'microservices',
            'webpack', 'vite', 'babel', 'eslint', 'prettier', 'jest',
            'linux', 'ubuntu', 'windows', 'mac', 'unix', 'shell', 'bash',
            'tailwind', 'bootstrap', 'material-ui', 'styled-components',
            'redux', 'mobx', 'context', 'zustand', 'recoil'
        }
        
        self.logger.info("SimpleRuleParser initialized successfully")
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        matches = self.email_pattern.findall(text)
        return matches[0] if matches else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        for pattern in self.phone_patterns:
            matches = pattern.findall(text)
            if matches:
                match = matches[0]
                if isinstance(match, tuple):
                    return ''.join(match)
                return match
        return None
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile from text."""
        matches = self.linkedin_pattern.findall(text)
        return f"https://{matches[0]}" if matches else None
    
    def extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub profile from text."""
        matches = self.github_pattern.findall(text)
        return f"https://{matches[0]}" if matches else None
    
    def extract_websites(self, text: str) -> List[str]:
        """Extract websites from text."""
        matches = self.website_pattern.findall(text)
        # Filter out social media links
        filtered = [m for m in matches if not any(social in m.lower() for social in ['linkedin', 'github', 'facebook', 'twitter'])]
        return list(set(filtered))
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        dates = []
        for pattern in self.date_patterns:
            matches = pattern.findall(text)
            dates.extend(matches)
        return list(set(dates))
    
    def extract_years_of_experience(self, text: str) -> Optional[float]:
        """Extract years of experience from text."""
        # Look for patterns like "3+ years", "3 years", "3 years of experience"
        patterns = [
            r'(\d+(?:\.\d+)?)\+?\s*years?',
            r'(\d+(?:\.\d+)?)\+?\s*years?\s*of\s*experience',
            r'experience[:\s]*(\d+(?:\.\d+)?)\+?\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        found_skills = []
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Check multi-word skills first
        multi_word_skills = ['node.js', 'react.js', 'typescript', 'tailwind css', 'material ui', 'styled components']
        text_lower = text.lower()
        
        for skill in multi_word_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Check single-word skills
        for word in words:
            if word in self.skill_keywords:
                found_skills.append(word.title())
        
        return list(set(found_skills))
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract name from text (simple heuristic)."""
        lines = text.strip().split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            # Simple heuristic: 2-4 words, capitalized, no numbers
            if 2 <= len(line.split()) <= 4:
                words = line.split()
                if all(word[0].isupper() for word in words if word) and not any(c.isdigit() for c in line):
                    # Exclude common non-name lines
                    exclude = ['resume', 'cv', 'curriculum', 'vitae', 'senior', 'junior', 'lead', 'manager']
                    if not any(exclude.lower() in line.lower() for exclude in exclude):
                        return line
        return None
    
    def parse_all(self, text: str) -> Dict[str, Any]:
        """Parse all entities from text."""
        return {
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'linkedin': self.extract_linkedin(text),
            'github': self.extract_github(text),
            'websites': self.extract_websites(text),
            'dates': self.extract_dates(text),
            'years_of_experience': self.extract_years_of_experience(text),
            'skills': self.extract_skills(text)
        }
