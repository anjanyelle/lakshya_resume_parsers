"""
AI-powered Named Entity Recognition parser using HuggingFace models.
Supports fine-tuned DeBERTa-v3 for resume-specific entities with fallback to bert-base-NER.
Extracts names, organizations, job titles, skills, education, dates, and locations from resume text.
"""

import torch
import os
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import logging
from typing import Dict, List, Optional, Tuple
import re
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

# Model paths
FINE_TUNED_MODEL_PATH = './models/resume-ner-deberta'
BASE_MODEL_NAME = 'dslim/bert-base-NER'

# Entity labels for fine-tuned model
FINE_TUNED_LABELS = ['O', 'B-NAME', 'I-NAME', 'B-ORG', 'I-ORG', 'B-TITLE', 'I-TITLE',
                    'B-SKILL', 'I-SKILL', 'B-EDU', 'I-EDU', 'B-DATE', 'I-DATE', 'B-LOC', 'I-LOC']

class AINamedEntityParser:
    """
    AI-powered Named Entity Recognition parser.
    Uses fine-tuned DeBERTa-v3 for resume-specific entities with fallback to bert-base-NER.
    Handles long texts through chunking and provides confidence-based filtering.
    """
    
    def __init__(self):
        """Initialize the NER model and pipeline."""
        # Check if fine-tuned model exists
        if os.path.exists(FINE_TUNED_MODEL_PATH):
            self.model_name = FINE_TUNED_MODEL_PATH
            self.model_type = 'fine-tuned-deberta'
            logger.info('Loading fine-tuned DeBERTa-v3 model — higher accuracy')
        else:
            self.model_name = BASE_MODEL_NAME
            self.model_type = 'base-bert'
            logger.info('Fine-tuned model not found, using bert-base-NER')
        
        try:
            logger.info(f"Loading NER model: {self.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)
            
            # Determine device (GPU if available, otherwise CPU)
            device = 0 if torch.cuda.is_available() else -1
            logger.info(f"Using device: {'GPU' if device == 0 else 'CPU'}")
            
            # Create NER pipeline with aggregation strategy
            self.ner_pipeline = pipeline(
                task='ner',
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy='max',  # Merges B-/I- sub-tokens automatically
                device=device
            )
            
            # Set label mapping based on model type
            if self.model_type == 'fine-tuned-deberta':
                self.setup_fine_tuned_labels()
            else:
                self.setup_base_labels()
            
            logger.info(f"NER model loaded successfully (type: {self.model_type})")
            
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
            raise
    
    def setup_fine_tuned_labels(self):
        """Setup label mapping for fine-tuned DeBERTa-v3 model."""
        self.entity_mapping = {
            'NAME': 'names',
            'ORG': 'organizations', 
            'TITLE': 'job_titles',
            'SKILL': 'skills',
            'EDU': 'education',
            'DATE': 'dates',
            'LOC': 'locations'
        }
        self.supported_entities = list(self.entity_mapping.keys())
        
    def setup_base_labels(self):
        """Setup label mapping for base bert-base-NER model."""
        self.entity_mapping = {
            'PER': 'names',
            'ORG': 'organizations',
            'LOC': 'locations',
            'MISC': 'miscellaneous'
        }
        self.supported_entities = list(self.entity_mapping.keys())
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the currently loaded model."""
        return {
            'model_name': self.model_name,
            'model_type': self.model_type,
            'supported_entities': self.supported_entities
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, any]]]:
        """
        Extract named entities from text using AI NER model.
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            Dictionary with categorized entities based on model type:
            
            Fine-tuned DeBERTa-v3:
            {
                'names': [{'value': str, 'score': float}, ...],
                'organizations': [{'value': str, 'score': float}, ...],
                'job_titles': [{'value': str, 'score': float}, ...],
                'skills': [{'value': str, 'score': float}, ...],
                'education': [{'value': str, 'score': float}, ...],
                'dates': [{'value': str, 'score': float}, ...],
                'locations': [{'value': str, 'score': float}, ...]
            }
            
            Base bert-base-NER:
            {
                'names': [{'value': str, 'score': float}, ...],
                'organizations': [{'value': str, 'score': float}, ...],
                'locations': [{'value': str, 'score': float}, ...],
                'miscellaneous': [{'value': str, 'score': float}, ...]
            }
        """
        try:
            if not text or not text.strip():
                # Return empty structure based on model type
                if self.model_type == 'fine-tuned-deberta':
                    return {
                        'names': [], 'organizations': [], 'job_titles': [], 
                        'skills': [], 'education': [], 'dates': [], 'locations': []
                    }
                else:
                    return {'names': [], 'organizations': [], 'locations': [], 'miscellaneous': []}
            
            # Handle long texts by chunking
            chunks = self._chunk_text(text, max_words=300, overlap=50)
            
            # Collect all entities from all chunks
            all_entities = []
            
            for i, chunk in enumerate(chunks):
                logger.debug(f"Processing chunk {i+1}/{len(chunks)}")
                entities = self.ner_pipeline(chunk)
                all_entities.extend(entities)
            
            # Initialize categorized entities based on model type
            if self.model_type == 'fine-tuned-deberta':
                categorized_entities = {
                    'names': [],
                    'organizations': [],
                    'job_titles': [],
                    'skills': [],
                    'education': [],
                    'dates': [],
                    'locations': []
                }
            else:
                categorized_entities = {
                    'names': [],
                    'organizations': [],
                    'locations': [],
                    'miscellaneous': []
                }
            
            # Group and deduplicate entities
            entity_groups = defaultdict(list)
            
            for entity in all_entities:
                entity_group = entity.get('entity_group', '').upper()
                entity_value = entity.get('word', '').strip()
                entity_score = entity.get('score', 0.0)
                
                if entity_value and len(entity_value) > 1:  # Filter out single characters
                    entity_groups[entity_group].append({
                        'value': entity_value,
                        'score': entity_score
                    })
            
            # Map entity groups to our categories and deduplicate
            for ner_label, category in self.entity_mapping.items():
                if ner_label in entity_groups:
                    # Deduplicate by value (keep highest score)
                    deduplicated = self._deduplicate_entities(entity_groups[ner_label])
                    categorized_entities[category] = deduplicated
            
            # Log extraction summary
            total_entities = sum(len(entities) for entities in categorized_entities.values())
            
            if self.model_type == 'fine-tuned-deberta':
                logger.info(f"Extracted {total_entities} entities with DeBERTa-v3: "
                           f"names={len(categorized_entities['names'])}, "
                           f"organizations={len(categorized_entities['organizations'])}, "
                           f"job_titles={len(categorized_entities['job_titles'])}, "
                           f"skills={len(categorized_entities['skills'])}, "
                           f"education={len(categorized_entities['education'])}, "
                           f"dates={len(categorized_entities['dates'])}, "
                           f"locations={len(categorized_entities['locations'])}")
            else:
                logger.info(f"Extracted {total_entities} entities with bert-base-NER: "
                           f"names={len(categorized_entities['names'])}, "
                           f"organizations={len(categorized_entities['organizations'])}, "
                           f"locations={len(categorized_entities['locations'])}, "
                           f"miscellaneous={len(categorized_entities['miscellaneous'])}")
            
            return categorized_entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            # Return empty structure based on model type
            if self.model_type == 'fine-tuned-deberta':
                return {
                    'names': [], 'organizations': [], 'job_titles': [], 
                    'skills': [], 'education': [], 'dates': [], 'locations': []
                }
            else:
                return {'names': [], 'organizations': [], 'locations': [], 'miscellaneous': []}
    
    def _chunk_text(self, text: str, max_words: int, overlap: int) -> List[str]:
        """
        Split text into overlapping chunks for processing.
        
        Args:
            text: Input text to chunk
            max_words: Maximum words per chunk
            overlap: Number of overlapping words between chunks
            
        Returns:
            List of text chunks
        """
        try:
            # Split text into words
            words = text.split()
            
            if len(words) <= max_words:
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(words):
                # Calculate end index for this chunk
                end = min(start + max_words, len(words))
                
                # Extract chunk
                chunk_words = words[start:end]
                chunk = ' '.join(chunk_words)
                chunks.append(chunk)
                
                # Move start position with overlap
                start = end - overlap
                
                # Prevent infinite loop
                if start >= len(words):
                    break
            
            logger.debug(f"Split text into {len(chunks)} chunks (max_words={max_words}, overlap={overlap})")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            return [text]
    
    def _deduplicate_entities(self, entities: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Deduplicate entities by value, keeping the highest scoring one.
        
        Args:
            entities: List of entity dictionaries with 'value' and 'score'
            
        Returns:
            Deduplicated list of entities
        """
        try:
            # Group by normalized value
            value_groups = {}
            
            for entity in entities:
                value = entity['value'].strip().lower()
                score = entity['score']
                
                if value not in value_groups or score > value_groups[value]['score']:
                    value_groups[value] = {
                        'value': entity['value'].strip(),  # Keep original case
                        'score': score
                    }
            
            # Convert back to list and sort by score (descending)
            deduplicated = list(value_groups.values())
            deduplicated.sort(key=lambda x: x['score'], reverse=True)
            
            return deduplicated
            
        except Exception as e:
            logger.error(f"Error deduplicating entities: {e}")
            return entities
    
    def get_top_person(self, entities: Optional[Dict[str, List[Dict[str, any]]]] = None, text: Optional[str] = None) -> Optional[str]:
        """
        Get the highest-scoring person entity (likely the candidate name).
        
        Args:
            entities: Pre-extracted entities (optional)
            text: Text to extract from if entities not provided
            
        Returns:
            Highest scoring person name or None
        """
        try:
            # Extract entities if not provided
            if entities is None:
                if text is None:
                    logger.warning("No entities or text provided for get_top_person")
                    return None
                entities = self.extract_entities(text)
            
            persons = entities.get('persons', [])
            
            if not persons:
                return None
            
            # Return the highest scoring person
            top_person = max(persons, key=lambda x: x.get('score', 0))
            
            logger.info(f"Top person found: '{top_person['value']}' (score: {top_person['score']:.3f})")
            return top_person['value']
            
        except Exception as e:
            logger.error(f"Error getting top person: {e}")
            return None
    
    def get_organizations(self, entities: Optional[Dict[str, List[Dict[str, any]]]] = None, text: Optional[str] = None, 
                         confidence_threshold: float = 0.85) -> List[str]:
        """
        Get all organization entities above confidence threshold.
        
        Args:
            entities: Pre-extracted entities (optional)
            text: Text to extract from if entities not provided
            confidence_threshold: Minimum confidence score (default: 0.85)
            
        Returns:
            List of organization names above threshold
        """
        try:
            # Extract entities if not provided
            if entities is None:
                if text is None:
                    logger.warning("No entities or text provided for get_organizations")
                    return []
                entities = self.extract_entities(text)
            
            organizations = entities.get('organizations', [])
            
            # Filter by confidence threshold
            filtered_orgs = [
                org['value'] for org in organizations 
                if org.get('score', 0) >= confidence_threshold
            ]
            
            logger.info(f"Found {len(filtered_orgs)} organizations above {confidence_threshold} threshold")
            return filtered_orgs
            
        except Exception as e:
            logger.error(f"Error getting organizations: {e}")
            return []
    
    def get_locations(self, entities: Optional[Dict[str, List[Dict[str, any]]]] = None, text: Optional[str] = None,
                     confidence_threshold: float = 0.80) -> List[str]:
        """
        Get all location entities above confidence threshold.
        
        Args:
            entities: Pre-extracted entities (optional)
            text: Text to extract from if entities not provided
            confidence_threshold: Minimum confidence score (default: 0.80)
            
        Returns:
            List of location names above threshold
        """
        try:
            # Extract entities if not provided
            if entities is None:
                if text is None:
                    logger.warning("No entities or text provided for get_locations")
                    return []
                entities = self.extract_entities(text)
            
            locations = entities.get('locations', [])
            
            # Filter by confidence threshold
            filtered_locations = [
                loc['value'] for loc in locations 
                if loc.get('score', 0) >= confidence_threshold
            ]
            
            logger.info(f"Found {len(filtered_locations)} locations above {confidence_threshold} threshold")
            return filtered_locations
            
        except Exception as e:
            logger.error(f"Error getting locations: {e}")
            return []
    
    def get_misc_entities(self, entities: Optional[Dict[str, List[Dict[str, any]]]] = None, text: Optional[str] = None,
                         confidence_threshold: float = 0.75) -> List[str]:
        """
        Get all miscellaneous entities above confidence threshold.
        
        Args:
            entities: Pre-extracted entities (optional)
            text: Text to extract from if entities not provided
            confidence_threshold: Minimum confidence score (default: 0.75)
            
        Returns:
            List of miscellaneous entities above threshold
        """
        try:
            # Extract entities if not provided
            if entities is None:
                if text is None:
                    logger.warning("No entities or text provided for get_misc_entities")
                    return []
                entities = self.extract_entities(text)
            
            misc = entities.get('misc', [])
            
            # Filter by confidence threshold
            filtered_misc = [
                item['value'] for item in misc 
                if item.get('score', 0) >= confidence_threshold
            ]
            
            logger.info(f"Found {len(filtered_misc)} miscellaneous entities above {confidence_threshold} threshold")
            return filtered_misc
            
        except Exception as e:
            logger.error(f"Error getting miscellaneous entities: {e}")
            return []
    
    def get_entity_summary(self, text: str) -> Dict[str, any]:
        """
        Get a comprehensive summary of entities in the text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with entity summary including counts and top entities
        """
        try:
            entities = self.extract_entities(text)
            
            summary = {
                'total_entities': sum(len(cat_entities) for cat_entities in entities.values()),
                'persons_count': len(entities['persons']),
                'organizations_count': len(entities['organizations']),
                'locations_count': len(entities['locations']),
                'misc_count': len(entities['misc']),
                'top_person': self.get_top_person(entities),
                'top_organizations': self.get_organizations(entities)[:5],  # Top 5
                'top_locations': self.get_locations(entities)[:3],  # Top 3
                'all_entities': entities
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting entity summary: {e}")
            return {
                'total_entities': 0,
                'persons_count': 0,
                'organizations_count': 0,
                'locations_count': 0,
                'misc_count': 0,
                'top_person': None,
                'top_organizations': [],
                'top_locations': [],
                'all_entities': {'persons': [], 'organizations': [], 'locations': [], 'misc': []}
            }
    
    def is_model_available(self) -> bool:
        """
        Check if the NER model is properly loaded and available.
        
        Returns:
            True if model is available, False otherwise
        """
        try:
            # Test with a simple text
            test_result = self.ner_pipeline("John Doe")
            return test_result is not None
        except Exception as e:
            logger.error(f"Model availability check failed: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Sample resume text for testing
    sample_text = """
    John Michael Doe
    Senior Software Engineer at Google
    
    EDUCATION
    Stanford University - Master of Science in Computer Science
    University of California, Berkeley - Bachelor of Science
    
    EXPERIENCE
    Senior Software Engineer
    Microsoft Corporation
    Redmond, Washington
    
    Software Developer
    Apple Inc.
    Cupertino, California
    """
    
    try:
        # Initialize the parser
        parser = AINamedEntityParser()
        
        # Check model availability
        if parser.is_model_available():
            print("✅ NER model is available and ready")
            
            # Extract entities
            entities = parser.extract_entities(sample_text)
            
            print("\n📊 Extracted Entities:")
            print(f"Persons: {[p['value'] for p in entities['persons']]}")
            print(f"Organizations: {[o['value'] for o in entities['organizations']]}")
            print(f"Locations: {[l['value'] for l in entities['locations']]}")
            print(f"Miscellaneous: {[m['value'] for m in entities['misc']]}")
            
            # Get top person
            top_person = parser.get_top_person(entities)
            print(f"\n👤 Top Person: {top_person}")
            
            # Get organizations with high confidence
            orgs = parser.get_organizations(entities)
            print(f"🏢 High-Confidence Organizations: {orgs}")
            
            # Get comprehensive summary
            summary = parser.get_entity_summary(sample_text)
            print(f"\n📈 Entity Summary:")
            print(f"Total Entities: {summary['total_entities']}")
            print(f"Top Person: {summary['top_person']}")
            print(f"Top Organizations: {summary['top_organizations']}")
            
        else:
            print("❌ NER model is not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: First run will download the model (~400MB). Subsequent runs use cached model.")
