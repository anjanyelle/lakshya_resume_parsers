#!/usr/bin/env python3
"""
DeBERTa NER Parser - Integration with trained Resume NER model
Uses the fine-tuned DeBERTa-v3 model for entity extraction.
"""

import torch
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging
import re

# Import configuration
try:
    from config.deberta_config import DEBERTA_MODEL_PATH, REQUIRED_MODEL_FILES, REQUIRED_MODEL_WEIGHTS
except ImportError:
    # Fallback if config not available
    DEBERTA_MODEL_PATH = str(Path(__file__).parent.parent / "models" / "resume-ner-final")
    REQUIRED_MODEL_FILES = ['config.json', 'tokenizer_config.json', 'tokenizer.json']
    REQUIRED_MODEL_WEIGHTS = ['pytorch_model.bin', 'model.safetensors']

logger = logging.getLogger(__name__)


class DeBERTaNerParser:
    """
    DeBERTa-based NER parser for resume entity extraction.
    Uses a fine-tuned DeBERTa model trained on resume data.
    """
    
    def __init__(self, model_path: str = None):
        """Initialize DeBERTa NER parser with model path."""
        self.model_path = model_path or DEBERTA_MODEL_PATH
        self.model = None
        self.tokenizer = None
        self.id_to_label = {}
        self.label_to_id = {}
        self.is_loaded = False
        self.deberta_available = False
        
        # Import structured parser
        try:
            from .work_experience_structured_parser import StructuredWorkExperienceParser
            self.structured_parser = StructuredWorkExperienceParser()
        except ImportError:
            logger.warning("StructuredWorkExperienceParser not available")
            self.structured_parser = None
        
        self._load_model()
    
    def _check_model_files_exist(self) -> bool:
        """
        Check if all required DeBERTa model files exist.
        
        Required files:
        - config.json
        - pytorch_model.bin OR model.safetensors
        - tokenizer_config.json
        - tokenizer.json
        
        Returns:
            bool: True if all required files exist, False otherwise
        """
        if not os.path.exists(self.model_path):
            logger.info(f"📁 Model directory not found: {self.model_path}")
            return False
        
        # Check for model weights (at least one required)
        has_model_weights = any(
            os.path.exists(os.path.join(self.model_path, weight_file))
            for weight_file in REQUIRED_MODEL_WEIGHTS
        )
        
        if not has_model_weights:
            logger.warning(f"⚠️  DeBERTa model weights not found. Expected one of: {', '.join(REQUIRED_MODEL_WEIGHTS)}")
            return False
        
        # Check other required files
        missing_files = []
        for file_name in REQUIRED_MODEL_FILES:
            file_path = os.path.join(self.model_path, file_name)
            if not os.path.exists(file_path):
                missing_files.append(file_name)
        
        if missing_files:
            logger.warning(f"⚠️  Required files missing: {', '.join(missing_files)}")
            return False
        
        return True
    
    def _extract_years_from_text(self, text: str) -> tuple:
        """
        Extract start and end years from text containing date ranges.
        
        Handles patterns like:
        - "2011–2013", "2011-2013", "2011 - 2013"
        - "(2010-2014)", "2010 to 2014"
        - "2013" (single year)
        
        Returns:
            (start_year, end_year) as integers, or (None, None) if not found
        """
        if not text:
            return None, None
        
        import re
        
        # Remove parentheses and common separators
        cleaned = text.replace('(', '').replace(')', '')
        
        # Pattern 1: Year range with dash/en-dash/to (2011–2013, 2011-2013, 2011 - 2013, 2011 to 2013)
        match = re.search(r'(\d{4})\s*(?:[–\-—]|to)\s*(\d{4})', cleaned)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # Pattern 2: Single year (2013)
        match = re.search(r'(\d{4})', cleaned)
        if match:
            year = int(match.group(1))
            return year, year
        
        return None, None
    
    @staticmethod
    def _preprocess_text(text: str) -> str:
        """
        Pre-process text to normalize format for better model inference.
        Removes format artifacts that confuse the model.
        """
        import re
        
        # Remove common prefixes that confuse the model
        # These prefixes make the model think the label is part of the entity
        prefixes_to_remove = [
            r'^Role:\s*',
            r'^Responsibilities:\s*',
            r'^Environment:\s*',
            r'^Company:\s*',
            r'^Position:\s*',
            r'^Title:\s*',
            r'^Location:\s*',
            r'^Duration:\s*',
            r'^Period:\s*',
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = line
            # Remove prefixes from each line
            for prefix_pattern in prefixes_to_remove:
                cleaned_line = re.sub(prefix_pattern, '', cleaned_line, flags=re.IGNORECASE)
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _load_model(self):
        """Load the trained DeBERTa NER model with graceful fallback."""
        # First check if model files exist
        if not self._check_model_files_exist():
            logger.warning(f"⚠️  DeBERTa model not found at {self.model_path}. Using structured parser fallback.")
            self.is_loaded = False
            self.deberta_available = False
            return
        
        try:
            # Try to load transformers-based model
            from transformers import AutoTokenizer, AutoModelForTokenClassification
            import json
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_path, local_files_only=True)
            
            # Load label mappings - try multiple sources
            label_path = os.path.join(self.model_path, 'label_mappings.json')
            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    mappings = json.load(f)
                    # Handle both naming conventions: id2label/label2id and id_to_label/label_to_id
                    if 'id2label' in mappings:
                        self.id_to_label = {int(k): v for k, v in mappings['id2label'].items()}
                        self.label_to_id = mappings['label2id']
                    elif 'id_to_label' in mappings:
                        self.id_to_label = {int(k): v for k, v in mappings['id_to_label'].items()}
                        self.label_to_id = mappings['label_to_id']
                    else:
                        raise KeyError("Label mappings file missing required keys")
            elif hasattr(self.model.config, 'id2label'):
                # Fallback to model config
                self.id_to_label = self.model.config.id2label
                self.label_to_id = self.model.config.label2id
            else:
                # Last resort: create from model config
                num_labels = self.model.config.num_labels
                self.id_to_label = {i: f"LABEL_{i}" for i in range(num_labels)}
                self.label_to_id = {f"LABEL_{i}": i for i in range(num_labels)}
                logger.warning("⚠️ Using default label mappings - accuracy may be affected")
            
            self.is_loaded = True
            self.deberta_available = True
            logger.info(f"✅ DeBERTa NER model loaded successfully with {len(self.id_to_label)} labels")
            
        except Exception as e:
            logger.error(f"❌ Failed to load DeBERTa model: {e}")
            logger.warning(f"⚠️  DeBERTa model not found at {self.model_path}. Using structured parser fallback.")
            self.model = None
            self.tokenizer = None
            self.is_loaded = False
            self.deberta_available = False
    
    def is_available(self) -> bool:
        """Check if DeBERTa parser is available (model loaded or structured parser available)."""
        return self.is_loaded or self.structured_parser is not None
    
    def parse_text(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text using DeBERTa NER model with section-focused approach.
        IMPORTANT: DeBERTa only processes experience and education sections,
        never the full resume text. This prevents token overflow and improves accuracy.
        
        Args:
            text: Full resume text
            
        Returns:
            Dictionary with extracted entities from focused sections
        """
        # Skip DeBERTa entirely if not available
        if not self.deberta_available:
            logger.info("DeBERTa not available, using structured parser")
            sections = self.extract_target_sections(text)
            return self.parse_focused_sections(sections)
        
        # Additional safety check
        if not self.is_loaded or self.model is None:
            logger.warning("DeBERTa model not loaded, using structured parser fallback")
            sections = self.extract_target_sections(text)
            return self.parse_focused_sections(sections)
        
        try:
            # CRITICAL: Extract only relevant sections — don't pass full text to DeBERTa
            logger.info("🎯 Extracting focused sections for DeBERTa processing...")
            sections = self.extract_target_sections(text)
            
            # Parse only the extracted sections (not full text)
            exp_entities = {}
            edu_entities = {}
            
            # Parse work experience section
            if sections['work_experience_text']:
                logger.info(f"📊 Parsing work experience section ({len(sections['work_experience_text'])} chars)")
                exp_entities = self._parse_single_section(
                    sections['work_experience_text'], 
                    section_type='experience'
                )
            
            # Parse education section
            if sections['education_text']:
                logger.info(f"🎓 Parsing education section ({len(sections['education_text'])} chars)")
                edu_entities = self._parse_single_section(
                    sections['education_text'], 
                    section_type='education'
                )
            
            # Merge entities from both sections
            all_entities = self._merge_section_entities(exp_entities, edu_entities)
            
            # Check if DeBERTa found any entities
            entity_count = sum(len(v) for v in all_entities.values() if isinstance(v, list))
            
            if entity_count == 0:
                logger.warning("DeBERTa found no entities, using rule-based fallback")
                return self._rule_based_fallback(text)
            
            logger.info(f"✅ DeBERTa extracted {entity_count} entities from focused sections")
            
            # Store original text for position-based grouping
            all_entities['_original_text'] = sections.get('work_experience_text', text)
            
            # Convert to expected format
            return self._format_results(all_entities)
            
        except Exception as e:
            logger.error(f"Error parsing text with DeBERTa: {e}")
            return self._rule_based_fallback(text)
    
    def extract_target_sections(self, text: str) -> Dict[str, str]:
        """
        Extract only Work Experience and Education sections for DeBERTa processing.
        This focused approach prevents token truncation and improves accuracy.
        
        Args:
            text: Full resume text
            
        Returns:
            Dictionary with clean work_experience and education sections
        """
        import re
        
        # Split text into lines for better section detection
        lines = text.split('\n')
        
        sections = {'work_experience_text': '', 'education_text': ''}
        
        # Find section boundaries by detecting headers
        work_start = -1
        work_end = -1
        edu_start = -1
        edu_end = -1
        
        # Common section headers (case-insensitive)
        work_headers = ['work experience', 'employment history', 'professional experience', 
                       'experience', 'career history', 'work history', 'professional background']
        edu_headers = ['education', 'academic background', 'qualifications', 
                      'educational background', 'academic qualifications']
        other_headers = ['projects', 'certifications', 'skills', 'technical skills', 
                        'summary', 'objective', 'achievements', 'awards', 'publications']
        
        # Find work experience section
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Check if this line is a work experience header
            if any(header == line_lower or line_lower.startswith(header) for header in work_headers):
                work_start = i  # Include the header line (structured parser will handle it)
                continue
            
            # Check if this line is an education header (marks end of work experience)
            if work_start != -1 and work_end == -1:
                if any(header == line_lower or line_lower.startswith(header) for header in edu_headers + other_headers):
                    work_end = i
                    break
        
        # If work section found but no end, take rest of document
        if work_start != -1 and work_end == -1:
            work_end = len(lines)
        
        # Extract work experience text
        if work_start != -1 and work_end != -1:
            # Skip the header line (work_start) and extract content only
            work_lines = lines[work_start + 1:work_end]
            sections['work_experience_text'] = '\n'.join(work_lines).strip()
        else:
            # If no section headers found, assume entire text is work experience
            # This handles cases where text is already just the work experience section
            logger.info("No work experience header found, treating entire text as work experience")
            sections['work_experience_text'] = text.strip()
        
        # Find education section
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Check if this line is an education header
            if any(header == line_lower or line_lower.startswith(header) for header in edu_headers):
                edu_start = i  # Include the header line
                continue
            
            # Check if this line is another section header (marks end of education)
            if edu_start != -1 and edu_end == -1:
                if any(header == line_lower or line_lower.startswith(header) for header in other_headers):
                    edu_end = i
                    break
        
        # If education section found but no end, take rest of document
        if edu_start != -1 and edu_end == -1:
            edu_end = len(lines)
        
        # Extract education text
        if edu_start != -1 and edu_end != -1:
            # Skip the header line (edu_start) and extract content only
            edu_lines = lines[edu_start + 1:edu_end]
            sections['education_text'] = '\n'.join(edu_lines).strip()
        
        # Limit to reasonable length (prevent too much text)
        if len(sections['work_experience_text']) > 3000:
            sections['work_experience_text'] = sections['work_experience_text'][:3000]
        
        if len(sections['education_text']) > 1000:
            sections['education_text'] = sections['education_text'][:1000]
        
        logger.info(f"📄 Extracted sections: Work={len(sections['work_experience_text'])} chars, Education={len(sections['education_text'])} chars")
        return sections
    
    def parse_focused_sections(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse only the extracted sections with DeBERTa for maximum accuracy.
        Uses TRAINED DeBERTa model to extract entities, then builds structured experiences.
        
        Args:
            sections: Dictionary with work_experience_text and education_text
            
        Returns:
            Dictionary with extracted entities from both sections
        """
        if not self.is_loaded or self.model is None:
            logger.warning("DeBERTa model not loaded, using fallback")
            return self._structured_fallback_sections(sections)
        
        try:
            all_entities = {}
            
            # Parse Work Experience section with TRAINED DeBERTa MODEL
            if sections['work_experience_text']:
                logger.info("🤖 Parsing Work Experience with TRAINED DeBERTa model...")
                
                # Use DeBERTa to extract entities
                exp_entities = self._parse_single_section(
                    sections['work_experience_text'], 
                    section_type='experience'
                )
                
                logger.info(f"📊 DeBERTa extracted: {len(exp_entities.get('COMPANY', []))} companies, {len(exp_entities.get('ROLE', []))} roles")
                
                # Build structured experiences from DeBERTa entities
                from parsers.deberta_experience_builder import DeBERTaExperienceBuilder
                builder = DeBERTaExperienceBuilder()
                work_experiences = builder.build_experiences_from_entities(
                    exp_entities, 
                    sections['work_experience_text']
                )
                
                # If DeBERTa didn't find enough entities, fallback to extract_experience
                if len(work_experiences) == 0:
                    logger.warning("⚠️ DeBERTa found no experiences, using extract_experience fallback")
                    from parsers.experience_extractor import extract_experience
                    raw_experiences = extract_experience(sections['work_experience_text'])
                    
                    work_experiences = []
                    for exp in raw_experiences:
                        work_experiences.append({
                            'job_title': exp.get('title', ''),
                            'company_name': exp.get('company', ''),
                            'location': '',
                            'start_date': exp.get('start_date'),
                            'end_date': exp.get('end_date'),
                            'is_current': exp.get('is_current', False),
                            'clients': [],
                            'description': exp.get('description', '')
                        })
                
                # Collect entities for compatibility
                companies = [exp['company_name'] for exp in work_experiences if exp.get('company_name')]
                job_titles = [exp['job_title'] for exp in work_experiences if exp.get('job_title')]
                locations = [exp['location'] for exp in work_experiences if exp.get('location')]
                
                all_entities['companies'] = companies
                all_entities['locations'] = locations
                all_entities['job_titles'] = job_titles
                all_entities['clients'] = exp_entities.get('CLIENT', [])
                all_entities['work_experience'] = work_experiences
                
                logger.info(f"✅ DeBERTa model built {len(work_experiences)} work experiences")
            
            # Parse Education section  
            if sections['education_text']:
                logger.info("🎓 Parsing Education section with DeBERTa...")
                edu_entities = self._parse_single_section(sections['education_text'], 'education')
                all_entities.update(edu_entities)
            
            # Check if we found any entities
            entity_count = sum(len(v) for v in all_entities.values() if isinstance(v, list))
            
            if entity_count == 0:
                logger.warning("No entities found in sections, using fallback")
                return self._structured_fallback_sections(sections)
            
            logger.info(f"✅ Found {entity_count} entities in sections")
            return self._format_results(all_entities)
            
        except Exception as e:
            logger.error(f"Error parsing sections: {e}")
            return self._structured_fallback_sections(sections)
    
    def _merge_section_entities(self, exp_entities: Dict, edu_entities: Dict) -> Dict[str, List[str]]:
        """Merge entities from experience and education sections."""
        merged = {}
        
        # Merge all entity types
        all_keys = set(exp_entities.keys()) | set(edu_entities.keys())
        
        for key in all_keys:
            exp_list = exp_entities.get(key, [])
            edu_list = edu_entities.get(key, [])
            
            # Combine and deduplicate
            if isinstance(exp_list, list) and isinstance(edu_list, list):
                merged[key] = exp_list + edu_list
            elif isinstance(exp_list, list):
                merged[key] = exp_list
            elif isinstance(edu_list, list):
                merged[key] = edu_list
            else:
                merged[key] = []
        
        return merged
    
    def _detect_format(self, text: str) -> str:
        """
        Detect if text is in structured format (CSV, pipe-separated, etc.) or natural language.
        
        Returns:
            'csv' - Comma-separated format
            'double_colon' - Double colon separated (::)
            'pipe' - Pipe separated (|) but without @ symbol
            'double_angle' - Double angle bracket separated (>>)
            'natural' - Natural language format (has @ or natural phrasing)
        """
        lines = text.strip().split('\n')
        if not lines:
            return 'natural'
        
        # Sample first few lines
        sample_lines = lines[:3]
        
        # Check for natural language indicators
        natural_indicators = ['@', ' at ', ' in ', ' from ', ' to ']
        has_natural = any(indicator in text.lower() for indicator in natural_indicators)
        
        # Count delimiter occurrences per line
        comma_count = sum(line.count(',') for line in sample_lines) / len(sample_lines)
        double_colon_count = sum(line.count('::') for line in sample_lines) / len(sample_lines)
        pipe_count = sum(line.count('|') for line in sample_lines) / len(sample_lines)
        double_angle_count = sum(line.count('>>') for line in sample_lines) / len(sample_lines)
        
        # Detect format based on delimiter density
        if double_colon_count >= 2:
            return 'double_colon'
        elif double_angle_count >= 2:
            return 'double_angle'
        elif pipe_count >= 2 and not has_natural:
            return 'pipe'
        elif comma_count >= 3 and not has_natural:
            return 'csv'
        else:
            return 'natural'
    
    def _convert_to_natural_language(self, text: str) -> str:
        """
        Convert structured formats (CSV, pipe-separated, etc.) to natural language format
        that the DeBERTa model was trained on.
        
        Model expects: "Job Title @ Company | Location | Start Date - End Date"
        """
        format_type = self._detect_format(text)
        
        if format_type == 'natural':
            return text  # Already in correct format
        
        logger.info(f"📝 Detected {format_type} format, converting to natural language...")
        
        lines = text.strip().split('\n')
        converted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            converted = self._convert_line_to_natural(line, format_type)
            if converted:
                converted_lines.append(converted)
        
        result = '\n'.join(converted_lines)
        logger.info(f"✅ Converted {len(lines)} lines from {format_type} to natural language")
        logger.info(f"   Preview: {result[:200]}...")
        
        return result
    
    def _convert_line_to_natural(self, line: str, format_type: str) -> str:
        """
        Convert a single line from structured format to natural language.
        
        Common patterns:
        CSV: "Company,Location,Role,StartDate,EndDate"
        Double colon: "Company :: Location :: Role :: StartDate :: EndDate"
        Pipe: "Company | Location | Role | StartDate | EndDate"
        
        Target: "Role @ Company | Location | StartDate - EndDate"
        """
        # Split by delimiter
        if format_type == 'csv':
            parts = [p.strip() for p in line.split(',')]
        elif format_type == 'double_colon':
            parts = [p.strip() for p in line.split('::')]
        elif format_type == 'pipe':
            parts = [p.strip() for p in line.split('|')]
        elif format_type == 'double_angle':
            parts = [p.strip() for p in line.split('>>')]
        else:
            return line
        
        if len(parts) < 3:
            return line  # Not enough parts, return as-is
        
        # Heuristic to identify which part is which
        # Common patterns:
        # 1. Company, Location, Role, StartDate, EndDate
        # 2. Role, Company, Location, StartDate, EndDate
        
        company = None
        role = None
        location = None
        start_date = None
        end_date = None
        
        # Identify parts by keywords and patterns
        for i, part in enumerate(parts):
            part_lower = part.lower()
            
            # Role indicators (contains job keywords)
            role_keywords = ['engineer', 'developer', 'analyst', 'manager', 'architect', 
                           'consultant', 'designer', 'scientist', 'specialist', 'lead',
                           'senior', 'junior', 'principal', 'staff', 'director', 'vp']
            if any(keyword in part_lower for keyword in role_keywords) and not role:
                role = part
                continue
            
            # Date indicators (contains year or month)
            date_keywords = ['january', 'february', 'march', 'april', 'may', 'june',
                           'july', 'august', 'september', 'october', 'november', 'december',
                           'present', 'current', '20', '19']
            if any(keyword in part_lower for keyword in date_keywords):
                if not start_date:
                    start_date = part
                elif not end_date:
                    end_date = part
                continue
            
            # Location indicators (contains state/country or city patterns)
            location_keywords = ['india', 'usa', 'ca', 'ny', 'tx', 'wa', 'bangalore', 
                               'hyderabad', 'chennai', 'mumbai', 'delhi', 'pune',
                               'seattle', 'francisco', 'york', 'austin', 'boston']
            if any(keyword in part_lower for keyword in location_keywords) and not location:
                location = part
                continue
            
            # Company (usually first non-role, non-date, non-location part)
            if not company and not role:
                company = part
        
        # If we still don't have company, use first part
        if not company and len(parts) > 0:
            company = parts[0]
        
        # If we still don't have role, try to find it
        if not role and len(parts) > 2:
            # Check if second or third part looks like a role
            for part in parts[1:3]:
                if part and part != company and part != location:
                    role = part
                    break
        
        # Build natural language format: "Role @ Company | Location | StartDate - EndDate"
        result_parts = []
        
        if role:
            result_parts.append(role)
        
        if company:
            if result_parts:
                result_parts.append('@')
            result_parts.append(company)
        
        if location:
            if result_parts:
                result_parts.append('|')
            result_parts.append(location)
        
        if start_date or end_date:
            if result_parts:
                result_parts.append('|')
            if start_date:
                result_parts.append(start_date)
            if end_date:
                if start_date:
                    result_parts.append('-')
                result_parts.append(end_date)
        
        return ' '.join(result_parts)
    
    def _parse_single_section(self, text: str, section_type: str) -> Dict[str, List[str]]:
        """Parse a single section with DeBERTa using Hugging Face pipeline with aggregation."""
        if not text or not text.strip():
            logger.warning(f"Empty {section_type} section, skipping DeBERTa parsing")
            return {}
        
        # Detect and convert structured formats to natural language
        text = self._convert_to_natural_language(text)
        
        # Pre-process text to normalize format
        text = self._preprocess_text(text)
        
        # Log the input text for debugging
        logger.info(f"🔍 DeBERTa parsing {section_type} section:")
        logger.info(f"   Text length: {len(text)} chars")
        logger.info(f"   Text preview: {text[:300]}...")
        
        # Initialize entities with label names from trained model
        entities_with_positions = []  # List of {type, text, start, end}
        entities = {
            'COMPANY': [], 'CLIENT': [], 'ROLE': [], 'LOCATION': [],
            'START_DATE': [], 'END_DATE': [], 'DATE_START': [], 'DATE_END': [],
            'DEGREE': [], 'EDUCATION': [], 'INSTITUTION': [], 'FIELD': [], 'GRADE': [],
            'EDU_YEAR_START': [], 'EDU_YEAR_END': []
        }
        
        # Use Hugging Face pipeline with aggregation to properly combine multi-token entities
        try:
            from transformers import pipeline
            
            # Create NER pipeline with aggregation strategy
            ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple",  # Better for combining full entity text
                device=-1  # CPU
            )
            
            # Run prediction
            predictions = ner_pipeline(text)
            
            # Manually aggregate consecutive entities of the same type
            # (pipeline aggregation doesn't always work perfectly with DeBERTa tokenizer)
            aggregated = []
            current_entity = None
            
            for pred in predictions:
                entity_type = pred['entity_group']
                entity_start = pred['start']
                entity_end = pred['end']
                
                # Increase proximity window to 5 chars to catch space-separated tokens
                if current_entity and current_entity['type'] == entity_type and entity_start <= current_entity['end'] + 5:
                    # Extend current entity
                    current_entity['end'] = entity_end
                else:
                    # Save previous and start new
                    if current_entity:
                        aggregated.append(current_entity)
                    current_entity = {
                        'type': entity_type,
                        'start': entity_start,
                        'end': entity_end
                    }
            
            # Save last entity
            if current_entity:
                aggregated.append(current_entity)
            
            # Convert aggregated predictions to our format
            for agg in aggregated:
                entity_type = agg['type']
                entity_start = agg['start']
                entity_end = agg['end']
                
                # Extract full text from original string using positions
                entity_text = text[entity_start:entity_end].strip()
                
                # CRITICAL FIX: Clean up entities that span multiple lines
                # If entity contains newline, split and take the longest meaningful part
                if '\n' in entity_text:
                    lines = [line.strip() for line in entity_text.split('\n') if line.strip()]
                    if lines:
                        # Take the first non-empty line (usually the actual entity)
                        # For ROLE: "Full Stack Developer\nGatnix" -> "Full Stack Developer"
                        # For COMPANY: "Gatnix\nTechnologies" -> keep both if short
                        if len(lines) == 1:
                            entity_text = lines[0]
                        elif entity_type in ['COMPANY', 'INSTITUTION']:
                            # For companies/institutions, join short lines (e.g., "Tech\nSolutions" -> "Tech Solutions")
                            if all(len(line) < 20 for line in lines):
                                entity_text = ' '.join(lines)
                            else:
                                entity_text = lines[0]
                        else:
                            # For other types (ROLE, LOCATION), take first line only
                            entity_text = lines[0]
                
                # Map entity types to our schema
                if entity_type in entities and entity_text:
                    entities[entity_type].append(entity_text)
                    entities_with_positions.append({
                        'type': entity_type,
                        'text': entity_text,
                        'start': entity_start,
                        'end': entity_end
                    })
            
            logger.info(f"✅ Pipeline extracted {len(predictions)} aggregated entities")
            
        except Exception as e:
            logger.warning(f"Pipeline aggregation failed: {e}, falling back to manual extraction")
            
            # Fallback to manual token-by-token extraction
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=2048,
                return_offsets_mapping=True
            )
            offset_mapping = inputs.pop("offset_mapping")[0]
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            predictions = torch.argmax(outputs.logits[0], dim=1)
            tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            
            # Extract entities using offset mapping for accurate text (fallback only)
            current_entity = None
            current_text = ""
            current_label = None
            current_start = None
            
            for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
                if token in ['<s>', '</s>', '<pad>', '[CLS]', '[SEP]', '[PAD]']:
                    continue
                
                label = self.id_to_label[pred_id.item()]
                start, end = offset
                
                if start == end:
                    continue
                
                actual_text = text[start:end]
                
                if label.startswith('B-'):
                    if current_entity and current_text and current_start is not None:
                        clean_text = current_text.strip()
                        if clean_text and current_entity in entities:
                            entities[current_entity].append(clean_text)
                            entities_with_positions.append({
                                'type': current_entity,
                                'text': clean_text,
                                'start': current_start,
                                'end': start
                            })
                    
                    current_label = label[2:]
                    current_text = actual_text
                    current_entity = current_label
                    current_start = start
                    
                elif label.startswith('I-') and current_entity and label[2:] == current_label:
                    current_text += actual_text
                    
                else:
                    if current_entity and current_text and current_start is not None:
                        clean_text = current_text.strip()
                        if clean_text and current_entity in entities:
                            entities[current_entity].append(clean_text)
                            entities_with_positions.append({
                                'type': current_entity,
                                'text': clean_text,
                                'start': current_start,
                                'end': start
                            })
                        current_entity = None
                        current_text = ""
                        current_label = None
                        current_start = None
            
            # Save final entity
            if current_entity and current_text and current_start is not None:
                clean_text = current_text.strip()
                if clean_text and current_entity in entities:
                    entities[current_entity].append(clean_text)
                    entities_with_positions.append({
                        'type': current_entity,
                    'text': clean_text,
                    'start': current_start,
                    'end': len(text)  # End at text length
                })
        
        # Log extracted entities (after validation filters)
        entity_summary = {k: len(v) for k, v in entities.items() if v}
        if not entity_summary:
            logger.warning(f"⚠️ DeBERTa extracted ZERO entities from {section_type} after validation filters")
            logger.warning(f"   This could mean: (1) Model didn't detect entities, or (2) Validation filters rejected them")
        else:
            logger.info(f"✅ DeBERTa extracted from {section_type} (before hybrid post-processing): {entity_summary}")
            if entities.get('ROLE'):
                logger.info(f"   Roles extracted: {entities['ROLE']}")
            if entities.get('COMPANY'):
                logger.info(f"   Companies extracted: {entities['COMPANY'][:5]}")  # First 5
            logger.info(f"   Total entities with positions: {len(entities_with_positions)}")
        
        # Store positions for proximity-based grouping (before hybrid processing)
        entities['_positions'] = entities_with_positions
        
        # Apply hybrid post-processing (filters + rule-based person name extraction)
        # This will update _positions if needed
        try:
            from parsers.hybrid_ner_postprocessor import apply_hybrid_postprocessing
            entities = apply_hybrid_postprocessing(entities, text)
            
            # Log after hybrid processing
            entity_summary_after = {k: len(v) for k, v in entities.items() if v and k != '_positions'}
            logger.info(f"✅ After hybrid post-processing: {entity_summary_after}")
            if entities.get('PERSON_NAME'):
                logger.info(f"   Person names added: {entities['PERSON_NAME']}")
        except Exception as e:
            logger.warning(f"⚠️ Hybrid post-processing failed: {e}, using original entities")
        
        return entities
    
    def _is_person_name(self, text: str) -> bool:
        """Check if text looks like a person name."""
        text = text.strip()
        
        # Exclude company suffixes - these indicate it's a company, not a person
        company_suffixes = [
            'corporation', 'corp', 'inc', 'llc', 'ltd', 'limited', 
            'company', 'co', 'group', 'services', 'solutions', 'technologies',
            'systems', 'consulting', 'partners', 'associates', 'holdings',
            'enterprises', 'industries', 'international', 'global', 'worldwide',
            'airlines', 'airways', 'bank', 'financial', 'insurance', 'healthcare'
        ]
        
        text_lower = text.lower()
        if any(suffix in text_lower for suffix in company_suffixes):
            return False  # It's a company, not a person
        
        # Common person name patterns
        patterns = [
            r'^[A-Z][a-z]+ [A-Z][a-z]+$',  # First Last
            r'^[A-Z]\. [A-Z][a-z]+$',       # F. Last
            r'^[A-Z][a-z]+ [A-Z]\.$',       # First L.
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        # Check if it's exactly 2 capitalized words (typical person name)
        # But NOT 3+ words (more likely company name)
        words = text.split()
        if len(words) == 2:
            if all(word[0].isupper() and len(word) > 1 for word in words if word):
                # Additional check: person names are usually shorter
                if len(text) < 30:  # Person names rarely exceed 30 chars
                    return True
        
        return False
    
    def _is_skill(self, text: str) -> bool:
        """Check if text is a skill/technology."""
        skill_keywords = [
            'react', 'node', 'python', 'java', 'javascript', 'typescript',
            'angular', 'vue', 'django', 'flask', 'spring', 'aws', 'docker',
            'kubernetes', 'mongodb', 'sql', 'mysql', 'postgresql', 'redis',
            'html', 'css', 'git', 'jenkins', 'ci/cd', 'agile', 'scrum'
        ]
        text_lower = text.lower().strip()
        return any(skill in text_lower for skill in skill_keywords)
    
    def _is_valid_company(self, text: str) -> bool:
        """Validate if text is a legitimate company name."""
        text = text.strip()
        
        # Must be at least 2 characters
        if len(text) < 2:
            return False
        
        # Reject if it's just numbers or single letters
        if len(text) <= 3 and (text.isdigit() or len(text.split()) == 1):
            return False
        
        # Reject common tech/skill names
        tech_keywords = ['react', 'angular', 'vue', 'node', 'python', 'java', 'django', 
                        'flask', 'spring', 'mongodb', 'sql', 'postgresql', 'mysql']
        if text.lower() in tech_keywords:
            return False
        
        # Reject if it looks like an email fragment
        if '@' in text or '.com' in text.lower():
            return False
        
        # Accept if it contains company indicators
        company_indicators = ['ltd', 'pvt', 'inc', 'corp', 'llc', 'technologies', 
                             'solutions', 'systems', 'labs', 'software', 'group']
        if any(indicator in text.lower() for indicator in company_indicators):
            return True
        
        # Accept if it's multiple words (likely a company name)
        if len(text.split()) >= 2:
            return True
        
        return False
    
    def _is_valid_job_title(self, text: str) -> bool:
        """Validate if text is a legitimate job title - LESS STRICT."""
        text = text.strip()
        
        # Must be at least 3 characters
        if len(text) < 3:
            return False
        
        # Reject if it's a person name (from contact section)
        if self._is_person_name(text):
            return False
        
        # Reject ONLY obvious non-titles
        obvious_non_titles = ['responsive', 'scalable', 'modern', 'developed', 'building', 'working']
        if len(text.split()) == 1 and text.lower() in obvious_non_titles:
            return False
        
        # Accept if it contains job title keywords
        job_keywords = ['developer', 'engineer', 'manager', 'architect', 'analyst',
                       'designer', 'consultant', 'specialist', 'lead', 'senior',
                       'junior', 'trainee', 'intern', 'director', 'coordinator',
                       'programmer', 'administrator', 'technician', 'principal']
        if any(keyword in text.lower() for keyword in job_keywords):
            return True
        
        # Accept multi-word titles (likely legitimate)
        if len(text.split()) >= 2:
            return True
        
        # Accept single-word professional titles
        professional_titles = ['ceo', 'cto', 'cfo', 'vp', 'president', 'founder']
        if text.lower() in professional_titles:
            return True
        
        return False
    
    def _is_valid_location(self, text: str) -> bool:
        """Validate if text is a legitimate location."""
        text = text.strip()
        
        # Must be at least 2 characters
        if len(text) < 2:
            return False
        
        # Reject if it's just numbers
        if text.isdigit():
            return False
        
        # Reject tech/skill names
        tech_keywords = ['react', 'angular', 'vue', 'node', 'python', 'java', 'django',
                        'flask', 'spring', 'mongodb', 'sql', 'postgresql', 'mysql',
                        'javascript', 'typescript', 'html', 'css']
        if text.lower() in tech_keywords:
            return False
        
        # Accept if it contains location indicators
        location_indicators = ['india', 'usa', 'uk', 'city', 'bangalore', 'hyderabad',
                              'mumbai', 'delhi', 'chennai', 'pune', 'kolkata']
        if any(indicator in text.lower() for indicator in location_indicators):
            return True
        
        # Accept if it looks like "City, Country" format
        if ',' in text:
            return True
        
        return False
    
    def _is_valid_degree(self, text: str) -> bool:
        """Validate if text is a legitimate degree."""
        text = text.strip()
        
        # Reject if too short (less than 2 characters)
        if len(text) < 2:
            return False
        
        # Reject single punctuation or special characters
        if text in ['(', ')', '[', ']', '{', '}', ',', '.', ':', ';', '-', '_']:
            return False
        
        # Reject common non-degree single words
        invalid_single_words = [
            'certified', 'project', 'fundamentals', 'operational', 'administrative',
            'management', 'training', 'professional', 'business', 'technical',
            'advanced', 'basic', 'intermediate', 'senior', 'junior', 'lead',
            'the', 'and', 'or', 'in', 'at', 'of', 'for', 'with', 'to', 'from'
        ]
        if len(text.split()) == 1 and text.lower() in invalid_single_words:
            return False
        
        # Accept if it contains degree keywords
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'associate',
            'b.tech', 'm.tech', 'b.e', 'm.e', 'b.sc', 'm.sc', 'b.com', 'm.com',
            'b.a', 'm.a', 'mba', 'bba', 'bca', 'mca', 'llb', 'md', 'mbbs',
            'engineering', 'science', 'arts', 'commerce', 'technology',
            'degree', 'certification'
        ]
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in degree_keywords):
            return True
        
        # Accept multi-word degrees (likely legitimate)
        if len(text.split()) >= 2:
            # But reject if it's just adjectives + common words
            common_phrases = ['business process', 'project management', 'risk management']
            if text_lower in common_phrases:
                return False
            return True
        
        return False
    
    def _structured_fallback_sections(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Enhanced fallback using extract_experience function."""
        result = {}
        
        # Parse work experience with ENHANCED extract_experience function
        if sections['work_experience_text']:
            from parsers.experience_extractor import extract_experience
            
            raw_experiences = extract_experience(sections['work_experience_text'])
            
            # Convert to expected format
            work_experiences = []
            companies = []
            locations = []
            job_titles = []
            
            for exp in raw_experiences:
                formatted_exp = {
                    'job_title': exp.get('title', ''),
                    'company_name': exp.get('company', ''),
                    'location': '',
                    'start_date': exp.get('start_date'),
                    'end_date': exp.get('end_date'),
                    'is_current': exp.get('is_current', False),
                    'clients': [],
                    'description': exp.get('description', '')
                }
                work_experiences.append(formatted_exp)
                
                if exp.get('company'):
                    companies.append(exp['company'])
                if exp.get('title'):
                    job_titles.append(exp['title'])
            
            result['companies'] = companies
            result['locations'] = locations
            result['job_titles'] = job_titles
            result['clients'] = []
            result['work_experience'] = work_experiences
            
            logger.info(f"✅ Fallback extractor found {len(work_experiences)} work experiences")
        
        # Use rule-based for education if no structured parser
        if sections['education_text']:
            combined_text = f"{sections['work_experience_text']}\n{sections['education_text']}"
            fallback = self._rule_based_fallback(combined_text)
            result['education'] = fallback.get('education', [])
            result['degrees'] = fallback.get('degrees', [])
            result['institutions'] = fallback.get('institutions', [])
        
        return result
    
    def _rule_based_fallback_sections(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Rule-based fallback for extracted sections."""
        combined_text = f"{sections['work_experience_text']}\n{sections['education_text']}"
        return self._rule_based_fallback(combined_text)
    
    def _rule_based_fallback(self, text: str) -> Dict[str, Any]:
        import re
        
        # Simple regex patterns for common entities
        patterns = {
            'companies': [
                r'\b(?:Infosys|TCS|Wipro|Deloitte|Accenture|Capgemini|IBM|Microsoft|Google|Amazon|Facebook|Apple|Oracle|Cisco|Intel|HP|Dell|Dignity Health|Bank of America|Inno Minds)\b',
                r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'  # Capitalized company names
            ],
            'locations': [
                r'\b(?:Hyderabad|Bangalore|Pune|Mumbai|Delhi|Chennai|Kolkata|Bengaluru|San Francisco|New York|Atlanta|Pleasanton|San Francisco|CA|GA)\b',
                r'\b[A-Z][a-z]+,?\s+[A-Z]{2,}\b'  # City, State/Country
            ],
            'job_titles': [
                r'\b(?:Senior|Junior|Lead|Principal|Staff)?\s*(?:Software|Java|Python|Full Stack|Frontend|Backend|Data|Machine Learning|DevOps|Cloud|Security|QA|Test)?\s*(?:Engineer|Developer|Architect|Manager|Consultant|Analyst|Designer|Specialist)\b',
                r'\b(?:IT|Technical|Project|Product)?\s*(?:Manager|Lead|Head|Director|VP|Chief)\b'
            ],
            'degrees': [
                r'\b(?:B\.Tech|M\.Tech|B\.E|M\.E|B\.Sc|M\.Sc|B\.A|M\.A|Ph\.D|MBA|MCA|BCA)\b',
                r'\b(?:Bachelor|Master|Doctorate)s?\s+(?:of\s+)?(?:Engineering|Science|Arts|Business Administration|Computer Application|Philosophy|Technology)\b'
            ],
            'institutions': [
                r'\b(?:JNTU|IIT|NIT|IIIT|BITS|Anna|Mumbai|Delhi|Bangalore|Reddy Institute|Malla Reddy) University\b',
                r'\b[A-Z][a-z]+ (?:University|College|Institute|School of)\b'
            ]
        }
        
        entities = {}
        
        # Filter out common non-company words
        company_exclusions = {'responsibilities', 'developed', 'implemented', 'designed', 'created', 'managed', 'built', 'enhanced', 'optimized', 'maintained', 'supported', 'collaborated', 'utilized', 'applied', 'worked', 'experienced', 'proficient', 'skilled', 'expertise', 'knowledge', 'ability', 'experience', 'years', 'various', 'multiple', 'different', 'several', 'many', 'various', 'including', 'such', 'like', 'etc', 'etc.', 'and', 'or', 'with', 'for', 'in', 'on', 'at', 'by', 'through', 'from', 'to', 'of', 'the', 'a', 'an'}
        
        for entity_type, pattern_list in patterns.items():
            found_entities = set()
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                found_entities.update(matches)
            
            # Filter entities
            if entity_type == 'companies':
                filtered_entities = []
                for entity in found_entities:
                    # Skip if entity contains exclusion words
                    if not any(word in entity.lower() for word in company_exclusions):
                        # Skip if entity is too short or contains common words
                        if len(entity.strip()) > 2 and not entity.lower().startswith(('the ', 'a ', 'an ')):
                            filtered_entities.append(entity.strip())
                entities[entity_type] = filtered_entities
            else:
                entities[entity_type] = [e.strip() for e in found_entities if len(e.strip()) > 2]
        
        # Create structured work experience from found entities
        work_experience = []
        companies = entities.get('companies', [])
        locations = entities.get('locations', [])
        job_titles = entities.get('job_titles', [])
        
        for i, company in enumerate(companies[:3]):  # Limit to 3 companies
            exp = {
                'company': company,
                'role': job_titles[i] if i < len(job_titles) else 'Software Engineer',
                'location': locations[i] if i < len(locations) else None,
                'start_date': None,
                'end_date': None,
                'description': '',
                'source': 'rule_based_fallback'
            }
            work_experience.append(exp)
        
        # Create structured education
        education = []
        institutions = entities.get('institutions', [])
        degrees = entities.get('degrees', [])
        
        for i, institution in enumerate(institutions[:2]):  # Limit to 2 institutions
            edu = {
                'institution': institution,
                'degree': degrees[i] if i < len(degrees) else 'Bachelor Degree',
                'field_of_study': 'Computer Science',
                'start_year': None,
                'end_year': None,
                'grade': None,
                'source': 'rule_based_fallback'
            }
            education.append(edu)
        
        return {
            'companies': companies,
            'locations': locations,
            'work_experience': work_experience,
            'education': education,
            'job_titles': job_titles,
            'clients': [],
            'dates': [],
            'degrees': degrees,
            'institutions': institutions,
            'fields_of_study': [],
            'source': 'rule_based_fallback',
            'confidence': {
                'rule_based_confidence': 0.6,
                'entities_found': len(companies) + len(institutions) + len(job_titles)
            }
        }
    
    def _parse_long_resume(self, text: str) -> Dict[str, List[str]]:
        """
        Parse long resume by chunking and merging results.
        
        Args:
            text: Full resume text
            
        Returns:
            Merged entities from all chunks
        """
        # Simple chunking strategy - split by paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # Rough token count (1 token ≈ 1 word)
            current_words = len(current_chunk.split())
            paragraph_words = len(paragraph.split())
            
            if current_words + paragraph_words < 400:  # Safe margin from 512
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Process chunks and merge results
        all_entities = defaultdict(list)
        
        for i, chunk in enumerate(chunks):
            try:
                chunk_entities = self.model.predict(chunk)
                
                # Merge entities (avoid duplicates)
                for entity_type, entity_list in chunk_entities.items():
                    for entity in entity_list:
                        if entity not in all_entities[entity_type]:
                            all_entities[entity_type].append(entity)
                            
            except Exception as e:
                logger.warning(f"Error processing chunk {i+1}: {e}")
                continue
        
        return dict(all_entities)
    
    def _format_results(self, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Format DeBERTa results to match expected API format.
        
        Args:
            entities: Raw entities from DeBERTa model OR structured parser results
            
        Returns:
            Formatted results compatible with existing API
        """
        # CRITICAL: Check if structured parser already provided work_experience
        # Initialize variables to prevent 'not initialized' error
        start_dates = []
        end_dates = []
        
        # Structured parser uses lowercase keys and provides fully structured data
        if 'work_experience' in entities and isinstance(entities['work_experience'], list):
            # Use structured parser results directly (already in correct format)
            work_experience = entities['work_experience']
            companies_list = entities.get('companies', [])
            job_titles = entities.get('job_titles', [])
            locations_list = entities.get('locations', [])
            start_dates = entities.get('dates', [])
            end_dates = []
        else:
            # Extract from DeBERTa NER (uppercase keys)
            # Use DeBERTaExperienceBuilder for proper entity grouping by proximity
            from .deberta_experience_builder import DeBERTaExperienceBuilder
            
            experience_builder = DeBERTaExperienceBuilder()
            
            # Get the original text from entities if available
            text = entities.get('_original_text', '')
            
            # Build experiences using position-based grouping
            structured_experiences = experience_builder.build_experiences_from_entities(entities, text)
            
            # Convert to API format
            work_experience = []
            for exp in structured_experiences:
                work_experience.append({
                    'company': exp.get('company_name', ''),
                    'role': exp.get('job_title', ''),
                    'location': exp.get('location', ''),
                    'start_date': exp.get('start_date'),
                    'end_date': exp.get('end_date'),
                    'description': exp.get('description', ''),
                    'source': 'deberta_ner'
                })
            
            # Extract lists for compatibility
            companies_list = [exp.get('company_name', '') for exp in structured_experiences]
            job_titles = [exp.get('job_title', '') for exp in structured_experiences]
            locations_list = [exp.get('location', '') for exp in structured_experiences]
            start_dates = [exp.get('start_date') for exp in structured_experiences]
            end_dates = [exp.get('end_date') for exp in structured_experiences]
        
        # Extract education - FIXED to handle DEGREE-only cases
        education = []
        institutions = entities.get('EDUCATION', entities.get('INSTITUTION', []))
        degrees = entities.get('DEGREE', [])
        fields = entities.get('FIELD', [])
        edu_start = entities.get('EDU_YEAR_START', [])
        edu_end = entities.get('EDU_YEAR_END', [])
        
        # Fallback: If institutions not extracted but degrees exist, try regex extraction
        original_text = entities.get('_original_text', '')
        if not institutions and degrees and original_text:
            import re
            # Common institution patterns
            inst_patterns = [
                r'\b(JNTU|IIT|NIT|IIIT|BITS|MIT|Stanford|Harvard|Berkeley|CMU)\s*(?:Hyderabad|Delhi|Mumbai|Bangalore|Chennai|Pune)?\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:University|College|Institute)\b',
                r'\b([A-Z]{2,5})\s+(?:University|College|Institute)\b'
            ]
            for pattern in inst_patterns:
                matches = re.findall(pattern, original_text, re.IGNORECASE)
                if matches:
                    institutions = [m if isinstance(m, str) else m[0] for m in matches[:len(degrees)]]
                    logger.info(f"🔧 Fallback extracted {len(institutions)} institutions: {institutions}")
                    break
        
        # Build education entries
        max_edu = max(len(institutions), len(degrees)) if (institutions or degrees) else 0
        
        if max_edu > 0:
            for i in range(max_edu):
                # Get years from model if available
                start_year = edu_start[i] if i < len(edu_start) else None
                end_year = edu_end[i] if i < len(edu_end) else None
                
                # If years not extracted by model, try to parse from degree/institution text
                if not start_year and not end_year:
                    # Check degree text for year ranges like "Bachelor of Science (2010-2014)"
                    degree_text = degrees[i] if i < len(degrees) else ''
                    institution_text = institutions[i] if i < len(institutions) else ''
                    
                    # Try to extract years from degree or institution text
                    combined_text = f"{degree_text} {institution_text}"
                    extracted_start, extracted_end = self._extract_years_from_text(combined_text)
                    
                    if extracted_start:
                        start_year = extracted_start
                    if extracted_end:
                        end_year = extracted_end
                
                edu = {
                    'institution': institutions[i] if i < len(institutions) else '',
                    'degree': degrees[i] if i < len(degrees) else '',
                    'field_of_study': fields[i] if i < len(fields) else None,
                    'start_year': start_year,
                    'end_year': end_year,
                    'grade': entities.get('GRADE', [None])[i] if i < len(entities.get('GRADE', [])) else None,
                    'source': 'deberta_ner'
                }
                # Add if has institution OR degree (not both required)
                if edu['institution'] or edu['degree']:
                    education.append(edu)
        
        # Log education extraction for debugging
        if degrees:
            logger.info(f"📚 DeBERTa extracted {len(degrees)} degrees: {degrees}")
        if institutions:
            logger.info(f"🏫 DeBERTa extracted {len(institutions)} institutions: {institutions}")
        if education:
            logger.info(f"✅ DeBERTa built {len(education)} education entries")
        else:
            logger.warning(f"⚠️ DeBERTa built 0 education entries (degrees: {len(degrees)}, institutions: {len(institutions)})")
        
        # Extract other entities
        clients = entities.get('clients', entities.get('CLIENT', []))
        
        return {
            'companies': companies_list,
            'locations': locations_list,
            'work_experience': work_experience,
            'education': education,
            'job_titles': job_titles,
            'clients': clients,
            'dates': start_dates + end_dates if 'COMPANY' in entities else entities.get('dates', []),
            'degrees': degrees,
            'institutions': institutions,
            'fields_of_study': fields,
            'source': 'deberta_ner' if 'COMPANY' in entities else 'structured_parser',
            'confidence': {
                'deberta_confidence': 0.85,
                'entities_found': len(companies_list) + len(institutions) + len(job_titles)
            }
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'companies': [],
            'locations': [],
            'work_experience': [],
            'education': [],
            'job_titles': [],
            'clients': [],
            'dates': [],
            'degrees': [],
            'institutions': [],
            'fields_of_study': [],
            'source': 'deberta_ner',
            'confidence': {
                'deberta_confidence': 0.0,
                'entities_found': 0
            }
        }
