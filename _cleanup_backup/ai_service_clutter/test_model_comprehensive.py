#!/usr/bin/env python3
"""
Comprehensive test to verify the retrained model is working correctly.
"""

import json
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch
from pathlib import Path
from collections import Counter

MODEL_PATH = Path("models/resume-ner-deberta")

print("="*70)
print("🧪 COMPREHENSIVE MODEL TEST")
print("="*70)

# Test 1: Model Loading
print("\n1️⃣ TEST: Model Loading")
print("-"*70)
try:
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model = AutoModelForTokenClassification.from_pretrained(str(MODEL_PATH))
    print("✅ Model loaded successfully")
    print(f"   - Number of labels: {model.config.num_labels}")
    print(f"   - Label mapping: {model.config.id2label}")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    exit(1)

# Test 2: Check Training Data Distribution
print("\n2️⃣ TEST: Training Data Label Distribution")
print("-"*70)
try:
    with open('training/data/train.json', 'r') as f:
        train_data = json.load(f)
    
    all_labels = []
    for example in train_data:
        all_labels.extend(example['ner_tags'])
    
    label_counts = Counter(all_labels)
    total_tokens = len(all_labels)
    
    print(f"Total training examples: {len(train_data)}")
    print(f"Total tokens: {total_tokens}")
    print("\nLabel distribution:")
    for label_id in sorted(label_counts.keys()):
        count = label_counts[label_id]
        percentage = (count / total_tokens) * 100
        label_name = model.config.id2label.get(label_id, f"Unknown-{label_id}")
        print(f"   {label_id:2d} ({label_name:20s}): {count:6d} tokens ({percentage:5.2f}%)")
    
    # Check for class imbalance
    non_o_count = sum(count for label_id, count in label_counts.items() if label_id != 0)
    o_count = label_counts.get(0, 0)
    imbalance_ratio = o_count / non_o_count if non_o_count > 0 else float('inf')
    
    if imbalance_ratio > 10:
        print(f"\n⚠️  WARNING: High class imbalance detected!")
        print(f"   O labels: {o_count} ({(o_count/total_tokens)*100:.1f}%)")
        print(f"   Non-O labels: {non_o_count} ({(non_o_count/total_tokens)*100:.1f}%)")
        print(f"   Imbalance ratio: {imbalance_ratio:.1f}:1")
    else:
        print(f"\n✅ Class balance is reasonable (ratio: {imbalance_ratio:.1f}:1)")
       
except Exception as e:
    print(f"❌ Failed to analyze training data: {e}")

# Test 3: Raw Predictions on Sample Text
print("\n3️⃣ TEST: Raw Model Predictions")
print("-"*70)

test_samples = [
    "John Smith",
    "Email: john.smith@email.com",
    "Phone: +1-555-0123",
    "Senior Software Engineer at Google",
    "Stanford University - BS Computer Science",
    "Skills: Python, Java, AWS, Docker"
]

for sample_text in test_samples:
    inputs = tokenizer(sample_text, return_tensors="pt", truncation=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=2)
        probabilities = torch.softmax(outputs.logits, dim=2)
    
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    predicted_labels = [model.config.id2label[pred.item()] for pred in predictions[0]]
    max_probs = [prob.max().item() for prob in probabilities[0]]
    
    # Count non-O predictions
    non_o_predictions = [label for label in predicted_labels if label != 'O']
    
    print(f"\nText: '{sample_text}'")
    print(f"  Tokens: {len(tokens)}")
    print(f"  Non-O predictions: {len(non_o_predictions)}")
    
    if non_o_predictions:
        print(f"  Predicted entities:")
        for token, label, prob in zip(tokens, predicted_labels, max_probs):
            if label != 'O':
                print(f"    - {token:15s} → {label:20s} (confidence: {prob:.3f})")
    else:
        # Show top 3 predictions for first token to see what model is considering
        first_token_probs = probabilities[0][1]  # Skip [CLS] token
        top_3_indices = torch.topk(first_token_probs, 3).indices
        print(f"  Top 3 predictions for first content token '{tokens[1]}':")
        for idx in top_3_indices:
            label = model.config.id2label[idx.item()]
            prob = first_token_probs[idx].item()
            print(f"    - {label:20s}: {prob:.3f}")

# Test 4: Pipeline Test
print("\n4️⃣ TEST: HuggingFace Pipeline")
print("-"*70)

device = 0 if torch.cuda.is_available() else -1
ner_pipeline = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple",
    device=device,
)

full_resume_text = """
VARUN KRISHNA
Senior Big Data Engineer
Hyderabad, TS • +91 98765 43210 • varun.krishna.data@gmail.com

PROFESSIONAL SUMMARY
Results-driven Senior Big Data Engineer with 10+ years of experience.

SKILLS
Python, Java, AWS, Azure, Spark, Hadoop, Kafka
"""

print(f"Testing with resume text ({len(full_resume_text)} chars)...")
results = ner_pipeline(full_resume_text)

print(f"\nPipeline found {len(results)} entities:")
if results:
    for i, ent in enumerate(results[:10], 1):  # Show first 10
        print(f"  {i}. '{ent['word']}' → {ent['entity_group']} (score: {ent['score']:.3f})")
    if len(results) > 10:
        print(f"  ... and {len(results) - 10} more entities")
else:
    print("  ⚠️  No entities detected by pipeline")

# Test 5: Model vs Training Data Sanity Check
print("\n5️⃣ TEST: Model Predictions on Training Example")
print("-"*70)

# Take first training example
first_example = train_data[0]
sample_tokens = first_example['tokens'][:20]  # First 20 tokens
sample_labels = first_example['ner_tags'][:20]

# Join tokens to create text
sample_text = " ".join(sample_tokens)

print(f"Training example text: '{sample_text}'")
print(f"\nExpected labels (from training data):")
for token, label_id in zip(sample_tokens, sample_labels):
    label_name = model.config.id2label[label_id]
    if label_id != 0:
        print(f"  {token:15s} → {label_name}")

# Get model predictions
inputs = tokenizer(sample_text, return_tensors="pt", truncation=True)
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=2)

pred_tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
predicted_labels = [model.config.id2label[pred.item()] for pred in predictions[0]]

print(f"\nModel predictions:")
non_o_found = False
for token, label in zip(pred_tokens[1:-1], predicted_labels[1:-1]):  # Skip special tokens
    if label != 'O':
        print(f"  {token:15s} → {label}")
        non_o_found = True

if not non_o_found:
    print("  ⚠️  Model predicted all tokens as 'O'")

# Final Summary
print("\n" + "="*70)
print("📊 TEST SUMMARY")
print("="*70)

if len(results) > 0:
    print("✅ Model is working and detecting entities")
elif non_o_found:
    print("⚠️  Model makes some predictions but pipeline filters them out")
    print("   → Check confidence thresholds in pipeline")
else:
    print("❌ Model is NOT working correctly")
    print("   → Model predicts everything as 'O' (no entity)")
    print("   → Possible issues:")
    print("      1. Training didn't converge")
    print("      2. Class imbalance too severe")
    print("      3. Learning rate too high/low")
    print("      4. Dataset quality issues")

print("="*70)
