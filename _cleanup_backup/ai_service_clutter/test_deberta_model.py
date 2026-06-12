#!/usr/bin/env python3
"""
DeBERTa Model Testing Script
Test your trained DeBERTa-v3 model with raw resume text
Handles 512 token limit and provides detailed accuracy analysis
"""

import sys
import os
import json
import textwrap
from typing import List, Dict, Tuple, Any
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

sys.path.insert(0, os.path.dirname(__file__))

class DeBERTaModelTester:
    def __init__(self, model_path: str = "./models/resume-ner-deberta"):
        """Initialize the model tester"""
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.label_mappings = None
        self.id2label = None
        self.load_model()
    
    def load_model(self):
        """Load the DeBERTa model and tokenizer"""
        try:
            print("Loading DeBERTa model and tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_path)
            
            # Load label mappings
            with open(os.path.join(self.model_path, "label_mappings.json"), 'r') as f:
                self.label_mappings = json.load(f)
            
            self.id2label = {int(k): v for k, v in self.label_mappings['id2label'].items()}
            
            print(f"Model loaded successfully!")
            print(f"Available labels: {sorted(list(set(self.id2label.values())))}")
            print(f"Max tokens: {self.tokenizer.model_max_length}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def chunk_text(self, text: str, max_length: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into chunks that fit within the token limit
        Uses overlap to maintain context across chunk boundaries
        """
        # Tokenize the entire text
        tokens = self.tokenizer.tokenize(text)
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(tokens):
            # Calculate end index, leaving room for special tokens
            end_idx = min(start_idx + max_length - 2, len(tokens))  # -2 for [CLS] and [SEP]
            
            # Extract chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Convert back to text
            chunk_text = self.tokenizer.convert_tokens_to_string(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move to next chunk with overlap
            if end_idx >= len(tokens):
                break
            start_idx = end_idx - overlap
        
        return chunks
    
    def extract_entities_from_chunk(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from a single text chunk"""
        # Tokenize input
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512, 
            return_offsets_mapping=True
        )
        
        offset_mapping = inputs.pop("offset_mapping")[0]
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        predictions = torch.argmax(outputs.logits, dim=2)[0]
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
        # Extract entities using BIO tagging
        entities = []
        current_entity = None
        current_text = ""
        current_label = None
        
        for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
            if token in ['<s>', '</s>', '<pad>']:
                continue
            
            label = self.id2label[pred_id.item()]
            
            # Get actual text from offset
            start, end = offset
            if start == end:  # Special token
                continue
            
            actual_text = text[start:end]
            
            if label.startswith('B-'):
                # Save previous entity
                if current_entity:
                    entities.append({
                        'text': current_text.strip(),
                        'label': current_label,
                        'start': current_start,
                        'end': current_end
                    })
                
                # Start new entity
                current_label = label[2:]  # Remove 'B-'
                current_text = actual_text
                current_start = start
                current_end = end
                current_entity = True
                
            elif label.startswith('I-') and current_entity and label[2:] == current_label:
                # Continue current entity
                current_text += actual_text
                current_end = end
                
            else:
                # End current entity
                if current_entity:
                    entities.append({
                        'text': current_text.strip(),
                        'label': current_label,
                        'start': current_start,
                        'end': current_end
                    })
                    current_entity = None
                    current_text = ""
                    current_label = None
        
        # Add last entity if exists
        if current_entity:
            entities.append({
                'text': current_text.strip(),
                'label': current_label,
                'start': current_start,
                'end': current_end
            })
        
        return entities
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text, handling chunks and merging overlapping entities
        """
        # Split text into chunks
        chunks = self.chunk_text(text)
        
        print(f"Text split into {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {len(chunk)} chars, ~{len(self.tokenizer.tokenize(chunk))} tokens")
        
        all_entities = []
        
        # Extract entities from each chunk
        for i, chunk in enumerate(chunks):
            print(f"\nProcessing chunk {i+1}/{len(chunks)}...")
            entities = self.extract_entities_from_chunk(chunk)
            
            # Add chunk info
            for entity in entities:
                entity['chunk_id'] = i
                all_entities.append(entity)
        
        # Merge overlapping entities
        merged_entities = self.merge_overlapping_entities(all_entities)
        
        return merged_entities
    
    def merge_overlapping_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge overlapping entities from different chunks"""
        if not entities:
            return []
        
        # Sort entities by start position
        entities.sort(key=lambda x: x['start'])
        
        merged = []
        current = entities[0]
        
        for next_entity in entities[1:]:
            # Check if entities overlap and have same label
            if (next_entity['start'] <= current['end'] and 
                next_entity['label'] == current['label']):
                
                # Merge entities
                current['text'] = current['text'] + " " + next_entity['text']
                current['end'] = max(current['end'], next_entity['end'])
                current['chunk_id'] = f"{current['chunk_id']},{next_entity['chunk_id']}"
            else:
                merged.append(current)
                current = next_entity
        
        merged.append(current)
        return merged
    
    def display_results(self, entities: List[Dict[str, Any]], show_details: bool = True):
        """Display extraction results"""
        print("\n" + "="*80)
        print("EXTRACTION RESULTS")
        print("="*80)
        
        if not entities:
            print("No entities found!")
            return
        
        # Group by label
        grouped = {}
        for entity in entities:
            label = entity['label']
            if label not in grouped:
                grouped[label] = []
            grouped[label].append(entity)
        
        # Display grouped results
        for label in sorted(grouped.keys()):
            print(f"\n{label}:")
            for i, entity in enumerate(grouped[label], 1):
                print(f"  {i}. {entity['text']}")
                if show_details:
                    print(f"     Position: {entity['start']}-{entity['end']}, Chunk: {entity['chunk_id']}")
        
        print(f"\nTotal entities found: {len(entities)} across {len(grouped)} categories")
    
    def calculate_accuracy(self, entities: List[Dict[str, Any]], expected: Dict[str, List[str]]) -> Tuple[float, Dict[str, int]]:
        """Calculate accuracy against expected results"""
        if not expected:
            return 0.0, {}
        
        # Convert entities to dictionary
        extracted = {}
        for entity in entities:
            label = entity['label']
            if label not in extracted:
                extracted[label] = []
            extracted[label].append(entity['text'].strip())
        
        # Calculate accuracy for each label
        results = {}
        total_correct = 0
        total_expected = 0
        
        for label, expected_values in expected.items():
            extracted_values = extracted.get(label, [])
            
            # Calculate matches
            matches = 0
            for exp_val in expected_values:
                for ext_val in extracted_values:
                    if exp_val.lower() in ext_val.lower() or ext_val.lower() in exp_val.lower():
                        matches += 1
                        break
            
            results[label] = {
                'correct': matches,
                'expected': len(expected_values),
                'extracted': len(extracted_values),
                'accuracy': (matches / len(expected_values) * 100) if expected_values else 0
            }
            
            total_correct += matches
            total_expected += len(expected_values)
        
        overall_accuracy = (total_correct / total_expected * 100) if total_expected > 0 else 0
        results['overall'] = {
            'correct': total_correct,
            'expected': total_expected,
            'accuracy': overall_accuracy
        }
        
        return overall_accuracy, results
    
    def test_text(self, text: str, expected: Dict[str, List[str]] = None, show_details: bool = True):
        """Test the model with given text"""
        print("="*80)
        print("TESTING DEBERTA MODEL")
        print("="*80)
        
        print(f"Input text length: {len(text)} characters")
        print(f"Estimated tokens: {len(self.tokenizer.tokenize(text))}")
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Display results
        self.display_results(entities, show_details)
        
        # Calculate accuracy if expected provided
        if expected:
            print("\n" + "="*80)
            print("ACCURACY ANALYSIS")
            print("="*80)
            
            overall_accuracy, results = self.calculate_accuracy(entities, expected)
            
            for label, result in results.items():
                if label == 'overall':
                    print(f"\nOVERALL ACCURACY: {result['accuracy']:.1f}% ({result['correct']}/{result['expected']})")
                else:
                    print(f"{label}: {result['accuracy']:.1f}% ({result['correct']}/{result['expected']})")
        
        return entities


def interactive_test():
    """Interactive testing mode"""
    tester = DeBERTaModelTester()
    
    print("\n" + "="*80)
    print("INTERACTIVE DEBERTA MODEL TESTING")
    print("="*80)
    print("\nPaste your resume text below (press Enter twice to finish):")
    print("You can paste work experience, education, or full resume sections")
    print("-" * 80)
    
    while True:
        print("\nEnter text to test (or 'quit' to exit):")
        lines = []
        
        while True:
            try:
                line = input()
                if line.lower() == 'quit':
                    return
                if line.strip() == '' and lines:
                    break
                lines.append(line)
            except EOFError:
                break
        
        if not lines:
            continue
        
        text = '\n'.join(lines)
        
        # Test the text
        entities = tester.test_text(text, show_details=True)
        
        print("\n" + "="*80)
        input("Press Enter to test another text (or 'quit' to exit)...")


def test_examples():
    """Test with example texts"""
    tester = DeBERTaModelTester()
    
    examples = [
        {
            "name": "Multiple Work Experiences",
            "text": """
            Software Developer
            Lalataksha Consulting Services Pvt Ltd
            Jan 2024 - Present
            Developed and maintained web applications using React.js and Node.js
            
            React Developer
            Gatnix Technologies Pvt Ltd
            Jun 2022 - Dec 2023
            Implemented dynamic forms and dashboards
            
            Junior Web Developer
            Disha IT Consultant
            Apr 2021 - May 2022
            Built static and dynamic web pages
            """,
            "expected": {
                "COMPANY": ["Lalataksha Consulting Services Pvt Ltd", "Gatnix Technologies Pvt Ltd", "Disha IT Consultant"],
                "ROLE": ["Software Developer", "React Developer", "Junior Web Developer"],
                "START_DATE": ["Jan", "Jun", "Apr"],
                "END_DATE": ["Present", "Dec", "May"]
            }
        },
        {
            "name": "Education Section",
            "text": """
            Bachelor of Technology
            Computer Science Engineering
            IIT Delhi
            2017 - 2021
            
            Master of Science
            Data Science
            Stanford University
            2021 - 2023
            """,
            "expected": {
                "DEGREE": ["Bachelor of Technology", "Master of Science"],
                "EDUCATION": ["IIT Delhi", "Stanford University"],
                "START_DATE": ["2017", "2021"],
                "END_DATE": ["2021", "2023"]
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'='*80}")
        print(f"EXAMPLE {i}: {example['name']}")
        print(f"{'='*80}")
        
        entities = tester.test_text(example['text'], example['expected'], show_details=True)
        
        print("\n" + "="*80)
        input("Press Enter to continue to next example...")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test DeBERTa model with resume text")
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--examples', action='store_true', help='Test with examples')
    parser.add_argument('--text', type=str, help='Text to test')
    parser.add_argument('--file', type=str, help='File containing text to test')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_test()
    elif args.examples:
        test_examples()
    elif args.text:
        tester = DeBERTaModelTester()
        tester.test_text(args.text)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                text = f.read()
            tester = DeBERTaModelTester()
            tester.test_text(text)
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("Usage:")
        print("  python3 test_deberta_model.py --interactive")
        print("  python3 test_deberta_model.py --examples")
        print("  python3 test_deberta_model.py --text 'Your text here'")
        print("  python3 test_deberta_model.py --file resume.txt")
        print("\nStarting interactive mode...")
        interactive_test()
