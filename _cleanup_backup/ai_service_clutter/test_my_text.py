#!/usr/bin/env python3
"""
Simple script to test model with your own text
Just paste your text and see what entities are extracted
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# Load model
model_path = "./models/resume-ner-deberta"
print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)

with open(os.path.join(model_path, "label_mappings.json"), 'r') as f:
    label_mappings = json.load(f)
id2label = {int(k): v for k, v in label_mappings['id2label'].items()}

print("✅ Model loaded!\n")
print("="*80)
print("Paste your text below and press Enter twice:")
print("="*80)

# Read input
lines = []
while True:
    try:
        line = input()
        if line.strip() == '' and lines:
            break
        if line.strip():
            lines.append(line)
    except EOFError:
        break

text = ' '.join(lines)

if not text:
    print("No text provided!")
    sys.exit(1)

print("\n" + "="*80)
print("INPUT TEXT:")
print("="*80)
print(text)
print("="*80)

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
    start, end = offset
    
    if start == end:
        continue
    
    actual_text = text[start:end]
    
    if label.startswith('B-'):
        if current_entity:
            entities.append({'text': current_text.strip(), 'label': current_label})
        current_label = label[2:]
        current_text = actual_text
        current_entity = True
    elif label.startswith('I-') and current_entity and label[2:] == current_label:
        current_text += actual_text
    else:
        if current_entity:
            entities.append({'text': current_text.strip(), 'label': current_label})
            current_entity = None
            current_text = ""
            current_label = None

if current_entity:
    entities.append({'text': current_text.strip(), 'label': current_label})

# Display results
print("\n" + "="*80)
print("EXTRACTED ENTITIES:")
print("="*80)

if entities:
    grouped = {}
    for entity in entities:
        label = entity['label']
        if label not in grouped:
            grouped[label] = []
        grouped[label].append(entity['text'])
    
    for label, texts in sorted(grouped.items()):
        print(f"\n✅ {label}:")
        for text in texts:
            print(f"   • {text}")
    
    print("\n" + "="*80)
    print(f"Total: {len(entities)} entities found")
    print("="*80)
else:
    print("❌ No entities found")
    print("="*80)
