# ============================================================================
# GOOGLE COLAB - NER MODEL TESTING SCRIPT
# Quick test to verify your trained model works correctly
# ============================================================================

from google.colab import drive
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# Mount Google Drive
print("Mounting Google Drive...")
drive.mount('/content/drive')

# Load model from Drive
MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-CLEANED/resume-ner-deberta'

print(f"\nLoading model from: {MODEL_PATH}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

# Check GPU
device = 0 if torch.cuda.is_available() else -1
print(f"Using: {'GPU' if device == 0 else 'CPU'}")

# Create NER pipeline
ner = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple", device=device)

print("\n" + "="*70)
print("MODEL LOADED - RUNNING TEST")
print("="*70)

# Test resume text
test_text = """
John Smith worked as a Senior Software Engineer at Google from January 2020 
to December 2022 in Mountain View, California. He led projects for clients 
including Amazon and Microsoft.

Education:
Master of Science in Computer Science from Stanford University, 2018-2020, GPA 3.9
Bachelor of Technology in Software Engineering from MIT, 2014-2018, Grade 3.8
"""

print("\nTest Resume:")
print("-" * 70)
print(test_text)
print("-" * 70)

# Run NER
results = ner(test_text)

# Group by entity type
entities = {}
for r in results:
    etype = r['entity_group']
    if etype not in entities:
        entities[etype] = []
    entities[etype].append(f"{r['word']} ({r['score']:.2f})")

# Display results
print("\n" + "="*70)
print("EXTRACTED ENTITIES")
print("="*70)

for etype in sorted(entities.keys()):
    print(f"\n{etype}:")
    for text in entities[etype]:
        print(f"  - {text}")

# Expected entities
expected = {
    'PERSON_NAME': ['John Smith'],
    'ROLE': ['Senior Software Engineer'],
    'COMPANY': ['Google'],
    'DATE_START': ['January 2020'],
    'DATE_END': ['December 2022'],
    'LOCATION': ['Mountain View, California'],
    'CLIENT': ['Amazon', 'Microsoft'],
    'DEGREE': ['Master of Science', 'Bachelor of Technology'],
    'FIELD': ['Computer Science', 'Software Engineering'],
    'INSTITUTION': ['Stanford University', 'MIT'],
    'EDU_YEAR_START': ['2018', '2014'],
    'EDU_YEAR_END': ['2020', '2018'],
    'GRADE': ['3.9', '3.8']
}

# Count matches
total_expected = sum(len(v) for v in expected.values())
total_extracted = len(results)

print("\n" + "="*70)
print("QUICK ASSESSMENT")
print("="*70)
print(f"\nExpected entities: ~{total_expected}")
print(f"Extracted entities: {total_extracted}")

if total_extracted >= total_expected * 0.7:
    print("\n✅ Model is working! Extracting entities successfully.")
    print("✅ You can integrate this into your application.")
else:
    print("\n⚠️  Model extracted fewer entities than expected.")
    print("⚠️  May need retraining or data improvements.")

print("\n" + "="*70)
print("TRAINING F1 SCORE: 67.55%")
print("="*70)
print("\n⚠️  WARNING: F1 score is 67.55%, much lower than expected 90-92%!")
print("\nPossible reasons:")
print("1. ❌ Trained on wrong data (old dirty data instead of cleaned)")
print("2. ❌ Data cleaning didn't work properly")
print("3. ❌ Model needs more training epochs")
print("\n💡 RECOMMENDATION:")
print("   - Verify you uploaded the CLEANED ZIP file")
print("   - Check training logs showed 37,243 sentences (not 41,884)")
print("   - If wrong data was used, retrain with correct CLEANED ZIP")
print("\n" + "="*70)
