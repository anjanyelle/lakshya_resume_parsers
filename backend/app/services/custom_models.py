"""
Custom trained models for resume parsing
"""

import os
import joblib
import spacy
from typing import Dict, List, Any, Optional

class CustomModels:
    """Custom trained models for resume parsing"""
    
    def __init__(self):
        self.ner_model = None
        self.quality_classifier = None
        self.vectorizer = None
        self._load_models()
    
    def _load_models(self):
        """Load trained models"""
        try:
            # Load section-specific NER models
            self.section_models = {}
            
            section_models = {
                "work": "work_ner_model",
                "education": "education_ner_model", 
                "skills": "skills_ner_model",
                "projects": "projects_ner_model",
                "certifications": "certifications_ner_model"
            }
            
            for section, model_path in section_models.items():
                if os.path.exists(model_path):
                    self.section_models[section] = spacy.load(model_path)
                    print(f"✅ {section} NER model loaded")
                else:
                    print(f"❌ {section} NER model not found: {model_path}")
            
            # Load enhanced NER model as fallback
            if os.path.exists("enhanced_ner_model"):
                self.ner_model = spacy.load("enhanced_ner_model")
                print("✅ Enhanced NER model loaded (fallback)")
            elif os.path.exists("custom_ner_model"):
                self.ner_model = spacy.load("custom_ner_model")
                print("✅ Custom NER model loaded (fallback)")
            else:
                print("❌ No fallback NER model found")
            
            # Load quality classifier
            if os.path.exists("quality_classifier.pkl"):
                self.quality_classifier = joblib.load("quality_classifier.pkl")
                print("✅ Quality classifier loaded")
            else:
                print("❌ Quality classifier not found")
            
            # Load vectorizer
            if os.path.exists("tfidf_vectorizer.pkl"):
                self.vectorizer = joblib.load("tfidf_vectorizer.pkl")
                print("✅ TF-IDF vectorizer loaded")
            else:
                print("❌ TF-IDF vectorizer not found")
                
        except Exception as e:
            print(f"❌ Error loading models: {e}")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using custom NER model"""
        if not self.ner_model:
            return []
        
        doc = self.ner_model(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": 0.8  # Default confidence
            })
        
        return entities
    
    def validate_company(self, company_text: str) -> bool:
        """Validate if text is a valid company name"""
        if not self.quality_classifier or not self.vectorizer:
            return True  # Fallback to True if model not loaded
        
        try:
            # Vectorize the text
            X = self.vectorizer.transform([company_text])
            
            # Predict quality
            prediction = self.quality_classifier.predict(X)[0]
            probability = self.quality_classifier.predict_proba(X)[0]
            
            # Return True if predicted as valid with high confidence
            return prediction == 1 and probability[1] > 0.7
            
        except Exception as e:
            print(f"❌ Error validating company: {e}")
            return True  # Fallback to True
    
    def validate_title(self, title_text: str) -> bool:
        """Validate if text is a valid job title"""
        if not self.quality_classifier or not self.vectorizer:
            return True  # Fallback to True if model not loaded
        
        try:
            # Vectorize the text
            X = self.vectorizer.transform([title_text])
            
            # Predict quality
            prediction = self.quality_classifier.predict(X)[0]
            probability = self.quality_classifier.predict_proba(X)[0]
            
            # Return True if predicted as valid with high confidence
            return prediction == 1 and probability[1] > 0.7
            
        except Exception as e:
            print(f"❌ Error validating title: {e}")
            return True  # Fallback to True
    
    def extract_section_entities(self, text: str, section: str) -> List[Dict[str, Any]]:
        """Extract entities for a specific section using section-specific model"""
        if section in self.section_models:
            model = self.section_models[section]
            doc = model(text)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.8
                })
            
            return entities
        else:
            # Fallback to general model
            return self.extract_entities(text)

    def enhance_extraction(self, work_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance work entries with custom model validation"""
        enhanced_entries = []
        
        for entry in work_entries:
            # Validate company
            company = entry.get("company", "")
            if company and not self.validate_company(company):
                print(f"❌ Invalid company detected: {company}")
                continue  # Skip invalid entry
            
            # Validate title
            title = entry.get("title", "")
            if title and not self.validate_title(title):
                print(f"❌ Invalid title detected: {title}")
                continue  # Skip invalid entry
            
            # If both company and title are valid, keep the entry
            if company and title:
                enhanced_entries.append(entry)
        
        return enhanced_entries

# Global instance
custom_models = CustomModels()
