#!/usr/bin/env python3
"""Test what the model is actually predicting"""

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

model_path = "models/resume-ner-deberta"

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)

test_text = "I worked as a Junior Full Stack Developer at Infosys Ltd in Bangalore"

print(f"\n📝 Input: {test_text}\n")

inputs = tokenizer(test_text, return_tensors="pt", return_offsets_mapping=True)
offset_mapping = inputs.pop("offset_mapping")[0]

with torch.no_grad():
    outputs = model(**inputs)

predictions = torch.argmax(outputs.logits[0], dim=1)
tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

print("🔍 Token-by-token predictions:\n")
print(f"{'Token':<20} {'Label':<20} {'Text':<30}")
print("="*70)

for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
    if token in ['<s>', '</s>', '<pad>', '[CLS]', '[SEP]', '[PAD]']:
        continue
    
    label = model.config.id2label[pred_id.item()]
    start, end = offset
    
    if start == end:
        continue
    
    actual_text = test_text[start:end]
    print(f"{token:<20} {label:<20} {actual_text:<30}")

print("\n" + "="*70)
