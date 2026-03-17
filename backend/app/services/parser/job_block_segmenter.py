"""
Job Block Segmenter for Resume Parsing
Intelligent segmentation of job experience blocks from resume text
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class JobBlockType(Enum):
    """Enumeration of job block types"""
    COMPANY_HEADER = "company_header"
    ROLE_HEADER = "role_header"
    DURATION = "duration"
    LOCATION = "location"
    DESCRIPTION = "description"
    BULLET_POINTS = "bullet_points"
    ACHIEVEMENTS = "achievements"
    RESPONSIBILITIES = "responsibilities"
    UNKNOWN = "unknown"

@dataclass
class JobBlock:
    """Data class representing a job block"""
    block_type: JobBlockType
    content: str
    start_line: int
    end_line: int
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class JobExperience:
    """Data class representing a complete job experience"""
    company: str
    title: str
    duration: str
    location: str
    description: str
    bullet_points: List[str]
    start_line: int
    end_line: int
    confidence: float
    metadata: Dict[str, Any]

class JobBlockSegmenter:
    """
    Intelligent job block segmenter using pattern recognition,
    machine learning, and contextual analysis
    """
    
    def __init__(self):
        """Initialize the job block segmenter"""
        self.block_patterns = self._build_block_patterns()
        self.transition_patterns = self._build_transition_patterns()
        self.content_indicators = self._build_content_indicators()
        self.formatting_patterns = self._build_formatting_patterns()
        
        logger.info("Job Block Segmenter initialized")
    
    def _build_block_patterns(self) -> Dict[JobBlockType, List[Dict]]:
        """Build comprehensive block patterns"""
        return {
            JobBlockType.COMPANY_HEADER: [
                {'pattern': r'^\s*(?:Company|Employer|Organization):?\s*(.+)$', 'weight': 1.0},
                {'pattern': r'^\s*(.+)\s*(?:Inc|Corp|LLC|Ltd|Co|Company|Corporation)\s*$', 'weight': 0.9},
                {'pattern': r'^\s*[A-Z][a-zA-Z\s&\-]+(?:\s+(?:Inc|Corp|LLC|Ltd|Co))?\s*$', 'weight': 0.8},
                {'pattern': r'^\s*[A-Z][a-zA-Z\s&\-]{3,}\s*$', 'weight': 0.7},
                {'pattern': r'^\s*Client:\s*(.+)$', 'weight': 0.9},
                {'pattern': r'^\s*(.+\s+(?:Technologies|Solutions|Systems|Services|Consulting))\s*$', 'weight': 0.8}
            ],
            JobBlockType.ROLE_HEADER: [
                {'pattern': r'^\s*(?:Role|Position|Title):?\s*(.+)$', 'weight': 1.0},
                {'pattern': r'^\s*(?:Senior|Junior|Lead|Principal|Staff|Chief|Executive|VP|Director|Manager)\s+(.+\s+(?:Engineer|Developer|Analyst|Manager|Specialist|Consultant|Architect|Designer))\s*$', 'weight': 0.9},
                {'pattern': r'^\s*(.+\s+(?:Engineer|Developer|Analyst|Manager|Specialist|Consultant|Architect|Designer))\s*$', 'weight': 0.8},
                {'pattern': r'^\s*(?:Software|Data|Product|Project|Business|Technical)\s+(.+\s+(?:Engineer|Manager|Analyst|Specialist))\s*$', 'weight': 0.7},
                {'pattern': r'^\s*[A-Z][a-zA-Z\s]{3,}\s+(?:Engineer|Developer|Analyst|Manager|Specialist|Consultant)\s*$', 'weight': 0.6}
            ],
            JobBlockType.DURATION: [
                {'pattern': r'^\s*(?:Duration|Period|Employment|Tenure):?\s*(.+)$', 'weight': 1.0},
                {'pattern': r'^\s*(\d{1,2}/\d{1,2}/\d{4}\s*[-–—]\s*\d{1,2}/\d{1,2}/\d{4})\s*$', 'weight': 0.9},
                {'pattern': r'^\s*(\d{4}\s*[-–—]\s*\d{4})\s*$', 'weight': 0.9},
                {'pattern': r'^\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\s*$', 'weight': 0.8},
                {'pattern': r'^\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–—]\s*Present)\s*$', 'weight': 0.8},
                {'pattern': r'^\s*(\d{1,2}/\d{1,2}/\d{4}\s*[-–—]\s*Present)\s*$', 'weight': 0.7},
                {'pattern': r'^\s*(\d{4}\s*[-–—]\s*Present)\s*$', 'weight': 0.7},
                {'pattern': r'^\s*(\d{4}\s*[-–—]\s*\d{4}\s*\((.+)\))\s*$', 'weight': 0.8}
            ],
            JobBlockType.LOCATION: [
                {'pattern': r'^\s*(?:Location|City|State|Country):?\s*(.+)$', 'weight': 1.0},
                {'pattern': r'^\s*([^,]+,\s*[A-Z]{2,3})\s*$', 'weight': 0.9},
                {'pattern': r'^\s*([^,]+,\s*[A-Z]{2,3}\s*\([^)]+\))\s*$', 'weight': 0.8},
                {'pattern': r'^\s*(?:Remote|On-site|Hybrid)\s*$', 'weight': 0.7},
                {'pattern': r'^\s*([^,]+,\s*[A-Za-z\s]+)\s*$', 'weight': 0.6},
                {'pattern': r'^\s*\(([^)]+)\)\s*$', 'weight': 0.5}
            ],
            JobBlockType.DESCRIPTION: [
                {'pattern': r'^\s*(?:Description|Overview|Summary|About):?\s*(.+)$', 'weight': 1.0},
                {'pattern': r'^\s*[A-Z][a-z].{50,}\s*$', 'weight': 0.7},
                {'pattern': r'^\s*[A-Z][a-z].{30,}\s*$', 'weight': 0.6},
                {'pattern': r'^\s*[^•\-\*\d].{20,}\s*$', 'weight': 0.5}
            ],
            JobBlockType.BULLET_POINTS: [
                {'pattern': r'^\s*[•\-\*]\s*(.+)$', 'weight': 1.0},
                {'pattern': r'^\s*\d+\.\s*(.+)$', 'weight': 0.9},
                {'pattern': r'^\s*\d+\)\s*(.+)$', 'weight': 0.8},
                {'pattern': r'^\s*[a-zA-Z]\.\s*(.+)$', 'weight': 0.7},
                {'pattern': r'^\s*[-]\s*(.+)$', 'weight': 0.6}
            ],
            JobBlockType.RESPONSIBILITIES: [
                {'pattern': r'^\s*(?:Responsibilities|Duties|Tasks):?\s*(.+)$', 'weight': 1.0},
                {'pattern': r'^\s*(?:Responsible for|Handled|Managed|Developed|Created|Implemented|Designed|Built)\s+(.+)$', 'weight': 0.8},
                {'pattern': r'^\s*(?:Developed|Designed|Implemented|Created|Built|Managed|Led|Coordinated)\s+(.+)$', 'weight': 0.7}
            ],
            JobBlockType.ACHIEVEMENTS: [
                {'pattern': r'^\s*(?:Achievements|Accomplishments|Results|Impact):?\s*(.+)$', 'weight': 1.0},
                {'pattern': r'^\s*(?:Achieved|Accomplished|Improved|Increased|Decreased|Reduced|Enhanced|Optimized)\s+(.+)$', 'weight': 0.8},
                {'pattern': r'^\s*(?:Increased|Decreased|Reduced|Enhanced|Optimized|Improved|Boosted)\s+(.+)$', 'weight': 0.7}
            ]
        }
    
    def _build_transition_patterns(self) -> List[Dict]:
        """Build patterns for detecting job transitions"""
        return [
            {'pattern': r'^\s*(?:Company|Employer|Organization):?\s*', 'weight': 1.0},
            {'pattern': r'^\s*[A-Z][a-zA-Z\s&\-]+\s*(?:Inc|Corp|LLC|Ltd|Co)\s*$', 'weight': 0.9},
            {'pattern': r'^\s*Client:\s*', 'weight': 0.8},
            {'pattern': r'^\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–—]', 'weight': 0.7},
            {'pattern': r'^\s*\d{4}\s*[-–—]', 'weight': 0.6},
            {'pattern': r'^\s*(?:Senior|Junior|Lead|Principal|Staff|Chief|Executive|VP|Director|Manager)\s+', 'weight': 0.5}
        ]
    
    def _build_content_indicators(self) -> Dict[JobBlockType, List[str]]:
        """Build content indicators for block validation"""
        return {
            JobBlockType.COMPANY_HEADER: [
                'inc', 'corp', 'llc', 'ltd', 'co', 'company', 'corporation',
                'technologies', 'solutions', 'systems', 'services', 'consulting',
                'software', 'group', 'holdings', 'international', 'global'
            ],
            JobBlockType.ROLE_HEADER: [
                'engineer', 'developer', 'analyst', 'manager', 'specialist', 'consultant',
                'architect', 'designer', 'director', 'lead', 'senior', 'junior',
                'principal', 'staff', 'chief', 'executive', 'vp', 'coordinator'
            ],
            JobBlockType.DURATION: [
                'present', 'current', 'ongoing', 'month', 'year', 'date',
                'duration', 'period', 'tenure', 'employment'
            ],
            JobBlockType.LOCATION: [
                'street', 'avenue', 'road', 'drive', 'suite', 'floor', 'building',
                'remote', 'on-site', 'hybrid', 'office', 'campus', 'location'
            ],
            JobBlockType.DESCRIPTION: [
                'responsible', 'managed', 'developed', 'created', 'implemented',
                'designed', 'built', 'led', 'coordinated', 'oversaw', 'maintained'
            ],
            JobBlockType.BULLET_POINTS: [
                'developed', 'implemented', 'created', 'designed', 'built', 'managed',
                'led', 'coordinated', 'improved', 'enhanced', 'optimized', 'reduced'
            ],
            JobBlockType.RESPONSIBILITIES: [
                'responsible', 'handled', 'managed', 'oversaw', 'coordinated',
                'developed', 'implemented', 'maintained', 'supported', 'assisted'
            ],
            JobBlockType.ACHIEVEMENTS: [
                'achieved', 'accomplished', 'improved', 'increased', 'decreased',
                'reduced', 'enhanced', 'optimized', 'boosted', 'grew', 'expanded'
            ]
        }
    
    def _build_formatting_patterns(self) -> Dict[str, str]:
        """Build formatting patterns for block detection"""
        return {
            'bullet_start': r'^\s*[•\-\*\d]',
            'colon_separated': r'^\s*[^:]+:\s*',
            'parentheses_enclosed': r'^\s*\([^)]+\)\s*$',
            'date_range': r'\d{4}[-–—]\d{4}',
            'present_date': r'\d{4}[-–—]Present',
            'month_year': r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
            'company_suffix': r'(?:Inc|Corp|LLC|Ltd|Co|Company|Corporation)$',
            'job_title_keywords': r'(?:Engineer|Developer|Analyst|Manager|Specialist|Consultant|Architect|Designer)$'
        }
    
    def segment_job_blocks(self, text: str) -> List[JobExperience]:
        """
        Segment job experience blocks from resume text
        
        Args:
            text: Resume text to segment
            
        Returns:
            List of job experiences
        """
        lines = text.split('\n')
        blocks = self._detect_blocks(lines)
        job_experiences = self._group_blocks_into_experiences(blocks, lines)
        
        logger.info(f"Segmented {len(job_experiences)} job experiences")
        return job_experiences
    
    def _detect_blocks(self, lines: List[str]) -> List[JobBlock]:
        """Detect individual blocks from lines"""
        blocks = []
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            block_info = self._detect_block_type(line, lines, line_num)
            
            if block_info and block_info['confidence'] > 0.5:
                block = JobBlock(
                    block_type=block_info['type'],
                    content=line,
                    start_line=line_num,
                    end_line=line_num,
                    confidence=block_info['confidence'],
                    metadata=block_info['metadata']
                )
                blocks.append(block)
        
        return blocks
    
    def _detect_block_type(self, line: str, all_lines: List[str], line_num: int) -> Optional[Dict]:
        """Detect the type of block for a line"""
        best_match = None
        best_score = 0.0
        
        for block_type, patterns in self.block_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                weight = pattern_info['weight']
                
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Calculate confidence based on multiple factors
                    confidence = self._calculate_block_confidence(
                        line, all_lines, line_num, block_type, weight, match
                    )
                    
                    if confidence > best_score:
                        best_score = confidence
                        best_match = {
                            'type': block_type,
                            'confidence': confidence,
                            'metadata': {
                                'pattern_matched': pattern,
                                'weight': weight,
                                'match_groups': match.groups() if match.groups() else [],
                                'context_features': self._extract_context_features(line, all_lines, line_num)
                            }
                        }
        
        return best_match
    
    def _calculate_block_confidence(self, line: str, all_lines: List[str], line_num: int,
                                  block_type: JobBlockType, weight: float, match: re.Match) -> float:
        """Calculate confidence score for block detection"""
        confidence = weight
        
        # Pattern match quality
        if match.groups():
            confidence *= 1.1  # Boost for patterns with capture groups
        
        # Contextual validation
        context_score = self._validate_block_context(line, all_lines, line_num, block_type)
        confidence *= (0.8 + 0.2 * context_score)
        
        # Formatting validation
        format_score = self._validate_block_formatting(line, block_type)
        confidence *= (0.9 + 0.1 * format_score)
        
        return min(confidence, 1.0)
    
    def _validate_block_context(self, line: str, all_lines: List[str], line_num: int,
                              block_type: JobBlockType) -> float:
        """Validate block context"""
        if block_type not in self.content_indicators:
            return 0.5
        
        keywords = self.content_indicators[block_type]
        
        # Check surrounding lines for contextual keywords
        context_window = 2
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
    
    def _validate_block_formatting(self, line: str, block_type: JobBlockType) -> float:
        """Validate block formatting"""
        score = 0.0
        
        # Check formatting patterns
        if block_type == JobBlockType.BULLET_POINTS:
            if re.match(self.formatting_patterns['bullet_start'], line):
                score += 0.5
        elif block_type == JobBlockType.DURATION:
            if re.search(self.formatting_patterns['date_range'], line):
                score += 0.3
            elif re.search(self.formatting_patterns['present_date'], line):
                score += 0.3
            elif re.search(self.formatting_patterns['month_year'], line):
                score += 0.2
        elif block_type == JobBlockType.COMPANY_HEADER:
            if re.search(self.formatting_patterns['company_suffix'], line):
                score += 0.3
        elif block_type == JobBlockType.ROLE_HEADER:
            if re.search(self.formatting_patterns['job_title_keywords'], line):
                score += 0.3
        elif block_type == JobBlockType.LOCATION:
            if re.match(self.formatting_patterns['parentheses_enclosed'], line):
                score += 0.2
        
        return min(score, 1.0)
    
    def _extract_context_features(self, line: str, all_lines: List[str], line_num: int) -> Dict[str, Any]:
        """Extract context features"""
        features = {
            'line_position': line_num / len(all_lines),
            'line_length': len(line),
            'word_count': len(line.split()),
            'has_colon': ':' in line,
            'has_parentheses': '(' in line and ')' in line,
            'has_date': bool(re.search(r'\d{4}', line)),
            'has_company_suffix': bool(re.search(r'(?:Inc|Corp|LLC|Ltd|Co)', line, re.IGNORECASE)),
            'has_job_title_keywords': bool(re.search(r'(?:Engineer|Developer|Analyst|Manager)', line, re.IGNORECASE)),
            'is_bullet': bool(re.match(r'^\s*[•\-\*\d]', line)),
            'is_all_caps': line.isupper(),
            'is_title_case': line.istitle()
        }
        
        return features
    
    def _group_blocks_into_experiences(self, blocks: List[JobBlock], all_lines: List[str]) -> List[JobExperience]:
        """Group blocks into complete job experiences"""
        if not blocks:
            return []
        
        # Sort blocks by line number
        blocks.sort(key=lambda x: x.start_line)
        
        # Detect job transitions
        transitions = self._detect_job_transitions(blocks)
        
        # Group blocks between transitions
        experiences = []
        start_idx = 0
        
        for i, transition_idx in enumerate(transitions + [len(blocks)]):
            if i > 0:
                start_idx = transitions[i-1] + 1
            
            if start_idx < transition_idx:
                experience_blocks = blocks[start_idx:transition_idx]
                experience = self._create_job_experience(experience_blocks, all_lines)
                if experience:
                    experiences.append(experience)
        
        return experiences
    
    def _detect_job_transitions(self, blocks: List[JobBlock]) -> List[int]:
        """Detect job transition points"""
        transitions = []
        
        for i, block in enumerate(blocks):
            # Check if this block indicates a new job
            if self._is_job_transition(block, blocks, i):
                transitions.append(i)
        
        return transitions
    
    def _is_job_transition(self, block: JobBlock, all_blocks: List[JobBlock], index: int) -> bool:
        """Determine if a block indicates a job transition"""
        # Company headers are strong indicators
        if block.block_type == JobBlockType.COMPANY_HEADER:
            return True
        
        # Check transition patterns
        for pattern_info in self.transition_patterns:
            pattern = pattern_info['pattern']
            weight = pattern_info['weight']
            
            if re.search(pattern, block.content, re.IGNORECASE):
                return weight >= 0.7
        
        # Check context
        if index > 0:
            prev_block = all_blocks[index-1]
            # If previous block was a duration and this is a company, it's likely a transition
            if (prev_block.block_type == JobBlockType.DURATION and 
                block.block_type == JobBlockType.COMPANY_HEADER):
                return True
        
        return False
    
    def _create_job_experience(self, blocks: List[JobBlock], all_lines: List[str]) -> Optional[JobExperience]:
        """Create a job experience from blocks"""
        if not blocks:
            return None
        
        # Extract information from blocks
        company = ""
        title = ""
        duration = ""
        location = ""
        description = ""
        bullet_points = []
        
        for block in blocks:
            if block.block_type == JobBlockType.COMPANY_HEADER:
                company = self._extract_company_from_block(block)
            elif block.block_type == JobBlockType.ROLE_HEADER:
                title = self._extract_title_from_block(block)
            elif block.block_type == JobBlockType.DURATION:
                duration = self._extract_duration_from_block(block)
            elif block.block_type == JobBlockType.LOCATION:
                location = self._extract_location_from_block(block)
            elif block.block_type == JobBlockType.DESCRIPTION:
                description = block.content
            elif block.block_type == JobBlockType.BULLET_POINTS:
                bullet_points.append(block.content)
        
        # Calculate overall confidence
        confidences = [block.confidence for block in blocks]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Get line range
        start_line = blocks[0].start_line
        end_line = blocks[-1].end_line
        
        # Create metadata
        metadata = {
            'block_count': len(blocks),
            'block_types': [block.block_type.value for block in blocks],
            'extraction_method': 'block_segmentation'
        }
        
        return JobExperience(
            company=company,
            title=title,
            duration=duration,
            location=location,
            description=description,
            bullet_points=bullet_points,
            start_line=start_line,
            end_line=end_line,
            confidence=overall_confidence,
            metadata=metadata
        )
    
    def _extract_company_from_block(self, block: JobBlock) -> str:
        """Extract company name from block"""
        if block.metadata.get('match_groups'):
            return block.metadata['match_groups'][0].strip()
        
        # Fallback to content
        return block.content.strip()
    
    def _extract_title_from_block(self, block: JobBlock) -> str:
        """Extract job title from block"""
        if block.metadata.get('match_groups'):
            return block.metadata['match_groups'][0].strip()
        
        # Fallback to content
        return block.content.strip()
    
    def _extract_duration_from_block(self, block: JobBlock) -> str:
        """Extract duration from block"""
        if block.metadata.get('match_groups'):
            return block.metadata['match_groups'][0].strip()
        
        # Fallback to content
        return block.content.strip()
    
    def _extract_location_from_block(self, block: JobBlock) -> str:
        """Extract location from block"""
        if block.metadata.get('match_groups'):
            return block.metadata['match_groups'][0].strip()
        
        # Fallback to content
        return block.content.strip()
    
    def get_segmentation_statistics(self, experiences: List[JobExperience]) -> Dict[str, Any]:
        """Get statistics about segmentation results"""
        stats = {
            'total_experiences': len(experiences),
            'average_confidence': 0.0,
            'block_distribution': {},
            'content_analysis': {
                'companies_with_locations': 0,
                'experiences_with_bullets': 0,
                'average_bullets_per_experience': 0.0,
                'average_description_length': 0.0
            }
        }
        
        if not experiences:
            return stats
        
        total_confidence = 0.0
        total_bullets = 0
        total_description_length = 0
        
        for exp in experiences:
            total_confidence += exp.confidence
            total_bullets += len(exp.bullet_points)
            total_description_length += len(exp.description)
            
            if exp.location:
                stats['content_analysis']['companies_with_locations'] += 1
            
            if exp.bullet_points:
                stats['content_analysis']['experiences_with_bullets'] += 1
        
        stats['average_confidence'] = total_confidence / len(experiences)
        stats['content_analysis']['average_bullets_per_experience'] = total_bullets / len(experiences)
        stats['content_analysis']['average_description_length'] = total_description_length / len(experiences)
        
        return stats
