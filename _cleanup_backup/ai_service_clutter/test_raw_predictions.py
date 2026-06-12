#!/usr/bin/env python3
"""
Test raw model predictions without aggregation.
"""

from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from pathlib import Path

MODEL_PATH = Path("models/resume-ner-deberta")

print("="*60)
print("🔍 Testing Raw Model Predictions")
print("="*60)

tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
model = AutoModelForTokenClassification.from_pretrained(str(MODEL_PATH))

sample_text = "John Smith is a Senior Software Engineer at Google. Email: john@email.com"

print(f"\n📝 Input text: {sample_text}")
print("\n" + "="*60)

# Tokenize
inputs = tokenizer(sample_text, return_tensors="pt", truncation=True, max_length=512)
print(f"✅ Tokenized into {len(inputs['input_ids'][0])} tokens")

# Get predictions
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=2)
    probabilities = torch.softmax(outputs.logits, dim=2)

# Decode predictions
tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
predicted_labels = [model.config.id2label[pred.item()] for pred in predictions[0]]
max_probs = [prob.max().item() for prob in probabilities[0]]

print("\n📊 Token-by-token predictions:")
print("="*60)
print(f"{'Token':<20} {'Predicted Label':<20} {'Confidence':<10}")
print("-"*60)

for token, label, prob in zip(tokens, predicted_labels, max_probs):
    if label != 'O':  # Only show non-O predictions
        print(f"{token:<20} {label:<20} {prob:.3f}")

print("\n" + "="*60)
print("\n📈 Label distribution:")
label_counts = {}
for label in predicted_labels:
    label_counts[label] = label_counts.get(label, 0) + 1

for label, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {label}: {count} tokens")
