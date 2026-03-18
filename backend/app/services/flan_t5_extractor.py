#!/usr/bin/env python3
"""
Flan-T5 Work Experience Extractor
Optimized for CPU-based resume parsing
"""

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import json
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class FlanT5WorkExtractor:
    """Flan-T5-based work experience extractor for resume parsing"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load Flan-T5 model for CPU inference"""
        try:
            logger.info("🚀 Loading Flan-T5-base model...")
            
            # Load tokenizer
            self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
            
            # Load model with CPU optimization
            self.model = T5ForConditionalGeneration.from_pretrained(
                "google/flan-t5-base",
                torch_dtype=torch.float32  # CPU-friendly
            )
            
            # Move to CPU device
            self.model.to(self.device)
            
            # Set to evaluation mode
            self.model.eval()
            
            logger.info("✅ Flan-T5 model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error loading Flan-T5 model: {e}")
            raise
    
    def extract_work_experience(self, work_text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience from text using Flan-T5
        
        Args:
            work_text: Raw work experience text from resume
            
        Returns:
            List of work experience dictionaries
        """
        try:
            # Create prompt for Flan-T5
            prompt = self._create_extraction_prompt(work_text)
            
            # Generate response
            response = self._generate_response(prompt)
            
            # Parse response to JSON
            work_entries = self._parse_response_to_json(response)
            
            # Enhance with metadata
            enhanced_entries = self._add_metadata(work_entries)
            
            return enhanced_entries
            
        except Exception as e:
            logger.error(f"❌ Error extracting work experience: {e}")
            return []
    
    def _create_extraction_prompt(self, work_text: str) -> str:
        """Create extraction prompt for Flan-T5"""
        prompt = f"""You are a resume parsing expert. Extract work experience from the following text and return ONLY a JSON array.

Format: [
  {{
    "company": "Company Name",
    "job_title": "Job Title",
    "start_date": "YYYY-MM",
    "end_date": "YYYY-MM" or null,
    "is_current": true/false,
    "location": "City, State",
    "employment_type": "Full-time",
    "responsibilities": ["responsibility 1", "responsibility 2"],
    "tech_stack": ["skill1", "skill2"]
  }}
]

Resume Text:
{work_text}

JSON Array:"""
        return prompt
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response using Flan-T5"""
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=1024,
                    num_beams=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return "[]"
    
    def _parse_response_to_json(self, response: str) -> List[Dict[str, Any]]:
        """Parse Flan-T5 response to JSON"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try to parse entire response as JSON
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            logger.error(f"Response was: {response}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing response: {e}")
            return []
    
    def _add_metadata(self, work_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add metadata to work entries"""
        enhanced_entries = []
        
        for entry in work_entries:
            enhanced_entry = entry.copy()
            
            # Add model metadata
            enhanced_entry["_source_model"] = "flan-t5-base"
            enhanced_entry["_missing_fields"] = self._get_missing_fields(entry)
            
            # Calculate confidence
            enhanced_entry["confidence"] = self._calculate_confidence(entry)
            
            # Normalize dates
            enhanced_entry["start_date"] = self._normalize_date(entry.get("start_date"))
            enhanced_entry["end_date"] = self._normalize_date(entry.get("end_date"))
            
            enhanced_entries.append(enhanced_entry)
        
        return enhanced_entries
    
    def _get_missing_fields(self, entry: Dict[str, Any]) -> List[str]:
        """Identify missing fields"""
        required_fields = ["company", "job_title", "start_date", "location"]
        missing = []
        
        for field in required_fields:
            if not entry.get(field) or entry.get(field) == "":
                missing.append(field)
        
        return missing
    
    def _calculate_confidence(self, entry: Dict[str, Any]) -> float:
        """Calculate confidence score for entry"""
        score = 0.0
        max_score = 100.0
        
        # Company present (25 points)
        if entry.get("company") and entry.get("company") != "":
            score += 25
        
        # Job title present (25 points)
        if entry.get("job_title") and entry.get("job_title") != "":
            score += 25
        
        # Start date present (20 points)
        if entry.get("start_date") and entry.get("start_date") != "":
            score += 20
        
        # End date or is_current present (15 points)
        if entry.get("end_date") or entry.get("is_current"):
            score += 15
        
        # Responsibilities present (10 points)
        if entry.get("responsibilities") and len(entry.get("responsibilities", [])) > 0:
            score += 10
        
        # Location present (5 points)
        if entry.get("location") and entry.get("location") != "":
            score += 5
        
        return score / max_score
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM format"""
        if not date_str or date_str == "":
            return None
        
        try:
            # Handle various date formats
            date_patterns = [
                r'(\d{4})-(\d{2})',  # YYYY-MM
                r'(\d{4})/(\d{2})',  # YYYY/MM
                r'(\w{3})\s*(\d{4})',  # Month YYYY
                r'(\d{4})',  # YYYY only
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    if len(match.groups()) == 2:
                        year, month = match.groups()
                        # Convert month name to number if needed
                        if month.isalpha():
                            month_map = {
                                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                            }
                            month = month_map.get(month[:3], '01')
                        return f"{year}-{month.zfill(2)}"
                    else:
                        year = match.group(1)
                        return f"{year}-01"
            
            return date_str
            
        except Exception:
            return date_str

# Singleton instance
_flan_t5_extractor = None

def get_flan_t5_extractor():
    """Get singleton Flan-T5 extractor instance"""
    global _flan_t5_extractor
    if _flan_t5_extractor is None:
        _flan_t5_extractor = FlanT5WorkExtractor()
    return _flan_t5_extractor
