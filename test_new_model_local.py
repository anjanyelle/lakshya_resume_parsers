#!/usr/bin/env python3
"""
Test the new trained model locally before replacing production model
"""

from transformers import pipeline
import sys

# Test with the NEW model
NEW_MODEL_PATH = "ai-service/models-test/resume-ner-deberta"  # Change this to your test location
# OLD_MODEL_PATH = "ai-service/models/resume-ner-deberta"  # Your current production model

print("="*70)
print("🧪 TESTING NEW MODEL LOCALLY")
print("="*70)
print()

try:
    print(f"📂 Loading model from: {NEW_MODEL_PATH}")
    ner_pipeline = pipeline(
        "ner",
        model=NEW_MODEL_PATH,
        aggregation_strategy="simple"
    )
    print("✅ Model loaded successfully!\n")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("\n💡 Make sure you:")
    print("   1. Downloaded the model from Google Drive")
    print("   2. Extracted the ZIP file")
    print("   3. Updated NEW_MODEL_PATH in this script")
    sys.exit(1)

# Test cases
test_cases = [
    {
        "name": "Work Experience",
        "text": """John Smith worked at Infosys as Senior Data Engineer in Hyderabad from Jan 2021 to Mar 2023. Client was Google."""
    },
    {
        "name": "Education",
        "text": """Education: B.Tech in Computer Science from JNTU Hyderabad, 2015-2019, Grade 8.2"""
    },
    {
        "name": "Multiple Roles",
        "text": """Sarah Johnson worked at Microsoft as Senior Data Scientist in Seattle from January 2020 to December 2022. Client was Amazon."""
    }
]

print("="*70)
print("🧪 RUNNING TESTS")
print("="*70)
print()

all_predictions = []

for i, test in enumerate(test_cases, 1):
    print(f"TEST {i}: {test['name']}")
    print("-" * 70)
    print(f"📝 Input: {test['text'][:80]}...")
    print()
    
    predictions = ner_pipeline(test['text'])
    all_predictions.extend(predictions)
    
    if predictions:
        print(f"🔍 Extracted {len(predictions)} entities:")
        for pred in predictions:
            confidence_color = "🟢" if pred['score'] >= 0.9 else "🟡" if pred['score'] >= 0.7 else "🔴"
            print(f"  {confidence_color} [{pred['entity_group']:20s}] {pred['word']:30s} | {pred['score']:.1%}")
    else:
        print("  ⚠️  No entities extracted")
    
    print()

# Summary
print("="*70)
print("📊 SUMMARY")
print("="*70)
print()

if all_predictions:
    total = len(all_predictions)
    high_conf = sum(1 for p in all_predictions if p['score'] >= 0.9)
    med_conf = sum(1 for p in all_predictions if 0.7 <= p['score'] < 0.9)
    low_conf = sum(1 for p in all_predictions if p['score'] < 0.7)
    avg_conf = sum(p['score'] for p in all_predictions) / total
    
    print(f"✅ Total entities extracted: {total}")
    print(f"🎯 Average confidence: {avg_conf:.1%}")
    print()
    print(f"Confidence distribution:")
    print(f"  🟢 High (≥90%):     {high_conf} ({high_conf/total*100:.1f}%)")
    print(f"  🟡 Medium (70-90%): {med_conf} ({med_conf/total*100:.1f}%)")
    print(f"  🔴 Low (<70%):      {low_conf} ({low_conf/total*100:.1f}%)")
    print()
    
    print("="*70)
    print("🎯 RECOMMENDATION")
    print("="*70)
    print()
    
    if avg_conf >= 0.80:
        print("✅ Model shows good confidence (≥80%)")
        print("✅ You can replace your production model")
        print()
        print("📝 Next steps:")
        print("   1. Backup current model:")
        print("      mv ai-service/models/resume-ner-deberta ai-service/models/resume-ner-deberta-backup")
        print("   2. Move new model:")
        print("      mv ai-service/models-test/resume-ner-deberta ai-service/models/")
        print("   3. Test your full application")
    elif avg_conf >= 0.70:
        print("⚠️  Model shows moderate confidence (70-80%)")
        print("⚠️  Consider improving before replacing production model")
        print()
        print("💡 Options:")
        print("   1. Use it with human review")
        print("   2. Add more training data and retrain")
        print("   3. Keep current model for now")
    else:
        print("❌ Model shows low confidence (<70%)")
        print("❌ DO NOT replace production model")
        print()
        print("💡 Recommended actions:")
        print("   1. Add significantly more training examples")
        print("   2. Improve label quality")
        print("   3. Retrain the model")
        print("   4. Keep using your current model")
else:
    print("❌ No entities were extracted in any test")
    print("❌ Model may have issues - do not use in production")

print()
print("="*70)
print("🏁 TESTING COMPLETE")
print("="*70)
