# ============================================================================
# RUN THIS CELL AFTER RUNTIME RESTART
# ============================================================================

import os
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import json
from typing import List, Dict

# ============================================================================
# STEP 3: LOAD MODEL FROM GOOGLE DRIVE
# ============================================================================
print("="*70)
print("STEP 3: LOAD MODEL")
print("="*70)

# Update this path if your model is in a different location
MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-New/resume-ner-deberta'

print(f"📂 Loading from: {MODEL_PATH}")

# Check if model exists
if not os.path.exists(MODEL_PATH):
    print(f"❌ Model not found at: {MODEL_PATH}")
    print("\n💡 Available folders in MyDrive:")
    get_ipython().system('ls -la /content/drive/MyDrive/')
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

# Load label mappings
label_map_path = os.path.join(MODEL_PATH, "label_mappings.json")
with open(label_map_path, 'r') as f:
    mappings = json.load(f)
    id2label = {int(k): v for k, v in mappings['id2label'].items()}
    label2id = mappings['label2id']

print(f"📋 Loaded {len(id2label)} entity labels")

# Load tokenizer and model
print(f"🔤 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

print(f"🧠 Loading model...")
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

print(f"✅ Model loaded on: {device}")
print(f"💾 Model size: ~370MB")
print()

# ============================================================================
# STEP 4: DEFINE EXTRACTION FUNCTION
# ============================================================================

def extract_entities(text: str) -> List[Dict]:
    """Extract entities from text"""
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
        return_offsets_mapping=True
    )
    
    offset_mapping = inputs.pop("offset_mapping")[0]
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=-1)[0]
    
    entities = []
    current_entity = None
    
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    
    for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
        if token in ['[CLS]', '[SEP]', '<s>', '</s>', '<pad>']:
            continue
        
        label = id2label[pred_id.item()]
        
        if label == 'O':
            if current_entity:
                entities.append(current_entity)
                current_entity = None
            continue
        
        if label.startswith('B-'):
            if current_entity:
                entities.append(current_entity)
            
            entity_type = label[2:]
            start, end = offset
            current_entity = {
                'type': entity_type,
                'text': text[start:end],
                'start': int(start),
                'end': int(end),
                'confidence': torch.softmax(outputs.logits[0][idx], dim=0)[pred_id].item()
            }
        
        elif label.startswith('I-') and current_entity:
            entity_type = label[2:]
            if entity_type == current_entity['type']:
                start, end = offset
                current_entity['end'] = int(end)
                current_entity['text'] = text[current_entity['start']:current_entity['end']]
    
    if current_entity:
        entities.append(current_entity)
    
    return entities

def calculate_metrics(extracted: List[Dict], expected: List[Dict]) -> Dict:
    """Calculate precision, recall, F1"""
    extracted_set = {(e['type'], e['text'].strip().lower()) for e in extracted}
    expected_set = {(e['type'], e['text'].strip().lower()) for e in expected}
    
    true_positives = extracted_set & expected_set
    false_positives = extracted_set - expected_set
    false_negatives = expected_set - extracted_set
    
    precision = len(true_positives) / len(extracted_set) if extracted_set else 0
    recall = len(true_positives) / len(expected_set) if expected_set else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'tp': len(true_positives),
        'fp': len(false_positives),
        'fn': len(false_negatives),
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives
    }

# ============================================================================
# STEP 5: RUN COMPREHENSIVE TESTS
# ============================================================================
print("="*70)
print("STEP 5: RUNNING PRODUCTION-READINESS TESTS")
print("="*70)
print()

all_results = []

# ============================================================================
# TEST 1: Work Experience
# ============================================================================
print("🧪 TEST 1: Work Experience Extraction")
print("-" * 70)

test1_text = """
Sarah Johnson worked as a Senior Data Scientist at Microsoft from January 2020 
to December 2022 in Seattle, Washington. She led the Azure ML team and worked 
with enterprise clients including Amazon and Google.
"""

test1_expected = [
    {'type': 'PERSON_NAME', 'text': 'Sarah Johnson'},
    {'type': 'ROLE', 'text': 'Senior Data Scientist'},
    {'type': 'COMPANY', 'text': 'Microsoft'},
    {'type': 'DATE_START', 'text': 'January 2020'},
    {'type': 'DATE_END', 'text': 'December 2022'},
    {'type': 'LOCATION', 'text': 'Seattle, Washington'},
    {'type': 'CLIENT', 'text': 'Amazon'},
    {'type': 'CLIENT', 'text': 'Google'},
]

extracted1 = extract_entities(test1_text)
metrics1 = calculate_metrics(extracted1, test1_expected)

print(f"Expected: {len(test1_expected)} entities")
print(f"Extracted: {len(extracted1)} entities")
print(f"✅ Correct: {metrics1['tp']}")
print(f"❌ Wrong: {metrics1['fp']}")
print(f"⚠️  Missed: {metrics1['fn']}")
print(f"📊 Precision: {metrics1['precision']:.1%} | Recall: {metrics1['recall']:.1%} | F1: {metrics1['f1']:.1%}")

# Show what was extracted
print("\n🔍 Extracted entities:")
for e in extracted1:
    print(f"  [{e['type']}] {e['text']} (conf: {e['confidence']:.2%})")

print()
all_results.append(metrics1)

# ============================================================================
# TEST 2: Education Background
# ============================================================================
print("🧪 TEST 2: Education Background Extraction")
print("-" * 70)

test2_text = """
Michael Chen completed his Master of Science in Computer Science from Stanford 
University from September 2019 to June 2021 with a GPA of 3.95. He earned his 
Bachelor of Technology in Information Technology from MIT from August 2015 to 
May 2019 with a grade of 3.8.
"""

test2_expected = [
    {'type': 'PERSON_NAME', 'text': 'Michael Chen'},
    {'type': 'DEGREE', 'text': 'Master of Science'},
    {'type': 'FIELD', 'text': 'Computer Science'},
    {'type': 'INSTITUTION', 'text': 'Stanford University'},
    {'type': 'EDU_YEAR_START', 'text': 'September 2019'},
    {'type': 'EDU_YEAR_END', 'text': 'June 2021'},
    {'type': 'GRADE', 'text': '3.95'},
    {'type': 'DEGREE', 'text': 'Bachelor of Technology'},
    {'type': 'FIELD', 'text': 'Information Technology'},
    {'type': 'INSTITUTION', 'text': 'MIT'},
    {'type': 'EDU_YEAR_START', 'text': 'August 2015'},
    {'type': 'EDU_YEAR_END', 'text': 'May 2019'},
    {'type': 'GRADE', 'text': '3.8'},
]

extracted2 = extract_entities(test2_text)
metrics2 = calculate_metrics(extracted2, test2_expected)

print(f"Expected: {len(test2_expected)} entities")
print(f"Extracted: {len(extracted2)} entities")
print(f"✅ Correct: {metrics2['tp']}")
print(f"❌ Wrong: {metrics2['fp']}")
print(f"⚠️  Missed: {metrics2['fn']}")
print(f"📊 Precision: {metrics2['precision']:.1%} | Recall: {metrics2['recall']:.1%} | F1: {metrics2['f1']:.1%}")

print("\n🔍 Extracted entities:")
for e in extracted2:
    print(f"  [{e['type']}] {e['text']} (conf: {e['confidence']:.2%})")

print()
all_results.append(metrics2)

# ============================================================================
# TEST 3: Multiple Roles
# ============================================================================
print("🧪 TEST 3: Multiple Roles & Career Progression")
print("-" * 70)

test3_text = """
David Kim served as a Product Manager at Google from March 2021 to present in 
Mountain View. Previously, he was a Software Engineer at Facebook from June 2018 
to February 2021 in Menlo Park, working on the Instagram platform.
"""

test3_expected = [
    {'type': 'PERSON_NAME', 'text': 'David Kim'},
    {'type': 'ROLE', 'text': 'Product Manager'},
    {'type': 'COMPANY', 'text': 'Google'},
    {'type': 'DATE_START', 'text': 'March 2021'},
    {'type': 'LOCATION', 'text': 'Mountain View'},
    {'type': 'ROLE', 'text': 'Software Engineer'},
    {'type': 'COMPANY', 'text': 'Facebook'},
    {'type': 'DATE_START', 'text': 'June 2018'},
    {'type': 'DATE_END', 'text': 'February 2021'},
    {'type': 'LOCATION', 'text': 'Menlo Park'},
]

extracted3 = extract_entities(test3_text)
metrics3 = calculate_metrics(extracted3, test3_expected)

print(f"Expected: {len(test3_expected)} entities")
print(f"Extracted: {len(extracted3)} entities")
print(f"✅ Correct: {metrics3['tp']}")
print(f"❌ Wrong: {metrics3['fp']}")
print(f"⚠️  Missed: {metrics3['fn']}")
print(f"📊 Precision: {metrics3['precision']:.1%} | Recall: {metrics3['recall']:.1%} | F1: {metrics3['f1']:.1%}")

print("\n🔍 Extracted entities:")
for e in extracted3:
    print(f"  [{e['type']}] {e['text']} (conf: {e['confidence']:.2%})")

print()
all_results.append(metrics3)

# ============================================================================
# STEP 6: OVERALL ASSESSMENT
# ============================================================================
print()
print("="*70)
print("📊 OVERALL PERFORMANCE ASSESSMENT")
print("="*70)
print()

avg_precision = sum(r['precision'] for r in all_results) / len(all_results)
avg_recall = sum(r['recall'] for r in all_results) / len(all_results)
avg_f1 = sum(r['f1'] for r in all_results) / len(all_results)

total_tp = sum(r['tp'] for r in all_results)
total_fp = sum(r['fp'] for r in all_results)
total_fn = sum(r['fn'] for r in all_results)

print(f"Tests Run: {len(all_results)}")
print(f"Total Entities Expected: {total_tp + total_fn}")
print(f"Total Entities Extracted: {total_tp + total_fp}")
print()
print(f"✅ Correctly Extracted: {total_tp}")
print(f"❌ Incorrectly Extracted: {total_fp}")
print(f"⚠️  Missed Entities: {total_fn}")
print()
print(f"📈 Average Precision: {avg_precision:.1%}")
print(f"📈 Average Recall:    {avg_recall:.1%}")
print(f"📈 Average F1 Score:  {avg_f1:.1%}")
print()

# ============================================================================
# STEP 7: PRODUCTION-READINESS DECISION
# ============================================================================
print("="*70)
print("🎯 PRODUCTION-READINESS DECISION")
print("="*70)
print()

# Define thresholds
EXCELLENT_THRESHOLD = 0.90
GOOD_THRESHOLD = 0.75
ACCEPTABLE_THRESHOLD = 0.60

if avg_f1 >= EXCELLENT_THRESHOLD:
    decision = "✅ READY FOR PRODUCTION"
    color = "🟢"
    recommendation = """
RECOMMENDATION: DEPLOY TO PRODUCTION

✅ Model shows excellent performance (F1 ≥ 90%)
✅ Suitable for production use
✅ Continue monitoring performance on real data
✅ Set up error tracking for edge cases
    """
elif avg_f1 >= GOOD_THRESHOLD:
    decision = "⚠️  CONDITIONALLY READY"
    color = "🟡"
    recommendation = """
RECOMMENDATION: DEPLOY WITH MONITORING

⚠️  Model shows good performance (F1 ≥ 75%)
✅ Can be used in production with human review
⚠️  Set up confidence thresholds (e.g., flag predictions < 80%)
⚠️  Monitor false positives and false negatives
⚠️  Plan for model improvements
    """
elif avg_f1 >= ACCEPTABLE_THRESHOLD:
    decision = "⚠️  NOT RECOMMENDED"
    color = "🟠"
    recommendation = """
RECOMMENDATION: IMPROVE BEFORE PRODUCTION

⚠️  Model shows moderate performance (F1 ≥ 60%)
❌ Not recommended for production without improvements
💡 Consider:
   - Adding more diverse training examples
   - Improving label quality
   - Training for more epochs
   - Using data augmentation
⚠️  If deploying, require human review for ALL extractions
    """
else:
    decision = "❌ NOT READY FOR PRODUCTION"
    color = "🔴"
    recommendation = """
RECOMMENDATION: DO NOT DEPLOY

❌ Model shows poor performance (F1 < 60%)
❌ Not suitable for production use
💡 Required actions:
   - Review and improve training data quality
   - Add significantly more training examples
   - Check for data labeling errors
   - Consider different model architecture
   - Retrain from scratch with better data
    """

print(f"{color} {decision}")
print(f"{color} F1 Score: {avg_f1:.1%}")
print()
print(recommendation)

print("="*70)
print("📋 DETAILED METRICS BY TEST")
print("="*70)
print()

test_names = [
    "Work Experience",
    "Education Background",
    "Multiple Roles"
]

for i, (name, result) in enumerate(zip(test_names, all_results), 1):
    status = "✅" if result['f1'] >= GOOD_THRESHOLD else "⚠️" if result['f1'] >= ACCEPTABLE_THRESHOLD else "❌"
    print(f"{status} Test {i}: {name}")
    print(f"   P: {result['precision']:.1%} | R: {result['recall']:.1%} | F1: {result['f1']:.1%}")

print()
print("="*70)
print("🏁 TESTING COMPLETE")
print("="*70)
print()

print(f"📊 Training F1 Score: 66.92%")
print(f"🧪 Test F1 Score: {avg_f1:.1%}")
print()

if avg_f1 >= GOOD_THRESHOLD:
    print("✅ Model is performing well on test cases!")
    print("✅ You can integrate this into your pipeline.")
    print()
    print("NEXT STEPS:")
    print("1. Download model from Google Drive")
    print("2. Integrate into your AI service")
    print("3. Set up production monitoring")
else:
    print("⚠️  Model needs improvement before production use.")
    print("💡 Consider retraining with better data or skip for now.")
    print()
    print("NEXT STEPS:")
    print("1. Review which entity types are failing")
    print("2. Add more training examples for those types")
    print("3. Improve label quality")
    print("4. Retrain and test again")

print()
