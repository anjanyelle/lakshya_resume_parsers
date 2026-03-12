"""
Hybrid Work Experience Parser
Combines multiple parsing strategies for better accuracy
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.services.parser.work_experience_parser import JobEntry

logger = logging.getLogger(__name__)

@dataclass
class HybridParseResult:
    """Result from hybrid parsing"""
    jobs: List[JobEntry]
    confidence: float
    method_used: str

class HybridWorkExperienceParser:
    """Hybrid work experience parser combining multiple strategies"""
    
    def __init__(self):
        self.parsers = []
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize different parsing strategies in priority order"""
        self.parsers = []
        
        # 1. ML Parser (Highest priority for complex patterns)
        try:
            from app.services.parser.ml_work_experience_parser import MLWorkExperienceParser
            self.parsers.append(("ML", MLWorkExperienceParser()))
            logger.info("ML parser initialized")
        except ImportError:
            logger.warning("ML parser not available")
        
        # 2. Rule-based Parser (Standard patterns)
        try:
            from app.services.parser.work_experience_parser import WorkExperienceParser
            self.parsers.append(("Rule-based", WorkExperienceParser()))
            logger.info("Rule-based parser initialized")
        except ImportError:
            logger.warning("Rule-based parser not available")
        
        # 3. LLM Parser (Final fallback for edge cases)
        try:
            from app.services.llm_service import LLMParsingService
            self.parsers.append(("LLM", LLMParsingService()))
            logger.info("LLM parser initialized")
        except ImportError:
            logger.warning("LLM parser not available")
    
    def parse_work_experience(self, text: str) -> List[JobEntry]:
        """Parse work experience using hybrid approach"""
        if not text or not text.strip():
            return []
        
        best_result = None
        best_confidence = 0.0
        
        for method_name, parser in self.parsers:
            try:
                if method_name == "ML":
                    # ML gets first chance with confidence boost
                    jobs = parser.parse_experience_section(text)
                    method_confidence = 1.0  # Highest priority
                elif method_name == "Rule-based":
                    # Rule-based gets second chance
                    jobs = parser.parse_experience_section(text)
                    method_confidence = 0.8  # Medium priority
                elif method_name == "LLM":
                    # LLM gets final chance
                    jobs = self._llm_parse(text, parser)
                    method_confidence = 0.6  # Lowest priority
                else:
                    jobs = self._rule_based_parse(text)
                    method_confidence = 0.5
                
                if jobs:
                    base_confidence = self._calculate_confidence(jobs, text)
                    # Apply method priority weighting
                    weighted_confidence = base_confidence * method_confidence
                    
                    logger.info(f"{method_name} parser: {len(jobs)} jobs, confidence={weighted_confidence:.2f}")
                    
                    if weighted_confidence > best_confidence:
                        best_confidence = weighted_confidence
                        best_result = jobs
                        self.method_used = method_name
                        
            except Exception as e:
                logger.error(f"Parser {method_name} failed: {e}")
                continue
        
        return best_result or []
    
    def parse_experience_section(self, text: str, source_format: str = None) -> List[JobEntry]:
        """Parse experience section - compatibility method for pipeline"""
        return self.parse_work_experience(text)
    
    @staticmethod
    def build_date_anchor_excerpt(text: str, *, context_lines: int = 5) -> str:
        """Build date anchor excerpt - compatibility method for pipeline"""
        try:
            # Import the original method for compatibility
            from app.services.parser.work_experience_parser import WorkExperienceParser
            return WorkExperienceParser.build_date_anchor_excerpt(text, context_lines=context_lines)
        except ImportError:
            # Fallback: return first few lines
            lines = text.split('\n')
            if len(lines) <= context_lines * 2:
                return text
            return '\n'.join(lines[:context_lines * 2])
    
    def _llm_parse(self, text: str, llm_service) -> List[JobEntry]:
        """LLM parsing implementation"""
        try:
            # Use LLM service to extract work experience
            llm_result = llm_service.extract_work_experience(text)
            if not llm_result:
                return []
            
            jobs = []
            for item in llm_result:
                if isinstance(item, dict):
                    job = JobEntry(
                        company=item.get("company"),
                        title=item.get("title") or item.get("job_title"),
                        start_date=self._parse_date(item.get("start_date")),
                        end_date=self._parse_date(item.get("end_date")),
                        location=item.get("location"),
                        description=item.get("description", ""),
                        is_current=item.get("end_date") in ["present", "current", None],
                        bullets=[],
                        duration_months=None,
                        client=item.get("client"),
                        employment_type=item.get("employment_type"),
                        confidence=0.6
                    )
                    jobs.append(job)
            
            return jobs
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return []
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        
        try:
            import dateparser
            return dateparser.parse(date_str)
        except Exception:
            return None
    
    def _calculate_confidence(self, jobs: List[JobEntry], original_text: str) -> float:
        """Calculate confidence score for parsed jobs"""
        if not jobs:
            return 0.0
        
        # Base confidence on number of jobs and completeness
        confidence = 0.5
        
        # More jobs = higher confidence
        if len(jobs) >= 2:
            confidence += 0.2
        elif len(jobs) >= 3:
            confidence += 0.3
        
        # Check for complete information
        complete_jobs = 0
        for job in jobs:
            if job.company and job.title and job.start_date:
                complete_jobs += 1
        
        if complete_jobs == len(jobs):
            confidence += 0.2
        elif complete_jobs > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _rule_based_parse(self, text: str) -> List[JobEntry]:
        """Rule-based parsing implementation"""
        jobs = []
        
        # Split by common job separators
        job_patterns = [
            r'\n(?=[A-Z][a-z]+.*\d{4})',  # Company name followed by year
            r'\n(?=\d{1,2}/\d{4})',       # Date pattern
            r'\n(?=\w+.*Present)',         # Present/current
            r'\n(?=\w+.*\d{4}-\d{4})',    # Date range
        ]
        
        job_sections = [text]
        for pattern in job_patterns:
            new_sections = []
            for section in job_sections:
                new_sections.extend(re.split(pattern, section))
            job_sections = new_sections
        
        for section in job_sections:
            if not section.strip():
                continue
            
            job = self._parse_job_section(section.strip())
            if job:
                jobs.append(job)
        
        return jobs
    
    def _parse_job_section(self, section: str) -> Optional[JobEntry]:
        """Parse a single job section"""
        lines = section.split('\n')
        if not lines:
            return None
        
        # Extract information from lines
        company = ""
        title = ""
        location = ""
        start_date = None
        end_date = None
        description = ""
        
        # Find dates
        date_pattern = r'(\d{1,2}/\d{4}|\d{4}-\d{1,2}|\w+ \d{4}|\d{4}|\w+ \d{4} - \w+ \d{4}|\w+ \d{4} - Present|Present)'
        dates = []
        for line in lines:
            found_dates = re.findall(date_pattern, line)
            dates.extend(found_dates)
        
        # Extract company and title from first line
        first_line = lines[0].strip()
        
        # Remove dates from first line
        clean_line = re.sub(date_pattern, '', first_line).strip()
        
        # Look for common patterns
        if ' at ' in clean_line:
            parts = clean_line.split(' at ')
            title = parts[0].strip()
            company = parts[1].strip()
        elif '@' in clean_line:
            parts = clean_line.split('@')
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            # Try to identify company and title
            words = clean_line.split()
            if len(words) >= 2:
                # Assume first word(s) are title, last is company
                title = ' '.join(words[:-1])
                company = words[-1]
        
        # Extract location
        for line in lines:
            if re.search(r', [A-Z]{2}|^[A-Z][a-z]+, [A-Z]{2}', line):
                location = line.strip()
                break
        
        # Parse dates
        if dates:
            start_date = self._parse_date(dates[0])
            if len(dates) > 1:
                end_date = self._parse_date(dates[1])
        
        # Extract description (everything after the first line that's not dates/location)
        description_lines = []
        for line in lines[1:]:
            if not re.search(date_pattern, line) and line.strip():
                description_lines.append(line.strip())
        
        description = '\n'.join(description_lines)
        
        # Clean up description
        description = re.sub(r'^\s*[•·]\s*', '- ', description, flags=re.MULTILINE)
        description = re.sub(r'^\s*\d+\.\s*', '- ', description, flags=re.MULTILINE)
        
        # Validate we have minimum required info
        if not title or not company:
            return None
        
        return JobEntry(
            company=company,
            title=title,
            location=location,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str or date_str.lower() in ['present', 'current', 'ongoing']:
            return None
        
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
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
