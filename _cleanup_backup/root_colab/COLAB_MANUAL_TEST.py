# ============================================================================
# GOOGLE COLAB - MANUAL MODEL TESTING
# Simple pipeline-based testing for your NER model
# ============================================================================

# STEP 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# STEP 2: Install dependencies
print("Installing dependencies...")
get_ipython().system('pip install -q transformers torch')

# STEP 3: Load the model using pipeline
from transformers import pipeline

MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-New/resume-ner-deberta'

print("\n" + "="*70)
print("🤖 LOADING NER MODEL")
print("="*70)
print(f"📂 Model: {MODEL_PATH}\n")

ner_pipeline = pipeline(
    "ner",
    model=MODEL_PATH,
    aggregation_strategy="simple"
)

print("✅ Model loaded successfully!\n")

# ============================================================================
# TEST 1: WORK EXPERIENCE
# ============================================================================
print("="*70)
print("🧪 TEST 1: WORK EXPERIENCE")
print("="*70)

test1 = """John Smith worked at Infosys as Senior Data Engineer in Hyderabad from Jan 2021 to Mar 2023.
Client was Google."""

print("\n📝 Input Text:")
print(test1)
print("\n🔍 Extracted Entities:")
print("-"*70)

predictions1 = ner_pipeline(test1)
for pred in predictions1:
    print(f"{pred['entity_group']:20s} | {pred['word']:30s} | Score: {pred['score']:.3f}")

print()

# ============================================================================
# TEST 2: EDUCATION
# ============================================================================
print("="*70)
print("🧪 TEST 2: EDUCATION")
print("="*70)

test2 = """Education: B.Tech in Computer Science from JNTU Hyderabad, 2015-2019, Grade 8.2"""

print("\n📝 Input Text:")
print(test2)
print("\n🔍 Extracted Entities:")
print("-"*70)

predictions2 = ner_pipeline(test2)
for pred in predictions2:
    print(f"{pred['entity_group']:20s} | {pred['word']:30s} | Score: {pred['score']:.3f}")

print()

# ============================================================================
# TEST 3: COMBINED (WORK + EDUCATION)
# ============================================================================
print("="*70)
print("🧪 TEST 3: COMBINED WORK + EDUCATION")
print("="*70)

test3 = """Sarah Johnson worked at Microsoft as Senior Data Scientist in Seattle from January 2020 
to December 2022. Client was Amazon. She completed her Master of Science in Computer Science 
from Stanford University from 2018 to 2020 with a GPA of 3.95."""

print("\n📝 Input Text:")
print(test3)
print("\n🔍 Extracted Entities:")
print("-"*70)

predictions3 = ner_pipeline(test3)
for pred in predictions3:
    print(f"{pred['entity_group']:20s} | {pred['word']:30s} | Score: {pred['score']:.3f}")

print()

# ============================================================================
# TEST 4: MULTIPLE ROLES
# ============================================================================
print("="*70)
print("🧪 TEST 4: MULTIPLE ROLES")
print("="*70)

test4 = """David Kim served as Product Manager at Google from March 2021 to present in Mountain View. 
Previously, he was a Software Engineer at Facebook from June 2018 to February 2021 in Menlo Park."""

print("\n📝 Input Text:")
print(test4)
print("\n🔍 Extracted Entities:")
print("-"*70)

predictions4 = ner_pipeline(test4)
for pred in predictions4:
    print(f"{pred['entity_group']:20s} | {pred['word']:30s} | Score: {pred['score']:.3f}")

print()

# ============================================================================
# TEST 5: CONSULTING WITH CLIENTS
# ============================================================================
print("="*70)
print("🧪 TEST 5: CONSULTING WITH CLIENTS")
print("="*70)

test5 = """Emily Rodriguez worked as Management Consultant at McKinsey & Company from January 2019 
to August 2022 in New York. She delivered projects for clients including JPMorgan Chase and Goldman Sachs."""

print("\n📝 Input Text:")
print(test5)
print("\n🔍 Extracted Entities:")
print("-"*70)

predictions5 = ner_pipeline(test5)
for pred in predictions5:
    print(f"{pred['entity_group']:20s} | {pred['word']:30s} | Score: {pred['score']:.3f}")

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("="*70)
print("📊 TESTING SUMMARY")
print("="*70)
print()

all_predictions = [predictions1, predictions2, predictions3, predictions4, predictions5]
total_entities = sum(len(p) for p in all_predictions)
avg_confidence = sum(pred['score'] for preds in all_predictions for pred in preds) / total_entities if total_entities > 0 else 0

print(f"✅ Tests Completed: 5")
print(f"📊 Total Entities Extracted: {total_entities}")
print(f"🎯 Average Confidence: {avg_confidence:.1%}")
print()

# Confidence analysis
high_conf = sum(1 for preds in all_predictions for pred in preds if pred['score'] >= 0.9)
med_conf = sum(1 for preds in all_predictions for pred in preds if 0.7 <= pred['score'] < 0.9)
low_conf = sum(1 for preds in all_predictions for pred in preds if pred['score'] < 0.7)

print("Confidence Distribution:")
print(f"  🟢 High (≥90%):   {high_conf} entities ({high_conf/total_entities*100:.1f}%)")
print(f"  🟡 Medium (70-90%): {med_conf} entities ({med_conf/total_entities*100:.1f}%)")
print(f"  🔴 Low (<70%):     {low_conf} entities ({low_conf/total_entities*100:.1f}%)")
print()

# ============================================================================
# MANUAL TESTING SECTION
# ============================================================================
print("="*70)
print("✏️  MANUAL TESTING - ADD YOUR OWN TEXT")
print("="*70)
print()
print("Copy this code to test your own resume text:")
print()
print("""
# Your custom test
my_test = \"\"\"
Paste your resume text here...
\"\"\"

print("📝 Your Input:")
print(my_test)
print("\\n🔍 Extracted Entities:")
print("-"*70)

my_predictions = ner_pipeline(my_test)
for pred in my_predictions:
    print(f"{pred['entity_group']:20s} | {pred['word']:30s} | Score: {pred['score']:.3f}")
""")

print()
print("="*70)
print("🏁 TESTING COMPLETE")
print("="*70)
print()
print("💡 TIP: Review the extracted entities above")
print("   - Check if all important entities are captured")
print("   - Look at confidence scores (should be >80%)")
print("   - Test with your own resume texts")
print()
print("🎯 DECISION:")
if avg_confidence >= 0.80:
    print("   ✅ Model shows good confidence (≥80%)")
    print("   ✅ Consider using in your pipeline")
elif avg_confidence >= 0.70:
    print("   ⚠️  Model shows moderate confidence (70-80%)")
    print("   ⚠️  Use with human review")
else:
    print("   ❌ Model shows low confidence (<70%)")
    print("   ❌ Consider retraining")
print()
