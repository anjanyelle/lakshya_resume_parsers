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
            
            # Load label mappings
            label_path = os.path.join(self.model_path, 'label_mappings.json')
            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    mappings = json.load(f)
                    self.id_to_label = {int(k): v for k, v in mappings['id_to_label'].items()}
                    self.label_to_id = mappings['label_to_id']
            
            self.is_loaded = True
            self.deberta_available = True
            logger.info("✅ DeBERTa NER model loaded successfully")
            
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
            work_lines = lines[work_start:work_end]
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
            edu_lines = lines[edu_start:edu_end]
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
    
    def _parse_single_section(self, text: str, section_type: str) -> Dict[str, List[str]]:
        """Parse a single section with DeBERTa."""
        if not text or not text.strip():
            logger.warning(f"Empty {section_type} section, skipping DeBERTa parsing")
            return {}
        
        # Initialize entities with label names from trained model
        entities = {
            'COMPANY': [], 'CLIENT': [], 'ROLE': [], 'LOCATION': [],
            'DATE_START': [], 'DATE_END': [],
            'DEGREE': [], 'INSTITUTION': [], 'FIELD': [], 'GRADE': [],
            'EDU_YEAR_START': [], 'EDU_YEAR_END': []
        }
        
        # Tokenize and predict
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,  # Full token budget for focused text
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        predictions = torch.argmax(outputs.logits, dim=2)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        predicted_labels = [self.id_to_label[int(label_id)] for label_id in predictions[0]]
        
        # Debug: Log label distribution
        label_counts = {}
        for label in predicted_labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        logger.info(f"🔍 Label distribution: {label_counts}")
        
        # Debug: Log first 20 token-label pairs
        sample_pairs = [(t, l) for t, l in zip(tokens[:20], predicted_labels[:20]) if t not in ['[CLS]', '[SEP]', '[PAD]']]
        logger.info(f"🔍 Sample predictions (first 20): {sample_pairs}")
        
        # Group entities using BIO tagging
        current_entity = None
        current_tokens = []
        
        for token, label in zip(tokens, predicted_labels):
            if token in ['[CLS]', '[SEP]', '[PAD]']:
                continue
            
            if label.startswith('B-'):
                # Save previous entity
                if current_entity and current_tokens:
                    entity_text = ' '.join(current_tokens).replace(' ##', '').strip()
                    if entity_text and current_entity in entities:
                        entities[current_entity].append(entity_text)
                
                # Start new entity (extract label name after B-)
                current_entity = label[2:]
                current_tokens = [token]
            
            elif label.startswith('I-') and current_entity:
                # Continue current entity
                current_tokens.append(token)
            
            else:
                # Save current entity and reset
                if current_entity and current_tokens:
                    entity_text = ' '.join(current_tokens).replace(' ##', '').strip()
                    if entity_text and current_entity in entities:
                        entities[current_entity].append(entity_text)
                
                current_entity = None
                current_tokens = []
        
        # Save final entity
        if current_entity and current_tokens:
            entity_text = ' '.join(current_tokens).replace(' ##', '').strip()
            if entity_text and current_entity in entities:
                entities[current_entity].append(entity_text)
        
        # Log extracted entities
        entity_summary = {k: len(v) for k, v in entities.items() if v}
        if not entity_summary:
            logger.warning(f"⚠️ DeBERTa extracted ZERO entities from {section_type}. Text length: {len(text)} chars")
            logger.warning(f"⚠️ First 200 chars of text: {text[:200]}")
        else:
            logger.info(f"🔍 DeBERTa extracted from {section_type}: {entity_summary}")
        
        return entities
    
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
        # Structured parser uses lowercase keys and provides fully structured data
        if 'work_experience' in entities and isinstance(entities['work_experience'], list):
            # Use structured parser results directly (already in correct format)
            work_experience = entities['work_experience']
        else:
            # Extract companies and locations from DeBERTa NER (uppercase keys)
            companies = entities.get('COMPANY', [])
            locations = entities.get('LOCATION', [])
            
            # Extract work experience from DeBERTa entities
            work_experience = []
            if companies:
                # Create structured work experience from entities
                for i, company in enumerate(companies):
                    exp = {
                        'company': company,
                        'role': entities.get('ROLE', [f'Position {i+1}'])[i] if i < len(entities.get('ROLE', [])) else f'Position {i+1}',
                        'location': locations[i] if i < len(locations) else None,
                        'start_date': entities.get('DATE_START', [None])[i] if i < len(entities.get('DATE_START', [])) else None,
                        'end_date': entities.get('DATE_END', [None])[i] if i < len(entities.get('DATE_END', [])) else None,
                        'description': '',
                        'source': 'deberta_ner'
                    }
                    work_experience.append(exp)
        
        # Extract education
        education = []
        institutions = entities.get('INSTITUTION', [])
        degrees = entities.get('DEGREE', [])
        fields = entities.get('FIELD', [])
        
        for i, institution in enumerate(institutions):
            edu = {
                'institution': institution,
                'degree': degrees[i] if i < len(degrees) else None,
                'field_of_study': fields[i] if i < len(fields) else None,
                'start_year': entities.get('EDU_YEAR_START', [None])[i] if i < len(entities.get('EDU_YEAR_START', [])) else None,
                'end_year': entities.get('EDU_YEAR_END', [None])[i] if i < len(entities.get('EDU_YEAR_END', [])) else None,
                'grade': entities.get('GRADE', [None])[i] if i < len(entities.get('GRADE', [])) else None,
                'source': 'deberta_ner'
            }
            education.append(edu)
        
        # Extract job titles and other entities
        # Check both lowercase (structured parser) and uppercase (DeBERTa NER) keys
        job_titles = entities.get('job_titles', entities.get('ROLE', []))
        clients = entities.get('clients', entities.get('CLIENT', []))
        companies_list = entities.get('companies', entities.get('COMPANY', []))
        locations_list = entities.get('locations', entities.get('LOCATION', []))
        
        return {
            'companies': companies_list,
            'locations': locations_list,
            'work_experience': work_experience,
            'education': education,
            'job_titles': job_titles,
            'clients': clients,
            'dates': entities.get('dates', entities.get('DATE_START', []) + entities.get('DATE_END', [])),
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
