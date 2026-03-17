"""
ML Work Experience Parser
Uses machine learning models to parse work experience from resumes
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.services.parser.work_experience_parser import JobEntry

logger = logging.getLogger(__name__)

@dataclass
class MLWorkExperienceResult:
    """Result from ML work experience parsing"""
    company: str
    title: str
    location: str
    start_date: Optional[str]
    end_date: Optional[str]
    description: str
    confidence: float

class MLWorkExperienceParser:
    """ML-based work experience parser"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._load_models()
    
    def _load_models(self):
        """Load ML models"""
        try:
            # In a real implementation, this would load trained models
            # For now, we'll use rule-based parsing as fallback
            logger.info("ML models not found, using rule-based parsing")
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")
    
    def parse_work_experience(self, text: str) -> List[JobEntry]:
        """Parse work experience using ML models"""
        return self.parse_experience_section(text)
    
    def parse_experience_section(self, text: str) -> List[JobEntry]:
        """Parse experience section using ML models"""
        if not text or not text.strip():
            return []
        
        try:
            # ML-based parsing would go here
            # For now, use enhanced rule-based parsing
            return self._rule_based_parse(text)
        except Exception as e:
            logger.error(f"ML parsing failed: {e}")
            return []
    
    def _rule_based_parse(self, text: str) -> List[JobEntry]:
        """Rule-based parsing as fallback"""
        jobs = []
        
        # Split by common job separators
        job_sections = re.split(r'\n(?=\w+.*\d{4}|\w+.*Present|\w+.*Current)', text)
        
        for section in job_sections:
            if not section.strip():
                continue
            
            job = self._parse_job_section(section)
            if job:
                jobs.append(job)
        
        return jobs
    
    def _parse_job_section(self, section: str) -> Optional[JobEntry]:
        """Parse a single job section"""
        lines = section.strip().split('\n')
        if not lines:
            return None
        
        # Extract company and title from first line
        first_line = lines[0].strip()
        
        # Look for date patterns
        date_pattern = r'(\d{1,2}/\d{4}|\d{4}-\d{1,2}|\w+ \d{4}|\d{4}|\w+ \d{4} - \w+ \d{4}|\w+ \d{4} - Present|Present)'
        dates = re.findall(date_pattern, first_line)
        
        # Extract company and title
        company = ""
        title = ""
        
        if dates:
            # Remove dates from first line to get company/title
            clean_line = re.sub(date_pattern, '', first_line).strip()
            parts = clean_line.split('@')
            if len(parts) == 2:
                title = parts[0].strip()
                company = parts[1].strip()
            else:
                # Try to split by common patterns
                if ' at ' in clean_line:
                    parts = clean_line.split(' at ')
                    title = parts[0].strip()
                    company = parts[1].strip()
                else:
                    # Assume first part is title, look for company in other lines
                    title = clean_line
                    for line in lines[1:]:
                        if any(keyword in line.lower() for keyword in ['inc', 'corp', 'ltd', 'llc', 'company', 'technologies']):
                            company = line.strip()
                            break
        
        # Extract location
        location = ""
        for line in lines:
            if re.search(r', [A-Z]{2}|^[A-Z][a-z]+, [A-Z]{2}', line):
                location = line.strip()
                break
        
        # Extract dates
        start_date = None
        end_date = None
        if dates:
            if len(dates) >= 1:
                start_date = dates[0]
            if len(dates) >= 2:
                end_date = dates[1]
        
        # Extract description
        description = '\n'.join(lines[1:])
        
        # Clean up description
        description = re.sub(r'^\s*[•·]\s*', '- ', description, flags=re.MULTILINE)
        description = re.sub(r'^\s*\d+\.\s*', '- ', description, flags=re.MULTILINE)
        
        if not title or not company:
            return None
        
        return JobEntry(
            company=company,
            title=title,
            location=location,
            start_date=self._parse_date(start_date),
            end_date=self._parse_date(end_date),
            description=description.strip()
        )
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str or date_str.lower() in ['present', 'current']:
            return None
        
        try:
            # Try different date formats
            formats = [
                '%m/%Y',
                '%Y-%m',
                '%B %Y',
                '%Y',
                '%m-%Y',
                '%Y/%m'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
