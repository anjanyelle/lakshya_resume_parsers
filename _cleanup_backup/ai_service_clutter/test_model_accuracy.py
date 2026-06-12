#!/usr/bin/env python3
"""
Direct Model Accuracy Testing Script
Test the DeBERTa model with plain text input to verify entity extraction accuracy
"""

import sys
import os
import json
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.dirname(__file__))

def test_model_with_text(text: str, show_details: bool = True):
    """
    Test the model with plain text and show extracted entities
    
    Args:
        text: Plain text to test
        show_details: Whether to show detailed token-level predictions
    """
    try:
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        import torch
        
        model_path = "./models/resume-ner-deberta"
        
        print("="*80)
        print("🧪 TESTING MODEL ACCURACY")
        print("="*80)
        
        # Load model and tokenizer
        print("\n📖 Loading model and tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForTokenClassification.from_pretrained(model_path)
        
        # Load label mappings
        with open(os.path.join(model_path, "label_mappings.json"), 'r') as f:
            label_mappings = json.load(f)
        
        id2label = {int(k): v for k, v in label_mappings['id2label'].items()}
        
        print("✅ Model loaded successfully")
        print(f"📋 Available labels: {list(set(id2label.values()))}\n")
        
        # Tokenize input
        print("📝 INPUT TEXT:")
        print("-" * 80)
        print(text)
        print("-" * 80)
        
        # Get predictions
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, return_offsets_mapping=True)
        offset_mapping = inputs.pop("offset_mapping")[0]
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        predictions = torch.argmax(outputs.logits, dim=2)[0]
        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
        # Extract entities
        entities = []
        current_entity = None
        current_text = ""
        current_label = None
        
        for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
            if token in ['<s>', '</s>', '<pad>']:
                continue
            
            label = id2label[pred_id.item()]
            
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
                        'confidence': 'high'
                    })
                
                # Start new entity
                current_label = label[2:]  # Remove 'B-'
                current_text = actual_text
                current_entity = True
                
            elif label.startswith('I-') and current_entity and label[2:] == current_label:
                # Continue current entity
                current_text += actual_text
                
            else:
                # End current entity
                if current_entity:
                    entities.append({
                        'text': current_text.strip(),
                        'label': current_label,
                        'confidence': 'high'
                    })
                    current_entity = None
                    current_text = ""
                    current_label = None
        
        # Add last entity if exists
        if current_entity:
            entities.append({
                'text': current_text.strip(),
                'label': current_label,
                'confidence': 'high'
            })
        
        # Display results
        print("\n🎯 EXTRACTED ENTITIES:")
        print("="*80)
        
        if entities:
            # Group by label
            grouped = {}
            for entity in entities:
                label = entity['label']
                if label not in grouped:
                    grouped[label] = []
                grouped[label].append(entity['text'])
            
            for label, texts in sorted(grouped.items()):
                print(f"\n📌 {label}:")
                for text in texts:
                    print(f"   ✓ {text}")
        else:
            print("   ⚠️  No entities found")
        
        print("\n" + "="*80)
        print(f"📊 SUMMARY: Found {len(entities)} entities across {len(grouped)} categories")
        print("="*80)
        
        # Show detailed token predictions if requested
        if show_details:
            print("\n🔍 DETAILED TOKEN PREDICTIONS:")
            print("-" * 80)
            print(f"{'Token':<20} {'Prediction':<20} {'Text':<30}")
            print("-" * 80)
            
            for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
                if token in ['<s>', '</s>', '<pad>']:
                    continue
                
                label = id2label[pred_id.item()]
                start, end = offset
                
                if start != end:
                    actual_text = text[start:end]
                    if label != 'O':  # Only show non-O predictions
                        print(f"{token:<20} {label:<20} {actual_text:<30}")
            
            print("-" * 80)
        
        return entities
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def run_test_cases():
    """Run multiple test cases to verify accuracy"""
    
    print("\n" + "="*80)
    print("🧪 RUNNING TEST CASES")
    print("="*80)
    
    test_cases = [
        {
            "name": "Test 1: Simple Work Experience",
            "text": "John Doe worked at Google as Software Engineer from Jan 2020 to Dec 2023 in Bangalore.",
            "expected": {
                "COMPANY": ["Google"],
                "ROLE": ["Software Engineer"],
                "LOCATION": ["Bangalore"],
                "START_DATE": ["Jan 2020"],
                "END_DATE": ["Dec 2023"]
            }
        },
        {
            "name": "Test 2: Multiple Companies",
            "text": "Previously worked at Microsoft as Senior Developer and later joined Amazon as Tech Lead in Seattle.",
            "expected": {
                "COMPANY": ["Microsoft", "Amazon"],
                "ROLE": ["Senior Developer", "Tech Lead"],
                "LOCATION": ["Seattle"]
            }
        },
        {
            "name": "Test 3: Education",
            "text": "Completed Bachelor of Technology in Computer Science from IIT Delhi.",
            "expected": {
                "DEGREE": ["Bachelor of Technology"],
                "EDUCATION": ["IIT Delhi"]
            }
        },
        {
            "name": "Test 4: Client Projects",
            "text": "Worked on projects for Accenture client TCS implementing cloud solutions.",
            "expected": {
                "COMPANY": ["Accenture"],
                "CLIENT": ["TCS"]
            }
        }
    ]
    
    total_correct = 0
    total_expected = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"{'='*80}")
        
        entities = test_model_with_text(test_case['text'], show_details=False)
        
        # Compare with expected
        print(f"\n📊 COMPARISON:")
        print("-" * 80)
        
        extracted = {}
        for entity in entities:
            label = entity['label']
            if label not in extracted:
                extracted[label] = []
            extracted[label].append(entity['text'])
        
        for label, expected_values in test_case['expected'].items():
            extracted_values = extracted.get(label, [])
            
            print(f"\n{label}:")
            print(f"  Expected: {expected_values}")
            print(f"  Extracted: {extracted_values}")
            
            # Simple matching
            matches = sum(1 for exp in expected_values if any(exp.lower() in ext.lower() or ext.lower() in exp.lower() for ext in extracted_values))
            total_correct += matches
            total_expected += len(expected_values)
            
            if matches == len(expected_values):
                print(f"  ✅ PASS ({matches}/{len(expected_values)})")
            else:
                print(f"  ⚠️  PARTIAL ({matches}/{len(expected_values)})")
    
    print("\n" + "="*80)
    print("📊 OVERALL ACCURACY")
    print("="*80)
    accuracy = (total_correct / total_expected * 100) if total_expected > 0 else 0
    print(f"Correct: {total_correct}/{total_expected}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("="*80)


def interactive_mode():
    """Interactive mode to test custom text"""
    print("\n" + "="*80)
    print("🎯 INTERACTIVE TESTING MODE")
    print("="*80)
    print("\nEnter your text to test (or 'quit' to exit)")
    print("You can paste resume text, work experience, or any text with entities")
    print("-" * 80)
    
    while True:
        print("\n📝 Enter text (or 'quit' to exit):")
        print("> ", end="")
        
        lines = []
        while True:
            line = input()
            if line.lower() == 'quit':
                return
            if line.strip() == '' and lines:
                break
            if line.strip():
                lines.append(line)
        
        if not lines:
            continue
        
        text = ' '.join(lines)
        test_model_with_text(text, show_details=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test DeBERTa model accuracy")
    parser.add_argument('--text', type=str, help='Text to test')
    parser.add_argument('--test-cases', action='store_true', help='Run predefined test cases')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--details', action='store_true', default=True, help='Show detailed predictions')
    
    args = parser.parse_args()
    
    if args.text:
        # Test with provided text
        test_model_with_text(args.text, show_details=args.details)
    elif args.test_cases:
        # Run test cases
        run_test_cases()
    elif args.interactive:
        # Interactive mode
        interactive_mode()
    else:
        # Default: run test cases
        print("💡 Usage examples:")
        print("  python3 test_model_accuracy.py --test-cases")
        print("  python3 test_model_accuracy.py --interactive")
        print('  python3 test_model_accuracy.py --text "John worked at Google as Engineer"')
        print("\nRunning default test cases...\n")
        run_test_cases()
