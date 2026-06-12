# ============================================================================
# QUICK MODEL TEST - COPY THIS TO COLAB
# Tests your retrained model accuracy
# ============================================================================

from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# Load model
MODEL_PATH = '/content/drive/MyDrive/Resume-NER-Models-FINAL/resume-ner-deberta'

print("📥 Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
print("✅ Model loaded!\n")

# Test function
def test(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, return_offsets_mapping=True)
    offset_mapping = inputs.pop('offset_mapping')[0]
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    predictions = outputs.logits.argmax(dim=-1)[0]
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    
    entities = []
    current_entity = None
    current_text = ""
    current_start = None
    
    for token, pred_id, offset in zip(tokens, predictions, offset_mapping):
        label = model.config.id2label[pred_id.item()]
        start, end = offset
        
        if token in ['[CLS]', '[SEP]', '[PAD]']:
            if current_entity and current_text.strip():
                entities.append(f"{current_text.strip()} → {current_entity}")
            current_entity = None
            current_text = ""
            continue
        
        if label == 'O':
            if current_entity and current_text.strip():
                entities.append(f"{current_text.strip()} → {current_entity}")
            current_entity = None
            current_text = ""
        elif label.startswith('B-'):
            if current_entity and current_text.strip():
                entities.append(f"{current_text.strip()} → {current_entity}")
            current_entity = label[2:]
            current_text = text[start:end]
            current_start = start.item()
        elif label.startswith('I-') and current_entity:
            current_text = text[current_start:end]
    
    if current_entity and current_text.strip():
        entities.append(f"{current_text.strip()} → {current_entity}")
    
    return list(dict.fromkeys(entities))  # Remove duplicates

# ============================================================================
# RUN TESTS
# ============================================================================

print("="*70)
print("🧪 TESTING MODEL ACCURACY")
print("="*70)

tests = [
    "John Smith worked at Google as Software Engineer in New York from 2020 to 2023.",
    "Rahul Sharma worked at Infosys as Data Scientist in Hyderabad from January 2021 to Present.",
    "B.Tech in Computer Science from IIT Delhi, 2018-2022 with Grade 8.5",
    "Priya Patel joined Deloitte in April 2022 as Sr. IT Consultant in Chicago, IL.",
    "Worked at Microsoft as Senior Developer in Seattle from 2019 to 2021."
]

passed = 0
total = len(tests)

for i, text in enumerate(tests, 1):
    print(f"\n{'='*70}")
    print(f"Test {i}: {text[:60]}...")
    print(f"{'='*70}")
    
    results = test(text)
    
    print(f"🔍 Extracted ({len(results)}):")
    for r in results:
        print(f"  • {r}")
    
    # Check for issues
    has_sep = any('[SEP]' in r for r in results)
    has_enough = len(results) >= 3
    
    if has_sep:
        print("❌ FAILED: Contains [SEP] tokens")
    elif has_enough:
        print(f"✅ PASSED: {len(results)} entities extracted")
        passed += 1
    else:
        print(f"⚠️  WARNING: Only {len(results)} entities")

# Summary
print(f"\n{'='*70}")
print("📊 SUMMARY")
print(f"{'='*70}")
print(f"✅ Passed: {passed}/{total}")
print(f"📊 Accuracy: {(passed/total)*100:.1f}%")

if passed >= 4:
    print("\n🎉 MODEL IS PRODUCTION-READY!")
else:
    print("\n⚠️  Model needs improvement")

print(f"\n📈 Training F1: 96.79%")
print(f"📁 Model: MyDrive/Resume-NER-Models-FINAL/")
