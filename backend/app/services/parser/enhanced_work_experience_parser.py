"""
Enhanced Work Experience Parser - Comprehensive Fix
Resolves key-value mismatches, improves segmentation, and ensures proper field extraction
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import dateparser

from app.services.parser.utils.enhanced_dataset_loader import unified_loader
from app.services.parser.work_experience_parser import WorkExperienceParser, JobEntry

logger = logging.getLogger(__name__)

@dataclass
class EnhancedJobEntry:
    """Enhanced job entry with comprehensive field extraction"""
    jobTitle: str = ""
    company: str = ""
    location: str = ""
    startDate: str = ""
    endDate: str = ""
    description: str = ""
    confidence: float = 0.0
    sources_used: List[str] = None
    raw_text: str = ""
    
    def __post_init__(self):
        if self.sources_used is None:
            self.sources_used = []

class EnhancedWorkExperienceParser:
    """
    Enhanced work experience parser that:
    1. Properly segments multiple jobs
    2. Extracts all fields correctly
    3. Uses ALL datasets for normalization
    4. Ensures no key-value mismatches
    """
    
    def __init__(self):
        self.existing_parser = WorkExperienceParser()
        self.unified_loader = unified_loader
        
        # Load date patterns from dataset
        self.date_patterns = self._load_date_patterns()
        
        # Compile comprehensive regex patterns
        self._compile_enhanced_patterns()
        
        logger.info("Enhanced Work Experience Parser initialized")
        logger.info(f"Loaded {len(self.date_patterns)} date patterns")
    
    def _load_date_patterns(self) -> Dict[str, str]:
        """Load date patterns from external dataset"""
        patterns = {}
        try:
            date_data = self.unified_loader.get_unified_dataset('patterns')
            if date_data:
                for entry in date_data:
                    raw = entry.get('raw_date', '')
                    normalized = entry.get('normalized_date', '')
                    if raw and normalized:
                        patterns[raw.lower()] = normalized
            logger.info(f"Loaded {len(patterns)} date normalization patterns")
        except Exception as e:
            logger.warning(f"Failed to load date patterns: {e}")
        
        return patterns
    
    def _compile_enhanced_patterns(self):
        """Compile enhanced regex patterns for job extraction"""
        
        # Job boundary patterns - detect start of new job
        self.job_boundary_patterns = [
            # Title | Company | Date format
            r'^(?P<title>[^|]+?)\s*\|\s*(?P<company>[^|]+?)\s*\|\s*(?P<date>.+)$',
            # Company | Title | Date format  
            r'^(?P<company>[^|]+?)\s*\|\s*(?P<title>[^|]+?)\s*\|\s*(?P<date>.+)$',
            # Title at Company format
            r'^(?P<title>.+?)\s+at\s+(?P<company>.+?)(?:\s+(?P<date>.+))?$',
            # Worked at Company as Title
            r'^Worked\s+at\s+(?P<company>.+?)\s+as\s+(?P<title>.+?)(?:\s+(?P<date>.+))?$',
            # Company - Title format
            r'^(?P<company>.+?)\s*[-–—]\s*(?P<title>.+?)(?:\s+(?P<date>.+))?$',
            # Title, Company format
            r'^(?P<title>.+?),\s*(?P<company>.+?)(?:\s+(?P<date>.+))?$',
        ]
        
        # Date range patterns
        self.date_range_patterns = [
            r'(?P<start>\d{4})\s*[-–—]\s*(?P<present>present|current)',
            r'(?P<start>\w+\s+\d{4})\s*[-–—]\s*(?P<present>present|current)',
            r'(?P<start>\d{1,2}/\d{4})\s*[-–—]\s*(?P<present>present|current)',
            r'(?P<start>\d{4})\s*[-–—]\s*(?P<end>\d{4})',
            r'(?P<start>\w+\s+\d{4})\s*[-–—]\s*(?P<end>\w+\s+\d{4})',
            r'(?P<start>\d{1,2}/\d{4})\s*[-–—]\s*(?P<end>\d{1,2}/\d{4})',
            r'(?P<start>\w+\s+\d{4})\s*[-–—]\s*(?P<end>\w+\s+\d{4})',
            r'^(?P<start>\w+\s+\d{4})\s*(?:to|until)\s*(?P<present>present|current)',
            r'^(?P<start>\w+\s+\d{4})\s*(?:to|until)\s*(?P<end>\w+\s+\d{4})',
        ]
        
        # Compile all patterns
        self.compiled_job_patterns = []
        for pattern in self.job_boundary_patterns:
            try:
                self.compiled_job_patterns.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.warning(f"Failed to compile job pattern: {pattern} - {e}")
        
        self.compiled_date_patterns = []
        for pattern in self.date_range_patterns:
            try:
                self.compiled_date_patterns.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.warning(f"Failed to compile date pattern: {pattern} - {e}")
    
    def segment_jobs(self, text: str) -> List[str]:
        """
        Segment experience section into individual job entries
        This is the critical fix for proper job separation
        """
        if not text or not text.strip():
            return []
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        job_segments = []
        current_job = []
        
        for i, line in enumerate(lines):
            # Check if this line looks like a job header
            is_job_header = self._is_job_header(line)
            
            if is_job_header and current_job:
                # Save previous job and start new one
                job_segments.append('\n'.join(current_job))
                current_job = [line]
            elif is_job_header or not current_job:
                # Start new job
                current_job.append(line)
            else:
                # Continue current job
                current_job.append(line)
        
        # Add the last job
        if current_job:
            job_segments.append('\n'.join(current_job))
        
        logger.info(f"Segmented {len(job_segments)} jobs from experience section")
        return job_segments
    
    def _is_job_header(self, line: str) -> bool:
        """Check if a line is likely a job header"""
        line_lower = line.lower()
        
        # Check for job boundary patterns
        for pattern in self.compiled_job_patterns:
            if pattern.search(line):
                return True
        
        # Check for title keywords
        title_keywords = [
            'engineer', 'developer', 'manager', 'director', 'analyst', 
            'consultant', 'architect', 'lead', 'specialist', 'coordinator'
        ]
        
        # Check for company indicators
        company_indicators = ['inc', 'llc', 'ltd', 'corp', 'company']
        
        # Check for date patterns
        has_date = any(pattern.search(line) for pattern in self.compiled_date_patterns)
        
        # Heuristic: line with title keywords and company indicators or dates
        has_title = any(keyword in line_lower for keyword in title_keywords)
        has_company = any(indicator in line_lower for indicator in company_indicators)
        
        return (has_title and (has_company or has_date)) or has_date
    
    def extract_job_fields(self, job_text: str) -> EnhancedJobEntry:
        """
        Extract all fields from a job text segment
        This fixes the key-value mismatch issues
        """
        lines = job_text.split('\n')
        header_line = lines[0] if lines else ""
        description_lines = lines[1:] if len(lines) > 1 else []
        
        job_entry = EnhancedJobEntry()
        job_entry.raw_text = job_text
        job_entry.sources_used = ['enhanced_parser']
        
        # Extract fields from header
        self._extract_header_fields(header_line, job_entry)
        
        # Extract description
        job_entry.description = '\n'.join(description_lines).strip()
        
        # Apply normalization using unified datasets
        self._normalize_job_entry(job_entry)
        
        # Calculate confidence
        job_entry.confidence = self._calculate_confidence(job_entry)
        
        return job_entry
    
    def _extract_header_fields(self, header: str, job_entry: EnhancedJobEntry):
        """Extract fields from job header line"""
        # Try each pattern
        for pattern in self.compiled_job_patterns:
            match = pattern.search(header)
            if match:
                groups = match.groupdict()
                
                # Extract title
                if 'title' in groups and groups['title']:
                    job_entry.jobTitle = groups['title'].strip()
                
                # Extract company
                if 'company' in groups and groups['company']:
                    job_entry.company = groups['company'].strip()
                
                # Extract date
                if 'date' in groups and groups['date']:
                    self._parse_date_range(groups['date'], job_entry)
                
                break
        
        # If no pattern matched, try individual extraction
        if not job_entry.jobTitle or not job_entry.company:
            self._fallback_field_extraction(header, job_entry)
    
    def _fallback_field_extraction(self, header: str, job_entry: EnhancedJobEntry):
        """Fallback field extraction when patterns don't match"""
        # Try to extract dates first
        remaining_text = header
        for pattern in self.compiled_date_patterns:
            match = pattern.search(header)
            if match:
                self._parse_date_from_match(match, job_entry)
                # Remove date from text
                remaining_text = pattern.sub('', remaining_text).strip()
                break
        
        # Split remaining text by common separators
        separators = ['|', '-', '–', '—', 'at', ',']
        parts = [remaining_text]
        
        for sep in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(sep))
            parts = [p.strip() for p in new_parts if p.strip()]
        
        # Try to identify title vs company
        if len(parts) >= 2:
            # Use heuristics to identify title and company
            for i, part in enumerate(parts):
                if self._looks_like_job_title(part):
                    job_entry.jobTitle = part
                    # Company is likely the other part
                    other_idx = 1 - i if len(parts) == 2 else (i + 1) % len(parts)
                    if other_idx < len(parts):
                        job_entry.company = parts[other_idx]
                    break
                elif self._looks_like_company(part):
                    job_entry.company = part
                    # Title is likely the other part
                    other_idx = 1 - i if len(parts) == 2 else (i + 1) % len(parts)
                    if other_idx < len(parts):
                        job_entry.jobTitle = parts[other_idx]
                    break
        
        # If still not found, make educated guesses
        if not job_entry.jobTitle and parts:
            job_entry.jobTitle = parts[0]
        if not job_entry.company and len(parts) > 1:
            job_entry.company = parts[1]
    
    def _looks_like_job_title(self, text: str) -> bool:
        """Check if text looks like a job title"""
        title_keywords = [
            'engineer', 'developer', 'manager', 'director', 'analyst', 
            'consultant', 'architect', 'lead', 'specialist', 'coordinator',
            'officer', 'associate', 'head', 'executive', 'principal',
            'scientist', 'researcher', 'expert', 'intern', 'partner'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in title_keywords)
    
    def _looks_like_company(self, text: str) -> bool:
        """Check if text looks like a company name"""
        company_indicators = ['inc', 'llc', 'ltd', 'corp', 'corporation', 'company']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in company_indicators)
    
    def _parse_date_range(self, date_text: str, job_entry: EnhancedJobEntry):
        """Parse date range from text"""
        date_text = date_text.strip()
        
        # Check date patterns first
        for pattern in self.compiled_date_patterns:
            match = pattern.search(date_text)
            if match:
                self._parse_date_from_match(match, job_entry)
                return
        
        # Try dateparser as fallback
        try:
            if 'present' in date_text.lower() or 'current' in date_text.lower():
                parts = re.split(r'[-–—to]', date_text, flags=re.IGNORECASE)
                if parts:
                    start_part = parts[0].strip()
                    job_entry.startDate = self._normalize_date(start_part)
                    job_entry.endDate = 'Present'
            else:
                # Try to parse as date range
                parsed = dateparser.parse(date_text)
                if parsed:
                    job_entry.startDate = parsed.strftime('%Y-%m-%d')
        except Exception:
            pass
    
    def _parse_date_from_match(self, match: re.Match, job_entry: EnhancedJobEntry):
        """Parse date from regex match"""
        groups = match.groupdict()
        
        if 'start' in groups and groups['start']:
            job_entry.startDate = self._normalize_date(groups['start'])
        
        if 'end' in groups and groups['end']:
            if groups['end'].lower() in ['present', 'current']:
                job_entry.endDate = 'Present'
            else:
                job_entry.endDate = self._normalize_date(groups['end'])
        elif 'present' in groups and groups['present']:
            job_entry.endDate = 'Present'
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string using patterns and dateparser"""
        if not date_str:
            return ""
        
        date_str = date_str.strip().lower()
        
        # Check loaded patterns first
        if date_str in self.date_patterns:
            return self.date_patterns[date_str]
        
        # Try dateparser
        try:
            parsed = dateparser.parse(date_str)
            if parsed:
                return parsed.strftime('%Y-%m-%d')
        except Exception:
            pass
        
        # Return original if can't parse
        return date_str.title()
    
    def _normalize_job_entry(self, job_entry: EnhancedJobEntry):
        """Normalize job entry fields using unified datasets"""
        if job_entry.company:
            normalized = self.unified_loader.normalize_company_name(job_entry.company)
            if normalized != job_entry.company:
                job_entry.company = normalized
                job_entry.sources_used.append('company_normalization')
        
        if job_entry.jobTitle:
            normalized = self.unified_loader.normalize_job_title(job_entry.jobTitle)
            if normalized != job_entry.jobTitle:
                job_entry.jobTitle = normalized
                job_entry.sources_used.append('title_normalization')
        
        if job_entry.location:
            normalized = self.unified_loader.normalize_location(job_entry.location)
            if normalized != job_entry.location:
                job_entry.location = normalized
                job_entry.sources_used.append('location_normalization')
    
    def _calculate_confidence(self, job_entry: EnhancedJobEntry) -> float:
        """Calculate confidence score for job entry"""
        confidence = 0.0
        
        # Base confidence for having required fields
        if job_entry.jobTitle:
            confidence += 0.3
        if job_entry.company:
            confidence += 0.3
        if job_entry.startDate:
            confidence += 0.2
        if job_entry.endDate:
            confidence += 0.1
        if job_entry.description:
            confidence += 0.1
        
        # Boost for multiple sources
        source_boost = min(len(job_entry.sources_used) * 0.05, 0.15)
        confidence += source_boost
        
        return min(confidence, 1.0)
    
    def parse_experience_section(self, text: str, source_format: str = None) -> List[EnhancedJobEntry]:
        """
        Main parsing method with comprehensive fixes:
        1. Segment jobs properly
        2. Extract all fields
        3. Normalize using datasets
        4. Ensure no key-value mismatches
        """
        logger.info("Starting enhanced work experience parsing")
        
        if not text or not text.strip():
            logger.warning("Empty experience text provided")
            return []
        
        # Step 1: Segment into individual jobs
        job_segments = self.segment_jobs(text)
        
        # Step 2: Extract fields for each job
        enhanced_jobs = []
        for segment in job_segments:
            job_entry = self.extract_job_fields(segment)
            
            # Only include jobs with minimum required fields
            if job_entry.jobTitle and job_entry.company:
                enhanced_jobs.append(job_entry)
                logger.debug(f"Parsed job: {job_entry.jobTitle} at {job_entry.company}")
            else:
                logger.warning(f"Job segment missing required fields: {segment[:50]}...")
        
        # Step 3: Sort by confidence and date
        enhanced_jobs.sort(key=lambda x: (-x.confidence, x.startDate or ""), reverse=True)
        
        logger.info(f"Enhanced parsing complete: {len(enhanced_jobs)} valid jobs")
        return enhanced_jobs
    
    def convert_to_standard_format(self, enhanced_jobs: List[EnhancedJobEntry]) -> List[Dict[str, Any]]:
        """Convert enhanced entries to standard JSON format"""
        standard_jobs = []
        
        for job in enhanced_jobs:
            standard_job = {
                "jobTitle": job.jobTitle,
                "company": job.company,
                "location": job.location,
                "startDate": job.startDate,
                "endDate": job.endDate,
                "description": job.description
            }
            
            # Only include non-empty fields
            filtered_job = {k: v for k, v in standard_job.items() if v is not None and v != ""}
            
            if filtered_job:
                standard_jobs.append(filtered_job)
        
        return standard_jobs

# Global instance
enhanced_work_parser = EnhancedWorkExperienceParser()
