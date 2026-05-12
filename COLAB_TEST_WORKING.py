# ============================================================================
# COLAB TEST SCRIPT - WORKING VERSION
# Copy this entire code into a Colab cell and run
# ============================================================================

# STEP 1: Install compatible packages (no numpy downgrade needed)
print("="*70)
print("STEP 1: INSTALLING PACKAGES")
print("="*70)
!pip install -q transformers==4.44.0 torch accelerate

print("✅ Packages installed!\n")
print("⚠️  IMPORTANT: Click 'Runtime' → 'Restart runtime' now!")
print("⚠️  Then run the code below in a NEW cell after restart.\n")

print("="*70)
print("COPY THE CODE BELOW INTO A NEW CELL AFTER RESTART:")
print("="*70)
print("""
# ============================================================================
# RUN THIS AFTER RESTARTING RUNTIME
# ============================================================================

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Load model
from transformers import pipeline
import torch

MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-CLEANED/resume-ner-deberta'

print("Loading model...")
device = 0 if torch.cuda.is_available() else -1
print(f"Using: {'GPU' if device == 0 else 'CPU'}")

ner = pipeline("ner", model=MODEL_PATH, aggregation_strategy="simple", device=device)
print("✅ Model loaded!\\n")

# Test resume
test_resume = \"\"\"
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
\"\"\"

print("="*70)
print("TEST RESUME:")
print("="*70)
print(test_resume)

print("\\n" + "="*70)
print("EXTRACTED ENTITIES:")
print("="*70)

# Run NER
results = ner(test_resume)

# Display results
for r in results:
    print(f"{r['entity_group']:20s} | {r['word']:30s} | Score: {r['score']:.2f}")

print("\\n" + "="*70)
print(f"Total entities extracted: {len(results)}")
print("="*70)

# Assessment
if len(results) >= 10:
    print("\\n✅ Model is working! Extracted entities successfully.")
    print("✅ You can use this model in your application.")
else:
    print("\\n⚠️  Model extracted fewer entities than expected.")
    print("⚠️  May need retraining or configuration adjustments.")

print("\\n📊 Training F1 Score: 67.55%")
print("⚠️  This means ~67% accuracy - consider retraining for better results.")
""")
