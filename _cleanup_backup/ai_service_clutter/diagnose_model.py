#!/usr/bin/env python3
"""
Detailed diagnostic to see token-level predictions
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

# Test text with dates
text = "Anjan Yelle worked at Infosys Ltd as Senior Software Engineer from Jan 2021 to Mar 2023 in Bangalore. He completed Bachelor of Technology from JNTU Hyderabad."

print("="*100)
print("INPUT TEXT:")
print("="*100)
print(text)
print("="*100)

# Get predictions
inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, return_offsets_mapping=True)
offset_mapping = inputs.pop("offset_mapping")[0]

with torch.no_grad():
    outputs = model(**inputs)

predictions = torch.argmax(outputs.logits, dim=2)[0]
probabilities = torch.softmax(outputs.logits, dim=2)[0]
tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

print("\n" + "="*100)
print("DETAILED TOKEN-LEVEL PREDICTIONS:")
print("="*100)
print(f"{'Token':<25} {'Actual Text':<30} {'Prediction':<20} {'Confidence':<10}")
print("-"*100)

for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
    if token in ['<s>', '</s>', '<pad>']:
        continue
    
    label = id2label[pred_id.item()]
    confidence = probabilities[idx][pred_id].item()
    
    start, end = offset
    if start == end:
        continue
    
    actual_text = text[start:end]
    
    # Highlight non-O predictions
    if label != 'O':
        print(f"{token:<25} {actual_text:<30} {label:<20} {confidence:.2%}")
    else:
        # Show O predictions for date-related words
        if any(word in actual_text.lower() for word in ['jan', 'mar', '2021', '2023', 'from', 'to', 'jntu', 'hyderabad', 'anjan', 'yelle']):
            print(f"{token:<25} {actual_text:<30} {label:<20} {confidence:.2%}")

print("-"*100)

# Show what labels exist in the model
print("\n" + "="*100)
print("AVAILABLE LABELS IN MODEL:")
print("="*100)
unique_labels = sorted(set(id2label.values()))
for label in unique_labels:
    print(f"  • {label}")

print("\n" + "="*100)
print("ANALYSIS:")
print("="*100)

# Check if date labels exist
date_labels = [l for l in unique_labels if 'DATE' in l]
edu_labels = [l for l in unique_labels if 'EDUCATION' in l]

print(f"\n✅ Date-related labels found: {date_labels}")
print(f"✅ Education-related labels found: {edu_labels}")

print("\n🔍 ISSUES DETECTED:")
issues = []

# Check for person name being tagged as COMPANY
if any(pred == 'B-COMPANY' for pred in [id2label[p.item()] for p in predictions]):
    issues.append("❌ Person names are being tagged as COMPANY (e.g., 'Anjan Yelle')")

# Check if dates are being predicted
date_found = any('DATE' in id2label[p.item()] for p in predictions)
if not date_found and ('2021' in text or '2023' in text):
    issues.append("❌ Dates (Jan 2021, Mar 2023) are NOT being detected as START_DATE/END_DATE")

# Check if education institution is being predicted
edu_found = any('EDUCATION' in id2label[p.item()] for p in predictions)
if not edu_found and 'JNTU' in text:
    issues.append("❌ Education institution (JNTU Hyderabad) is NOT being detected as EDUCATION")

if issues:
    for issue in issues:
        print(f"  {issue}")
else:
    print("  ✅ No major issues detected")

print("\n" + "="*100)
print("POSSIBLE CAUSES:")
print("="*100)
print("""
1. Training Data Issue:
   - The model may not have seen enough examples of dates in "Jan 2021" format
   - Person names at the start of sentences might be confused with company names
   - Education institutions might not have been labeled properly in training data

2. Model Confusion:
   - Person names (Anjan Yelle) appearing before "worked at" are being tagged as COMPANY
   - Date formats like "Jan 2021" or "2021" might not match training data format
   - Education institutions need context words like "from" to be detected

3. Label Distribution:
   - Some labels might be underrepresented in training data
   - Model might be biased toward more common labels (COMPANY, ROLE, DEGREE)
""")

print("\n" + "="*100)
print("RECOMMENDATIONS:")
print("="*100)
print("""
1. Check Training Data:
   - Verify that START_DATE and END_DATE are properly labeled
   - Ensure person names are NOT labeled as entities
   - Confirm EDUCATION institutions are labeled correctly

2. Retrain with More Examples:
   - Add more examples with date formats: "Jan 2021", "2021-2023", "from 2020 to 2023"
   - Add examples where person names appear at sentence start
   - Add more education institution examples

3. Post-Processing Rules:
   - Add rule to remove person names from COMPANY predictions
   - Add regex patterns to detect dates if model misses them
   - Add known education institution list for fallback
""")

print("="*100)
