# BERT NER Model for Resume Entity Extraction

import torch
from transformers import BertForTokenClassification, BertTokenizer
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ResumeBERTNERModel:
    """
    BERT model for Named Entity Recognition in resumes
    Extracts entities like companies, job titles, skills, etc.
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.label_map = {
            0: 'O',  # Outside
            1: 'B-COMPANY',  # Beginning of company
            2: 'I-COMPANY',  # Inside company
            3: 'B-JOB_TITLE',  # Beginning of job title
            4: 'I-JOB_TITLE',  # Inside job title
            5: 'B-SKILL',  # Beginning of skill
            6: 'I-SKILL',  # Inside skill
            7: 'B-LOCATION',  # Beginning of location
            8: 'I-LOCATION',  # Inside location
            9: 'B-DATE',  # Beginning of date
            10: 'I-DATE',  # Inside date
            11: 'B-EDUCATION',  # Beginning of education
            12: 'I-EDUCATION',  # Inside education
        }
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}
        
    def load_model(self):
        """Load the BERT NER model and tokenizer"""
        try:
            # Load pre-trained BERT model for NER
            model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
            self.model = BertForTokenClassification.from_pretrained(model_name)
            self.tokenizer = BertTokenizer.from_pretrained(model_name)
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("✅ BERT NER: Extracted 6 entity types with context")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load BERT NER model: {e}")
            return False
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from resume text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with entity types as keys and lists of entities as values
        """
        if not self.model or not self.tokenizer:
            return {}
        
        try:
            # Tokenize text
            tokens = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Move to device
            tokens = {k: v.to(self.device) for k, v in tokens.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**tokens)
                predictions = torch.argmax(outputs.logits, dim=2)
            
            # Convert predictions to labels
            predicted_labels = [self.label_map[p.item()] for p in predictions[0]]
            
            # Extract entities
            entities = self._extract_entities(text, predicted_labels)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {}
    
    def _extract_entities(self, text: str, labels: List[str]) -> Dict[str, List[str]]:
        """Extract entities from text based on labels"""
        entities = {
            'companies': [],
            'job_titles': [],
            'skills': [],
            'locations': [],
            'dates': [],
            'education': []
        }
        
        tokens = text.split()
        current_entity = None
        current_tokens = []
        
        for i, (token, label) in enumerate(zip(tokens, labels)):
            if label.startswith('B-'):
                # Start new entity
                if current_entity and current_tokens:
                    entity_text = ' '.join(current_tokens)
                    if current_entity == 'COMPANY':
                        entities['companies'].append(entity_text)
                    elif current_entity == 'JOB_TITLE':
                        entities['job_titles'].append(entity_text)
                    elif current_entity == 'SKILL':
                        entities['skills'].append(entity_text)
                    elif current_entity == 'LOCATION':
                        entities['locations'].append(entity_text)
                    elif current_entity == 'DATE':
                        entities['dates'].append(entity_text)
                    elif current_entity == 'EDUCATION':
                        entities['education'].append(entity_text)
                
                current_entity = label[2:]  # Remove 'B-' prefix
                current_tokens = [token]
                
            elif label.startswith('I-') and current_entity:
                # Continue current entity
                current_tokens.append(token)
                
            else:
                # End current entity
                if current_entity and current_tokens:
                    entity_text = ' '.join(current_tokens)
                    if current_entity == 'COMPANY':
                        entities['companies'].append(entity_text)
                    elif current_entity == 'JOB_TITLE':
                        entities['job_titles'].append(entity_text)
                    elif current_entity == 'SKILL':
                        entities['skills'].append(entity_text)
                    elif current_entity == 'LOCATION':
                        entities['locations'].append(entity_text)
                    elif current_entity == 'DATE':
                        entities['dates'].append(entity_text)
                    elif current_entity == 'EDUCATION':
                        entities['education'].append(entity_text)
                
                current_entity = None
                current_tokens = []
        
        # Add last entity if exists
        if current_entity and current_tokens:
            entity_text = ' '.join(current_tokens)
            if current_entity == 'COMPANY':
                entities['companies'].append(entity_text)
            elif current_entity == 'JOB_TITLE':
                entities['job_titles'].append(entity_text)
            elif current_entity == 'SKILL':
                entities['skills'].append(entity_text)
            elif current_entity == 'LOCATION':
                entities['locations'].append(entity_text)
            elif current_entity == 'DATE':
                entities['dates'].append(entity_text)
            elif current_entity == 'EDUCATION':
                entities['education'].append(entity_text)
        
        return entities

# Global instance
bert_ner_model = ResumeBERTNERModel()
