"""
Layout-based Section Detector for Resume Parsing
Advanced section detection using layout analysis and pattern recognition
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SectionType(Enum):
    """Enumeration of resume section types"""
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    SUMMARY = "summary"
    CONTACT = "contact"
    LANGUAGES = "languages"
    INTERESTS = "interests"
    REFERENCES = "references"
    PUBLICATIONS = "publications"
    AWARDS = "awards"
    UNKNOWN = "unknown"

@dataclass
class Section:
    """Data class representing a detected section"""
    section_type: SectionType
    title: str
    start_line: int
    end_line: int
    content: List[str]
    confidence: float
    metadata: Dict[str, Any]

class LayoutSectionDetector:
    """
    Advanced section detector using layout analysis,
    pattern recognition, and machine learning techniques
    """
    
    def __init__(self):
        """Initialize the layout section detector"""
        self.section_patterns = self._build_section_patterns()
        self.layout_indicators = self._build_layout_indicators()
        self.contextual_patterns = self._build_contextual_patterns()
        self.section_hierarchy = self._build_section_hierarchy()
        
        logger.info("Layout Section Detector initialized")
    
    def _build_section_patterns(self) -> Dict[SectionType, List[Dict]]:
        """Build comprehensive section patterns"""
        return {
            SectionType.EXPERIENCE: [
                {'pattern': r'^\s*(?:PROFESSIONAL\s+)?EXPERIENCE\s*$', 'weight': 1.0},
                {'pattern': r'^\s*(?:WORK\s+)?EXPERIENCE\s*$', 'weight': 1.0},
                {'pattern': r'^\s*EMPLOYMENT\s+HISTORY\s*$', 'weight': 0.9},
                {'pattern': r'^\s*WORK\s+HISTORY\s*$', 'weight': 0.9},
                {'pattern': r'^\s*CAREER\s+HISTORY\s*$', 'weight': 0.8},
                {'pattern': r'^\s*EXPERIENCE\s*$', 'weight': 0.7},
                {'pattern': r'^\s*WORK\s*$', 'weight': 0.6},
                {'pattern': r'^\s*PROFESSIONAL\s+BACKGROUND\s*$', 'weight': 0.8},
                {'pattern': r'^\s*CAREER\s+OVERVIEW\s*$', 'weight': 0.7}
            ],
            SectionType.EDUCATION: [
                {'pattern': r'^\s*EDUCATION\s*$', 'weight': 1.0},
                {'pattern': r'^\s*EDUCATIONAL\s+BACKGROUND\s*$', 'weight': 0.9},
                {'pattern': r'^\s*ACADEMIC\s+BACKGROUND\s*$', 'weight': 0.9},
                {'pattern': r'^\s*QUALIFICATIONS\s*$', 'weight': 0.8},
                {'pattern': r'^\s*ACADEMIC\s+QUALIFICATIONS\s*$', 'weight': 0.8},
                {'pattern': r'^\s*TRAINING\s+&\s+DEVELOPMENT\s*$', 'weight': 0.7},
                {'pattern': r'^\s*EDUCATION\s+&\s+TRAINING\s*$', 'weight': 0.7}
            ],
            SectionType.SKILLS: [
                {'pattern': r'^\s*SKILLS\s*$', 'weight': 1.0},
                {'pattern': r'^\s*TECHNICAL\s+SKILLS\s*$', 'weight': 1.0},
                {'pattern': r'^\s*SKILLS\s+&\s+COMPETENCIES\s*$', 'weight': 0.9},
                {'pattern': r'^\s*CORE\s+COMPETENCIES\s*$', 'weight': 0.8},
                {'pattern': r'^\s*TECHNICAL\s+EXPERTISE\s*$', 'weight': 0.8},
                {'pattern': r'^\s*SKILL\s+SET\s*$', 'weight': 0.7},
                {'pattern': r'^\s*COMPETENCIES\s*$', 'weight': 0.7},
                {'pattern': r'^\s*EXPERTISE\s*$', 'weight': 0.6},
                {'pattern': r'^\s*PROFICIENCIES\s*$', 'weight': 0.6}
            ],
            SectionType.PROJECTS: [
                {'pattern': r'^\s*PROJECTS\s*$', 'weight': 1.0},
                {'pattern': r'^\s*PROJECT\s+EXPERIENCE\s*$', 'weight': 0.9},
                {'pattern': r'^\s*ACADEMIC\s+PROJECTS\s*$', 'weight': 0.8},
                {'pattern': r'^\s*PERSONAL\s+PROJECTS\s*$', 'weight': 0.8},
                {'pattern': r'^\s*PROJECT\s+PORTFOLIO\s*$', 'weight': 0.7},
                {'pattern': r'^\s*KEY\s+PROJECTS\s*$', 'weight': 0.7}
            ],
            SectionType.CERTIFICATIONS: [
                {'pattern': r'^\s*CERTIFICATIONS\s*$', 'weight': 1.0},
                {'pattern': r'^\s*CERTIFICATES\s*$', 'weight': 0.9},
                {'pattern': r'^\s*PROFESSIONAL\s+CERTIFICATIONS\s*$', 'weight': 0.9},
                {'pattern': r'^\s*CREDENTIALS\s*$', 'weight': 0.8},
                {'pattern': r'^\s*LICENSURES\s*$', 'weight': 0.7},
                {'pattern': r'^\s*ACCREDITATIONS\s*$', 'weight': 0.7}
            ],
            SectionType.SUMMARY: [
                {'pattern': r'^\s*(?:PROFESSIONAL\s+)?SUMMARY\s*$', 'weight': 1.0},
                {'pattern': r'^\s*OBJECTIVE\s*$', 'weight': 0.9},
                {'pattern': r'^\s*PROFILE\s*$', 'weight': 0.9},
                {'pattern': r'^\s*OVERVIEW\s*$', 'weight': 0.8},
                {'pattern': r'^\s*INTRODUCTION\s*$', 'weight': 0.8},
                {'pattern': r'^\s*ABOUT\s+ME\s*$', 'weight': 0.7},
                {'pattern': r'^\s*CAREER\s+SUMMARY\s*$', 'weight': 0.7},
                {'pattern': r'^\s*EXECUTIVE\s+SUMMARY\s*$', 'weight': 0.7}
            ],
            SectionType.CONTACT: [
                {'pattern': r'^\s*CONTACT\s*$', 'weight': 1.0},
                {'pattern': r'^\s*CONTACT\s+INFORMATION\s*$', 'weight': 0.9},
                {'pattern': r'^\s*PERSONAL\s+INFORMATION\s*$', 'weight': 0.8},
                {'pattern': r'^\s*CONTACT\s+DETAILS\s*$', 'weight': 0.7}
            ],
            SectionType.LANGUAGES: [
                {'pattern': r'^\s*LANGUAGES\s*$', 'weight': 1.0},
                {'pattern': r'^\s*LANGUAGE\s+SKILLS\s*$', 'weight': 0.9},
                {'pattern': r'^\s*LANGUAGE\s+PROFICIENCY\s*$', 'weight': 0.8},
                {'pattern': r'^\s*SPOKEN\s+LANGUAGES\s*$', 'weight': 0.7}
            ],
            SectionType.INTERESTS: [
                {'pattern': r'^\s*INTERESTS\s*$', 'weight': 1.0},
                {'pattern': r'^\s*HOBBIES\s*$', 'weight': 0.9},
                {'pattern': r'^\s*PERSONAL\s+INTERESTS\s*$', 'weight': 0.8},
                {'pattern': r'^\s*ACTIVITIES\s*$', 'weight': 0.7}
            ],
            SectionType.REFERENCES: [
                {'pattern': r'^\s*REFERENCES\s*$', 'weight': 1.0},
                {'pattern': r'^\s*PROFESSIONAL\s+REFERENCES\s*$', 'weight': 0.9},
                {'pattern': r'^\s*REFERENCES\s+AVAILABLE\s+UPON\s+REQUEST\s*$', 'weight': 0.8}
            ],
            SectionType.PUBLICATIONS: [
                {'pattern': r'^\s*PUBLICATIONS\s*$', 'weight': 1.0},
                {'pattern': r'^\s*RESEARCH\s+PUBLICATIONS\s*$', 'weight': 0.9},
                {'pattern': r'^\s*ACADEMIC\s+PUBLICATIONS\s*$', 'weight': 0.8},
                {'pattern': r'^\s*PAPERS\s*$', 'weight': 0.7}
            ],
            SectionType.AWARDS: [
                {'pattern': r'^\s*AWARDS\s*$', 'weight': 1.0},
                {'pattern': r'^\s*ACHIEVEMENTS\s*$', 'weight': 0.9},
                {'pattern': r'^\s*HONORS\s+&\s+AWARDS\s*$', 'weight': 0.8},
                {'pattern': r'^\s*RECOGNITION\s*$', 'weight': 0.7}
            ]
        }
    
    def _build_layout_indicators(self) -> Dict[str, Any]:
        """Build layout-based indicators"""
        return {
            'capitalization_patterns': {
                'all_caps': r'^[A-Z\s\-]+$',
                'title_case': r'^[A-Z][a-zA-Z\s\-]*$',
                'mixed_case': r'^[A-Za-z\s\-]+$'
            },
            'formatting_patterns': {
                'colon_separated': r'^[^:]+:\s*$',
                'dash_separated': r'^[^-]+\s*-\s*$',
                'underline_separated': r'^[^_]+_+$',
                'hash_separated': r'^#+\s*[^#]+$',
                'bullet_separated': r'^[•\-\*]\s+[^•\-\*]+$'
            },
            'position_indicators': {
                'centered': r'^\s*[A-Z\s\-]+\s*$',
                'left_aligned': r'^[A-Z\s\-]+',
                'right_aligned': r'\s*[A-Z\s\-]+$'
            },
            'spacing_patterns': {
                'double_space': r'^\s*[A-Z\s\-]+\s*$',
                'single_space': r'^[A-Z\s\-]+$',
                'no_space': r'^[A-Z\-]+$'
            }
        }
    
    def _build_contextual_patterns(self) -> Dict[SectionType, List[str]]:
        """Build contextual patterns for section validation"""
        return {
            SectionType.EXPERIENCE: [
                'company', 'position', 'role', 'duration', 'responsibilities',
                'achievements', 'employment', 'work', 'career', 'professional'
            ],
            SectionType.EDUCATION: [
                'university', 'college', 'degree', 'major', 'gpa', 'graduation',
                'academic', 'school', 'institution', 'qualification', 'diploma'
            ],
            SectionType.SKILLS: [
                'programming', 'technical', 'software', 'tools', 'languages',
                'frameworks', 'databases', 'technologies', 'expertise', 'proficiency'
            ],
            SectionType.PROJECTS: [
                'project', 'developed', 'built', 'created', 'designed', 'implemented',
                'application', 'system', 'platform', 'solution', 'product'
            ],
            SectionType.CERTIFICATIONS: [
                'certified', 'certificate', 'license', 'accreditation', 'credential',
                'qualified', 'training', 'course', 'workshop', 'seminar'
            ],
            SectionType.SUMMARY: [
                'experienced', 'professional', 'skilled', 'expert', 'specialized',
                'background', 'overview', 'profile', 'objective', 'goal'
            ]
        }
    
    def _build_section_hierarchy(self) -> List[SectionType]:
        """Build typical section hierarchy in resumes"""
        return [
            SectionType.CONTACT,
            SectionType.SUMMARY,
            SectionType.EXPERIENCE,
            SectionType.EDUCATION,
            SectionType.SKILLS,
            SectionType.PROJECTS,
            SectionType.CERTIFICATIONS,
            SectionType.AWARDS,
            SectionType.PUBLICATIONS,
            SectionType.LANGUAGES,
            SectionType.INTERESTS,
            SectionType.REFERENCES
        ]
    
    def detect_sections(self, text: str) -> List[Section]:
        """
        Detect sections in resume text using layout analysis
        
        Args:
            text: Resume text to analyze
            
        Returns:
            List of detected sections
        """
        lines = text.split('\n')
        sections = []
        current_section = None
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect section header
            section_info = self._detect_section_header(line, lines, line_num)
            
            if section_info and section_info['confidence'] > 0.6:
                # Close previous section if exists
                if current_section:
                    current_section.end_line = line_num - 1
                    current_section.content = lines[current_section.start_line:current_section.end_line + 1]
                    sections.append(current_section)
                
                # Start new section
                current_section = Section(
                    section_type=section_info['type'],
                    title=line,
                    start_line=line_num,
                    end_line=line_num,
                    content=[],
                    confidence=section_info['confidence'],
                    metadata=section_info['metadata']
                )
        
        # Close last section
        if current_section:
            current_section.end_line = len(lines) - 1
            current_section.content = lines[current_section.start_line:current_section.end_line + 1]
            sections.append(current_section)
        
        # Post-process sections
        sections = self._post_process_sections(sections, lines)
        
        logger.info(f"Detected {len(sections)} sections")
        return sections
    
    def _detect_section_header(self, line: str, all_lines: List[str], line_num: int) -> Optional[Dict]:
        """Detect if a line is a section header"""
        best_match = None
        best_score = 0.0
        
        for section_type, patterns in self.section_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                weight = pattern_info['weight']
                
                if re.search(pattern, line, re.IGNORECASE):
                    # Calculate confidence based on multiple factors
                    confidence = self._calculate_confidence(
                        line, all_lines, line_num, section_type, weight
                    )
                    
                    if confidence > best_score:
                        best_score = confidence
                        best_match = {
                            'type': section_type,
                            'confidence': confidence,
                            'metadata': {
                                'pattern_matched': pattern,
                                'weight': weight,
                                'layout_features': self._extract_layout_features(line)
                            }
                        }
        
        return best_match
    
    def _calculate_confidence(self, line: str, all_lines: List[str], line_num: int, 
                           section_type: SectionType, weight: float) -> float:
        """Calculate confidence score for section detection"""
        confidence = weight
        
        # Layout-based scoring
        layout_score = self._calculate_layout_score(line)
        confidence *= (0.7 + 0.3 * layout_score)
        
        # Contextual scoring
        context_score = self._calculate_context_score(line, all_lines, line_num, section_type)
        confidence *= (0.8 + 0.2 * context_score)
        
        # Position-based scoring
        position_score = self._calculate_position_score(line_num, len(all_lines), section_type)
        confidence *= (0.9 + 0.1 * position_score)
        
        return min(confidence, 1.0)
    
    def _calculate_layout_score(self, line: str) -> float:
        """Calculate layout-based confidence score"""
        score = 0.0
        
        # Capitalization patterns
        if re.match(self.layout_indicators['capitalization_patterns']['all_caps'], line):
            score += 0.3
        elif re.match(self.layout_indicators['capitalization_patterns']['title_case'], line):
            score += 0.2
        
        # Formatting patterns
        if re.match(self.layout_indicators['formatting_patterns']['colon_separated'], line):
            score += 0.2
        elif re.match(self.layout_indicators['formatting_patterns']['hash_separated'], line):
            score += 0.15
        
        # Length patterns (section headers are typically short)
        if len(line.split()) <= 4:
            score += 0.1
        elif len(line.split()) <= 6:
            score += 0.05
        
        return min(score, 1.0)
    
    def _calculate_context_score(self, line: str, all_lines: List[str], line_num: int, 
                                section_type: SectionType) -> float:
        """Calculate contextual confidence score"""
        if section_type not in self.contextual_patterns:
            return 0.5
        
        keywords = self.contextual_patterns[section_type]
        
        # Check surrounding lines for contextual keywords
        context_window = 3
        start = max(0, line_num - context_window)
        end = min(len(all_lines), line_num + context_window + 1)
        
        keyword_matches = 0
        total_words = 0
        
        for i in range(start, end):
            if i == line_num:
                continue
            
            words = all_lines[i].lower().split()
            total_words += len(words)
            
            for word in words:
                if any(keyword in word for keyword in keywords):
                    keyword_matches += 1
        
        if total_words > 0:
            return min(keyword_matches / total_words * 10, 1.0)
        
        return 0.5
    
    def _calculate_position_score(self, line_num: int, total_lines: int, 
                                section_type: SectionType) -> float:
        """Calculate position-based confidence score"""
        position_ratio = line_num / total_lines
        
        # Typical position ranges for different sections
        position_ranges = {
            SectionType.CONTACT: (0.0, 0.1),
            SectionType.SUMMARY: (0.05, 0.2),
            SectionType.EXPERIENCE: (0.1, 0.5),
            SectionType.EDUCATION: (0.3, 0.7),
            SectionType.SKILLS: (0.4, 0.8),
            SectionType.PROJECTS: (0.5, 0.8),
            SectionType.CERTIFICATIONS: (0.6, 0.9),
            SectionType.LANGUAGES: (0.7, 0.9),
            SectionType.INTERESTS: (0.8, 1.0),
            SectionType.REFERENCES: (0.9, 1.0)
        }
        
        if section_type in position_ranges:
            min_pos, max_pos = position_ranges[section_type]
            if min_pos <= position_ratio <= max_pos:
                return 1.0
            else:
                # Calculate distance from expected range
                if position_ratio < min_pos:
                    distance = min_pos - position_ratio
                else:
                    distance = position_ratio - max_pos
                
                return max(0.0, 1.0 - distance)
        
        return 0.5
    
    def _extract_layout_features(self, line: str) -> Dict[str, Any]:
        """Extract layout features from line"""
        features = {
            'capitalization': 'unknown',
            'formatting': 'none',
            'length': len(line),
            'word_count': len(line.split()),
            'has_colon': ':' in line,
            'has_hash': line.startswith('#'),
            'has_underscore': line.endswith('_'),
            'is_all_caps': line.isupper(),
            'is_title_case': line.istitle()
        }
        
        # Determine capitalization pattern
        if features['is_all_caps']:
            features['capitalization'] = 'all_caps'
        elif features['is_title_case']:
            features['capitalization'] = 'title_case'
        elif line.islower():
            features['capitalization'] = 'all_lower'
        else:
            features['capitalization'] = 'mixed_case'
        
        # Determine formatting pattern
        if features['has_colon']:
            features['formatting'] = 'colon_separated'
        elif features['has_hash']:
            features['formatting'] = 'hash_separated'
        elif features['has_underscore']:
            features['formatting'] = 'underline_separated'
        elif line.endswith('-'):
            features['formatting'] = 'dash_separated'
        
        return features
    
    def _post_process_sections(self, sections: List[Section], all_lines: List[str]) -> List[Section]:
        """Post-process detected sections"""
        # Sort sections by start line
        sections.sort(key=lambda x: x.start_line)
        
        # Merge adjacent sections of same type
        merged_sections = []
        for section in sections:
            if merged_sections and merged_sections[-1].section_type == section.section_type:
                # Merge with previous section
                prev_section = merged_sections[-1]
                prev_section.end_line = section.end_line
                prev_section.content = all_lines[prev_section.start_line:prev_section.end_line + 1]
                prev_section.confidence = (prev_section.confidence + section.confidence) / 2
            else:
                merged_sections.append(section)
        
        # Validate section hierarchy
        validated_sections = self._validate_section_hierarchy(merged_sections)
        
        return validated_sections
    
    def _validate_section_hierarchy(self, sections: List[Section]) -> List[Section]:
        """Validate section ordering and reorder if necessary"""
        if len(sections) <= 1:
            return sections
        
        # Calculate hierarchy score for current ordering
        current_score = self._calculate_hierarchy_score(sections)
        
        # Try to improve ordering
        improved_sections = sections.copy()
        improved = True
        
        while improved:
            improved = False
            for i in range(len(improved_sections) - 1):
                for j in range(i + 1, len(improved_sections)):
                    # Try swapping sections
                    test_sections = improved_sections.copy()
                    test_sections[i], test_sections[j] = test_sections[j], test_sections[i]
                    
                    test_score = self._calculate_hierarchy_score(test_sections)
                    
                    if test_score > current_score:
                        improved_sections = test_sections
                        current_score = test_score
                        improved = True
                        break
                
                if improved:
                    break
        
        return improved_sections
    
    def _calculate_hierarchy_score(self, sections: List[Section]) -> float:
        """Calculate hierarchy compliance score"""
        score = 0.0
        total_comparisons = 0
        
        for i, section1 in enumerate(sections):
            for j, section2 in enumerate(sections):
                if i < j:
                    # Check if ordering follows hierarchy
                    type1_index = self.section_hierarchy.index(section1.section_type) if section1.section_type in self.section_hierarchy else len(self.section_hierarchy)
                    type2_index = self.section_hierarchy.index(section2.section_type) if section2.section_type in self.section_hierarchy else len(self.section_hierarchy)
                    
                    if type1_index <= type2_index:
                        score += 1.0
                    else:
                        score += 0.5  # Partial credit for close ordering
                    
                    total_comparisons += 1
        
        return score / total_comparisons if total_comparisons > 0 else 0.0
    
    def get_section_statistics(self, sections: List[Section]) -> Dict[str, Any]:
        """Get statistics about detected sections"""
        stats = {
            'total_sections': len(sections),
            'section_types': {},
            'average_confidence': 0.0,
            'content_distribution': {},
            'layout_features': {
                'all_caps': 0,
                'title_case': 0,
                'colon_separated': 0,
                'hash_separated': 0
            }
        }
        
        total_confidence = 0.0
        total_content_length = 0
        
        for section in sections:
            # Count section types
            section_type = section.section_type.value
            stats['section_types'][section_type] = stats['section_types'].get(section_type, 0) + 1
            
            # Accumulate confidence
            total_confidence += section.confidence
            
            # Content distribution
            content_length = len(' '.join(section.content))
            stats['content_distribution'][section_type] = stats['content_distribution'].get(section_type, 0) + content_length
            total_content_length += content_length
            
            # Layout features
            features = section.metadata.get('layout_features', {})
            if features.get('is_all_caps'):
                stats['layout_features']['all_caps'] += 1
            if features.get('is_title_case'):
                stats['layout_features']['title_case'] += 1
            if features.get('formatting') == 'colon_separated':
                stats['layout_features']['colon_separated'] += 1
            if features.get('formatting') == 'hash_separated':
                stats['layout_features']['hash_separated'] += 1
        
        stats['average_confidence'] = total_confidence / len(sections) if sections else 0.0
        stats['average_content_length'] = total_content_length / len(sections) if sections else 0.0
        
        return stats
