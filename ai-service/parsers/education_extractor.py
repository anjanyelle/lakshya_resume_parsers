"""
Advanced education extractor for resume parsing.
Extracts structured education information with degree normalization and GPA analysis.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class EducationExtractor:
    """
    Advanced education extractor with comprehensive parsing capabilities.
    Extracts structured education history with degree normalization and GPA analysis.
    """
    
    # Degree patterns for recognition
    DEGREE_PATTERNS = [
        'Bachelor', 'Master', 'PhD', 'Doctorate', 'Associate',
        'B.Sc', 'M.Sc', 'B.Tech', 'M.Tech', 'MBA', 'B.E', 'B.A', 'M.A',
        'B.S', 'M.S', 'B.Com', 'M.Com', 'BBA', 'BCA', 'MCA'
    ]
    
    # Degree level hierarchy for determining highest degree
    DEGREE_HIERARCHY = {
        'PhD': 8, 'Doctorate': 8, 'Doctor': 8,
        'Master': 7, 'M.Sc': 7, 'M.S': 7, 'M.Tech': 7, 'M.A': 7, 'M.Com': 7, 'MBA': 7, 'MCA': 7,
        'Bachelor': 6, 'B.Sc': 6, 'B.S': 6, 'B.Tech': 6, 'B.A': 6, 'B.Com': 6, 'BBA': 6, 'BCA': 6, 'B.E': 6,
        'Associate': 5,
        'Diploma': 4, 'Certificate': 3,
        'High School': 2, 'GED': 1
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pre-compile patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for education extraction."""
        
        # Degree patterns
        self.degree_pattern = re.compile(
            r'\b(' + '|'.join(self.DEGREE_PATTERNS) + r')(?:\s+(?:of|in)\s+([A-Za-z\s&]+))?',
            re.IGNORECASE
        )
        
        # Institution patterns
        self.institution_patterns = [
            r'\b([A-Za-z\s&]+(?:University|College|Institute|School|Academy))\b',
            r'\b([A-Za-z\s&]+(?:Polytechnic|Campus|Center|Centre))\b',
            r'\b([A-Z][a-zA-Z\s&]+(?:University|College|Institute))\b'
        ]
        
        # Year patterns
        self.year_pattern = re.compile(r'\b(19|20)\d{2}\b')
        self.year_range_pattern = re.compile(r'\b(19|20)\d{2}\s*[-–—]\s*(19|20)\d{4}\b')
        
        # GPA patterns
        self.gpa_patterns = [
            r'GPA[:\s]*([0-4]\.?\d*)',
            r'CGPA[:\s]*([0-4]\.?\d*)',
            r'Grade[:\s]*([A][-+]?|[B][-+]?|[C][-+]?|[D][-+]?)',
            r'Percentage[:\s]*([0-9]{1,3})%'
        ]
        
        # Field of study patterns
        self.field_patterns = [
            r'(?:in|of)\s+([A-Za-z\s&]+)(?:\s+(?:Engineering|Science|Arts|Commerce|Business|Studies))?',
            r'(?:Computer Science|Data Science|Machine Learning|Artificial Intelligence|Software Engineering|Information Technology)',
            r'(?:Mechanical|Electrical|Civil|Chemical|Biomedical|Aerospace)\s+Engineering',
            r'(?:Business Administration|Finance|Marketing|Human Resources|Economics|Accounting)'
        ]
    
    def extract_education(self, education_section_text: str) -> List[Dict]:
        """
        Extract structured education information from education section text.
        
        Args:
            education_section_text: Text from the education section
            
        Returns:
            List of education dictionaries with detailed information
        """
        try:
            if not education_section_text or not education_section_text.strip():
                return []
            
            # Split into individual education blocks
            edu_blocks = self._split_into_education_blocks(education_section_text)
            
            education_list = []
            
            for block in edu_blocks:
                education = self._parse_education_block(block)
                if education:
                    education_list.append(education)
            
            # Determine highest degree
            education_list = self._mark_highest_degree(education_list)
            
            # Sort by end year (most recent first)
            education_list.sort(key=lambda x: x.get('end_year', 0), reverse=True)
            
            self.logger.info(f"Extracted {len(education_list)} education entries")
            return education_list
            
        except Exception as e:
            self.logger.error(f"Error extracting education: {e}")
            return []
    
    def _split_into_education_blocks(self, text: str) -> List[str]:
        """
        Split education text into individual education blocks.
        
        Args:
            text: Education section text
            
        Returns:
            List of education blocks
        """
        # Split by common education separators
        separators = [
            r'\n(?=[A-Z][a-zA-Z\s]*\s*(?:University|College|Institute|School))',
            r'\n(?=\b(?:Bachelor|Master|PhD|Associate|Diploma|Certificate))',
            r'\n(?=\d{4})',
            r'\n(?=[A-Z][A-Za-z\s]{15,})'  # Long capitalized lines (likely institutions)
        ]
        
        combined_pattern = '|'.join(separators)
        blocks = re.split(combined_pattern, text, flags=re.MULTILINE)
        
        return [block.strip() for block in blocks if block.strip()]
    
    def _parse_education_block(self, block: str) -> Optional[Dict]:
        """
        Parse a single education block into structured data.
        
        Args:
            block: Education block text
            
        Returns:
            Dictionary with structured education information
        """
        try:
            education = {
                'degree': '',
                'field_of_study': None,
                'institution': '',
                'start_year': None,
                'end_year': None,
                'gpa': None,
                'is_highest_degree': False
            }
            
            # Extract degree
            education['degree'] = self._extract_degree(block)
            
            # Extract field of study
            education['field_of_study'] = self._extract_field_of_study(block)
            
            # Extract institution
            education['institution'] = self._extract_institution(block)
            
            # Extract years
            start_year, end_year = self._extract_years(block)
            education['start_year'] = start_year
            education['end_year'] = end_year
            
            # Extract GPA
            education['gpa'] = self._extract_gpa(block)
            
            return education if education['degree'] or education['institution'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing education block: {e}")
            return None
    
    def _extract_degree(self, block: str) -> str:
        """Extract degree from block."""
        matches = self.degree_pattern.findall(block)
        if matches:
            degree = matches[0][0]
            # Normalize degree
            return self.normalize_degree(degree)
        
        # Check for degree variations
        degree_variations = {
            'B.S.': 'Bachelor of Science',
            'M.S.': 'Master of Science',
            'B.A.': 'Bachelor of Arts',
            'M.A.': 'Master of Arts',
            'B.Tech': 'Bachelor of Technology',
            'M.Tech': 'Master of Technology'
        }
        
        for variation, normalized in degree_variations.items():
            if variation in block:
                return normalized
        
        return ''
    
    def _extract_field_of_study(self, block: str) -> Optional[str]:
        """Extract field of study from block."""
        for pattern in self.field_patterns:
            matches = re.findall(pattern, block, re.IGNORECASE)
            if matches:
                field = matches[0].strip()
                # Clean up field name
                field = re.sub(r'\s+', ' ', field)
                if len(field) > 2:
                    return field
        
        return None
    
    def _extract_institution(self, block: str) -> str:
        """Extract institution name from block."""
        for pattern in self.institution_patterns:
            matches = re.findall(pattern, block, re.IGNORECASE)
            if matches:
                institution = matches[0].strip()
                # Clean up institution name
                institution = re.sub(r'[\|\-•].*$', '', institution).strip()
                if len(institution) > 3:
                    return institution
        
        return ''
    
    def _extract_years(self, block: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract start and end years from block."""
        # Try year range first
        range_matches = self.year_range_pattern.findall(block)
        if range_matches:
            start_year, end_year = range_matches[0]
            return int(start_year), int(end_year)
        
        # Try individual years
        year_matches = self.year_pattern.findall(block)
        if len(year_matches) >= 2:
            return int(year_matches[0]), int(year_matches[1])
        elif year_matches:
            return None, int(year_matches[0])
        
        return None, None
    
    def _extract_gpa(self, block: str) -> Optional[float]:
        """Extract GPA from block."""
        for pattern in self.gpa_patterns:
            matches = re.findall(pattern, block, re.IGNORECASE)
            if matches:
                try:
                    gpa_value = matches[0]
                    # Handle letter grades
                    if gpa_value in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D']:
                        # Convert letter grade to GPA scale
                        grade_to_gpa = {'A+': 4.0, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0}
                        return grade_to_gpa.get(gpa_value, None)
                    
                    # Handle percentage
                    if '%' in gpa_value:
                        percentage = float(gpa_value.replace('%', ''))
                        return min(4.0, percentage / 25)  # Convert percentage to 4.0 scale
                    
                    # Handle numeric GPA
                    return float(gpa_value)
                except ValueError:
                    continue
        
        return None
    
    def normalize_degree(self, raw_degree: str) -> str:
        """
        Normalize degree name to standard format.
        
        Args:
            raw_degree: Raw degree string
            
        Returns:
            Normalized degree name
        """
        if not raw_degree:
            return raw_degree
        
        # Degree mapping for normalization
        degree_mapping = {
            # Bachelor variations
            'BS': 'Bachelor of Science',
            'B.S': 'Bachelor of Science',
            'B.S.': 'Bachelor of Science',
            'BSc': 'Bachelor of Science',
            'B.Sc': 'Bachelor of Science',
            'B.Sc.': 'Bachelor of Science',
            
            'BA': 'Bachelor of Arts',
            'B.A': 'Bachelor of Arts',
            'B.A.': 'Bachelor of Arts',
            
            'B.Tech': 'Bachelor of Technology',
            'B.Tech.': 'Bachelor of Technology',
            'BTech': 'Bachelor of Technology',
            
            'B.E': 'Bachelor of Engineering',
            'B.E.': 'Bachelor of Engineering',
            'BE': 'Bachelor of Engineering',
            
            'B.Com': 'Bachelor of Commerce',
            'B.Com.': 'Bachelor of Commerce',
            'BBA': 'Bachelor of Business Administration',
            
            # Master variations
            'MS': 'Master of Science',
            'M.S': 'Master of Science',
            'M.S.': 'Master of Science',
            'MSc': 'Master of Science',
            'M.Sc': 'Master of Science',
            'M.Sc.': 'Master of Science',
            
            'MA': 'Master of Arts',
            'M.A': 'Master of Arts',
            'M.A.': 'Master of Arts',
            
            'M.Tech': 'Master of Technology',
            'M.Tech.': 'Master of Technology',
            'MTech': 'Master of Technology',
            
            'M.Com': 'Master of Commerce',
            'M.Com.': 'Master of Commerce',
            'MBA': 'Master of Business Administration',
            'MCA': 'Master of Computer Applications',
            
            # PhD variations
            'Ph.D': 'PhD',
            'Ph.D.': 'PhD',
            'Doctorate': 'PhD'
        }
        
        # Clean and normalize input
        clean_degree = raw_degree.strip()
        
        # Direct mapping
        if clean_degree in degree_mapping:
            return degree_mapping[clean_degree]
        
        # Pattern matching for variations
        for pattern, normalized in degree_mapping.items():
            if pattern.lower() in clean_degree.lower():
                return normalized
        
        # Return original if no mapping found
        return clean_degree
    
    def _mark_highest_degree(self, education_list: List[Dict]) -> List[Dict]:
        """
        Mark the highest degree in the education list.
        
        Args:
            education_list: List of education dictionaries
            
        Returns:
            Updated education list with highest degree marked
        """
        if not education_list:
            return education_list
        
        max_level = -1
        highest_degree_index = 0
        
        for i, edu in enumerate(education_list):
            degree = edu.get('degree', '')
            level = self._get_degree_level(degree)
            
            if level > max_level:
                max_level = level
                highest_degree_index = i
        
        # Mark the highest degree
        if highest_degree_index < len(education_list):
            education_list[highest_degree_index]['is_highest_degree'] = True
        
        return education_list
    
    def _get_degree_level(self, degree: str) -> int:
        """
        Get the hierarchy level of a degree.
        
        Args:
            degree: Degree name
            
        Returns:
            Hierarchy level (higher number = higher degree)
        """
        if not degree:
            return 0
        
        for normalized_degree, level in self.DEGREE_HIERARCHY.items():
            if normalized_degree.lower() in degree.lower():
                return level
        
        return 0
    
    def get_education_summary(self, education_list: List[Dict]) -> Dict:
        """
        Get summary statistics for education history.
        
        Args:
            education_list: List of education dictionaries
            
        Returns:
            Dictionary with education summary
        """
        try:
            summary = {
                'total_degrees': len(education_list),
                'highest_degree': '',
                'institutions': [],
                'fields_of_study': [],
                'average_gpa': None,
                'education_span_years': 0
            }
            
            if not education_list:
                return summary
            
            # Find highest degree
            for edu in education_list:
                if edu.get('is_highest_degree'):
                    summary['highest_degree'] = edu.get('degree', '')
                    break
            
            # Collect unique institutions and fields
            institutions = set()
            fields = set()
            gpa_values = []
            years = []
            
            for edu in education_list:
                if edu.get('institution'):
                    institutions.add(edu['institution'])
                if edu.get('field_of_study'):
                    fields.add(edu['field_of_study'])
                if edu.get('gpa'):
                    gpa_values.append(edu['gpa'])
                if edu.get('end_year'):
                    years.append(edu['end_year'])
            
            summary['institutions'] = sorted(list(institutions))
            summary['fields_of_study'] = sorted(list(fields))
            
            # Calculate average GPA
            if gpa_values:
                summary['average_gpa'] = round(sum(gpa_values) / len(gpa_values), 2)
            
            # Calculate education span
            if years:
                summary['education_span_years'] = max(years) - min(years)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error calculating education summary: {e}")
            return {
                'total_degrees': 0,
                'highest_degree': '',
                'institutions': [],
                'fields_of_study': [],
                'average_gpa': None,
                'education_span_years': 0
            }


# Example usage and testing
if __name__ == "__main__":
    # Sample education text for testing
    sample_education = """
    Bachelor of Science in Computer Science
    University of Technology
    2014 - 2018
    GPA: 3.8
    
    Master of Technology in Software Engineering
    Indian Institute of Technology
    2019 - 2021
    CGPA: 8.5
    
    PhD in Artificial Intelligence
    Stanford University
    2022 - Present
    """
    
    extractor = EducationExtractor()
    
    # Test education extraction
    education_list = extractor.extract_education(sample_education)
    print(f"Extracted {len(education_list)} education entries:")
    
    for i, edu in enumerate(education_list, 1):
        print(f"\n{i}. {edu['degree']}")
        print(f"   Field: {edu['field_of_study']}")
        print(f"   Institution: {edu['institution']}")
        print(f"   Years: {edu['start_year']} - {edu['end_year']}")
        print(f"   GPA: {edu['gpa']}")
        print(f"   Highest Degree: {edu['is_highest_degree']}")
    
    # Test degree normalization
    test_degrees = ['BS', 'B.S.', 'M.S.', 'Ph.D', 'B.Tech', 'MBA']
    print(f"\nDegree Normalization:")
    for degree in test_degrees:
        normalized = extractor.normalize_degree(degree)
        print(f"{degree} -> {normalized}")
    
    # Test education summary
    summary = extractor.get_education_summary(education_list)
    print(f"\nEducation Summary:")
    print(f"Highest Degree: {summary['highest_degree']}")
    print(f"Total Degrees: {summary['total_degrees']}")
    print(f"Institutions: {', '.join(summary['institutions'])}")
    print(f"Average GPA: {summary['average_gpa']}")
