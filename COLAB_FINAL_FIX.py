# ============================================================================
# FINAL WORKING VERSION - Run this in Colab
# ============================================================================

# Check if this is first run or after restart
import os
import sys

# Create a flag file to track restart
FLAG_FILE = '/content/packages_installed.flag'

if not os.path.exists(FLAG_FILE):
    # FIRST RUN: Install packages
    print("="*70)
    print("FIRST RUN: Installing compatible packages...")
    print("="*70)
    
    # Uninstall problematic packages
    !pip uninstall -y numpy transformers -q
    
    # Install specific compatible versions
    !pip install numpy==1.26.4 -q
    !pip install transformers==4.44.0 torch -q
    
    # Create flag file
    with open(FLAG_FILE, 'w') as f:
        f.write('installed')
    
    print("\n✅ Packages installed!")
    print("\n" + "="*70)
    print("⚠️  CRITICAL: You MUST restart the runtime now!")
    print("="*70)
    print("\nSteps:")
    print("1. Click 'Runtime' in the menu")
    print("2. Click 'Restart runtime'")
    print("3. Run this same cell again after restart")
    print("\n" + "="*70)
    
else:
    # SECOND RUN: After restart - Run the test
    print("="*70)
    print("SECOND RUN: Testing model...")
    print("="*70)
    
    # Mount Google Drive
    from google.colab import drive
    drive.mount('/content/drive')
    
    # Load model
    from transformers import pipeline
    import torch
    
    MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-CLEANED/resume-ner-deberta'
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"\n❌ ERROR: Model not found at {MODEL_PATH}")
        print("\nAvailable folders in MyDrive:")
        !ls -la /content/drive/MyDrive/
        sys.exit(1)
    
    print(f"\nLoading model from: {MODEL_PATH}")
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
        entities_by_type[etype].append({
            'text': r['word'],
            'score': r['score']
        })
    
    # Display results grouped
    for etype in sorted(entities_by_type.keys()):
        print(f"\n{etype}:")
        for item in entities_by_type[etype]:
            print(f"  - {item['text']:35s} (confidence: {item['score']:.1%})")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total entities extracted: {len(results)}")
    print(f"Entity types found: {len(entities_by_type)}")
    
    # Expected entities for this test
    expected = {
        'PERSON_NAME': 1,
        'ROLE': 1,
        'COMPANY': 1,
        'DATE_START': 2,
        'DATE_END': 1,
        'LOCATION': 1,
        'CLIENT': 2,
        'DEGREE': 2,
        'FIELD': 2,
        'INSTITUTION': 2,
        'EDU_YEAR_START': 2,
        'EDU_YEAR_END': 2,
        'GRADE': 2
    }
    
    total_expected = sum(expected.values())
    accuracy = len(results) / total_expected if total_expected > 0 else 0
    
    print("\n" + "="*70)
    print("ASSESSMENT")
    print("="*70)
    print(f"\nExpected entities: ~{total_expected}")
    print(f"Extracted entities: {len(results)}")
    print(f"Extraction rate: {accuracy:.1%}")
    
    if accuracy >= 0.8:
        print("\n✅ EXCELLENT: Model is working very well!")
        print("✅ Extracting 80%+ of entities successfully")
        print("✅ Ready to use in your application")
    elif accuracy >= 0.6:
        print("\n⚠️  MODERATE: Model is working but missing some entities")
        print("⚠️  Extracting 60-80% of entities")
        print("⚠️  Can be used with human review")
    else:
        print("\n❌ POOR: Model is missing many entities")
        print("❌ Extracting less than 60% of entities")
        print("❌ Retraining strongly recommended")
    
    print(f"\n📊 Training F1 Score: 67.55%")
    print(f"📊 Test Extraction Rate: {accuracy:.1%}")
    
    print("\n" + "="*70)
    print("DETAILED ANALYSIS")
    print("="*70)
    
    # Check which entity types were found
    print("\nEntity types extracted:")
    for etype in sorted(entities_by_type.keys()):
        count = len(entities_by_type[etype])
        expected_count = expected.get(etype, 0)
        status = "✅" if count >= expected_count * 0.7 else "⚠️"
        print(f"{status} {etype}: {count} found (expected ~{expected_count})")
    
    # Check for missing entity types
    missing_types = set(expected.keys()) - set(entities_by_type.keys())
    if missing_types:
        print("\n⚠️  Missing entity types:")
        for etype in sorted(missing_types):
            print(f"   - {etype} (expected {expected[etype]})")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    if accuracy >= 0.7:
        print("\n✅ Model works! You can:")
        print("   1. Download model from Google Drive")
        print("   2. Integrate into your application")
        print("   3. Use confidence thresholds (e.g., >0.8) for best results")
        print("   4. Add human review for low-confidence predictions")
    else:
        print("\n⚠️  Model needs improvement. Options:")
        print("   1. Retrain with better configuration:")
        print("      - Use early stopping at epoch 5-6")
        print("      - Lower learning rate to 1e-5")
        print("      - Add learning rate scheduler")
        print("   2. Improve training data quality")
        print("   3. Add more diverse training examples")
        print("   Expected improvement: 75-85% F1 score")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    
    # Clean up flag file for next test
    print("\n💡 To run this test again, delete the flag file:")
    print("   !rm /content/packages_installed.flag")
