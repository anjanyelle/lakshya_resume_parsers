"""
Enhanced Skills Parser - Removes Noise and Normalizes Skills
Fixes issues with non-skill phrases and ensures clean skill extraction
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from app.services.parser.utils.enhanced_dataset_loader import unified_loader

logger = logging.getLogger(__name__)

@dataclass
class EnhancedSkillEntry:
    """Enhanced skill entry with validation and normalization"""
    name: str = ""
    category: str = ""
    confidence: float = 0.0
    proficiency: str = ""
    yearsExperience: str = ""
    sources_used: List[str] = None
    
    def __post_init__(self):
        if self.sources_used is None:
            self.sources_used = []

class EnhancedSkillsParser:
    """
    Enhanced skills parser that:
    1. Removes noise and non-skill phrases
    2. Validates against skill datasets
    3. Normalizes skill names
    4. Ensures clean skill extraction
    """
    
    def __init__(self):
        self.unified_loader = unified_loader
        
        # Load valid skills from datasets
        self.valid_skills = self._load_valid_skills()
        
        # Compile noise filtering patterns
        self._compile_noise_patterns()
        
        logger.info("Enhanced Skills Parser initialized")
        logger.info(f"Loaded {len(self.valid_skills)} valid skills")
    
    def _load_valid_skills(self) -> Set[str]:
        """Load valid skills from unified datasets"""
        valid_skills = set()
        
        try:
            skills_data = self.unified_loader.get_unified_dataset('skills')
            for skill in skills_data:
                # Check multiple possible name fields
                for field in ['name', 'skill_name', 'skill']:
                    skill_name = skill.get(field, '')
                    if skill_name:
                        valid_skills.add(skill_name.lower().strip())
            
            logger.info(f"Loaded {len(valid_skills)} valid skills from datasets")
        except Exception as e:
            logger.warning(f"Failed to load valid skills: {e}")
        
        return valid_skills
    
    def _compile_noise_patterns(self):
        """Compile patterns to filter out noise"""
        # Common noise phrases that appear as skills but aren't
        self.noise_patterns = [
            r'\b(?:technologies?\s*reference|tech\s*reference)\b',
            r'\b(?:conferences?|conference\s*attendance)\b',
            r'\b(?:projects?|project\s*work)\b',
            r'\b(?:responsibilities?|key\s*responsibilities?)\b',
            r'\b(?:achievements?|key\s*achievements?)\b',
            r'\b(?:environment|environments?|tech\s*stack)\b',
            r'\b(?:tools?|technologies?|frameworks?|libraries?)\b',
            r'\b(?:languages?|programming\s*languages?)\b',
            r'\b(?:databases?|database\s*systems?)\b',
            r'\b(?:platforms?|cloud\s*platforms?)\b',
            r'\b(?:methodologies?|development\s*methodologies?)\b',
            r'\b(?:certifications?|professional\s*certifications?)\b',
            r'\b(?:education|academic\s*background)\b',
            r'\b(?:experience|work\s*experience)\b',
            r'\b(?:summary|professional\s*summary)\b',
            r'\b(?:objective|career\s*objective)\b',
            r'\b(?:interests?|areas?\s*of\s*interest)\b',
            r'\b(?:hobbies?|personal\s*interests?)\b',
            r'\b(?:references|professional\s*references)\b',
            r'\b(?:availability|work\s*availability)\b',
            r'\b(?:salary|compensation|expected\s*salary)\b',
            r'\b(?:location|work\s*location|relocation)\b',
        ]
        
        # Compile regex patterns
        self.compiled_noise_patterns = []
        for pattern in self.noise_patterns:
            try:
                self.compiled_noise_patterns.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.warning(f"Failed to compile noise pattern: {pattern} - {e}")
        
        # Generic patterns for non-skill content
        self.generic_noise_patterns = [
            r'^.{0,3}$',  # Too short
            r'^\d+$',    # Only numbers
            r'^[A-Z]{2,5}$',  # Only uppercase abbreviations
            r'^[a-z]+$',  # Only lowercase
            r'^.{50,}$',  # Too long
        ]
        
        for pattern in self.generic_noise_patterns:
            try:
                self.compiled_noise_patterns.append(re.compile(pattern))
            except Exception as e:
                logger.warning(f"Failed to compile generic pattern: {pattern} - {e}")
    
    def is_noise(self, skill_text: str) -> bool:
        """Check if skill text is noise"""
        if not skill_text:
            return True
        
        skill_text = skill_text.strip()
        
        # Check against noise patterns
        for pattern in self.compiled_noise_patterns:
            if pattern.search(skill_text):
                return True
        
        # Check if it contains too many common words
        common_words = ['and', 'or', 'the', 'with', 'for', 'in', 'on', 'at', 'to', 'of']
        words = skill_text.lower().split()
        if len(words) > 5 and sum(1 for word in words if word in common_words) > 2:
            return True
        
        return False
    
    def is_valid_skill(self, skill_text: str) -> bool:
        """Check if skill text is a valid skill"""
        if not skill_text or self.is_noise(skill_text):
            return False
        
        skill_lower = skill_text.lower().strip()
        
        # Check against valid skills dataset
        if skill_lower in self.valid_skills:
            return True
        
        # Check partial matches
        for valid_skill in self.valid_skills:
            if skill_lower in valid_skill or valid_skill in skill_lower:
                return True
        
        # Check for technical indicators
        tech_indicators = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'oracle',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'git', 'github', 'gitlab', 'ci/cd', 'devops', 'linux', 'unix',
            'html', 'css', 'sass', 'less', 'webpack', 'babel', 'npm',
            'machine learning', 'ai', 'data science', 'analytics', 'big data',
            'rest', 'api', 'graphql', 'microservices', 'backend', 'frontend',
            'mobile', 'ios', 'android', 'swift', 'kotlin', 'flutter',
            'testing', 'cypress', 'jest', 'mocha', 'selenium', 'junit',
            'agile', 'scrum', 'kanban', 'jira', 'confluence', 'slack'
        ]
        
        return any(indicator in skill_lower for indicator in tech_indicators)
    
    def normalize_skill(self, skill_text: str) -> str:
        """Normalize skill name using unified datasets"""
        if not skill_text:
            return skill_text
        
        # Try exact match in datasets
        lookup = self.unified_loader.lookup_skill(skill_text)
        if lookup:
            for field in ['name', 'skill_name']:
                if lookup.get(field):
                    return lookup[field]
        
        # Apply basic normalization
        normalized = skill_text.strip()
        
        # Capitalize properly
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        
        # Common abbreviations
        abbreviations = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'css': 'CSS',
            'html': 'HTML',
            'sql': 'SQL',
            'nosql': 'NoSQL',
            'ai': 'Artificial Intelligence',
            'ml': 'Machine Learning',
            'nlp': 'Natural Language Processing',
            'cv': 'Computer Vision',
            'ui': 'UI',
            'ux': 'UX',
            'api': 'API',
            'ci': 'CI',
            'cd': 'CD',
            'qa': 'Quality Assurance',
            'hr': 'Human Resources',
            'it': 'Information Technology'
        }
        
        # Apply abbreviations
        for abbr, full in abbreviations.items():
            if normalized.lower() == abbr.lower():
                normalized = full
                break
            elif f' {abbr.lower()} ' in f' {normalized.lower()} ':
                normalized = re.sub(rf'\b{abbr}\b', full, normalized, flags=re.IGNORECASE)
                break
        
        return normalized
    
    def extract_skills_from_text(self, text: str) -> List[EnhancedSkillEntry]:
        """Extract skills from raw text"""
        if not text:
            return []
        
        # Split by common separators
        separators = [',', ';', '|', '•', '·', '\n']
        
        # Replace all separators with comma for consistent splitting
        normalized_text = text
        for sep in separators:
            normalized_text = normalized_text.replace(sep, ',')
        
        # Split and clean
        raw_skills = [skill.strip() for skill in normalized_text.split(',') if skill.strip()]
        
        enhanced_skills = []
        for raw_skill in raw_skills:
            if self.is_valid_skill(raw_skill):
                normalized = self.normalize_skill(raw_skill)
                
                skill_entry = EnhancedSkillEntry()
                skill_entry.name = normalized
                skill_entry.sources_used = ['enhanced_parser']
                skill_entry.confidence = 0.8 if normalized.lower() in self.valid_skills else 0.6
                
                enhanced_skills.append(skill_entry)
                logger.debug(f"Extracted valid skill: {normalized}")
            else:
                logger.debug(f"Filtered noise skill: {raw_skill}")
        
        return enhanced_skills
    
    def enhance_existing_skills(self, existing_skills: List[Dict]) -> List[EnhancedSkillEntry]:
        """Enhance existing skills with validation and normalization"""
        enhanced_skills = []
        
        for skill_dict in existing_skills:
            if not isinstance(skill_dict, dict):
                continue
            
            # Get skill name from multiple possible fields
            skill_name = (skill_dict.get('name') or 
                         skill_dict.get('skill_name') or 
                         skill_dict.get('skill') or '')
            
            if not skill_name:
                continue
            
            # Validate and normalize
            if self.is_valid_skill(skill_name):
                normalized = self.normalize_skill(skill_name)
                
                skill_entry = EnhancedSkillEntry()
                skill_entry.name = normalized
                skill_entry.category = skill_dict.get('category', '')
                skill_entry.confidence = skill_dict.get('confidence', 0.7)
                skill_entry.proficiency = skill_dict.get('proficiency', '')
                skill_entry.yearsExperience = skill_dict.get('yearsExperience') or skill_dict.get('years_experience', '')
                skill_entry.sources_used = ['enhanced_parser', 'existing']
                
                enhanced_skills.append(skill_entry)
            else:
                logger.debug(f"Filtered invalid skill: {skill_name}")
        
        return enhanced_skills
    
    def parse_skills_section(self, skills_data: Any) -> List[EnhancedSkillEntry]:
        """
        Main parsing method for skills section
        Handles both raw text and structured data
        """
        logger.info("Starting enhanced skills parsing")
        
        enhanced_skills = []
        
        if isinstance(skills_data, str):
            # Raw text parsing
            enhanced_skills = self.extract_skills_from_text(skills_data)
            
        elif isinstance(skills_data, list):
            # Structured data enhancement
            enhanced_skills = self.enhance_existing_skills(skills_data)
            
        elif isinstance(skills_data, dict):
            # Handle dict with content field
            content = skills_data.get('content', '')
            if content:
                enhanced_skills = self.extract_skills_from_text(content)
        
        # Remove duplicates and sort by confidence
        unique_skills = {}
        for skill in enhanced_skills:
            key = skill.name.lower()
            if key not in unique_skills or skill.confidence > unique_skills[key].confidence:
                unique_skills[key] = skill
        
        final_skills = list(unique_skills.values())
        final_skills.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.info(f"Enhanced skills parsing complete: {len(final_skills)} valid skills")
        return final_skills
    
    def convert_to_standard_format(self, enhanced_skills: List[EnhancedSkillEntry]) -> List[Dict[str, Any]]:
        """Convert enhanced skills to standard JSON format"""
        standard_skills = []
        
        for skill in enhanced_skills:
            standard_skill = {
                "name": skill.name,
                "category": skill.category,
                "confidence": skill.confidence
            }
            
            # Add optional fields only if present
            if skill.proficiency:
                standard_skill["proficiency"] = skill.proficiency
            if skill.yearsExperience:
                standard_skill["yearsExperience"] = skill.yearsExperience
            
            standard_skills.append(standard_skill)
        
        return standard_skills

# Global instance
enhanced_skills_parser = EnhancedSkillsParser()
