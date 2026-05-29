#!/usr/bin/env python3
"""
Hybrid NER Post-Processor - Combines DeBERTa NER with rule-based extraction.

This module improves DeBERTa predictions by:
1. Filtering out common first names misclassified as COMPANY
2. Adding rule-based PERSON_NAME extraction using spaCy
3. Validating and merging results to prevent conflicts
"""

import logging
import re
from typing import Dict, List, Any, Set
import spacy

logger = logging.getLogger(__name__)


class HybridNERPostProcessor:
    """
    Post-processes DeBERTa NER results with rule-based corrections.
    """
    
    # Common Indian first names that get misclassified as COMPANY
    INDIAN_FIRST_NAMES = {
        'rahul', 'priya', 'amit', 'anjali', 'vikram', 'neha', 'karan', 'pooja',
        'ravi', 'deepak', 'sanjay', 'kavita', 'suresh', 'meera', 'anil', 'divya',
        'rajesh', 'sneha', 'manoj', 'swati', 'nitin', 'preeti', 'ashok', 'rekha',
        'vishal', 'nisha', 'sachin', 'anita', 'rohan', 'simran', 'arjun', 'isha',
        'kunal', 'tanvi', 'gaurav', 'shruti', 'mohit', 'pallavi', 'varun', 'megha'
    }
    
    # Common Western first names
    WESTERN_FIRST_NAMES = {
        'john', 'sarah', 'michael', 'emily', 'david', 'jessica', 'james', 'lisa',
        'robert', 'jennifer', 'william', 'linda', 'richard', 'patricia', 'thomas',
        'mary', 'charles', 'barbara', 'daniel', 'susan', 'matthew', 'karen',
        'christopher', 'nancy', 'andrew', 'betty', 'joseph', 'helen', 'mark', 'sandra'
    }
    
    ALL_FIRST_NAMES = INDIAN_FIRST_NAMES | WESTERN_FIRST_NAMES
    
    # Common last names (for validation)
    COMMON_LAST_NAMES = {
        'kumar', 'singh', 'sharma', 'verma', 'gupta', 'reddy', 'patel', 'mehta',
        'nair', 'desai', 'joshi', 'iyer', 'rao', 'krishnan', 'menon', 'pillai',
        'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller',
        'davis', 'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez'
    }
    
    def __init__(self):
        """Initialize the hybrid post-processor."""
        self.logger = logging.getLogger(__name__)
        self.nlp = None
        self._load_spacy()
    
    def _load_spacy(self):
        """Load spaCy model for person name extraction."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info("✅ spaCy model loaded for person name extraction")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load spaCy model: {e}")
            self.logger.warning("   Person name extraction will be limited")
            self.nlp = None
    
    def process(self, entities: Dict[str, List[str]], text: str) -> Dict[str, List[str]]:
        """
        Post-process DeBERTa entities with hybrid corrections.
        
        Args:
            entities: Dictionary of entity types to lists of extracted values
            text: Original text for context
            
        Returns:
            Corrected entities dictionary
        """
        self.logger.info("🔧 Running hybrid NER post-processing...")
        
        # Step 1: Filter out misclassified first names from COMPANY
        removed_companies = []
        entities, removed_companies = self._filter_first_names_from_companies(entities)
        
        # Step 1b: Update _positions array to remove filtered companies
        if '_positions' in entities and removed_companies:
            original_positions = entities['_positions']
            filtered_positions = [
                pos for pos in original_positions 
                if not (pos['type'] == 'COMPANY' and pos['text'] in removed_companies)
            ]
            entities['_positions'] = filtered_positions
            self.logger.debug(f"   Updated _positions: {len(original_positions)} -> {len(filtered_positions)}")
        
        # Step 2: Extract person names using spaCy (rule-based)
        if self.nlp:
            person_names = self._extract_person_names_spacy(text)
            if person_names:
                entities['PERSON_NAME'] = person_names
                self.logger.info(f"✅ Added {len(person_names)} person names via spaCy")
        
        # Step 3: Validate and clean entities
        entities = self._validate_entities(entities)
        
        self.logger.info("✅ Hybrid post-processing complete")
        return entities
    
    def _filter_first_names_from_companies(self, entities: Dict[str, List[str]]) -> tuple:
        """
        Remove common first names that were misclassified as COMPANY.
        
        Args:
            entities: Dictionary of entity types to lists
            
        Returns:
            Tuple of (filtered entities, list of removed company names)
        """
        if 'COMPANY' not in entities:
            return entities, []
        
        original_companies = entities['COMPANY']
        filtered_companies = []
        removed = []
        
        for company in original_companies:
            company_lower = company.lower().strip()
            
            # Check if it's a single word that matches a first name
            words = company_lower.split()
            if len(words) == 1 and words[0] in self.ALL_FIRST_NAMES:
                removed.append(company)
                self.logger.debug(f"   Filtered '{company}' from COMPANY (first name)")
            else:
                filtered_companies.append(company)
        
        if removed:
            self.logger.info(f"🧹 Removed {len(removed)} first names from COMPANY: {removed}")
        
        entities['COMPANY'] = filtered_companies
        return entities, removed
    
    def _extract_person_names_spacy(self, text: str) -> List[str]:
        """
        Extract person names using spaCy NER (rule-based).
        
        Args:
            text: Text to extract from
            
        Returns:
            List of person names
        """
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            person_names = []
            
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    
                    # Validate it looks like a real name
                    if self._is_valid_person_name(name):
                        person_names.append(name)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_names = []
            for name in person_names:
                name_lower = name.lower()
                if name_lower not in seen:
                    seen.add(name_lower)
                    unique_names.append(name)
            
            return unique_names
            
        except Exception as e:
            self.logger.warning(f"⚠️ spaCy person name extraction failed: {e}")
            return []
    
    def _is_valid_person_name(self, name: str) -> bool:
        """
        Validate if a string looks like a real person name.
        
        Args:
            name: Name to validate
            
        Returns:
            True if valid person name
        """
        # Must be 2-50 characters
        if len(name) < 2 or len(name) > 50:
            return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', name):
            return False
        
        # Should not contain numbers (except suffixes like "Jr.", "III")
        if re.search(r'\d{2,}', name):
            return False
        
        # Should not be all uppercase (likely an acronym)
        if name.isupper() and len(name) > 3:
            return False
        
        # Should have 2-4 words (First Last, First Middle Last, etc.)
        words = name.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        # First word should look like a first name or last name
        first_word = words[0].lower()
        last_word = words[-1].lower()
        
        # At least one word should be a known first/last name
        if (first_word in self.ALL_FIRST_NAMES or 
            last_word in self.COMMON_LAST_NAMES or
            first_word in self.COMMON_LAST_NAMES):
            return True
        
        # If not in our dictionaries, check if it has proper capitalization
        # (Title Case is typical for names)
        if all(word[0].isupper() for word in words if word):
            return True
        
        return False
    
    def _validate_entities(self, entities: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Validate and clean all entities.
        
        Args:
            entities: Dictionary of entity types to lists
            
        Returns:
            Validated entities
        """
        validated = {}
        
        for entity_type, entity_list in entities.items():
            # Skip positions metadata list from validation/cleaning
            if entity_type == '_positions':
                validated[entity_type] = entity_list
                continue
                
            if not entity_list:
                continue
            
            # Remove empty strings and duplicates
            cleaned = []
            seen = set()
            
            for entity in entity_list:
                if not entity or not entity.strip():
                    continue
                
                entity_clean = entity.strip()
                entity_lower = entity_clean.lower()
                
                # Skip if already seen (case-insensitive)
                if entity_lower in seen:
                    continue
                
                # Additional validation based on entity type
                if entity_type == 'COMPANY':
                    # Companies should be at least 2 characters
                    if len(entity_clean) < 2:
                        continue
                    # Should not be a single common word
                    if entity_lower in {'the', 'and', 'or', 'in', 'at', 'to', 'from'}:
                        continue
                
                elif entity_type == 'PERSON_NAME':
                    # Person names should have at least 2 words
                    if len(entity_clean.split()) < 2:
                        continue
                
                elif entity_type in ['DATE_START', 'DATE_END', 'EDU_YEAR_START', 'EDU_YEAR_END']:
                    # Dates should contain numbers or month names
                    if not re.search(r'\d|january|february|march|april|may|june|july|august|september|october|november|december|present|current', entity_lower):
                        continue
                
                cleaned.append(entity_clean)
                seen.add(entity_lower)
            
            if cleaned:
                validated[entity_type] = cleaned
        
        return validated


def apply_hybrid_postprocessing(entities: Dict[str, List[str]], text: str) -> Dict[str, List[str]]:
    """
    Convenience function to apply hybrid post-processing.
    
    Args:
        entities: DeBERTa extracted entities
        text: Original text
        
    Returns:
        Post-processed entities
    """
    processor = HybridNERPostProcessor()
    return processor.process(entities, text)
