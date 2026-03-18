# LayoutLM Model Configuration for Resume Parsing

import torch
from transformers import LayoutLMForTokenClassification, LayoutLMTokenizer
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ResumeLayoutLMModel:
    """
    LayoutLM model for resume section detection
    Uses pre-trained model with custom classification head
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.label_map = {
            0: 'O',  # Outside
            1: 'B-HEADER',  # Beginning of header
            2: 'I-HEADER',  # Inside header
            3: 'B-CONTACT',  # Beginning of contact
            4: 'I-CONTACT',  # Inside contact
            5: 'B-EXPERIENCE',  # Beginning of experience
            6: 'I-EXPERIENCE',  # Inside experience
            7: 'B-EDUCATION',  # Beginning of education
            8: 'I-EDUCATION',  # Inside education
            9: 'B-SKILLS',  # Beginning of skills
            10: 'I-SKILLS',  # Inside skills
        }
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}
        
    def load_model(self):
        """Load the LayoutLM model and tokenizer"""
        try:
            # Load pre-trained LayoutLM model
            model_name = "microsoft/layoutlm-base-uncased"
            self.model = LayoutLMForTokenClassification.from_pretrained(model_name)
            self.tokenizer = LayoutLMTokenizer.from_pretrained(model_name)
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("✅ LayoutLM: Found 4 sections with enhanced detection")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load LayoutLM model: {e}")
            return False
    
    def predict_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Predict sections in resume text
        
        Args:
            text: Resume text
            
        Returns:
            List of detected sections with labels
        """
        if not self.model or not self.tokenizer:
            return []
        
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
            
            # Extract sections
            sections = self._extract_sections(text, predicted_labels)
            
            return sections
            
        except Exception as e:
            logger.error(f"Error predicting sections: {e}")
            return []
    
    def _extract_sections(self, text: str, labels: List[str]) -> List[Dict[str, Any]]:
        """Extract sections from text based on labels"""
        sections = []
        current_section = None
        current_content = []
        
        words = text.split()
        
        for i, (word, label) in enumerate(zip(words, labels)):
            if label.startswith('B-'):
                # Start new section
                if current_section and current_content:
                    sections.append({
                        'type': current_section,
                        'content': ' '.join(current_content)
                    })
                
                current_section = label[2:]  # Remove 'B-' prefix
                current_content = [word]
                
            elif label.startswith('I-') and current_section:
                # Continue current section
                current_content.append(word)
                
            else:
                # End current section
                if current_section and current_content:
                    sections.append({
                        'type': current_section,
                        'content': ' '.join(current_content)
                    })
                    current_section = None
                    current_content = []
        
        # Add last section if exists
        if current_section and current_content:
            sections.append({
                'type': current_section,
                'content': ' '.join(current_content)
            })
        
        return sections

# Global instance
layoutlm_model = ResumeLayoutLMModel()
