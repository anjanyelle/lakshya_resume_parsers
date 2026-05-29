#!/usr/bin/env python3
"""
DeBERTa NER Parser - Production Ready Version
Fixes chunking, token limits, and cross-section entity leakage.
"""

import logging
import re
import torch
from typing import Dict, List, Any, Tuple
from transformers import AutoTokenizer, AutoModelForTokenClassification

logger = logging.getLogger(__name__)


class DeBERTaNerParserFixed:
    """
    Production-ready DeBERTa NER parser with proper chunking and token management.
    
    Key fixes:
    1. Token counting before model inference
    2. Automatic chunking for long texts
    3. Section separation to prevent cross-section leakage
    4. Comprehensive logging for debugging
    """
    
    def __init__(self, model_path: str = None, max_tokens: int = 512):
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.chunk_overlap = 50  # Tokens overlap between chunks
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.deberta_available = False
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load DeBERTa model with error handling."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_path, local_files_only=True)
            
            # Get label mappings
            import json
            import os
            label_path = os.path.join(self.model_path, 'label_mappings.json')
            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    mappings = json.load(f)
                    self.id_to_label = {int(k): v for k, v in mappings['id2label'].items()}
                    self.label_to_id = mappings['label2id']
            else:
                self.id_to_label = self.model.config.id2label
                self.label_to_id = self.model.config.label2id
            
            self.is_loaded = True
            self.deberta_available = True
            logger.info(f"✅ DeBERTa model loaded with {len(self.id_to_label)} labels")
            
        except Exception as e:
            logger.error(f"❌ Failed to load DeBERTa model: {e}")
            self.is_loaded = False
            self.deberta_available = False
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens for given text."""
        if not self.tokenizer:
            return 0
        return len(self.tokenizer.encode(text, add_special_tokens=False))
    
    def _split_into_chunks(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Split text into chunks with overlap.
        
        Returns:
            List of (chunk_text, start_char, end_char) tuples
        """
        if not text:
            return []
        
        # Count total tokens
        total_tokens = self._count_tokens(text)
        logger.info(f"📊 Text: {len(text)} chars = {total_tokens} tokens")
        
        # If within limit, return as single chunk
        if total_tokens <= self.max_tokens:
            logger.info(f"✅ Text within limit ({total_tokens} ≤ {self.max_tokens})")
            return [(text, 0, len(text))]
        
        # Calculate chunk size in characters (approximate)
        chars_per_token = len(text) / total_tokens
        max_chars = int(self.max_tokens * chars_per_token * 0.9)  # 90% to be safe
        overlap_chars = int(self.chunk_overlap * chars_per_token)
        
        logger.info(f"🔪 Splitting into chunks: max_chars={max_chars}, overlap={overlap_chars}")
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + max_chars, len(text))
            
            # Try to break at sentence or line boundary
            if end < len(text):
                # Look for sentence end
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + max_chars * 0.7:  # At least 70% of max
                    end = sentence_end + 1
                else:
                    # Look for line break
                    line_end = text.rfind('\n', start, end)
                    if line_end > start + max_chars * 0.5:  # At least 50% of max
                        end = line_end + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_tokens = self._count_tokens(chunk_text)
                logger.info(f"   Chunk {len(chunks)+1}: {len(chunk_text)} chars = {chunk_tokens} tokens")
                chunks.append((chunk_text, start, end))
            
            start = end - overlap_chars if end < len(text) else end
        
        logger.info(f"✅ Split into {len(chunks)} chunks")
        return chunks
    
    def _parse_chunk(self, chunk_text: str) -> Dict[str, List]:
        """Parse a single chunk with DeBERTa."""
        try:
            # Use HuggingFace pipeline for better aggregation
            from transformers import pipeline
            ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple",
                device=-1  # CPU
            )
            
            predictions = ner_pipeline(chunk_text)
            
            # Convert to entity dictionary
            entities = {label: [] for label in self.label_to_id.keys()}
            
            for pred in predictions:
                entity_type = pred['entity_group']
                entity_text = pred['word'].strip()
                
                if entity_type in entities and entity_text:
                    entities[entity_type].append(entity_text)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error parsing chunk: {e}")
            return {}
    
    def _merge_chunk_entities(self, chunk_results: List[Dict[str, List]]) -> Dict[str, List]:
        """Merge entities from multiple chunks, removing duplicates."""
        merged = {}
        
        # Get all entity types
        all_types = set()
        for chunk in chunk_results:
            all_types.update(chunk.keys())
        
        # Merge each entity type
        for entity_type in all_types:
            seen = set()
            merged_list = []
            
            for chunk in chunk_results:
                for entity in chunk.get(entity_type, []):
                    if entity not in seen:
                        seen.add(entity)
                        merged_list.append(entity)
            
            if merged_list:
                merged[entity_type] = merged_list
        
        return merged
    
    def parse_section_safe(self, text: str, section_type: str) -> Dict[str, List]:
        """
        Parse a section with token limit protection and chunking.
        
        Args:
            text: Section text
            section_type: 'experience' or 'education'
            
        Returns:
            Dictionary of extracted entities
        """
        if not text or not text.strip():
            logger.warning(f"Empty {section_type} section")
            return {}
        
        logger.info(f"🔍 Parsing {section_type} section: {len(text)} chars")
        
        # Split into chunks
        chunks = self._split_into_chunks(text)
        
        if not chunks:
            logger.warning(f"No chunks created for {section_type}")
            return {}
        
        # Parse each chunk
        chunk_results = []
        for i, (chunk_text, start, end) in enumerate(chunks):
            logger.info(f"   Processing chunk {i+1}/{len(chunks)}")
            chunk_entities = self._parse_chunk(chunk_text)
            chunk_results.append(chunk_entities)
        
        # Merge results
        merged_entities = self._merge_chunk_entities(chunk_results)
        
        # Log results
        entity_summary = {k: len(v) for k, v in merged_entities.items() if v}
        logger.info(f"✅ {section_type} extracted: {entity_summary}")
        
        return merged_entities
    
    def parse_separated_sections(self, experience_text: str, education_text: str) -> Dict[str, Any]:
        """
        Parse experience and education sections separately to prevent cross-section leakage.
        
        Args:
            experience_text: Work experience section text
            education_text: Education section text
            
        Returns:
            Dictionary with separated results
        """
        logger.info("🎯 Parsing sections separately to prevent cross-section leakage")
        
        results = {
            'work_experience': [],
            'education': [],
            'companies': [],
            'job_titles': [],
            'locations': [],
            'degrees': [],
            'institutions': [],
            'fields_of_study': []
        }
        
        # Parse experience section
        if experience_text and experience_text.strip():
            exp_entities = self.parse_section_safe(experience_text, 'experience')
            
            # Extract experience entries
            if exp_entities:
                from .deberta_experience_builder import DeBERTaExperienceBuilder
                builder = DeBERTaExperienceBuilder()
                
                # Add position data for experience builder
                exp_entities['_original_text'] = experience_text
                
                experiences = builder.build_experiences_from_entities(exp_entities, experience_text)
                results['work_experience'] = experiences
                results['companies'] = [exp.get('company_name', '') for exp in experiences]
                results['job_titles'] = [exp.get('job_title', '') for exp in experiences]
                results['locations'] = [exp.get('location', '') for exp in experiences]
        
        # Parse education section SEPARATELY
        if education_text and education_text.strip():
            edu_entities = self.parse_section_safe(education_text, 'education')
            
            # Extract education entries
            if edu_entities:
                degrees = edu_entities.get('DEGREE', [])
                institutions = edu_entities.get('INSTITUTION', [])
                fields = edu_entities.get('FIELD', [])
                years = edu_entities.get('EDU_YEAR_END', [])
                
                # Build education entries
                max_edu = max(len(degrees), len(institutions))
                for i in range(max_edu):
                    edu = {
                        'institution': institutions[i] if i < len(institutions) else '',
                        'degree': degrees[i] if i < len(degrees) else '',
                        'field_of_study': fields[i] if i < len(fields) else None,
                        'end_year': years[i] if i < len(years) else None,
                        'source': 'deberta_ner'
                    }
                    if edu['institution'] or edu['degree']:
                        results['education'].append(edu)
                
                results['degrees'] = degrees
                results['institutions'] = institutions
                results['fields_of_study'] = fields
        
        # Log final results
        logger.info(f"📊 Final results: {len(results['work_experience'])} experiences, {len(results['education'])} education")
        
        return results
