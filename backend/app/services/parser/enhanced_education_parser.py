"""
Enhanced Education Parser - Structured Field Extraction
Fixes education parsing to ensure proper field extraction and normalization
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.services.parser.utils.enhanced_dataset_loader import unified_loader

logger = logging.getLogger(__name__)

@dataclass
class EnhancedEducationEntry:
    """Enhanced education entry with comprehensive field extraction"""
    institution: str = ""
    degree: str = ""
    fieldOfStudy: str = ""
    graduationYear: str = ""
    startDate: str = ""
    endDate: str = ""
    gpa: str = ""
    confidence: float = 0.0
    sources_used: List[str] = None
    raw_text: str = ""
    
    def __post_init__(self):
        if self.sources_used is None:
            self.sources_used = []

class EnhancedEducationParser:
    """
    Enhanced education parser that:
    1. Properly extracts all education fields
    2. Normalizes using datasets
    3. Ensures structured output
    """
    
    def __init__(self):
        self.unified_loader = unified_loader
        
        # Compile education patterns
        self._compile_education_patterns()
        
        logger.info("Enhanced Education Parser initialized")
    
    def _compile_education_patterns(self):
        """Compile regex patterns for education extraction"""
        
        # Education entry patterns
        self.education_patterns = [
            # Degree in Field at Institution (Year)
            r'^(?P<degree>.+?)\s+in\s+(?P<field>.+?)\s+at\s+(?P<institution>.+?)(?:\s*\((?P<year>\d{4})\))?$',
            # Institution - Degree (Year)
            r'^(?P<institution>.+?)\s*[-–—]\s*(?P<degree>.+?)(?:\s*\((?P<year>\d{4})\))?$',
            # Degree, Institution, Year
            r'^(?P<degree>.+?),\s*(?P<institution>.+?)(?:,\s*(?P<year>\d{4}))?$',
            # Institution | Degree | Year
            r'^(?P<institution>.+?)\s*\|\s*(?P<degree>.+?)(?:\s*\|\s*(?P<year>\d{4}))?$',
            # Degree from Institution (Year)
            r'^(?P<degree>.+?)\s+from\s+(?P<institution>.+?)(?:\s*\((?P<year>\d{4})\))?$',
        ]
        
        # Degree patterns
        self.degree_patterns = [
            r'\b(?:bachelor|master|ph\.?d|mba|b\.?s|m\.?s|b\.?tech|m\.?tech|b\.?sc|m\.?sc)\b',
            r'\b(?:associate|doctorate|postgraduate|undergraduate)\b',
            r'\b(?:certificate|diploma)\b',
        ]
        
        # Institution patterns
        self.institution_patterns = [
            r'\b(?:university|college|institute|institute\s+of\s+technology|school)\b',
            r'\b(?:academy|academy\s+of)\b',
        ]
        
        # Field of study patterns
        self.field_patterns = [
            r'\b(?:engineering|science|arts|business|computer|information\s+technology)\b',
            r'\b(?:mathematics|physics|chemistry|biology|economics|psychology)\b',
        ]
        
        # Date patterns
        self.date_patterns = [
            r'\b\d{4}\b',
            r'\b(?:graduated|completion|awarded)\s+(?:in\s+)?\d{4}\b',
        ]
        
        # GPA patterns
        self.gpa_patterns = [
            r'\b(?:gpa|grade)\s*[:\-]?\s*([\d.]+)',
            r'\b([\d.]+)\s*(?:out\s*of\s*[\d.]+|/[\d.]+)\s*(?:gpa)?\b',
        ]
        
        # Compile all patterns
        self.compiled_education_patterns = []
        for pattern in self.education_patterns:
            try:
                self.compiled_education_patterns.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.warning(f"Failed to compile education pattern: {pattern} - {e}")
        
        self.compiled_degree_patterns = []
        for pattern in self.degree_patterns:
            try:
                self.compiled_degree_patterns.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.warning(f"Failed to compile degree pattern: {pattern} - {e}")
        
        self.compiled_gpa_patterns = []
        for pattern in self.gpa_patterns:
            try:
                self.compiled_gpa_patterns.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.warning(f"Failed to compile GPA pattern: {pattern} - {e}")
    
    def extract_education_fields(self, education_text: str) -> EnhancedEducationEntry:
        """Extract all fields from education text"""
        education_entry = EnhancedEducationEntry()
        education_entry.raw_text = education_text
        education_entry.sources_used = ['enhanced_parser']
        
        # Try structured patterns first
        for pattern in self.compiled_education_patterns:
            match = pattern.search(education_text)
            if match:
                groups = match.groupdict()
                
                if 'institution' in groups and groups['institution']:
                    education_entry.institution = groups['institution'].strip()
                if 'degree' in groups and groups['degree']:
                    education_entry.degree = groups['degree'].strip()
                if 'field' in groups and groups['field']:
                    education_entry.fieldOfStudy = groups['field'].strip()
                if 'year' in groups and groups['year']:
                    education_entry.graduationYear = groups['year'].strip()
                
                break
        
        # If pattern didn't match, try individual extraction
        if not education_entry.institution or not education_entry.degree:
            self._fallback_field_extraction(education_text, education_entry)
        
        # Extract GPA
        self._extract_gpa(education_text, education_entry)
        
        # Extract dates
        self._extract_dates(education_text, education_entry)
        
        # Normalize using datasets
        self._normalize_education_entry(education_entry)
        
        # Calculate confidence
        education_entry.confidence = self._calculate_confidence(education_entry)
        
        return education_entry
    
    def _fallback_field_extraction(self, text: str, entry: EnhancedEducationEntry):
        """Fallback field extraction when patterns don't match"""
        # Extract institution
        if not entry.institution:
            for pattern in self.compiled_degree_patterns:
                # Look for institution before degree
                matches = list(pattern.finditer(text))
                for match in matches:
                    before = text[:match.start()].strip()
                    if before and len(before.split()) <= 5:  # Likely institution
                        entry.institution = before
                        break
                if entry.institution:
                    break
        
        # Extract degree
        if not entry.degree:
            degrees_found = []
            for pattern in self.compiled_degree_patterns:
                matches = pattern.findall(text)
                degrees_found.extend(matches)
            
            if degrees_found:
                entry.degree = degrees_found[0]
        
        # Extract field of study
        if not entry.fieldOfStudy:
            # Look for field patterns
            for pattern in self.field_patterns:
                matches = pattern.findall(text)
                if matches:
                    entry.fieldOfStudy = matches[0]
                    break
        
        # Extract graduation year
        if not entry.graduationYear:
            for pattern in self.date_patterns:
                matches = pattern.findall(text)
                if matches:
                    entry.graduationYear = matches[0]
                    break
    
    def _extract_gpa(self, text: str, entry: EnhancedEducationEntry):
        """Extract GPA from text"""
        for pattern in self.compiled_gpa_patterns:
            match = pattern.search(text)
            if match:
                gpa_value = match.group(1) if match.groups() else match.group(0)
                if gpa_value:
                    entry.gpa = gpa_value.strip()
                    break
    
    def _extract_dates(self, text: str, entry: EnhancedEducationEntry):
        """Extract education dates"""
        # Look for date ranges
        date_range_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|\b(?:present|current)\b)'
        match = re.search(date_range_pattern, text, re.IGNORECASE)
        if match:
            entry.startDate = match.group(1)
            end_date = match.group(2)
            entry.endDate = 'Present' if end_date.lower() in ['present', 'current'] else end_date
        else:
            # Look for single year (graduation year)
            year_pattern = r'\b(\d{4})\b'
            matches = re.findall(year_pattern, text)
            if matches:
                # Use the last year as graduation year
                entry.graduationYear = matches[-1]
    
    def _normalize_education_entry(self, entry: EnhancedEducationEntry):
        """Normalize education entry using unified datasets"""
        if entry.institution:
            normalized = self.unified_loader.normalize_education(entry.institution)
            if normalized != entry.institution:
                entry.institution = normalized
                entry.sources_used.append('institution_normalization')
        
        if entry.degree:
            # Normalize degree using patterns
            normalized = self._normalize_degree(entry.degree)
            if normalized != entry.degree:
                entry.degree = normalized
                entry.sources_used.append('degree_normalization')
        
        if entry.fieldOfStudy:
            # Capitalize properly
            entry.fieldOfStudy = ' '.join(word.capitalize() for word in entry.fieldOfStudy.split())
    
    def _normalize_degree(self, degree: str) -> str:
        """Normalize degree name"""
        if not degree:
            return degree
        
        degree_lower = degree.lower().strip()
        
        # Common degree normalizations
        degree_mappings = {
            'b.s.': 'Bachelor of Science',
            'm.s.': 'Master of Science',
            'b.a.': 'Bachelor of Arts',
            'm.a.': 'Master of Arts',
            'b.tech': 'Bachelor of Technology',
            'm.tech': 'Master of Technology',
            'b.sc': 'Bachelor of Science',
            'm.sc': 'Master of Science',
            'phd': 'PhD',
            'ph.d': 'PhD',
            'mba': 'MBA',
        }
        
        for abbr, full in degree_mappings.items():
            if degree_lower == abbr:
                return full
            if f' {abbr} ' in f' {degree_lower} ':
                return re.sub(rf'\b{abbr}\b', full, degree, flags=re.IGNORECASE)
        
        return degree.title()
    
    def _calculate_confidence(self, entry: EnhancedEducationEntry) -> float:
        """Calculate confidence score for education entry"""
        confidence = 0.0
        
        # Base confidence for having required fields
        if entry.institution:
            confidence += 0.3
        if entry.degree:
            confidence += 0.3
        if entry.fieldOfStudy:
            confidence += 0.2
        if entry.graduationYear or entry.startDate:
            confidence += 0.1
        if entry.gpa:
            confidence += 0.1
        
        # Boost for multiple sources
        source_boost = min(len(entry.sources_used) * 0.05, 0.15)
        confidence += source_boost
        
        return min(confidence, 1.0)
    
    def parse_education_section(self, education_data: Any) -> List[EnhancedEducationEntry]:
        """
        Main parsing method for education section
        Handles both raw text and structured data
        """
        logger.info("Starting enhanced education parsing")
        
        enhanced_education = []
        
        if isinstance(education_data, str):
            # Raw text parsing - split by common separators
            entries = self._split_education_text(education_data)
            for entry_text in entries:
                education_entry = self.extract_education_fields(entry_text)
                if education_entry.institution or education_entry.degree:
                    enhanced_education.append(education_entry)
        
        elif isinstance(education_data, list):
            # Structured data enhancement
            for edu_dict in education_data:
                if not isinstance(edu_dict, dict):
                    continue
                
                # Convert dict to text for parsing
                text_parts = []
                for field in ['institution', 'degree', 'field_of_study', 'fieldOfStudy', 'graduationYear']:
                    value = edu_dict.get(field, '')
                    if value:
                        text_parts.append(str(value))
                
                if text_parts:
                    entry_text = ' '.join(text_parts)
                    education_entry = self.extract_education_fields(entry_text)
                    
                    # Preserve additional fields from original
                    education_entry.startDate = edu_dict.get('startDate') or edu_dict.get('start_date', '')
                    education_entry.endDate = edu_dict.get('endDate') or edu_dict.get('end_date', '')
                    education_entry.gpa = edu_dict.get('gpa', '')
                    
                    enhanced_education.append(education_entry)
        
        elif isinstance(education_data, dict):
            # Handle dict with content field
            content = education_data.get('content', '')
            if content:
                entries = self._split_education_text(content)
                for entry_text in entries:
                    education_entry = self.extract_education_fields(entry_text)
                    if education_entry.institution or education_entry.degree:
                        enhanced_education.append(education_entry)
        
        # Sort by confidence and graduation year
        enhanced_education.sort(key=lambda x: (-x.confidence, x.graduationYear or ""), reverse=True)
        
        logger.info(f"Enhanced education parsing complete: {len(enhanced_education)} valid entries")
        return enhanced_education
    
    def _split_education_text(self, text: str) -> List[str]:
        """Split education text into individual entries"""
        if not text:
            return []
        
        # Common separators for education entries
        separators = ['\n\n', '\n', ';', '|']
        
        # Try to find the best separator
        for sep in separators:
            parts = [part.strip() for part in text.split(sep) if part.strip()]
            if len(parts) > 1:
                return parts
        
        # If no separator found, return as single entry
        return [text.strip()]
    
    def convert_to_standard_format(self, enhanced_education: List[EnhancedEducationEntry]) -> List[Dict[str, Any]]:
        """Convert enhanced education to standard JSON format"""
        standard_education = []
        
        for edu in enhanced_education:
            standard_edu = {
                "institution": edu.institution,
                "degree": edu.degree,
                "fieldOfStudy": edu.fieldOfStudy,
                "graduationYear": edu.graduationYear,
                "startDate": edu.startDate,
                "endDate": edu.endDate,
                "gpa": edu.gpa
            }
            
            # Only include non-empty fields
            filtered_edu = {k: v for k, v in standard_edu.items() if v is not None and v != ""}
            
            if filtered_edu:
                standard_education.append(filtered_edu)
        
        return standard_education

# Global instance
enhanced_education_parser = EnhancedEducationParser()
