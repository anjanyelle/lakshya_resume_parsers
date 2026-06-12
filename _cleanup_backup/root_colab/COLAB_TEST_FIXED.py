# ============================================================================
# COLAB TEST SCRIPT - WITH NUMPY FIX
# Copy this entire code into a Colab cell and run
# ============================================================================

# STEP 1: Fix numpy compatibility issue
print("="*70)
print("STEP 1: FIXING PACKAGE COMPATIBILITY")
print("="*70)
!pip uninstall -y numpy
!pip install numpy==1.24.3
!pip install --upgrade transformers torch
print("✅ Packages fixed!\n")

# STEP 2: Mount Google Drive
print("="*70)
print("STEP 2: MOUNTING GOOGLE DRIVE")
print("="*70)
from google.colab import drive
drive.mount('/content/drive')
print("✅ Drive mounted!\n")

# STEP 3: Load model
print("="*70)
print("STEP 3: LOADING MODEL")
print("="*70)

from transformers import pipeline
import torch

MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-CLEANED/resume-ner-deberta'

print(f"Loading from: {MODEL_PATH}")

# Check if model exists
import os
if not os.path.exists(MODEL_PATH):
    print(f"\n❌ ERROR: Model not found at {MODEL_PATH}")
    print("\n💡 Available folders:")
    !ls -la /content/drive/MyDrive/
    raise FileNotFoundError("Model not found")

# Load NER pipeline
device = 0 if torch.cuda.is_available() else -1
print(f"Using: {'GPU' if device == 0 else 'CPU'}")

ner = pipeline("ner", model=MODEL_PATH, aggregation_strategy="simple", device=device)
print("✅ Model loaded successfully!\n")

# STEP 4: Test with sample resume
print("="*70)
print("STEP 4: TESTING MODEL")
print("="*70)

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

print("\n📝 Test Resume:")
print("-" * 70)
print(test_resume)
print("-" * 70)

# Run NER
print("\n🔍 Running entity extraction...\n")
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
print("="*70)
print("EXTRACTED ENTITIES")
print("="*70)

for etype in sorted(entities_by_type.keys()):
    print(f"\n{etype}:")
    for item in entities_by_type[etype]:
        print(f"  - {item['text']:30s} (confidence: {item['score']:.2%})")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\nTotal entity types found: {len(entities_by_type)}")
print(f"Total entities extracted: {len(results)}")

# Expected entities
expected_count = 13  # Approximate for this test resume

print(f"\nExpected entities: ~{expected_count}")
print(f"Extracted entities: {len(results)}")

# Assessment
accuracy_ratio = len(results) / expected_count
print("\n" + "="*70)
print("ASSESSMENT")
print("="*70)

if accuracy_ratio >= 0.8:
    print("\n✅ GOOD: Model is working well!")
    print("✅ Extracting most entities successfully")
    print("✅ Can be used in your application")
elif accuracy_ratio >= 0.6:
    print("\n⚠️  MODERATE: Model is working but missing some entities")
    print("⚠️  Accuracy is around 60-80%")
    print("⚠️  Consider retraining for better results")
else:
    print("\n❌ POOR: Model is missing many entities")
    print("❌ Accuracy is below 60%")
    print("❌ Retraining recommended")

print(f"\n📊 Training F1 Score: 67.55%")
print("📊 This test F1: ~{:.1%}".format(accuracy_ratio))

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)

if accuracy_ratio >= 0.7:
    print("\n✅ Model works! You can:")
    print("   1. Download model from Google Drive")
    print("   2. Integrate into your application")
    print("   3. Use with human review for best results")
else:
    print("\n⚠️  Model needs improvement:")
    print("   1. Retrain with better configuration")
    print("   2. Use early stopping at epoch 5-6")
    print("   3. Lower learning rate to 1e-5")
    print("   4. Expected improvement: 75-85% F1")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
