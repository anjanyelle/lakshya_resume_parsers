# ============================================================================
# SIMPLE COLAB TEST - Copy this entire cell and run in Colab
# ============================================================================

# Step 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Step 2: Install packages
!pip install -q transformers torch

# Step 3: Load model
from transformers import pipeline
import torch

MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-CLEANED/resume-ner-deberta'

print("Loading model...")
ner = pipeline("ner", model=MODEL_PATH, aggregation_strategy="simple", device=0 if torch.cuda.is_available() else -1)
print("✅ Model loaded!\n")

# Step 4: Test with sample resume
test_resume = """
John Smith
Senior Software Engineer at Google
January 2020 - December 2022
Mountain View, California

Led cloud infrastructure projects for clients including Amazon and Microsoft.

EDUCATION:
Master of Science in Computer Science
Stanford University, 2018-2020, GPA 3.9
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

# Display results
for r in results:
    print(f"{r['entity_group']:20s} | {r['word']:30s} | Score: {r['score']:.2f}")

print("\n" + "="*70)
print(f"Total entities extracted: {len(results)}")
print("="*70)

# Assessment
if len(results) >= 10:
    print("\n✅ Model is working! Extracted entities successfully.")
    print("✅ You can use this model in your application.")
else:
    print("\n⚠️  Model extracted fewer entities than expected.")
    print("⚠️  May need retraining or configuration adjustments.")

print("\n📊 Training F1 Score: 67.55%")
print("⚠️  This means ~67% accuracy - consider retraining for better results.")
