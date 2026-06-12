#!/usr/bin/env python3
"""
Resume NER Model - Inference Example
Demonstrates how to use the trained model for resume parsing
"""

from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from pathlib import Path
from collections import defaultdict

# Model path - points to project root models directory
MODEL_PATH = Path(__file__).parent.parent / "models" / "resume-ner-deberta"

class ResumeParser:
    def __init__(self, model_path=MODEL_PATH):
        """Initialize the resume parser"""
        print(f"Loading model from {model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path), use_fast=False)
        self.model = AutoModelForTokenClassification.from_pretrained(str(model_path))
        self.model.eval()
        print("✅ Model loaded successfully!")
        
    def extract_entities_from_text(self, text, max_length=256, overlap=50):
        """
        Extract entities from resume text with chunking for long documents
        
        Args:
            text: Resume text
            max_length: Maximum tokens per chunk
            overlap: Overlapping tokens between chunks
            
        Returns:
            List of extracted entities
        """
        # Split into sentences
        sentences = text.replace('\n', '. ').split('. ')
        
        all_entities = []
        current_chunk = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            # Check if adding this sentence exceeds max_length
            test_chunk = current_chunk + sentence + ". "
            tokens = self.tokenizer(test_chunk, return_tensors="pt", truncation=False)
            
            if tokens['input_ids'].shape[1] > max_length:
                # Process current chunk
                if current_chunk.strip():
                    entities = self._process_chunk(current_chunk)
                    all_entities.extend(entities)
                
                # Start new chunk
                current_chunk = sentence + ". "
            else:
                current_chunk = test_chunk
        
        # Process final chunk
        if current_chunk.strip():
            entities = self._process_chunk(current_chunk)
            all_entities.extend(entities)
        
        # Remove duplicates
        return self._deduplicate_entities(all_entities)
    
    def _process_chunk(self, text, chunk_offset=0):
        """Process a single chunk of text"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        predictions = torch.argmax(outputs.logits, dim=2)
        probs = torch.softmax(outputs.logits, dim=2)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
        entities = []
        current_entity = None
        token_position = chunk_offset
        
        for idx, (token, pred_id) in enumerate(zip(tokens, predictions[0])):
            # Skip special tokens
            if token in ['<s>', '</s>', '<pad>']:
                continue
                
            label = self.model.config.id2label[pred_id.item()]
            confidence = probs[0][idx][pred_id].item()
            
            if label.startswith('B-'):
                # Save previous entity
                if current_entity:
                    entities.append(current_entity)
                
                # Start new entity
                current_entity = {
                    'type': label[2:],
                    'text': token.replace('▁', ' ').strip(),
                    'confidence': confidence,
                    'position': token_position
                }
            elif label.startswith('I-') and current_entity:
                # Continue current entity
                current_entity['text'] += token.replace('▁', ' ')
                current_entity['confidence'] = (current_entity['confidence'] + confidence) / 2
            else:
                # End current entity
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
            
            token_position += 1
        
        # Add last entity
        if current_entity:
            entities.append(current_entity)
        
        return entities
    
    def _deduplicate_entities(self, entities):
        """Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            # Clean text
            text = entity['text'].strip()
            key = (entity['type'], text.lower())
            
            if key not in seen and text:
                seen.add(key)
                entity['text'] = text
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_structured_data(self, text, confidence_threshold=0.7, proximity_window=50):
        """
        Extract structured resume data (person, work experience, education)
        Groups entities by positional proximity rather than simple index matching.
        
        Args:
            text: Resume text
            confidence_threshold: Minimum confidence for entities
            proximity_window: Maximum token distance to consider entities as related
            
        Returns:
            Dictionary with structured resume data
        """
        entities = self.extract_entities_from_text(text)
        
        # Filter by confidence
        entities = [e for e in entities if e['confidence'] >= confidence_threshold]
        
        # Separate entities by type
        work_types = {'COMPANY', 'ROLE', 'LOCATION', 'CLIENT', 'START_DATE', 'END_DATE'}
        edu_types = {'DEGREE', 'EDUCATION'}
        
        work_entities = [e for e in entities if e['type'] in work_types]
        edu_entities = [e for e in entities if e['type'] in edu_types]
        person_entities = [e for e in entities if e['type'] == 'PERSON']
        
        # Structure the data
        result = {
            'person_name': person_entities[0]['text'] if person_entities else None,
            'work_experience': self._group_work_experience(work_entities, proximity_window),
            'education': self._group_education(edu_entities, proximity_window)
        }
        
        return result
    
    def _group_work_experience(self, entities, proximity_window=50):
        """
        Group work experience entities by positional proximity.
        Each job entry combines COMPANY, ROLE, LOCATION, CLIENT, dates that appear close together.
        """
        if not entities:
            return []
        
        # Sort entities by position
        entities = sorted(entities, key=lambda x: x.get('position', 0))
        
        # Group entities into clusters based on proximity
        clusters = []
        current_cluster = [entities[0]]
        
        for i in range(1, len(entities)):
            prev_pos = entities[i-1].get('position', 0)
            curr_pos = entities[i].get('position', 0)
            
            # If entities are close together, add to current cluster
            if curr_pos - prev_pos <= proximity_window:
                current_cluster.append(entities[i])
            else:
                # Start new cluster
                clusters.append(current_cluster)
                current_cluster = [entities[i]]
        
        # Add last cluster
        if current_cluster:
            clusters.append(current_cluster)
        
        # Convert clusters to structured work experience entries
        work_experience = []
        for cluster in clusters:
            entry = {
                'company': None,
                'role': None,
                'location': None,
                'client': None,
                'start_date': None,
                'end_date': None
            }
            
            for entity in cluster:
                entity_type = entity['type'].lower()
                if entity_type in entry:
                    # Take first occurrence of each type in the cluster
                    if entry[entity_type] is None:
                        entry[entity_type] = entity['text']
            
            # Only add entry if it has at least a company or role
            if entry['company'] or entry['role']:
                work_experience.append(entry)
        
        return work_experience
    
    def _group_education(self, entities, proximity_window=50):
        """
        Group education entities by positional proximity.
        Each education entry combines DEGREE and EDUCATION (institution) that appear close together.
        """
        if not entities:
            return []
        
        # Sort entities by position
        entities = sorted(entities, key=lambda x: x.get('position', 0))
        
        # Group entities into clusters based on proximity
        clusters = []
        current_cluster = [entities[0]]
        
        for i in range(1, len(entities)):
            prev_pos = entities[i-1].get('position', 0)
            curr_pos = entities[i].get('position', 0)
            
            # If entities are close together, add to current cluster
            if curr_pos - prev_pos <= proximity_window:
                current_cluster.append(entities[i])
            else:
                # Start new cluster
                clusters.append(current_cluster)
                current_cluster = [entities[i]]
        
        # Add last cluster
        if current_cluster:
            clusters.append(current_cluster)
        
        # Convert clusters to structured education entries
        education = []
        for cluster in clusters:
            entry = {
                'degree': None,
                'institution': None
            }
            
            for entity in cluster:
                if entity['type'] == 'DEGREE' and entry['degree'] is None:
                    entry['degree'] = entity['text']
                elif entity['type'] == 'EDUCATION' and entry['institution'] is None:
                    entry['institution'] = entity['text']
            
            # Only add entry if it has at least a degree or institution
            if entry['degree'] or entry['institution']:
                education.append(entry)
        
        return education
    
    def print_structured_output(self, data):
        """Pretty print structured resume data"""
        print("\n" + "="*60)
        print("📋 EXTRACTED RESUME INFORMATION")
        print("="*60)
        
        if data['person_name']:
            print(f"\n👤 PERSON: {data['person_name']}")
        
        if data['work_experience']:
            print("\n💼 WORK EXPERIENCE:")
            for i, exp in enumerate(data['work_experience'], 1):
                print(f"\n  {i}. {exp['role'] or 'N/A'}")
                print(f"     Company: {exp['company'] or 'N/A'}")
                if exp['location']:
                    print(f"     Location: {exp['location']}")
                if exp['client']:
                    print(f"     Client: {exp['client']}")
                if exp['start_date'] or exp['end_date']:
                    period = f"{exp['start_date'] or 'N/A'} to {exp['end_date'] or 'Present'}"
                    print(f"     Period: {period}")
        
        if data['education']:
            print("\n🎓 EDUCATION:")
            for i, edu in enumerate(data['education'], 1):
                degree = edu['degree'] or 'N/A'
                institution = edu['institution'] or 'N/A'
                print(f"  {i}. {degree} from {institution}")
        
        print("\n" + "="*60 + "\n")


def main():
    """Example usage"""
    
    # Initialize parser
    parser = ResumeParser()
    
    # Example 1: Short resume text
    print("\n" + "="*60)
    print("EXAMPLE 1: Short Resume")
    print("="*60)
    
    short_resume = """
    Rajesh Kumar is a Senior Software Engineer with 8 years of experience.
    He worked at Infosys as a Full Stack Developer in Bangalore from January 2018 to December 2021.
    During this time, he developed applications for Microsoft as a client.
    Currently, he works at TCS as a Tech Lead in Hyderabad.
    
    Education:
    - B.Tech in Computer Science from IIT Delhi (2014-2018)
    - M.Tech in Artificial Intelligence from IIT Bombay (2018-2020)
    """
    
    data = parser.extract_structured_data(short_resume)
    parser.print_structured_output(data)
    
    # Example 2: Extract all entities with confidence scores
    print("\n" + "="*60)
    print("EXAMPLE 2: All Entities with Confidence Scores")
    print("="*60)
    
    entities = parser.extract_entities_from_text(short_resume)
    
    print("\n📊 All Extracted Entities:")
    for entity in entities:
        print(f"  • {entity['type']}: {entity['text']} (confidence: {entity['confidence']:.2f})")
    
    # Example 3: Process resume from file
    print("\n" + "="*60)
    print("EXAMPLE 3: Process Resume from File")
    print("="*60)
    
    # Uncomment to use with actual file
    # resume_file = Path("sample_resume.txt")
    # if resume_file.exists():
    #     with open(resume_file, 'r') as f:
    #         resume_text = f.read()
    #     
    #     data = parser.extract_structured_data(resume_text)
    #     parser.print_structured_output(data)
    # else:
    #     print(f"File not found: {resume_file}")
    
    print("✅ Examples completed!")


if __name__ == "__main__":
    main()
