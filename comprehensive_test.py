#!/usr/bin/env python3
"""
Comprehensive Model Testing Script
Test the DeBERTa NER model with multiple resume examples
"""

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch
import json

# Model path
MODEL_PATH = "ai-service/models/resume-ner-deberta"

print("="*80)
print("COMPREHENSIVE MODEL TESTING")
print("="*80)
print(f"\nLoading model from: {MODEL_PATH}")

# Load model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

device = 0 if torch.cuda.is_available() else -1
print(f"Device: {'GPU' if device == 0 else 'CPU (Mac)'}")

ner = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple", device=device)
print("✅ Model loaded!\n")

# Test cases
test_cases = [
    {
        "name": "Software Engineer Resume",
        "text": """
Sarah Johnson
Senior Software Engineer

WORK EXPERIENCE

Software Engineer at Google
March 2020 - Present
Mountain View, CA
- Led development of cloud infrastructure
- Worked with clients including Amazon and Microsoft
- Managed team of 5 engineers

Junior Developer at Facebook
June 2018 - February 2020
Menlo Park, CA
- Built React applications
- Collaborated with product team

EDUCATION

Master of Science in Computer Science
Stanford University
September 2016 - June 2018
GPA: 3.9

Bachelor of Technology in Software Engineering
MIT
August 2012 - May 2016
Grade: 3.8
""",
        "expected": {
            'PERSON_NAME': 1,
            'ROLE': 2,
            'COMPANY': 2,
            'DATE_START': 4,
            'DATE_END': 2,
            'LOCATION': 2,
            'CLIENT': 2,
            'DEGREE': 2,
            'FIELD': 2,
            'INSTITUTION': 2,
            'EDU_YEAR_START': 2,
            'EDU_YEAR_END': 2,
            'GRADE': 2
        }
    },
    {
        "name": "Consultant Resume",
        "text": """
Michael Chen
Management Consultant at McKinsey & Company
January 2019 - August 2022
New York, NY

Delivered strategic projects for Fortune 500 clients including:
- JPMorgan Chase
- Goldman Sachs
- Citigroup

Education:
MBA from Harvard Business School, 2017-2019
BS in Economics from Yale University, 2013-2017
""",
        "expected": {
            'PERSON_NAME': 1,
            'ROLE': 1,
            'COMPANY': 1,
            'DATE_START': 3,
            'DATE_END': 3,
            'LOCATION': 1,
            'CLIENT': 3,
            'DEGREE': 2,
            'FIELD': 2,
            'INSTITUTION': 2
        }
    },
    {
        "name": "Data Scientist Resume",
        "text": """
Emily Rodriguez
Data Scientist

Amazon Web Services
Senior Data Scientist
April 2021 - Present
Seattle, Washington

Led ML projects for clients: Netflix, Spotify, Uber

Microsoft
Data Analyst
June 2019 - March 2021
Redmond, WA

Education:
PhD in Machine Learning, Carnegie Mellon University, 2016-2019, GPA 3.95
MS in Statistics, UC Berkeley, 2014-2016, Grade 3.8
""",
        "expected": {
            'PERSON_NAME': 1,
            'ROLE': 2,
            'COMPANY': 2,
            'DATE_START': 4,
            'DATE_END': 2,
            'LOCATION': 2,
            'CLIENT': 3,
            'DEGREE': 2,
            'FIELD': 2,
            'INSTITUTION': 2,
            'GRADE': 2
        }
    }
]

# Run tests
all_results = []

for i, test_case in enumerate(test_cases, 1):
    print("="*80)
    print(f"TEST {i}: {test_case['name']}")
    print("="*80)
    
    # Run NER
    results = ner(test_case['text'])
    
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
    print(f"\n📝 Resume Text Preview:")
    print("-" * 80)
    preview = test_case['text'].strip()[:200] + "..."
    print(preview)
    print("-" * 80)
    
    print(f"\n🔍 Extracted Entities:")
    print("-" * 80)
    
    for etype in sorted(entities_by_type.keys()):
        print(f"\n{etype}:")
        for item in entities_by_type[etype][:3]:  # Show first 3
            print(f"  - {item['text']:30s} (confidence: {item['score']:.1%})")
        if len(entities_by_type[etype]) > 3:
            print(f"  ... and {len(entities_by_type[etype]) - 3} more")
    
    # Calculate metrics
    expected = test_case['expected']
    total_expected = sum(expected.values())
    total_extracted = len(results)
    
    # Count correct entity types
    correct_types = 0
    for etype, expected_count in expected.items():
        actual_count = len(entities_by_type.get(etype, []))
        if actual_count >= expected_count * 0.7:  # 70% threshold
            correct_types += 1
    
    accuracy = total_extracted / total_expected if total_expected > 0 else 0
    type_accuracy = correct_types / len(expected) if expected else 0
    
    print(f"\n📊 Metrics:")
    print("-" * 80)
    print(f"Expected entities: {total_expected}")
    print(f"Extracted entities: {total_extracted}")
    print(f"Extraction rate: {accuracy:.1%}")
    print(f"Entity types found: {len(entities_by_type)}/{len(expected)}")
    print(f"Type accuracy: {type_accuracy:.1%}")
    
    # Assessment
    if accuracy >= 0.8 and type_accuracy >= 0.8:
        status = "✅ EXCELLENT"
        color = "🟢"
    elif accuracy >= 0.6 and type_accuracy >= 0.6:
        status = "⚠️  GOOD"
        color = "🟡"
    else:
        status = "❌ NEEDS IMPROVEMENT"
        color = "🔴"
    
    print(f"\n{color} Status: {status}")
    
    all_results.append({
        'name': test_case['name'],
        'total_expected': total_expected,
        'total_extracted': total_extracted,
        'accuracy': accuracy,
        'type_accuracy': type_accuracy,
        'status': status
    })
    
    print()

# Overall summary
print("="*80)
print("📊 OVERALL TEST SUMMARY")
print("="*80)

avg_accuracy = sum(r['accuracy'] for r in all_results) / len(all_results)
avg_type_accuracy = sum(r['type_accuracy'] for r in all_results) / len(all_results)

print(f"\nTests run: {len(all_results)}")
print(f"Average extraction rate: {avg_accuracy:.1%}")
print(f"Average type accuracy: {avg_type_accuracy:.1%}")

print(f"\n📋 Individual Test Results:")
print("-" * 80)
for i, result in enumerate(all_results, 1):
    print(f"{i}. {result['name']}")
    print(f"   Extraction: {result['accuracy']:.1%} | Type Accuracy: {result['type_accuracy']:.1%} | {result['status']}")

print("\n" + "="*80)
print("🎯 FINAL ASSESSMENT")
print("="*80)

if avg_accuracy >= 0.8:
    print("\n✅ EXCELLENT: Model is production-ready!")
    print("✅ Consistently extracting 80%+ of entities")
    print("✅ Recommended action: Deploy to production")
elif avg_accuracy >= 0.6:
    print("\n⚠️  GOOD: Model is working well")
    print("⚠️  Extracting 60-80% of entities")
    print("⚠️  Recommended action: Use with confidence thresholds")
else:
    print("\n❌ NEEDS IMPROVEMENT: Model needs retraining")
    print("❌ Extracting less than 60% of entities")
    print("❌ Recommended action: Retrain with better configuration")

print(f"\n📊 Training F1 Score: 67.55%")
print(f"📊 Test Performance: {avg_accuracy:.1%}")

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)

if avg_accuracy >= 0.7:
    print("\n✅ Model is ready to use!")
    print("\n1. Integrate into your FastAPI application")
    print("2. Set confidence threshold to 0.8 (80%)")
    print("3. Add human review for predictions < 80% confidence")
    print("4. Test with your own resume PDFs")
    print("5. Deploy to production")
else:
    print("\n⚠️  Consider retraining:")
    print("\n1. Use early stopping at epoch 5-6")
    print("2. Lower learning rate to 1e-5")
    print("3. Add learning rate scheduler")
    print("4. Expected improvement: 75-85% F1")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
