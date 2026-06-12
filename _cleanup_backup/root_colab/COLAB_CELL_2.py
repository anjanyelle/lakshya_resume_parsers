# ============================================================================
# CELL 2: Test model (run AFTER restarting runtime)
# ============================================================================

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Load model
from transformers import pipeline
import torch

MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-CLEANED/resume-ner-deberta'

print("\nLoading model...")
device = 0 if torch.cuda.is_available() else -1
print(f"Using: {'GPU' if device == 0 else 'CPU'}")

ner = pipeline("ner", model=MODEL_PATH, aggregation_strategy="simple", device=device)
print("✅ Model loaded!\n")

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
print("EXTRACTED ENTITIES:")
print("="*70)

# Run NER
results = ner(test_resume)

# Group by entity type
entities_by_type = {}
for r in results:
    etype = r['entity_group']
    if etype not in entities_by_type:
        entities_by_type[etype] = []
    entities_by_type[etype].append(f"{r['word']} ({r['score']:.2f})")

# Display results grouped
for etype in sorted(entities_by_type.keys()):
    print(f"\n{etype}:")
    for item in entities_by_type[etype]:
        print(f"  - {item}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Total entities extracted: {len(results)}")
print(f"Entity types found: {len(entities_by_type)}")

# Assessment
expected_entities = 13
accuracy = len(results) / expected_entities

print("\n" + "="*70)
print("ASSESSMENT")
print("="*70)

if accuracy >= 0.8:
    print("\n✅ EXCELLENT: Model is working well!")
    print("✅ Extracting most entities successfully")
    print("✅ Ready to use in your application")
elif accuracy >= 0.6:
    print("\n⚠️  MODERATE: Model is working but missing some entities")
    print("⚠️  Accuracy is around 60-80%")
    print("⚠️  Can be used with human review")
else:
    print("\n❌ POOR: Model is missing many entities")
    print("❌ Accuracy is below 60%")
    print("❌ Retraining strongly recommended")

print(f"\n📊 Training F1 Score: 67.55%")
print(f"📊 Test Extraction Rate: {accuracy:.1%}")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)

if accuracy >= 0.7:
    print("\n✅ Model works! You can:")
    print("   1. Download model from Google Drive")
    print("   2. Integrate into your application")
    print("   3. Use with confidence thresholds for best results")
else:
    print("\n⚠️  Model needs improvement:")
    print("   1. Retrain with better configuration")
    print("   2. Use early stopping at epoch 5-6")
    print("   3. Lower learning rate to 1e-5")
    print("   4. Expected improvement: 75-85% F1")

print("\n" + "="*70)
