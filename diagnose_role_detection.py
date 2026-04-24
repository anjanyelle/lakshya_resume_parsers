#!/usr/bin/env python3
"""
Diagnostic script to analyze why DeBERTa model only detects ~50% of roles.
Tests the model directly and shows confidence scores for each prediction.
"""

import sys
sys.path.insert(0, 'ai-service')

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Load model
MODEL_PATH = "ai-service/models/resume-ner-deberta"

print("=" * 80)
print("ROLE DETECTION DIAGNOSTIC")
print("=" * 80)

print(f"\n📦 Loading model from: {MODEL_PATH}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

# Load label mappings
import json
with open(f"{MODEL_PATH}/label_mappings.json", 'r') as f:
    label_data = json.load(f)
    id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}

print(f"✅ Model loaded with {len(id_to_label)} labels")

# Test texts
test_cases = [
    {
        "name": "Test 1: 4 Jobs",
        "text": """Senior Software Engineer @ Amazon | Seattle, WA | March 2022 - Present
Software Engineer @ Microsoft | Redmond, WA | June 2019 - February 2022
Software Developer @ IBM | Bangalore, India | July 2016 - May 2019
Junior Software Engineer @ Infosys | Hyderabad, India | June 2014 - June 2016""",
        "expected_roles": ["Senior Software Engineer", "Software Engineer", "Software Developer", "Junior Software Engineer"],
        "expected_companies": ["Amazon", "Microsoft", "IBM", "Infosys"]
    },
    {
        "name": "Test 2: 2 Jobs",
        "text": """Senior Software Engineer @ Amazon | Seattle, WA | March 2022 - Present
Software Engineer @ Microsoft | Redmond, WA | June 2019 - February 2022""",
        "expected_roles": ["Senior Software Engineer", "Software Engineer"],
        "expected_companies": ["Amazon", "Microsoft"]
    }
]

for test_case in test_cases:
    print("\n" + "=" * 80)
    print(f"🧪 {test_case['name']}")
    print("=" * 80)
    
    text = test_case['text']
    expected_roles = test_case['expected_roles']
    expected_companies = test_case['expected_companies']
    
    print(f"\n📝 Input text ({len(text)} chars):")
    print(f"{text}\n")
    
    print(f"Expected to find:")
    print(f"  Roles: {len(expected_roles)} - {expected_roles}")
    print(f"  Companies: {len(expected_companies)} - {expected_companies}")
    
    # Tokenize
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
        return_offsets_mapping=True
    )
    offset_mapping = inputs.pop("offset_mapping")[0]
    
    # Predict
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits[0]
    probabilities = torch.softmax(logits, dim=1)
    predictions = torch.argmax(logits, dim=1)
    confidences = torch.max(probabilities, dim=1)[0]
    
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    
    # Analyze predictions
    print(f"\n🔍 Model Predictions:")
    
    role_tokens = []
    company_tokens = []
    all_entity_tokens = []
    
    for idx, (token, pred_id, confidence, offset) in enumerate(zip(tokens, predictions, confidences, offset_mapping)):
        if token in ['<s>', '</s>', '<pad>', '[CLS]', '[SEP]', '[PAD]']:
            continue
        
        label = id_to_label[pred_id.item()]
        start, end = offset
        
        if start == end:
            continue
        
        actual_text = text[start:end]
        
        if label != 'O':
            all_entity_tokens.append({
                'token': token,
                'text': actual_text,
                'label': label,
                'confidence': confidence.item(),
                'position': start
            })
            
            if 'ROLE' in label:
                role_tokens.append({
                    'token': token,
                    'text': actual_text,
                    'label': label,
                    'confidence': confidence.item(),
                    'position': start
                })
            elif 'COMPANY' in label:
                company_tokens.append({
                    'token': token,
                    'text': actual_text,
                    'label': label,
                    'confidence': confidence.item(),
                    'position': start
                })
    
    # Group tokens into entities
    def group_tokens_into_entities(tokens_list):
        entities = []
        current_entity = None
        current_text = ""
        current_label = None
        
        for t in tokens_list:
            if t['label'].startswith('B-'):
                if current_entity:
                    entities.append({'text': current_text.strip(), 'label': current_label})
                current_text = t['text']
                current_label = t['label'][2:]
                current_entity = t
            elif t['label'].startswith('I-') and current_entity:
                current_text += t['text']
            else:
                if current_entity:
                    entities.append({'text': current_text.strip(), 'label': current_label})
                current_entity = None
                current_text = ""
        
        if current_entity:
            entities.append({'text': current_text.strip(), 'label': current_label})
        
        return entities
    
    role_entities = group_tokens_into_entities(role_tokens)
    company_entities = group_tokens_into_entities(company_tokens)
    
    print(f"\n👔 ROLE Entities Detected: {len(role_entities)}/{len(expected_roles)}")
    for i, entity in enumerate(role_entities, 1):
        print(f"  {i}. {entity['text']}")
    
    if len(role_entities) < len(expected_roles):
        print(f"\n  ❌ MISSING {len(expected_roles) - len(role_entities)} ROLES:")
        detected_texts = [e['text'] for e in role_entities]
        for expected in expected_roles:
            if expected not in detected_texts:
                print(f"     - {expected}")
    
    print(f"\n🏢 COMPANY Entities Detected: {len(company_entities)}/{len(expected_companies)}")
    for i, entity in enumerate(company_entities, 1):
        print(f"  {i}. {entity['text']}")
    
    # Show all entity tokens with confidence
    print(f"\n📊 All Entity Predictions (with confidence):")
    for t in all_entity_tokens[:50]:  # First 50 tokens
        print(f"  {t['text']:20s} → {t['label']:20s} (confidence: {t['confidence']:.3f})")
    
    # Analyze confidence distribution
    if all_entity_tokens:
        confidences_list = [t['confidence'] for t in all_entity_tokens]
        avg_confidence = sum(confidences_list) / len(confidences_list)
        min_confidence = min(confidences_list)
        max_confidence = max(confidences_list)
        
        print(f"\n📈 Confidence Statistics:")
        print(f"  Average: {avg_confidence:.3f}")
        print(f"  Min: {min_confidence:.3f}")
        print(f"  Max: {max_confidence:.3f}")
        
        # Count low confidence predictions
        low_conf = sum(1 for c in confidences_list if c < 0.5)
        med_conf = sum(1 for c in confidences_list if 0.5 <= c < 0.8)
        high_conf = sum(1 for c in confidences_list if c >= 0.8)
        
        print(f"  Low (<0.5): {low_conf}")
        print(f"  Medium (0.5-0.8): {med_conf}")
        print(f"  High (≥0.8): {high_conf}")
    
    # Check if text was truncated
    if len(tokens) >= 1024:
        print(f"\n⚠️  WARNING: Text was truncated at 1024 tokens!")
        print(f"   This may cause missing entities at the end of the text.")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
