"""
Named Entity Recognition (NER) Extractor for Resume Parsing

This module provides advanced NER capabilities for extracting entities from resumes,
including:
- Personal information (names, emails, phone numbers)
- Skills and technologies
- Education details
- Certifications
- Locations and addresses
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents a named entity extracted from text"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


class NERExtractor:
    """Named Entity Recognition extractor for resume parsing"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize NER extractor
        
        Args:
            data_dir: Directory containing external data files
        """
        self.data_dir = data_dir or Path(__file__).parent.parent.parent.parent / "data" / "external"
        
        # Load external datasets
        self.skills = self._load_skills()
        self.job_titles = self._load_job_titles()
        self.companies = self._load_companies()
        self.education_keywords = self._load_education_keywords()
        self.certification_keywords = self._load_certification_keywords()
        
        # Compile regex patterns
        self._compile_patterns()
    
    def _load_skills(self) -> Set[str]:
        """Load skills from external dataset"""
        skills_file = self.data_dir / "skills.csv"
        skills = set()
        
        if skills_file.exists():
            try:
                with open(skills_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        skill = line.strip().lower()
                        if skill and not line.startswith('skill'):
                            skills.add(skill)
            except Exception as e:
                logger.warning(f"Error loading skills from {skills_file}: {e}")
        
        # Add common technical skills as fallback
        fallback_skills = {
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'html', 'css',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'mongodb', 'postgresql',
            'machine learning', 'data analysis', 'deep learning', 'tensorflow', 'pytorch',
            'agile', 'scrum', 'devops', 'ci/cd', 'rest api', 'graphql', 'microservices'
        }
        skills.update(fallback_skills)
        
        return skills
    
    def _load_job_titles(self) -> Set[str]:
        """Load job titles from external dataset"""
        job_titles_file = self.data_dir / "job_titles.csv"
        job_titles = set()
        
        if job_titles_file.exists():
            try:
                with open(job_titles_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        title = line.strip().lower()
                        if title and not line.startswith('title'):
                            job_titles.add(title)
            except Exception as e:
                logger.warning(f"Error loading job titles from {job_titles_file}: {e}")
        
        # Add common job titles as fallback
        fallback_titles = {
            'software engineer', 'senior software engineer', 'full stack developer',
            'frontend developer', 'backend developer', 'data scientist', 'machine learning engineer',
            'devops engineer', 'product manager', 'project manager', 'business analyst',
            'software architect', 'technical lead', 'engineering manager', 'cto', 'ceo'
        }
        job_titles.update(fallback_titles)
        
        return job_titles
    
    def _load_companies(self) -> Set[str]:
        """Load company names from external dataset"""
        companies_file = self.data_dir / "companies.csv"
        companies = set()
        
        if companies_file.exists():
            try:
                with open(companies_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        company = line.strip().lower()
                        if company and not line.startswith('company'):
                            companies.add(company)
            except Exception as e:
                logger.warning(f"Error loading companies from {companies_file}: {e}")
        
        # Add common tech companies as fallback
        fallback_companies = {
            'google', 'microsoft', 'amazon', 'apple', 'facebook', 'netflix', 'twitter',
            'linkedin', 'uber', 'airbnb', 'spotify', 'adobe', 'oracle', 'salesforce',
            'ibm', 'intel', 'nvidia', 'tesla', 'spaceX', 'dropbox', 'slack'
        }
        companies.update(fallback_companies)
        
        return companies
    
    def _load_education_keywords(self) -> Set[str]:
        """Load education-related keywords"""
        return {
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'diploma', 'certificate',
            'university', 'college', 'institute', 'school', 'academy', 'education',
            'computer science', 'engineering', 'business administration', 'arts', 'science',
            'mathematics', 'physics', 'chemistry', 'biology', 'medicine', 'law'
        }
    
    def _load_certification_keywords(self) -> Set[str]:
        """Load certification-related keywords"""
        return {
            'certified', 'certification', 'pmp', 'cfa', 'cpa', 'aws certified',
            'azure certified', 'google certified', 'oracle certified', 'cisco certified',
            'comptia', 'isc2', 'pmi', 'six sigma', 'itil', 'scrum master'
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for entity extraction"""
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        # Phone pattern (US and international formats)
        self.phone_pattern = re.compile(
            r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            re.IGNORECASE
        )
        
        # LinkedIn URL pattern
        self.linkedin_pattern = re.compile(
            r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[\w-]+',
            re.IGNORECASE
        )
        
        # GitHub URL pattern
        self.github_pattern = re.compile(
            r'(?:https?:\/\/)?(?:www\.)?github\.com\/[\w-]+',
            re.IGNORECASE
        )
        
        # Date pattern (YYYY, MM/YYYY, Month YYYY, etc.)
        self.date_pattern = re.compile(
            r'\b(?:\d{1,2}\/\d{4}|\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4})\b',
            re.IGNORECASE
        )
        
        # Location pattern (City, State or City, Country)
        self.location_pattern = re.compile(
            r'\b[A-Za-z\s]+,\s*(?:[A-Z]{2}|[A-Za-z\s]+)\b',
            re.IGNORECASE
        )
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract all entities from text
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Extract personal information
        entities.extend(self._extract_emails(text))
        entities.extend(self._extract_phones(text))
        entities.extend(self._extract_links(text))
        
        # Extract skills
        entities.extend(self._extract_skills(text))
        
        # Extract job titles
        entities.extend(self._extract_job_titles(text))
        
        # Extract companies
        entities.extend(self._extract_companies(text))
        
        # Extract education
        entities.extend(self._extract_education(text))
        
        # Extract certifications
        entities.extend(self._extract_certifications(text))
        
        # Extract locations
        entities.extend(self._extract_locations(text))
        
        # Extract dates
        entities.extend(self._extract_dates(text))
        
        # Sort entities by start position
        entities.sort(key=lambda x: x.start)
        
        return entities
    
    def _extract_emails(self, text: str) -> List[Entity]:
        """Extract email addresses"""
        entities = []
        for match in self.email_pattern.finditer(text):
            entity = Entity(
                text=match.group(),
                label='EMAIL',
                start=match.start(),
                end=match.end(),
                confidence=0.95
            )
            entities.append(entity)
        return entities
    
    def _extract_phones(self, text: str) -> List[Entity]:
        """Extract phone numbers"""
        entities = []
        for match in self.phone_pattern.finditer(text):
            entity = Entity(
                text=match.group(),
                label='PHONE',
                start=match.start(),
                end=match.end(),
                confidence=0.90
            )
            entities.append(entity)
        return entities
    
    def _extract_links(self, text: str) -> List[Entity]:
        """Extract LinkedIn and GitHub profiles"""
        entities = []
        
        # LinkedIn profiles
        for match in self.linkedin_pattern.finditer(text):
            entity = Entity(
                text=match.group(),
                label='LINKEDIN',
                start=match.start(),
                end=match.end(),
                confidence=0.95
            )
            entities.append(entity)
        
        # GitHub profiles
        for match in self.github_pattern.finditer(text):
            entity = Entity(
                text=match.group(),
                label='GITHUB',
                start=match.start(),
                end=match.end(),
                confidence=0.95
            )
            entities.append(entity)
        
        return entities
    
    def _extract_skills(self, text: str) -> List[Entity]:
        """Extract skills from text"""
        entities = []
        text_lower = text.lower()
        
        for skill in sorted(self.skills, key=len, reverse=True):
            # Find exact matches
            pattern = re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    label='SKILL',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.80
                )
                entities.append(entity)
        
        return entities
    
    def _extract_job_titles(self, text: str) -> List[Entity]:
        """Extract job titles from text"""
        entities = []
        text_lower = text.lower()
        
        for title in sorted(self.job_titles, key=len, reverse=True):
            # Find exact matches
            pattern = re.compile(r'\b' + re.escape(title) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    label='JOB_TITLE',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.75
                )
                entities.append(entity)
        
        return entities
    
    def _extract_companies(self, text: str) -> List[Entity]:
        """Extract company names from text"""
        entities = []
        text_lower = text.lower()
        
        for company in sorted(self.companies, key=len, reverse=True):
            # Find exact matches
            pattern = re.compile(r'\b' + re.escape(company) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    label='COMPANY',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.70
                )
                entities.append(entity)
        
        return entities
    
    def _extract_education(self, text: str) -> List[Entity]:
        """Extract education-related entities"""
        entities = []
        text_lower = text.lower()
        
        for keyword in sorted(self.education_keywords, key=len, reverse=True):
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    label='EDUCATION',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.65
                )
                entities.append(entity)
        
        return entities
    
    def _extract_certifications(self, text: str) -> List[Entity]:
        """Extract certification-related entities"""
        entities = []
        text_lower = text.lower()
        
        for keyword in sorted(self.certification_keywords, key=len, reverse=True):
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    label='CERTIFICATION',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.70
                )
                entities.append(entity)
        
        return entities
    
    def _extract_locations(self, text: str) -> List[Entity]:
        """Extract location entities"""
        entities = []
        
        for match in self.location_pattern.finditer(text):
            entity = Entity(
                text=match.group(),
                label='LOCATION',
                start=match.start(),
                end=match.end(),
                confidence=0.60
            )
            entities.append(entity)
        
        return entities
    
    def _extract_dates(self, text: str) -> List[Entity]:
        """Extract date entities"""
        entities = []
        
        for match in self.date_pattern.finditer(text):
            entity = Entity(
                text=match.group(),
                label='DATE',
                start=match.start(),
                end=match.end(),
                confidence=0.85
            )
            entities.append(entity)
        
        return entities
    
    def get_entities_by_label(self, text: str, label: str) -> List[Entity]:
        """
        Get entities of a specific type
        
        Args:
            text: Text to extract entities from
            label: Entity label to filter by
            
        Returns:
            List of entities with the specified label
        """
        all_entities = self.extract_entities(text)
        return [entity for entity in all_entities if entity.label == label]
    
    def extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        """
        Extract contact information from text
        
        Args:
            text: Text to extract contact info from
            
        Returns:
            Dictionary with contact information
        """
        contact_info = {
            'emails': [],
            'phones': [],
            'linkedin': [],
            'github': []
        }
        
        entities = self.extract_entities(text)
        
        for entity in entities:
            if entity.label == 'EMAIL':
                contact_info['emails'].append(entity.text)
            elif entity.label == 'PHONE':
                contact_info['phones'].append(entity.text)
            elif entity.label == 'LINKEDIN':
                contact_info['linkedin'].append(entity.text)
            elif entity.label == 'GITHUB':
                contact_info['github'].append(entity.text)
        
        return contact_info
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skills from text
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of unique skills found
        """
        skill_entities = self.get_entities_by_label(text, 'SKILL')
        return list(set(entity.text for entity in skill_entities))
    
    def extract_job_titles_from_text(self, text: str) -> List[str]:
        """
        Extract job titles from text
        
        Args:
            text: Text to extract job titles from
            
        Returns:
            List of unique job titles found
        """
        title_entities = self.get_entities_by_label(text, 'JOB_TITLE')
        return list(set(entity.text for entity in title_entities))
