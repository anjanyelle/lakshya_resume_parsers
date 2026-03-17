"""
Enhanced Parser Integration Service
Integrates all enhanced normalization components for improved resume parsing
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .utils.dataset_loader import DatasetLoader
from .enhanced_normalization_service import EnhancedNormalizationService
from .company_matcher import CompanyMatcher
from .job_title_normalizer import JobTitleNormalizer
from .skills_validator import SkillsValidator
from .education_normalizer import EducationNormalizer
from .layout_section_detector import LayoutSectionDetector
from .job_block_segmenter import JobBlockSegmenter
from .ner_extractor import NERExtractor

# Import ML models for advanced parsing
try:
    from backend.models import ModelManager
    from backend.models.lightweight_model_manager import LightweightModelManager
    ML_MODELS_AVAILABLE = True
except ImportError:
    ML_MODELS_AVAILABLE = False
    ModelManager = None
    LightweightModelManager = None

logger = logging.getLogger(__name__)

@dataclass
class ParsedExperience:
    """Data class for parsed work experience"""
    company: str
    company_confidence: float
    title: str
    title_confidence: float
    seniority: str
    category: str
    location: str
    location_confidence: float
    start_date: Optional[str]
    end_date: Optional[str]
    description: str
    duration_months: Optional[int]

@dataclass
class ParsedEducation:
    """Data class for parsed education"""
    institution: str
    institution_confidence: float
    degree: str
    degree_level: str
    degree_confidence: float
    field_of_study: str
    start_date: Optional[str]
    end_date: Optional[str]
    gpa: Optional[str]
    honors: List[str]

@dataclass
class ParsedSkills:
    """Data class for parsed skills"""
    technical_skills: List[Tuple[str, float]]
    soft_skills: List[Tuple[str, float]]
    certifications: List[Tuple[str, float]]
    skill_categories: Dict[str, List[Tuple[str, float]]]
    skill_combinations: List[Tuple[str, float, List[str]]]
    inferred_industry: Optional[str]
    industry_confidence: float

@dataclass
class EnhancedParseResult:
    """Enhanced parse result with confidence scores and metadata"""
    experiences: List[ParsedExperience]
    education: List[ParsedEducation]
    skills: ParsedSkills
    summary: Dict[str, Any]
    confidence_scores: Dict[str, float]
    processing_time: float
    metadata: Dict[str, Any]

class EnhancedParserIntegration:
    """
    Enhanced parser integration service that combines all normalization components
    for comprehensive resume parsing with confidence scoring
    """
    
    def __init__(self, cache_ttl_hours: int = 24, use_fuzzy_matching: bool = True):
        """
        Initialize enhanced parser integration
        
        Args:
            cache_ttl_hours: Cache time-to-live in hours
            use_fuzzy_matching: Whether to use fuzzy matching
        """
        self.use_fuzzy_matching = use_fuzzy_matching
        self.start_time = datetime.now()
        
        # Initialize dataset loader
        self.dataset_loader = DatasetLoader(cache_ttl_hours=cache_ttl_hours)
        
        # Load datasets
        self._load_datasets()
        
        # Initialize normalization components
        self.enhanced_normalizer = EnhancedNormalizationService()
        self.company_matcher = CompanyMatcher(self.enhanced_normalizer.companies_data)
        self.job_title_normalizer = JobTitleNormalizer(self.enhanced_normalizer.job_titles_data)
        self.skills_validator = SkillsValidator(self.enhanced_normalizer.skills_data)
        self.education_normalizer = EducationNormalizer(self.enhanced_normalizer.education_data)
        
        # Initialize new parsing components
        self.layout_detector = LayoutSectionDetector()
        self.job_segmenter = JobBlockSegmenter()
        self.ner_extractor = NERExtractor()
        
        # Initialize ML models if available
        self.model_manager = None
        self.lightweight_manager = None
        if ML_MODELS_AVAILABLE:
            try:
                # Try full model manager first
                self.model_manager = ModelManager()
                logger.info("Full ModelManager available - will load on first use")
                
                # Also initialize lightweight as backup
                self.lightweight_manager = LightweightModelManager()
                logger.info("LightweightModelManager available as backup")
            except Exception as e:
                logger.warning(f"Failed to initialize ModelManager: {e}")
                self.model_manager = None
                
                # Try lightweight as fallback
                try:
                    self.lightweight_manager = LightweightModelManager()
                    logger.info("Using LightweightModelManager as primary")
                except Exception as e2:
                    logger.error(f"Failed to initialize LightweightModelManager: {e2}")
                    self.lightweight_manager = None
        
        # Initialize parsing statistics
        self.stats = {
            'total_parsed': 0,
            'successful_parses': 0,
            'average_confidence': 0.0,
            'component_performance': {
                'company_matching': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'title_normalization': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'skill_validation': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'education_normalization': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'layout_detection': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'job_segmentation': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'ner_extraction': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'layoutlm_ml': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'bert_ner_ml': {'success_rate': 0.0, 'avg_confidence': 0.0},
                'spacy_ml': {'success_rate': 0.0, 'avg_confidence': 0.0}
            }
        }
        
        logger.info("Enhanced Parser Integration initialized successfully")
    
    def _load_datasets(self):
        """Load all required datasets"""
        try:
            self.companies_data = self.dataset_loader.load_dataset('companies')
            self.job_titles_data = self.dataset_loader.load_dataset('job_titles')
            self.skills_data = self.dataset_loader.load_dataset('skills')
            self.education_data = self.dataset_loader.load_dataset('education')
            self.locations_data = self.dataset_loader.load_dataset('locations')
            
            logger.info(f"Loaded datasets: {len(self.companies_data)} companies, "
                       f"{len(self.job_titles_data)} job titles, "
                       f"{len(self.skills_data)} skills, "
                       f"{len(self.education_data)} education institutions, "
                       f"{len(self.locations_data)} locations")
            
        except Exception as e:
            logger.error(f"Failed to load datasets: {e}")
            raise
    
    def parse_resume_enhanced(self, resume_text: str) -> EnhancedParseResult:
        """
        Parse resume with enhanced normalization and confidence scoring
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            EnhancedParseResult with comprehensive parsing results
        """
        start_time = datetime.now()
        
        try:
            # Use ML models if available, otherwise fallback to rule-based
            if self.model_manager or self.lightweight_manager:
                # Try full model manager first
                if self.model_manager:
                    # Load ML models if not already loaded
                    if not any(status.is_loaded for status in self.model_manager.get_model_status().values()):
                        self.model_manager.load_all_models()
                    
                    # Parse with full ML models
                    ml_result = self.model_manager.parse_resume_complete(resume_text)
                    
                    # Extract ML results
                    if ml_result.layout_result:
                        sections = self._convert_layout_sections(ml_result.layout_result.sections)
                    else:
                        sections = self.layout_detector.detect_sections(resume_text)
                    
                    entities = ml_result.ner_result.entities if ml_result.ner_result else []
                    spacy_entities = ml_result.spacy_result.entities if ml_result.spacy_result else []
                    
                    # Update ML performance stats
                    self._update_ml_performance_stats(ml_result)
                    
                elif self.lightweight_manager:
                    # Use lightweight models (spaCy + LayoutLM)
                    lightweight_result = self.lightweight_manager.parse_resume_lightweight(resume_text)
                    
                    if lightweight_result.layout_result:
                        sections = self._convert_layout_sections(lightweight_result.layout_result.sections)
                    else:
                        sections = self.layout_detector.detect_sections(resume_text)
                    
                    # Combine entities from spaCy
                    spacy_entities = lightweight_result.spacy_result.entities if lightweight_result.spacy_result else []
                    entities = spacy_entities  # spaCy entities are our primary source
                    
                    logger.info(f"Used lightweight models: {lightweight_result.models_used}")
                
                # Combine entities from both NER models
                all_entities = entities + spacy_entities
                
            else:
                # Fallback to rule-based parsing
                sections = self.layout_detector.detect_sections(resume_text)
                all_entities = self.ner_extractor.extract_entities(resume_text)
            
            # Parse work experience using job segmentation
            experiences = self._parse_experiences(resume_text, sections, all_entities)
            
            # Parse education
            education = self._parse_education(resume_text, sections, all_entities)
            
            # Parse skills using NER results
            skills = self._parse_skills(resume_text, all_entities)
            
            # Generate summary
            summary = self._generate_summary(experiences, education, skills)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(experiences, education, skills)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_statistics(experiences, education, skills, confidence_scores)
            
            # Convert experiences to work_history format
            work_history = self._convert_experiences_to_work_history(experiences)
            
            # Create result
            result = EnhancedParseResult(
                experiences=experiences,
                education=education,
                skills=skills,
                summary=summary,
                confidence_scores=confidence_scores,
                processing_time=processing_time,
                metadata={
                    'dataset_stats': self._get_dataset_stats(),
                    'parser_version': '2.0-enhanced',
                    'parsing_timestamp': datetime.now().isoformat(),
                    'work_history': work_history
                }
            )
            
            self.stats['total_parsed'] += 1
            self.stats['successful_parses'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            self.stats['total_parsed'] += 1
            
            # Return minimal result on error
            return EnhancedParseResult(
                experiences=[],
                education=[],
                skills=ParsedSkills([], [], [], {}, [], None, 0.0),
                summary={'error': str(e)},
                confidence_scores={'overall': 0.0},
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={'error': True}
            )
    
    def _parse_experiences(self, resume_text: str, sections: List = None, entities: List = None) -> List[ParsedExperience]:
        """Parse work experience with enhanced normalization using new components"""
        experiences = []
        
        # Extract experience section content
        experience_section = ""
        if sections and isinstance(sections, dict):
            exp_section = sections.get("experience", {})
            if isinstance(exp_section, dict) and "content" in exp_section:
                experience_section = exp_section["content"]
        
        # Check if this is Client/Role/Location format
        if "Client:" in experience_section and "Role:" in experience_section:
            client_experiences = self._parse_client_role_format(experience_section)
            experiences.extend(client_experiences)
            return experiences
        
        # Check if this is Company | Dates | Location format (like your resume)
        if "|" in experience_section and any(year in experience_section for year in ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]):
            company_experiences = self._parse_company_dates_location_format(experience_section)
            experiences.extend(company_experiences)
            return experiences
        
        # Use job block segmenter for intelligent parsing
        job_experiences = self.job_segmenter.segment_job_blocks(resume_text)
        
        for job_exp in job_experiences:
            try:
                # Parse company name
                normalized_company, company_confidence, company_metadata = self.company_matcher.match_company(
                    job_exp.company, threshold=0.6
                )
                
                # Parse job title
                normalized_title, seniority, category, title_confidence = self.job_title_normalizer.normalize_job_title(
                    job_exp.title, use_fuzzy=self.use_fuzzy_matching
                )
                
                # Parse location
                normalized_location, location_confidence = self.enhanced_normalizer.normalize_location(job_exp.location)
                
                # Parse dates
                start_date, end_date = self._parse_dates(job_exp.duration)
                
                # Calculate duration
                duration_months = self._calculate_duration_months(start_date, end_date)
                
                experience = ParsedExperience(
                    company=normalized_company or job_exp.company,
                    company_confidence=company_confidence,
                    title=normalized_title or job_exp.title,
                    title_confidence=title_confidence,
                    seniority=seniority or 'Unknown',
                    category=category or 'Unknown',
                    location=normalized_location or job_exp.location,
                    location_confidence=location_confidence,
                    start_date=start_date,
                    end_date=end_date,
                    description=job_exp.description,
                    duration_months=duration_months
                )
                
                experiences.append(experience)
                
            except Exception as e:
                logger.warning(f"Error parsing experience section: {e}")
                continue
        
        return experiences
    
    def _parse_client_role_format(self, experience_text: str) -> List[ParsedExperience]:
        """Parse Client/Role/Location formatted experience sections"""
        import re
        from datetime import datetime
        
        experiences = []
        
        # Split by "Client:" markers
        client_sections = experience_text.split("Client:")
        
        for section in client_sections[1:]:  # Skip first empty section
            lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
            
            if len(lines) < 3:
                continue
                
            try:
                # Parse company line (first line)
                company_line = lines[0]
                company = company_line.split('\n')[0].strip()
                
                # Handle company names with nested parentheses like "Cigna Health (Client: Express Scripts)"
                if '(' in company and ')' not in company:
                    # Look for the closing parenthesis in the next few lines
                    full_company = company
                    for i in range(1, min(3, len(lines))):
                        if ')' in lines[i]:
                            full_company += ' ' + lines[i].strip()
                            break
                    company = full_company
                
                # Parse role line (second line) - extract title and dates
                role_line = lines[1]
                role_pattern = r'Role:\s*(.+?)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*-\s*(Current|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}'
                role_match = re.search(role_pattern, role_line)
                
                if not role_match:
                    continue
                    
                title = role_match.group(1).strip()
                date_start = role_match.group(2) + " " + role_match.group(3)
                date_end = role_match.group(4)
                
                if date_end == "Current":
                    end_date = None
                else:
                    end_date = date_end
                    
                # Parse location from company line if present
                location = None
                location_pattern = r'(.+?)\s+([A-Z]{2}|[A-Z][a-z]+(?:\s+[A-Z]{2})?)$'
                location_match = re.search(location_pattern, company)
                if location_match:
                    company = location_match.group(1).strip()
                    location = location_match.group(2).strip()
                
                # Parse description (remaining lines)
                description = '\n'.join(lines[2:])
                
                # Parse dates
                start_date = self._parse_date_string(date_start)
                end_date = self._parse_date_string(end_date) if end_date != "Current" else None
                
                # Calculate duration
                duration_months = self._calculate_duration_months(start_date, end_date)
                
                experience = ParsedExperience(
                    company=company,
                    company_confidence=0.8,
                    title=title,
                    title_confidence=0.8,
                    seniority='Unknown',
                    category='Unknown',
                    location=location,
                    location_confidence=0.7,
                    start_date=start_date,
                    end_date=end_date,
                    description=description,
                    duration_months=duration_months
                )
                
                experiences.append(experience)
                
            except Exception as e:
                logger.warning(f"Error parsing client role format: {e}")
                continue
                
        return experiences
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats"""
        if not date_str:
            return None
            
        try:
            from datetime import datetime
            
            # Try different date formats
            formats = [
                "%Y-%m-%d",  # "2023-01-01"
                "%b %Y",  # "Jan 2023"
                "%B %Y",  # "January 2023"
                "%m/%Y",  # "01/2023"
                "%Y-%m",  # "2023-01"
                "%Y",     # "2023"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
        except Exception:
            pass
            
        return None
    
    def _parse_company_colon_dates_format(self, experience_text: str) -> List[ParsedExperience]:
        """Parse Company: Title Date Range Location format like Sai Bhargav's resume"""
        import re
        from datetime import datetime
        
        experiences = []
        
        # Split by company lines (look for lines with ## pattern)
        lines = experience_text.split('\n')
        current_job = {}
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('PROFESSIONAL EXPERIENCE') or line.startswith('Key Measurable Achievements'):
                i += 1
                continue
            
            # Check if this is a company line (starts with ## and contains : and years)
            if line.startswith('##') and ':' in line and any(year in line for year in ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]):
                # Parse company line: "## Home Depot: Senior Data Engineer March 2023 - Current Location: Atlanta, GA"
                clean_line = line.replace('##', '').strip()
                
                # Extract company, title, dates, location
                company_match = re.match(r'([^:]+):\s*(.+?)\s+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})\s*(\d{4})\s*-\s*(Current|Present|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})\s*(\d{4}|\d{1,2})\s*(.*)', clean_line)
                
                if company_match:
                    company = company_match.group(1).strip()
                    title_and_rest = company_match.group(2).strip()
                    start_month = company_match.group(3)
                    start_year = company_match.group(4)
                    end_month = company_match.group(5) 
                    end_year = company_match.group(6) if company_match.group(6) != 'Current' and company_match.group(6) != 'Present' else None
                    location_part = company_match.group(7).strip()
                    
                    # Extract location
                    location = None
                    if 'Location:' in location_part:
                        location = location_part.replace('Location:', '').strip()
                    
                    # Parse dates
                    start_date = self._parse_date_string(f"{start_month} {start_year}")
                    if end_year:
                        end_date = self._parse_date_string(f"{end_month} {end_year}")
                    else:
                        end_date = None
                    
                    # Get description (next lines until next company or end)
                    description_lines = []
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if next_line.startswith('##') or (next_line and ':' in next_line and any(year in next_line for year in ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"])):
                            break
                        if next_line:
                            description_lines.append(next_line)
                        j += 1
                    
                    description = '\n'.join(description_lines) if description_lines else None
                    
                    experience = ParsedExperience(
                        company=company,
                        company_confidence=0.9,
                        title=title_and_rest,
                        title_confidence=0.9,
                        seniority="Senior",  # Default
                        category="Data Engineering",  # Default
                        location=location or "",
                        location_confidence=0.8,
                        start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
                        end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
                        description=description or "",
                        duration_months=None
                    )
                    experiences.append(experience)
                    i = j - 1  # -1 because will be incremented at end of loop
                else:
                    # Fallback: simpler parsing
                    parts = clean_line.split(':')
                    if len(parts) >= 2:
                        company = parts[0].strip()
                        rest = ':'.join(parts[1:]).strip()
                        
                        # Try to extract dates
                        date_match = re.search(r'(\d{4})\s*-\s*(Current|Present|\d{4})', rest)
                        if date_match:
                            start_year = date_match.group(1)
                            end_year = date_match.group(2)
                            
                            start_date = self._parse_date_string(start_year)
                            end_date = None if end_year in ['Current', 'Present'] else self._parse_date_string(end_year)
                            
                            # Extract location
                            location = None
                            if 'Location:' in rest:
                                location_match = re.search(r'Location:\s*([^:]+)', rest)
                                if location_match:
                                    location = location_match.group(1).strip()
                            
                            # Extract title (before dates)
                            title_part = rest.split(date_match.group(0))[0].strip()
                            
                            # Get description
                            description_lines = []
                            j = i + 1
                            while j < len(lines):
                                next_line = lines[j].strip()
                                if next_line.startswith('##') or (next_line and ':' in next_line and any(year in next_line for year in ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"])):
                                    break
                                if next_line:
                                    description_lines.append(next_line)
                                j += 1
                            
                            description = '\n'.join(description_lines) if description_lines else None
                            
                            experience = ParsedExperience(
                                company=company,
                                company_confidence=0.8,
                                title=title_part,
                                title_confidence=0.8,
                                seniority="Senior",  # Default
                                category="Data Engineering",  # Default
                                location=location or "",
                                location_confidence=0.7,
                                start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
                                end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
                                description=description or "",
                                duration_months=None
                            )
                            experiences.append(experience)
                            i = j - 1
            
            i += 1
        
        return experiences
    
    def _parse_company_dates_location_format(self, experience_text: str) -> List[ParsedExperience]:
        """Parse Company | Dates | Location format like your resume"""
        import re
        from datetime import datetime
        
        experiences = []
        
        # Split by company lines (look for lines with | character)
        lines = experience_text.split('\n')
        current_job = {}
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('PROFESSIONAL EXPERIENCE') or line.startswith('Key Measurable Achievements'):
                i += 1
                continue
            
            # Check if this is a company line (contains | and years)
            if '|' in line and any(year in line for year in ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]):
                # Parse company line: "Cigna Health (Client: Express Scripts)   |   2022 – Present  |  Bloomfield, CT (Remote)"
                parts = [part.strip() for part in line.split('|')]
                
                if len(parts) >= 3:
                    company = parts[0]
                    dates = parts[1]
                    location = parts[2] if len(parts) > 2 else ""
                    
                    # Parse dates
                    start_date = None
                    end_date = None
                    
                    # Handle "2022 – Present" format
                    if '–' in dates or '-' in dates:
                        date_parts = re.split(r'–|-', dates)
                        if len(date_parts) >= 2:
                            start_part = date_parts[0].strip()
                            end_part = date_parts[1].strip()
                            
                            # Parse start date - just use the year
                            if re.match(r'\d{4}', start_part):
                                start_date = self._parse_date_string(start_part + "-01-01")
                            
                            # Parse end date
                            if 'Present' in end_part:
                                end_date = None
                            elif re.match(r'\d{4}', end_part):
                                end_date = self._parse_date_string(end_part + "-12-31")
                    
                    # Get job title from next line
                    job_title = ""
                    description = ""
                    
                    if i + 1 < len(lines):
                        title_line = lines[i + 1].strip()
                        if title_line and not any(char in title_line for char in ['|', '•', 'Key Measurable Achievements']):
                            job_title = title_line
                    
                    # Get description (collect bullet points until next job)
                    description_lines = []
                    j = i + 2
                    while j < len(lines):
                        desc_line = lines[j].strip()
                        if not desc_line:
                            j += 1
                            continue
                        
                        # Stop if we hit the next job
                        if '|' in desc_line and any(year in desc_line for year in ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]):
                            break
                        
                        # Stop if we hit a new section
                        if desc_line.startswith('Key Measurable Achievements') or desc_line.startswith('Environment:'):
                            break
                        
                        # Add bullet points or description lines
                        if desc_line.startswith('•') or desc_line.startswith('-'):
                            description_lines.append(desc_line)
                        elif desc_line and not desc_line.startswith('PROFESSIONAL EXPERIENCE'):
                            description_lines.append(desc_line)
                        
                        j += 1
                    
                    description = '\n'.join(description_lines)
                    
                    # Calculate duration
                    duration_months = self._calculate_duration_months(start_date, end_date)
                    
                    experience = ParsedExperience(
                        company=company,
                        company_confidence=0.9,
                        title=job_title,
                        title_confidence=0.9,
                        seniority='Unknown',
                        category='Unknown',
                        location=location,
                        location_confidence=0.8,
                        start_date=start_date,
                        end_date=end_date,
                        description=description,
                        duration_months=duration_months
                    )
                    
                    experiences.append(experience)
                    i = j - 1  # Skip to where we stopped
            i += 1
        
        return experiences
    
    def _convert_experiences_to_work_history(self, experiences: List[ParsedExperience]) -> List[Dict]:
        """Convert ParsedExperience objects to work_history JSON format"""
        work_history = []
        
        for exp in experiences:
            work_entry = {
                "company_name": exp.company,
                "job_title": exp.title,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "description": exp.description,
                "location": exp.location,
                "confidence": getattr(exp, 'company_confidence', 0.8)
            }
            work_history.append(work_entry)
            
        return work_history
    
    def _parse_education(self, resume_text: str, sections: List = None, entities: List = None) -> List[ParsedEducation]:
        """Parse education with enhanced normalization"""
        education_entries = []
        
        # Extract education sections
        education_sections = self._extract_education_sections(resume_text)
        
        for section in education_sections:
            try:
                # Parse institution name
                institution_name = section.get('institution', '')
                normalized_institution, institution_confidence, institution_metadata = self.education_normalizer.normalize_institution(
                    institution_name, use_fuzzy=self.use_fuzzy_matching
                )
                
                # Parse degree
                degree = section.get('degree', '')
                normalized_degree, degree_level, degree_confidence = self.education_normalizer.normalize_degree(degree)
                
                # Parse field of study
                field_of_study = section.get('field_of_study', '')
                
                # Parse dates
                start_date, end_date = self._parse_dates(section.get('duration', ''))
                
                # Parse GPA and honors
                gpa = self._extract_gpa(section.get('details', ''))
                honors = self._extract_honors(section.get('details', ''))
                
                education = ParsedEducation(
                    institution=normalized_institution or institution_name,
                    institution_confidence=institution_confidence,
                    degree=normalized_degree or degree,
                    degree_level=degree_level,
                    degree_confidence=degree_confidence,
                    field_of_study=field_of_study,
                    start_date=start_date,
                    end_date=end_date,
                    gpa=gpa,
                    honors=honors
                )
                
                education_entries.append(education)
                
            except Exception as e:
                logger.warning(f"Error parsing education section: {e}")
                continue
        
        return education_entries
    
    def _parse_skills(self, resume_text: str, entities: List = None) -> ParsedSkills:
        """Parse skills with enhanced validation and categorization using NER results"""
        # Extract skills using NER if available
        if entities:
            skill_entities = [entity for entity in entities if entity.label == 'SKILL']
            extracted_skills = [entity.text for entity in skill_entities]
        else:
            # Fallback to text extraction
            extracted_skills = self._extract_skills_from_text(resume_text)
        
        # Validate and categorize skills
        validated_skills = []
        technical_skills = []
        soft_skills = []
        certifications = []
        
        for skill in extracted_skills:
            is_valid, skill_data, confidence = self.skills_validator.validate_skill(skill, use_fuzzy=self.use_fuzzy_matching)
            
            if is_valid:
                validated_skills.append((skill, confidence, skill_data))
                
                # Categorize skill
                category = skill_data.get('category', '').lower()
                if category in ['programming', 'web development', 'database', 'devops', 'cloud computing', 'mobile development']:
                    technical_skills.append((skill, confidence))
                elif category in ['soft skill', 'communication', 'leadership', 'management']:
                    soft_skills.append((skill, confidence))
                elif category == 'certification':
                    certifications.append((skill, confidence))
        
        # Get skill categories
        skill_names = [skill for skill, _, _ in validated_skills]
        skill_categories = self.skills_validator.categorize_skills(skill_names)
        
        # Detect skill combinations
        skill_combinations = self.skills_validator.detect_skill_combinations(skill_names)
        
        # Infer industry from skills
        inferred_industry, industry_confidence = self.skills_validator.infer_industry_from_skills(skill_names)
        
        return ParsedSkills(
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            certifications=certifications,
            skill_categories=skill_categories,
            skill_combinations=skill_combinations,
            inferred_industry=inferred_industry,
            industry_confidence=industry_confidence
        )
    
    def _extract_experience_sections(self, text: str) -> List[Dict]:
        """Extract work experience sections from resume text"""
        # Simplified extraction - in real implementation, this would use NLP
        sections = []
        
        # Look for common experience patterns
        lines = text.split('\n')
        current_section = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for company patterns
            if re.search(r'^(Company:|Employer:|Worked at|Current|Previous)', line, re.IGNORECASE):
                if current_section:
                    sections.append(current_section)
                current_section = {'company': line.split(':', 1)[-1].strip()}
            
            # Look for title patterns
            elif re.search(r'^(Title:|Role:|Position:|Job:)', line, re.IGNORECASE):
                current_section['title'] = line.split(':', 1)[-1].strip()
            
            # Look for date patterns
            elif re.search(r'(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', line):
                current_section['duration'] = line
            
            # Look for location patterns
            elif re.search(r'^(Location:|City:|State:)', line, re.IGNORECASE):
                current_section['location'] = line.split(':', 1)[-1].strip()
            
            # Look for description patterns
            elif len(line) > 50:  # Assume longer lines are descriptions
                current_section['description'] = current_section.get('description', '') + ' ' + line
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_education_sections(self, text: str) -> List[Dict]:
        """Extract education sections from resume text"""
        sections = []
        
        # Look for common education patterns
        lines = text.split('\n')
        current_section = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for education patterns
            if re.search(r'^(Education:|University:|College:|School:|Degree:)', line, re.IGNORECASE):
                if current_section:
                    sections.append(current_section)
                current_section = {'institution': line.split(':', 1)[-1].strip()}
            
            # Look for degree patterns
            elif re.search(r'^(Bachelor|Master|PhD|Doctorate|Associate|B\.|M\.|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.)', line):
                current_section['degree'] = line
            
            # Look for field of study
            elif re.search(r'^(Major:|Field:|Specialization:|Concentration:)', line, re.IGNORECASE):
                current_section['field_of_study'] = line.split(':', 1)[-1].strip()
            
            # Look for date patterns
            elif re.search(r'(\d{4}-\d{4}|\d{4}|\d{1,2}/\d{1,2}/\d{4})', line):
                current_section['duration'] = line
            
            # Look for details
            elif re.search(r'(GPA:|Honors:|Dean\'s List|Cum Laude|Magna Cum Laude|Summa Cum Laude)', line, re.IGNORECASE):
                current_section['details'] = current_section.get('details', '') + ' ' + line
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        skills = []
        
        # Common skill section headers
        skill_headers = [
            r'Skills?:',
            r'Technical Skills?:',
            r'Programming Languages?:',
            r'Frameworks?:',
            r'Databases?:',
            r'Certifications?:',
            r'Languages?:',
            r'Tools?:',
            r'Proficiencies?:'
        ]
        
        lines = text.split('\n')
        in_skills_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if we're entering a skills section
            entering_skills_section = False
            for header in skill_headers:
                if re.search(header, line, re.IGNORECASE):
                    in_skills_section = True
                    entering_skills_section = True
                    # Extract skills from this line
                    skills_part = line.split(':', 1)[-1].strip()
                    if skills_part:
                        skills.extend([skill.strip() for skill in skills_part.split(',')])
                    break
            
            # If we're in a skills section, extract skills
            if in_skills_section and not entering_skills_section:
                # Look for skill patterns
                if re.search(r'^\w+(?:\s+\w+)*,?\s*(?:\w+(?:\s+\w+)*)*$', line):
                    # Line contains comma-separated skills
                    line_skills = [skill.strip() for skill in line.split(',') if skill.strip()]
                    skills.extend(line_skills)
                elif re.search(r'^[\w\-\.\s]+$', line) and len(line.split()) <= 3:
                    # Single or short skill
                    skills.append(line)
                elif re.search(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', line):
                    # Properly capitalized skill
                    skills.append(line)
                # End skills section if we hit a major section header
                elif re.search(r'^(Experience|Education|Projects|Publications|References)', line, re.IGNORECASE):
                    in_skills_section = False
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills
    
    def _parse_dates(self, date_string: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse date string into start and end dates"""
        if not date_string:
            return None, None
        
        # Common date patterns
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4})\s*-\s*(\d{4})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*-\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
            r'(\d{1,2}/\d{1,2}/\d{4})\s*-\s*Present',
            r'(\d{4})\s*-\s*Present',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*-\s*Present'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_string, re.IGNORECASE)
            if match:
                start_date = match.group(1)
                end_date = match.group(2) if len(match.groups()) > 1 else 'Present'
                return start_date, end_date
        
        return None, None
    
    def _calculate_duration_months(self, start_date: Optional[str], end_date: Optional[str]) -> Optional[int]:
        """Calculate duration in months from start and end dates"""
        if not start_date:
            return None
        
        # Simplified calculation - in real implementation, use proper date parsing
        try:
            if end_date == 'Present':
                end_date = datetime.now().strftime('%Y-%m')
            
            # Extract years and months (simplified)
            if '-' in start_date:
                start_parts = start_date.split('-')
                start_year = int(start_parts[0])
                start_month = int(start_parts[1]) if len(start_parts) > 1 else 1
            else:
                start_year = int(start_date[:4])
                start_month = 1
            
            if '-' in end_date:
                end_parts = end_date.split('-')
                end_year = int(end_parts[0])
                end_month = int(end_parts[1]) if len(end_parts) > 1 else 1
            else:
                end_year = int(end_date[:4])
                end_month = 12
            
            months = (end_year - start_year) * 12 + (end_month - start_month)
            return max(0, months)
            
        except Exception:
            return None
    
    def _extract_gpa(self, text: str) -> Optional[str]:
        """Extract GPA from text"""
        gpa_patterns = [
            r'GPA:\s*([0-9]\.[0-9]+)',
            r'GPA\s*([0-9]\.[0-9]+)',
            r'([0-9]\.[0-9]+)\s*GPA'
        ]
        
        for pattern in gpa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_honors(self, text: str) -> List[str]:
        """Extract honors from text"""
        honor_patterns = [
            r'(Dean\'s List)',
            r'(President\'s List)',
            r'(Magna Cum Laude)',
            r'(Summa Cum Laude)',
            r'(Cum Laude)',
            r'(Honors)',
            r'(Distinction)',
            r'(High Honors)',
            r'(Highest Honors)'
        ]
        
        honors = []
        for pattern in honor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            honors.extend(matches)
        
        return honors
    
    def _generate_summary(self, experiences: List[ParsedExperience], education: List[ParsedEducation], skills: ParsedSkills) -> Dict:
        """Generate comprehensive summary of parsed resume"""
        summary = {
            'total_experiences': len(experiences),
            'total_education': len(education),
            'total_technical_skills': len(skills.technical_skills),
            'total_soft_skills': len(skills.soft_skills),
            'total_certifications': len(skills.certifications),
            'skill_categories': list(skills.skill_categories.keys()),
            'inferred_industry': skills.inferred_industry,
            'experience_duration_months': sum(exp.duration_months for exp in experiences if exp.duration_months),
            'highest_degree': self._get_highest_degree(education),
            'career_level': self._determine_career_level(experiences),
            'location_distribution': self._analyze_locations(experiences),
            'company_types': self._analyze_company_types(experiences),
            'seniority_distribution': self._analyze_seniority(experiences)
        }
        
        return summary
    
    def _get_highest_degree(self, education: List[ParsedEducation]) -> str:
        """Determine highest degree from education list"""
        if not education:
            return 'None'
        
        degree_hierarchy = {
            'Doctorate': 5,
            'Master': 4,
            'Bachelor': 3,
            'Associate': 2,
            'Certificate': 1,
            'Diploma': 1,
            'Unknown': 0
        }
        
        highest_degree = 'None'
        highest_level = 0
        
        for edu in education:
            level = degree_hierarchy.get(edu.degree_level, 0)
            if level > highest_level:
                highest_level = level
                highest_degree = edu.degree
        
        return highest_degree
    
    def _determine_career_level(self, experiences: List[ParsedExperience]) -> str:
        """Determine career level from experiences"""
        if not experiences:
            return 'Unknown'
        
        seniority_levels = []
        for exp in experiences:
            if exp.seniority == 'Executive':
                seniority_levels.append(5)
            elif exp.seniority == 'Senior':
                seniority_levels.append(4)
            elif exp.seniority == 'Mid-Level':
                seniority_levels.append(3)
            elif exp.seniority == 'Junior':
                seniority_levels.append(2)
            elif exp.seniority == 'Intern':
                seniority_levels.append(1)
            else:
                seniority_levels.append(0)
        
        if not seniority_levels:
            return 'Unknown'
        
        avg_level = sum(seniority_levels) / len(seniority_levels)
        
        if avg_level >= 4.5:
            return 'Executive'
        elif avg_level >= 3.5:
            return 'Senior'
        elif avg_level >= 2.5:
            return 'Mid-Level'
        elif avg_level >= 1.5:
            return 'Junior'
        else:
            return 'Entry-Level'
    
    def _analyze_locations(self, experiences: List[ParsedExperience]) -> Dict:
        """Analyze location distribution"""
        locations = [exp.location for exp in experiences if exp.location]
        location_counts = {}
        
        for location in locations:
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return {
            'unique_locations': len(location_counts),
            'most_common': max(location_counts.items(), key=lambda x: x[1])[0] if location_counts else None,
            'distribution': location_counts
        }
    
    def _analyze_company_types(self, experiences: List[ParsedExperience]) -> Dict:
        """Analyze company types"""
        company_types = {}
        
        for exp in experiences:
            # Simple heuristic to determine company type
            company = exp.company.lower()
            if any(keyword in company for keyword in ['university', 'college', 'school']):
                company_type = 'Education'
            elif any(keyword in company for keyword in ['hospital', 'medical', 'health']):
                company_type = 'Healthcare'
            elif any(keyword in company for keyword in ['government', 'federal', 'state']):
                company_type = 'Government'
            elif any(keyword in company for keyword in ['inc', 'corp', 'llc', 'ltd']):
                company_type = 'Corporate'
            else:
                company_type = 'Unknown'
            
            company_types[company_type] = company_types.get(company_type, 0) + 1
        
        return company_types
    
    def _analyze_seniority(self, experiences: List[ParsedExperience]) -> Dict:
        """Analyze seniority distribution"""
        seniority_counts = {}
        
        for exp in experiences:
            seniority = exp.seniority
            seniority_counts[seniority] = seniority_counts.get(seniority, 0) + 1
        
        return seniority_counts
    
    def _calculate_confidence_scores(self, experiences: List[ParsedExperience], education: List[ParsedEducation], skills: ParsedSkills) -> Dict:
        """Calculate overall confidence scores"""
        scores = {}
        
        # Experience confidence
        if experiences:
            exp_confidences = [exp.company_confidence * exp.title_confidence for exp in experiences]
            scores['experience'] = sum(exp_confidences) / len(exp_confidences)
        else:
            scores['experience'] = 0.0
        
        # Education confidence
        if education:
            edu_confidences = [edu.institution_confidence * edu.degree_confidence for edu in education]
            scores['education'] = sum(edu_confidences) / len(edu_confidences)
        else:
            scores['education'] = 0.0
        
        # Skills confidence
        all_skills = skills.technical_skills + skills.soft_skills + skills.certifications
        if all_skills:
            skill_confidences = [confidence for _, confidence in all_skills]
            scores['skills'] = sum(skill_confidences) / len(skill_confidences)
        else:
            scores['skills'] = 0.0
        
        # Overall confidence
        weights = {'experience': 0.4, 'education': 0.3, 'skills': 0.3}
        scores['overall'] = sum(scores[key] * weight for key, weight in weights.items())
        
        return scores
    
    def _update_statistics(self, experiences: List[ParsedExperience], education: List[ParsedEducation], skills: ParsedSkills, confidence_scores: Dict):
        """Update parsing statistics"""
        # Update component performance
        if experiences:
            avg_exp_confidence = sum(exp.company_confidence * exp.title_confidence for exp in experiences) / len(experiences)
            self.stats['component_performance']['company_matching']['avg_confidence'] = (
                self.stats['component_performance']['company_matching']['avg_confidence'] * 0.9 + avg_exp_confidence * 0.1
            )
        
        if education:
            avg_edu_confidence = sum(edu.institution_confidence * edu.degree_confidence for edu in education) / len(education)
            self.stats['component_performance']['education_normalization']['avg_confidence'] = (
                self.stats['component_performance']['education_normalization']['avg_confidence'] * 0.9 + avg_edu_confidence * 0.1
            )
        
        if skills.technical_skills or skills.soft_skills:
            all_skill_confidences = [conf for _, conf in skills.technical_skills + skills.soft_skills]
            avg_skill_confidence = sum(all_skill_confidences) / len(all_skill_confidences)
            self.stats['component_performance']['skill_validation']['avg_confidence'] = (
                self.stats['component_performance']['skill_validation']['avg_confidence'] * 0.9 + avg_skill_confidence * 0.1
            )
        
        # Update overall average confidence
        overall_conf = confidence_scores.get('overall', 0.0)
        self.stats['average_confidence'] = (
            self.stats['average_confidence'] * 0.9 + overall_conf * 0.1
        )
    
    def _get_dataset_stats(self) -> Dict:
        """Get dataset statistics"""
        return {
            'companies': len(self.companies_data),
            'job_titles': len(self.job_titles_data),
            'skills': len(self.skills_data),
            'education': len(self.education_data),
            'locations': len(self.locations_data)
        }
    
    def _convert_layout_sections(self, layout_sections: List) -> List[Dict]:
        """Convert LayoutLM sections to standard format"""
        sections = []
        for section in layout_sections:
            sections.append({
                'type': section.section_type,
                'text': section.text_content,
                'bbox': section.bbox,
                'confidence': section.confidence,
                'page': section.page_number
            })
        return sections
    
    def _update_ml_performance_stats(self, ml_result):
        """Update ML model performance statistics"""
        if not ml_result:
            return
        
        # Update LayoutLM stats
        if ml_result.layout_result:
            layoutlm_perf = self.stats['component_performance']['layoutlm_ml']
            layoutlm_perf['success_rate'] = 1.0  # Success if we got here
            layoutlm_perf['avg_confidence'] = (
                layoutlm_perf['avg_confidence'] * 0.9 + ml_result.layout_result.confidence * 0.1
            )
        
        # Update BERT NER stats
        if ml_result.ner_result:
            bert_perf = self.stats['component_performance']['bert_ner_ml']
            bert_perf['success_rate'] = 1.0
            bert_perf['avg_confidence'] = (
                bert_perf['avg_confidence'] * 0.9 + ml_result.ner_result.confidence * 0.1
            )
        
        # Update spaCy stats
        if ml_result.spacy_result:
            spacy_perf = self.stats['component_performance']['spacy_ml']
            spacy_perf['success_rate'] = 1.0
            spacy_perf['avg_confidence'] = (
                spacy_perf['avg_confidence'] * 0.9 + ml_result.spacy_result.confidence * 0.1
            )
    
    def get_ml_model_status(self) -> Dict:
        """Get ML model status and availability"""
        if not self.model_manager:
            return {
                'available': False,
                'reason': 'ModelManager not initialized',
                'models': {}
            }
        
        try:
            model_status = self.model_manager.get_model_status()
            model_info = self.model_manager.get_model_info()
            health = self.model_manager.health_check()
            
            return {
                'available': True,
                'models_loaded': any(status.is_loaded for status in model_status.values()),
                'model_status': {name: {
                    'loaded': status.is_loaded,
                    'error': status.error_message,
                    'load_time': status.load_time
                } for name, status in model_status.items()},
                'health': health,
                'performance': self.stats['component_performance']
            }
            
        except Exception as e:
            return {
                'available': False,
                'reason': f'Error getting model status: {e}',
                'models': {}
            }
    
    def enable_ml_models(self, force_reload: bool = False) -> bool:
        """Enable and load ML models"""
        if not self.model_manager:
            logger.error("ModelManager not available")
            return False
        
        try:
            if force_reload:
                # Clear caches and reload
                self.model_manager.clear_all_caches()
            
            load_results = self.model_manager.load_all_models()
            success = any(load_results.values())
            
            if success:
                logger.info(f"ML models enabled: {sum(load_results.values())}/{len(load_results)} loaded")
            else:
                logger.warning("Failed to load any ML models")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to enable ML models: {e}")
            return False
    
    def disable_ml_models(self) -> bool:
        """Disable ML models to free memory"""
        if not self.model_manager:
            return True
        
        try:
            unload_results = {}
            for model_name in ['layoutlm', 'bert_ner', 'spacy']:
                unload_results[model_name] = self.model_manager.unload_model(model_name)
            
            success = all(unload_results.values())
            
            if success:
                logger.info("ML models disabled successfully")
            else:
                logger.warning(f"Some models failed to unload: {unload_results}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to disable ML models: {e}")
            return False
    
    def get_parser_statistics(self) -> Dict:
        """Get comprehensive parser statistics"""
        return {
            'performance': self.stats,
            'datasets': self._get_dataset_stats(),
            'ml_models': self.get_ml_model_status(),
            'component_stats': {
                'company_matcher': self.company_matcher.get_company_statistics(),
                'job_title_normalizer': self.job_title_normalizer.get_title_statistics(),
                'skills_validator': self.skills_validator.get_skill_statistics(),
                'education_normalizer': self.education_normalizer.get_institution_statistics()
            }
        }
    
    def refresh_datasets(self):
        """Refresh all datasets"""
        logger.info("Refreshing datasets...")
        self.dataset_loader.refresh_cache()
        self._load_datasets()
        
        # Reinitialize components with new data
        self.enhanced_normalizer = EnhancedNormalizationService()
        self.company_matcher = CompanyMatcher(self.enhanced_normalizer.companies_data)
        self.job_title_normalizer = JobTitleNormalizer(self.enhanced_normalizer.job_titles_data)
        self.skills_validator = SkillsValidator(self.enhanced_normalizer.skills_data)
        self.education_normalizer = EducationNormalizer(self.enhanced_normalizer.education_data)
        
        logger.info("Datasets refreshed successfully")
    
    def validate_datasets(self) -> Dict:
        """Validate all datasets"""
        return self.dataset_loader.validate_datasets()
