#!/usr/bin/env python3
"""
Production-Ready Resume Parsing Pipeline
Handles smart section extraction, chunking fallback, and entity extraction
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch


class SectionExtractor:
    """Extract EXPERIENCE and EDUCATION sections from resume text"""
    
    EXPERIENCE_KEYWORDS = [
        "experience", "work history", "employment", "professional experience",
        "work experience", "career history", "professional background"
    ]
    
    EDUCATION_KEYWORDS = [
        "education", "academic", "qualification", "academic background",
        "educational background", "academic qualification"
    ]
    
    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """
        Extract EXPERIENCE and EDUCATION sections from resume text
        
        Args:
            text: Full resume text
            
        Returns:
            Dict with 'experience' and 'education' sections
        """
        lines = text.split('\n')
        sections = {'experience': '', 'education': ''}
        current_section = None
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            is_experience = any(keyword in line_lower for keyword in SectionExtractor.EXPERIENCE_KEYWORDS)
            is_education = any(keyword in line_lower for keyword in SectionExtractor.EDUCATION_KEYWORDS)
            
            # Detect section headers (usually short lines with keywords)
            if len(line_lower) < 50:
                if is_experience:
                    if current_section and section_content:
                        sections[current_section] = '\n'.join(section_content)
                    current_section = 'experience'
                    section_content = []
                    continue
                elif is_education:
                    if current_section and section_content:
                        sections[current_section] = '\n'.join(section_content)
                    current_section = 'education'
                    section_content = []
                    continue
            
            # Add content to current section
            if current_section and line.strip():
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections


class TextChunker:
    """Chunk text with overlap for model processing"""
    
    def __init__(self, tokenizer, chunk_size: int = 450, overlap: int = 50):
        """
        Initialize chunker
        
        Args:
            tokenizer: HuggingFace tokenizer
            chunk_size: Maximum tokens per chunk
            overlap: Overlapping tokens between chunks
        """
        self.tokenizer = tokenizer
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Pre-process text to normalize format for better model inference
        
        Args:
            text: Raw text
            
        Returns:
            Normalized text
        """
        import re
        
        # Convert "Client XYZ" to "Company: XYZ" format
        text = re.sub(r'\bClient\s+', 'Company: ', text, flags=re.IGNORECASE)
        
        # Normalize "Role" and "Duration" keywords
        text = re.sub(r'\bRole\s+', 'Role: ', text, flags=re.IGNORECASE)
        text = re.sub(r'\bDuration\s+', 'Duration: ', text, flags=re.IGNORECASE)
        
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into overlapping segments
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        # Tokenize full text
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            # Get chunk
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            
            # Decode chunk
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            chunks.append(chunk_text)
            
            # Move to next chunk with overlap
            if end >= len(tokens):
                break
            start = end - self.overlap
        
        return chunks
    
    @staticmethod
    def filter_relevant_chunks(chunks: List[str]) -> List[str]:
        """
        Filter chunks that contain experience or education keywords
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Filtered chunks containing relevant keywords
        """
        relevant_keywords = [
            # Experience keywords
            'worked', 'developer', 'engineer', 'role', 'company', 'position',
            'responsibilities', 'duration', 'present', 'current',
            # Education keywords
            'bachelor', 'master', 'degree', 'university', 'college', 'institute',
            'b.tech', 'm.tech', 'btech', 'mtech', 'graduation', 'phd'
        ]
        
        filtered = []
        for chunk in chunks:
            chunk_lower = chunk.lower()
            if any(keyword in chunk_lower for keyword in relevant_keywords):
                filtered.append(chunk)
        
        return filtered


class ModelInference:
    """Wrapper for DeBERTa model inference"""
    
    def __init__(self, model_path: str):
        """
        Initialize model
        
        Args:
            model_path: Path to trained model
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.model.eval()
        
        # Load label mappings
        with open(f"{model_path}/label_mappings.json", 'r') as f:
            label_mappings = json.load(f)
        self.id2label = {int(k): v for k, v in label_mappings['id2label'].items()}
    
    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extract entities from text
        
        Args:
            text: Text to process
            
        Returns:
            List of entities with text, label, and confidence
        """
        # Pre-process text to normalize format
        text = TextChunker.preprocess_text(text)
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            return_offsets_mapping=True
        )
        offset_mapping = inputs.pop("offset_mapping")[0]
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        predictions = torch.argmax(outputs.logits, dim=2)[0]
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
        # Extract entities
        entities = []
        current_entity = None
        current_text = ""
        current_label = None
        
        for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
            if token in ['<s>', '</s>', '<pad>']:
                continue
            
            label = self.id2label[pred_id.item()]
            start, end = offset
            
            if start == end:
                continue
            
            actual_text = text[start:end]
            
            if label.startswith('B-'):
                # Save previous entity
                if current_entity:
                    entities.append({
                        'text': current_text.strip(),
                        'label': current_label
                    })
                
                # Start new entity
                current_label = label[2:]
                current_text = actual_text
                current_entity = True
                
            elif label.startswith('I-') and current_entity and label[2:] == current_label:
                # Continue entity
                current_text += actual_text
                
            else:
                # End entity
                if current_entity:
                    entities.append({
                        'text': current_text.strip(),
                        'label': current_label
                    })
                    current_entity = None
                    current_text = ""
                    current_label = None
        
        # Add last entity
        if current_entity:
            entities.append({
                'text': current_text.strip(),
                'label': current_label
            })
        
        return entities


class PostProcessor:
    """Post-process extracted entities"""
    
    # Common person name patterns
    PERSON_NAME_PATTERNS = [
        r'^[A-Z][a-z]+ [A-Z][a-z]+$',  # First Last
        r'^[A-Z]\. [A-Z][a-z]+$',       # F. Last
        r'^[A-Z][a-z]+ [A-Z]\.$',       # First L.
    ]
    
    # Common skills/technologies to remove from DEGREE
    SKILL_KEYWORDS = [
        'react', 'node', 'python', 'java', 'javascript', 'typescript',
        'angular', 'vue', 'django', 'flask', 'spring', 'aws', 'docker',
        'kubernetes', 'mongodb', 'sql', 'mysql', 'postgresql', 'redis',
        'html', 'css', 'git', 'jenkins', 'ci/cd', 'agile', 'scrum'
    ]
    
    @staticmethod
    def is_person_name(text: str) -> bool:
        """Check if text looks like a person name"""
        text = text.strip()
        
        # Exclude company suffixes
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
        
        # Check patterns
        for pattern in PostProcessor.PERSON_NAME_PATTERNS:
            if re.match(pattern, text):
                return True
        
        # Check if it's exactly 2 capitalized words (typical person name)
        # But NOT 3+ words (more likely company name)
        words = text.split()
        if len(words) == 2:
            if all(word[0].isupper() and len(word) > 1 for word in words):
                # Additional check: person names are usually shorter
                if len(text) < 30:  # Person names rarely exceed 30 chars
                    return True
        
        return False
    
    @staticmethod
    def is_skill(text: str) -> bool:
        """Check if text is a skill/technology"""
        text_lower = text.lower().strip()
        return any(skill in text_lower for skill in PostProcessor.SKILL_KEYWORDS)
    
    @staticmethod
    def clean_entities(entities: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Clean entities by removing person names from COMPANY and skills from DEGREE
        
        Args:
            entities: List of extracted entities
            
        Returns:
            Cleaned entities
        """
        cleaned = []
        
        for entity in entities:
            label = entity['label']
            text = entity['text']
            
            # Remove person names from COMPANY
            if label == 'COMPANY' and PostProcessor.is_person_name(text):
                continue
            
            # Remove skills from DEGREE
            if label == 'DEGREE' and PostProcessor.is_skill(text):
                continue
            
            cleaned.append(entity)
        
        return cleaned


class ResumeParser:
    """Main resume parsing pipeline"""
    
    def __init__(self, model_path: str):
        """
        Initialize parser
        
        Args:
            model_path: Path to trained model
        """
        self.model = ModelInference(model_path)
        self.chunker = TextChunker(self.model.tokenizer, chunk_size=450, overlap=50)
    
    def parse(self, resume_text: str) -> Dict:
        """
        Parse resume and extract structured data
        
        Args:
            resume_text: Full resume text
            
        Returns:
            Structured resume data
        """
        # Step 1: Try section extraction
        sections = SectionExtractor.extract_sections(resume_text)
        
        experience_text = sections.get('experience', '').strip()
        education_text = sections.get('education', '').strip()
        
        # Step 2: Fallback to chunking if sections not found
        if not experience_text and not education_text:
            chunks = self.chunker.chunk_text(resume_text)
            relevant_chunks = TextChunker.filter_relevant_chunks(chunks)
            
            # Combine relevant chunks
            combined_text = '\n'.join(relevant_chunks)
            experience_text = combined_text
            education_text = combined_text
        
        # Step 3: Extract entities from relevant text
        all_entities = []
        
        if experience_text:
            exp_entities = self.model.extract_entities(experience_text)
            all_entities.extend(exp_entities)
        
        if education_text and education_text != experience_text:
            edu_entities = self.model.extract_entities(education_text)
            all_entities.extend(edu_entities)
        
        # Step 4: Post-process entities
        cleaned_entities = PostProcessor.clean_entities(all_entities)
        
        # Step 5: Structure output
        output = self._structure_output(cleaned_entities)
        
        return output
    
    def _structure_output(self, entities: List[Dict[str, str]]) -> Dict:
        """
        Structure entities into experience and education format
        
        Args:
            entities: List of cleaned entities
            
        Returns:
            Structured output
        """
        # Group entities by type
        companies = [e['text'] for e in entities if e['label'] == 'COMPANY']
        roles = [e['text'] for e in entities if e['label'] == 'ROLE']
        locations = [e['text'] for e in entities if e['label'] == 'LOCATION']
        start_dates = [e['text'] for e in entities if e['label'] == 'START_DATE']
        end_dates = [e['text'] for e in entities if e['label'] == 'END_DATE']
        degrees = [e['text'] for e in entities if e['label'] == 'DEGREE']
        institutions = [e['text'] for e in entities if e['label'] == 'EDUCATION']
        
        # Build experience entries
        experience = []
        max_exp = max(len(companies), len(roles))
        
        for i in range(max_exp):
            exp_entry = {
                'company': companies[i] if i < len(companies) else '',
                'role': roles[i] if i < len(roles) else '',
                'start_date': start_dates[i] if i < len(start_dates) else '',
                'end_date': end_dates[i] if i < len(end_dates) else '',
                'location': locations[i] if i < len(locations) else ''
            }
            
            # Only add if has meaningful data
            if exp_entry['company'] or exp_entry['role']:
                experience.append(exp_entry)
        
        # Build education entries
        education = []
        max_edu = max(len(degrees), len(institutions))
        
        # Track used start/end dates for experience
        exp_dates_used = max_exp
        
        for i in range(max_edu):
            edu_entry = {
                'degree': degrees[i] if i < len(degrees) else '',
                'institution': institutions[i] if i < len(institutions) else '',
                'start_date': start_dates[exp_dates_used + i] if (exp_dates_used + i) < len(start_dates) else '',
                'end_date': end_dates[exp_dates_used + i] if (exp_dates_used + i) < len(end_dates) else ''
            }
            
            # Only add if has meaningful data
            if edu_entry['degree'] or edu_entry['institution']:
                education.append(edu_entry)
        
        return {
            'experience': experience,
            'education': education
        }


# FastAPI compatible function
def parse_resume(resume_text: str, model_path: str = "./models/resume-ner-deberta") -> Dict:
    """
    Parse resume text and extract structured information
    
    Args:
        resume_text: Full resume text (plain text from PDF/DOC)
        model_path: Path to trained model
        
    Returns:
        Structured resume data with experience and education
    """
    parser = ResumeParser(model_path)
    return parser.parse(resume_text)


if __name__ == "__main__":
    # Example usage
    sample_resume = """
    Anjan Yelle
    
    WORK EXPERIENCE:
    Software Developer
    Lalataksha Consulting Services Pvt Ltd
    Jan 2023 - Present
    Bangalore, India
    - Developed web applications using React.js and Node.js
    
    Software Developer
    Gatnix Technologies Pvt Ltd
    Jun 2021 - Dec 2022
    Hyderabad, India
    - Worked on mobile applications
    
    EDUCATION:
    Bachelor of Technology in Computer Science
    JNTU Hyderabad
    2016 - 2020
    """
    
    result = parse_resume(sample_resume)
    print(json.dumps(result, indent=2))
