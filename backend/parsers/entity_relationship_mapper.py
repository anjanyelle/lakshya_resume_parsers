#!/usr/bin/env python3
"""
TASK 1 - Entity Relationship Mapper
Groups NER entities into structured job records
"""

import spacy
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class JobExperience:
    """Structured job experience"""
    title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    description: str = ""

class EntityRelationshipMapper:
    """Maps NER entities to structured job experiences"""
    
    def __init__(self):
        self.nlp = spacy.load("skills_ner_trained/")
        
    def group_experience_entities(self, doc) -> List[Dict[str, Any]]:
        """Group NER entities into structured job records"""
        
        jobs = []
        current_job = JobExperience()
        
        # Get entities in document order
        entities = [(ent.start_char, ent.end_char, ent.label_, ent.text) for ent in doc.ents]
        entities.sort()  # Sort by position
        
        i = 0
        while i < len(entities):
            start_char, end_char, label, text = entities[i]
            
            # Look for TITLE entity first
            if label == "TITLE":
                # Start new job
                current_job = JobExperience()
                current_job.title = text.strip()
                
                # Look for related entities within ±3 window
                window_start = max(0, i - 3)
                window_end = min(len(entities), i + 4)
                
                for j in range(window_start, window_end):
                    if j == i:
                        continue
                    
                    _, _, other_label, other_text = entities[j]
                    other_text = other_text.strip()
                    
                    if other_label == "COMPANY" and not current_job.company:
                        current_job.company = other_text
                    elif other_label == "DATE" and not current_job.start_date:
                        # Parse date range
                        dates = self._parse_date_range(other_text)
                        if dates:
                            current_job.start_date, current_job.end_date = dates
                    elif other_label == "LOCATION" and not current_job.location:
                        current_job.location = other_text
                
                # Check for CLIENT pattern in surrounding text
                client_company = self._extract_client_company(doc.text, start_char)
                if client_company and not current_job.company:
                    current_job.company = client_company
                
                # Add job if it has at least title and company
                if current_job.title and current_job.company:
                    jobs.append({
                        "title": current_job.title,
                        "company": current_job.company,
                        "start_date": current_job.start_date,
                        "end_date": current_job.end_date,
                        "location": current_job.location
                    })
            
            i += 1
        
        return jobs
    
    def _parse_date_range(self, date_text: str) -> Optional[tuple]:
        """Parse date range from text"""
        
        # Common date range patterns
        patterns = [
            r"(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|Present|Current)",
            r"(\w+\s+\d{4})\s*to\s*(\w+\s+\d{4}|Present|Current)",
            r"(\d{4})\s*[-–—]\s*(\d{4}|Present|Current)",
            r"(\d{4})\s*to\s*(\d{4}|Present|Current)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                start_date = match.group(1).strip()
                end_date = match.group(2).strip()
                return (start_date, end_date)
        
        # Single date case
        single_date_pattern = r"(\w+\s+\d{4}|\d{4})"
        match = re.search(single_date_pattern, date_text)
        if match:
            return (match.group(1).strip(), "Present")
        
        return None
    
    def _extract_client_company(self, text: str, position: int) -> Optional[str]:
        """Extract company from CLIENT: pattern near position"""
        
        # Look for CLIENT: pattern within 200 characters
        start_pos = max(0, position - 200)
        end_pos = min(len(text), position + 200)
        context = text[start_pos:end_pos]
        
        # CLIENT patterns
        client_patterns = [
            r"CLIENT:\s*([^\n\r]+)",
            r"CLIENT\s*([^\n\r]+)",
        ]
        
        for pattern in client_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

def test_entity_mapper():
    """Test the entity relationship mapper"""
    
    print("🔧 TASK 1 - TESTING ENTITY RELATIONSHIP MAPPER")
    print("=" * 60)
    
    mapper = EntityRelationshipMapper()
    
    # Test texts
    test_texts = [
        "Senior Data Analyst at Home Depot from June 2023 to Present",
        "CLIENT: Home Depot\nROLE: Senior Data Analyst June 2023 - Present",
        "Sr Java Developer at Amazon August 2020 - May 2023 Seattle",
        "Machine Learning Engineer Microsoft 2019 - 2022 Redmond",
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\n📄 Test {i+1}: {text}")
        
        doc = mapper.nlp(text)
        jobs = mapper.group_experience_entities(doc)
        
        print(f"✅ Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"  - {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            if job.get('start_date'):
                print(f"    Period: {job.get('start_date')} - {job.get('end_date', 'N/A')}")
    
    return mapper

if __name__ == "__main__":
    mapper = test_entity_mapper()
    print(f"\n✅ Entity Relationship Mapper created and tested")
