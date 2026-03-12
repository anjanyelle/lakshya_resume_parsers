"""
Enhanced Work Experience Parser
Improved parsing with better pattern recognition and error handling
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from app.services.parser.work_experience_parser import JobEntry

logger = logging.getLogger(__name__)

@dataclass
class EnhancedParseResult:
    """Result from enhanced parsing"""
    jobs: List[JobEntry]
    confidence_scores: List[float]
    parsing_method: str

class WorkExperienceEnhanced:
    """Enhanced work experience parser with improved patterns"""
    
    def __init__(self):
        self.company_patterns = self._load_company_patterns()
        self.title_patterns = self._load_title_patterns()
        self.date_patterns = self._load_date_patterns()
    
    def _load_company_patterns(self) -> List[str]:
        """Load company name patterns"""
        return [
            r'^[A-Z][a-zA-Z\s&]+(?:Inc|Corp|Ltd|LLC|Technologies|Solutions|Systems|Group|Company)',
            r'^[A-Z][a-zA-Z\s]+(?:\s+at\s+)?[A-Z][a-zA-Z\s&]+$',
            r'^[A-Z][a-zA-Z\s&]+(?:\s*-\s*[A-Z][a-zA-Z\s&]+)*$'
        ]
    
    def _load_title_patterns(self) -> List[str]:
        """Load job title patterns"""
        return [
            r'(Senior|Junior|Lead|Principal|Chief|Head|Director|Manager|Engineer|Developer|Analyst|Consultant|Specialist|Coordinator|Administrator)',
            r'(Software|Data|Business|Financial|Marketing|Sales|Product|Project|Operations|HR|Human Resources)',
            r'(Engineer|Developer|Manager|Analyst|Director|Consultant|Specialist|Coordinator|Administrator)'
        ]
    
    def _load_date_patterns(self) -> List[str]:
        """Load date patterns"""
        return [
            r'(\d{1,2}/\d{4})',
            r'(\d{4}-\d{1,2})',
            r'(\w+ \d{4})',
            r'(\w+ \d{4} - \w+ \d{4})',
            r'(\w+ \d{4} - Present)',
            r'(\d{4} - \d{4})',
            r'(\d{4} - Present)',
            r'(Present|Current)'
        ]
    
    def parse_work_experience(self, text: str) -> List[JobEntry]:
        """Parse work experience with enhanced patterns"""
        if not text or not text.strip():
            return []
        
        jobs = []
        
        # Try different splitting strategies
        sections = self._split_into_sections(text)
        
        for section in sections:
            if not section.strip():
                continue
            
            job = self._parse_section_enhanced(section)
            if job:
                jobs.append(job)
        
        return jobs
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split text into job sections using multiple strategies"""
        sections = [text]
        
        # Strategy 1: Split by date patterns
        date_split_pattern = r'\n(?=\d{1,2}/\d{4}|\w+ \d{4}|\d{4}|\w+ \d{4} - |Present)'
        new_sections = []
        for section in sections:
            new_sections.extend(re.split(date_split_pattern, section))
        sections = new_sections
        
        # Strategy 2: Split by company patterns (if no dates found)
        if len(sections) == 1:
            company_split_pattern = r'\n(?=[A-Z][a-zA-Z\s&]+(?:Inc|Corp|Ltd|LLC|Technologies|Solutions|Systems|Group|Company))'
            new_sections = []
            for section in sections:
                new_sections.extend(re.split(company_split_pattern, section))
            sections = new_sections
        
        # Strategy 3: Split by common job section indicators
        if len(sections) == 1:
            section_patterns = [
                r'\n(?=\w+.*\d{4})',
                r'\n(?=.*Engineer|.*Manager|.*Director|.*Analyst|.*Developer)',
                r'\n(?=.*at\s+[A-Z])'
            ]
            for pattern in section_patterns:
                if len(sections) > 1:
                    break
                new_sections = []
                for section in sections:
                    new_sections.extend(re.split(pattern, section))
                sections = new_sections
        
        return sections
    
    def _parse_section_enhanced(self, section: str) -> Optional[JobEntry]:
        """Parse a single section with enhanced logic"""
        lines = section.strip().split('\n')
        if not lines:
            return None
        
        # Extract information
        company, title, location, dates, description = self._extract_job_info(lines)
        
        # Validate and clean
        if not title:
            return None
        
        # Parse dates
        start_date, end_date = self._parse_date_range(dates)
        
        return JobEntry(
            company=company or "",
            title=title,
            location=location or "",
            start_date=start_date,
            end_date=end_date,
            description=description
        )
    
    def _extract_job_info(self, lines: List[str]) -> Tuple[str, str, str, List[str], str]:
        """Extract job information from lines"""
        company = ""
        title = ""
        location = ""
        dates = []
        description_lines = []
        
        # Process first line (usually contains title/company/date)
        first_line = lines[0].strip()
        
        # Extract dates from first line
        date_matches = re.findall(r'(\d{1,2}/\d{4}|\w+ \d{4}|\d{4}|\w+ \d{4} - \w+ \d{4}|\w+ \d{4} - Present|Present|Current)', first_line)
        if date_matches:
            dates.extend(date_matches)
            # Remove dates from first line
            first_line = re.sub(r'(\d{1,2}/\d{4}|\w+ \d{4}|\d{4}|\w+ \d{4} - \w+ \d{4}|\w+ \d{4} - Present|Present|Current)', '', first_line).strip()
        
        # Extract company and title from cleaned first line
        company, title = self._extract_company_title(first_line)
        
        # Process remaining lines
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Check for location
            if re.search(r', [A-Z]{2}|^[A-Z][a-z]+, [A-Z]{2}|^[A-Z][a-z]+, [A-Z][a-z]+', line):
                location = line
                continue
            
            # Check for dates in other lines
            date_matches = re.findall(r'(\d{1,2}/\d{4}|\w+ \d{4}|\d{4}|\w+ \d{4} - \w+ \d{4}|\w+ \d{4} - Present|Present|Current)', line)
            if date_matches:
                dates.extend(date_matches)
                continue
            
            # Everything else is description
            description_lines.append(line)
        
        description = '\n'.join(description_lines)
        
        # Clean up description
        description = re.sub(r'^\s*[•·]\s*', '- ', description, flags=re.MULTILINE)
        description = re.sub(r'^\s*\d+\.\s*', '- ', description, flags=re.MULTILINE)
        description = re.sub(r'^\s*-\s+', '- ', description, flags=re.MULTILINE)
        
        return company, title, location, dates, description
    
    def _extract_company_title(self, line: str) -> Tuple[str, str]:
        """Extract company and title from a line"""
        # Pattern 1: Title at Company
        if ' at ' in line:
            parts = line.split(' at ', 1)
            title = parts[0].strip()
            company = parts[1].strip()
            return company, title
        
        # Pattern 2: Title @ Company
        if '@' in line:
            parts = line.split('@', 1)
            title = parts[0].strip()
            company = parts[1].strip()
            return company, title
        
        # Pattern 3: Title, Company
        if ',' in line:
            parts = line.split(',', 1)
            title = parts[0].strip()
            company = parts[1].strip()
            return company, title
        
        # Pattern 4: Look for company indicators
        company_indicators = ['Inc', 'Corp', 'Ltd', 'LLC', 'Technologies', 'Solutions', 'Systems', 'Group', 'Company']
        for indicator in company_indicators:
            if indicator in line:
                # Company name likely contains the indicator
                if line.endswith(indicator):
                    # Assume everything before is title
                    title = line[:-len(indicator)].strip()
                    company = line
                else:
                    # Try to split around the indicator
                    parts = line.split(indicator)
                    if len(parts) >= 2:
                        title = parts[0].strip()
                        company = indicator + parts[1].strip()
                    else:
                        title = line
                        company = ""
                return company, title
        
        # Default: Assume whole line is title, no company found
        return "", line
    
    def _parse_date_range(self, dates: List[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Parse date range from date strings"""
        if not dates:
            return None, None
        
        # Clean and dedupe dates
        clean_dates = []
        for date_str in dates:
            date_str = date_str.strip()
            if date_str and date_str not in clean_dates:
                clean_dates.append(date_str)
        
        if not clean_dates:
            return None, None
        
        # Parse dates
        parsed_dates = []
        for date_str in clean_dates:
            parsed = self._parse_single_date(date_str)
            if parsed:
                parsed_dates.append(parsed)
        
        if not parsed_dates:
            return None, None
        
        # Sort dates
        parsed_dates.sort()
        
        # Return start and end dates
        start_date = parsed_dates[0]
        end_date = parsed_dates[-1] if len(parsed_dates) > 1 else None
        
        # Check if end date is "present" or "current"
        if len(clean_dates) > 1 and clean_dates[-1].lower() in ['present', 'current']:
            end_date = None
        
        return start_date, end_date
    
    def _parse_single_date(self, date_str: str) -> Optional[datetime]:
        """Parse a single date string"""
        if not date_str or date_str.lower() in ['present', 'current', 'ongoing']:
            return None
        
        # Clean date string
        date_str = date_str.strip()
        
        # Handle date ranges
        if ' - ' in date_str:
            parts = date_str.split(' - ')
            date_str = parts[0]  # Take the first part as start date
        
        try:
            # Try different date formats
            formats = [
                '%m/%Y',
                '%Y-%m',
                '%B %Y',
                '%b %Y',
                '%Y',
                '%m-%Y',
                '%Y/%m',
                '%m/%d/%Y',
                '%Y-%m-%d',
                '%d/%m/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
