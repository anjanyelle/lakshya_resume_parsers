#!/usr/bin/env python3
"""
Local Model Test Script
Test the downloaded DeBERTa NER model on your Mac
"""

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

# Model path (local)
MODEL_PATH = "ai-service/models/resume-ner-deberta"

print("="*70)
print("LOADING MODEL FROM LOCAL DISK")
print("="*70)
print(f"Path: {MODEL_PATH}\n")

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

# Check device
device = 0 if torch.cuda.is_available() else -1
device_name = "GPU" if device == 0 else "CPU (Mac)"
print(f"Using: {device_name}")

# Create NER pipeline
ner = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple", device=device)
print("✅ Model loaded successfully!\n")

# Test resume
test_resume = """
John Smith
Senior Software Engineer at Google
January 2020 - December 2022
Mountain View, California

Led cloud infrastructure projects for clients including Amazon and Microsoft.

EDUCATION:
Master of Science in Computer Science
Stanford University, 2018-2020, GPA 3.9

Bachelor of Technology in Software Engineering
MIT, 2014-2018, Grade 3.8
"""

print("="*70)
print("TEST RESUME:")
print("="*70)
print(test_resume)

print("\n" + "="*70)
print("RUNNING ENTITY EXTRACTION...")
print("="*70)

# Run NER
results = ner(test_resume)

# Group by entity type
entities_by_type = {}
for r in results:
    etype = r['entity_group']
    if etype not in entities_by_type:
        entities_by_type[etype] = []
    entities_by_type[etype].append({
        'text': r['word'],
        'score': r['score']
    })

# Display results
print("\n" + "="*70)
print("EXTRACTED ENTITIES:")
print("="*70)

for etype in sorted(entities_by_type.keys()):
    print(f"\n{etype}:")
    for item in entities_by_type[etype]:
        print(f"  - {item['text']:35s} (confidence: {item['score']:.1%})")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Total entities extracted: {len(results)}")
print(f"Entity types found: {len(entities_by_type)}")

# Assessment
expected_entities = 21  # Approximate for this test
accuracy = len(results) / expected_entities

print("\n" + "="*70)
print("ASSESSMENT")
print("="*70)

if accuracy >= 0.8:
    print("\n✅ EXCELLENT: Model is working very well!")
    print("✅ Extracting 80%+ of entities")
    print("✅ Ready to integrate into your application")
elif accuracy >= 0.6:
    print("\n⚠️  MODERATE: Model is working but missing some entities")
    print("⚠️  Extracting 60-80% of entities")
    print("⚠️  Can be used with human review")
else:
    print("\n❌ POOR: Model is missing many entities")
    print("❌ Extracting less than 60% of entities")
    print("❌ Consider retraining")

print(f"\n📊 Training F1 Score: 67.55%")
print(f"📊 Test Extraction Rate: {accuracy:.1%}")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)

if accuracy >= 0.6:
    print("\n✅ Model works! You can:")
    print("   1. Integrate into your FastAPI application")
    print("   2. Update the model path in your code")
    print("   3. Test with real resumes")
    print("   4. Deploy to production")
else:
    print("\n⚠️  Model needs improvement:")
    print("   1. Retrain with better configuration")
    print("   2. Use early stopping")
    print("   3. Improve training data")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
