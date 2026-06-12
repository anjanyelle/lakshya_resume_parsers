# 🚀 Model Improvement Action Plan
**Date**: May 12, 2026  
**Current F1**: 67.55%  
**Target F1**: 85-90%

---

## 📊 **Current Model Test Results**

### Test 1: TCS Resume
```json
Input: "Full Stack Developer\nTata Consultancy Services (TCS)\nHyderabad, India\nJune 2024 – Present"

Output:
✅ Job 1: "Full Stack Developer" at "Tata Consultancy Services" (2024-06-01 - Present)
❌ Job 2: "web pages" at "React" (2023-01-01 - 2024-05-01)  // WRONG!
```

### Test 2: Google Resume
```json
Input: "Senior Software Engineer at Google\nMountain View, California\nJanuary 2020 - Present"

Output:
✅ Job 1: "Senior Software Engineer" at "Google" (2020-01-01 - Present)
❌ Job 2: "Developer" at "Software" (2018-06-01 - 2019-12-01)  // DUPLICATE!
❌ Job 3: "Developer" at "Microsoft" (2018-06-01 - 2019-12-01)  // DUPLICATE!
```

### **Issues Identified:**
1. ❌ **Extracting technology names as companies** ("React", "Software")
2. ❌ **Partial role extraction** ("web pages" instead of "Software Engineer")
3. ❌ **Creating duplicate job entries** (2-3 entries for same job)
4. ❌ **Missing institutions** (JNTU, Stanford not extracted)
5. ❌ **Incomplete degree text** ("Bachelor of Technology (B.Tech" - missing ")")

---

## 🎯 **3-Phase Improvement Plan**

---

## **PHASE 1: Quick Wins (No Retraining) - 1-2 Hours**
**Goal**: Fix extraction logic without retraining model  
**Expected Improvement**: 67% → 72-75% F1

### **Step 1.1: Fix Entity Aggregation** ✅ DONE
**File**: `ai-service/parsers/deberta_ner_parser.py`

```python
# Changed aggregation_strategy from "max" to "simple"
# Increased proximity window from 2 to 5 characters
```

**Impact**: Better multi-word entity extraction ("Full Stack Developer" instead of "Full Stack")

### **Step 1.2: Add Post-Processing Filters**
**File**: `ai-service/parsers/deberta_experience_builder.py`

**Add these filters:**

```python
def _filter_invalid_companies(self, companies: List[str]) -> List[str]:
    """Remove technology names mistakenly extracted as companies."""
    tech_keywords = ['react', 'node', 'angular', 'vue', 'python', 'java', 
                     'javascript', 'typescript', 'software', 'web', 'api']
    
    filtered = []
    for company in companies:
        company_lower = company.lower()
        # Skip if it's a single tech keyword
        if company_lower in tech_keywords:
            continue
        # Skip if it's just "Software" or "Developer"
        if company_lower in ['software', 'developer', 'engineer']:
            continue
        filtered.append(company)
    
    return filtered

def _deduplicate_experiences(self, experiences: List[Dict]) -> List[Dict]:
    """Remove duplicate job entries based on company + dates."""
    seen = set()
    unique = []
    
    for exp in experiences:
        key = (exp['company_name'], exp['start_date'], exp['end_date'])
        if key not in seen:
            seen.add(key)
            unique.append(exp)
    
    return unique
```

**Action**: Add these methods and call them in `build_experiences_from_entities()`

---

### **Step 1.3: Improve Institution Extraction**
**File**: `ai-service/parsers/deberta_ner_parser.py`

**Problem**: Institutions not being extracted

**Solution**: Add fallback regex for common patterns

```python
def _extract_institutions_fallback(self, text: str) -> List[str]:
    """Fallback regex for institution extraction."""
    import re
    
    # Pattern: University/College/Institute names
    patterns = [
        r'\b([A-Z][A-Za-z\s]+(?:University|College|Institute|School))\b',
        r'\b(IIT|NIT|BITS|MIT|Stanford|Harvard|Berkeley|CMU)\s*[A-Za-z]*\b',
        r'\b([A-Z]{2,5})\s+(?:University|College)\b'  # JNTU, UCLA, etc.
    ]
    
    institutions = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        institutions.extend(matches)
    
    return list(set(institutions))
```

---

## **PHASE 2: Data Quality Improvements (2-3 Hours)**
**Goal**: Fix training data issues  
**Expected Improvement**: 75% → 82-85% F1

### **Step 2.1: Analyze Training Data**

Run this script to check data quality:

```python
# analyze_training_data.py
import json

def analyze_labels(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    stats = {
        'total_examples': len(data),
        'entity_counts': {},
        'incomplete_entities': [],
        'missing_institutions': 0
    }
    
    for idx, example in enumerate(data):
        entities = example.get('entities', [])
        
        for entity in entities:
            label = entity['label']
            text = entity['text']
            
            # Count entities
            stats['entity_counts'][label] = stats['entity_counts'].get(label, 0) + 1
            
            # Check for incomplete entities
            if label == 'ROLE' and len(text.split()) == 1:
                stats['incomplete_entities'].append({
                    'index': idx,
                    'label': label,
                    'text': text,
                    'issue': 'Single-word role (might be incomplete)'
                })
            
            if label == 'DEGREE' and '(' in text and ')' not in text:
                stats['incomplete_entities'].append({
                    'index': idx,
                    'label': label,
                    'text': text,
                    'issue': 'Incomplete degree (missing closing paren)'
                })
        
        # Check for missing institutions
        has_degree = any(e['label'] == 'DEGREE' for e in entities)
        has_institution = any(e['label'] == 'INSTITUTION' for e in entities)
        
        if has_degree and not has_institution:
            stats['missing_institutions'] += 1
    
    return stats

# Run analysis
for file in ['label1.json', 'label2.json', 'label3.json']:
    print(f"\n=== {file} ===")
    stats = analyze_labels(f'training/data/{file}')
    print(f"Total examples: {stats['total_examples']}")
    print(f"Missing institutions: {stats['missing_institutions']}")
    print(f"Incomplete entities: {len(stats['incomplete_entities'])}")
    print("\nTop 10 incomplete entities:")
    for item in stats['incomplete_entities'][:10]:
        print(f"  - {item}")
```

### **Step 2.2: Fix Training Data Issues**

Based on analysis results:

1. **Fix incomplete ROLE labels**:
   - "Developer" → "Software Developer"
   - "Engineer" → "Software Engineer"
   - "Full Stack" → "Full Stack Developer"

2. **Add missing INSTITUTION labels**:
   - Find education sections without institutions
   - Add institution entities

3. **Fix incomplete DEGREE labels**:
   - "Bachelor of Technology (B.Tech" → "Bachelor of Technology (B.Tech)"
   - Add closing parentheses

**Tool**: Create a data cleaning script

```python
# fix_training_data.py
import json
import re

def fix_incomplete_roles(entities):
    """Expand single-word roles to full titles."""
    role_expansions = {
        'developer': 'software developer',
        'engineer': 'software engineer',
        'analyst': 'data analyst',
        'designer': 'ui/ux designer'
    }
    
    for entity in entities:
        if entity['label'] == 'ROLE':
            text_lower = entity['text'].lower()
            if text_lower in role_expansions:
                entity['text'] = role_expansions[text_lower].title()
    
    return entities

def add_missing_institutions(text, entities):
    """Add institution entities if missing."""
    has_degree = any(e['label'] == 'DEGREE' for e in entities)
    has_institution = any(e['label'] == 'INSTITUTION' for e in entities)
    
    if has_degree and not has_institution:
        # Try to find institution in text
        inst_pattern = r'([A-Z][A-Za-z\s]+(?:University|College|Institute))'
        match = re.search(inst_pattern, text)
        
        if match:
            inst_text = match.group(1)
            inst_start = match.start(1)
            inst_end = match.end(1)
            
            entities.append({
                'label': 'INSTITUTION',
                'text': inst_text,
                'start': inst_start,
                'end': inst_end
            })
    
    return entities

# Process all files
for file in ['label1.json', 'label2.json', 'label3.json']:
    with open(f'training/data/{file}', 'r') as f:
        data = json.load(f)
    
    for example in data:
        example['entities'] = fix_incomplete_roles(example['entities'])
        example['entities'] = add_missing_institutions(example['text'], example['entities'])
    
    # Save fixed data
    with open(f'training/data/{file}_fixed.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Fixed {file}")
```

---

## **PHASE 3: Retrain with Better Config (3-4 Hours)**
**Goal**: Retrain model with fixed data and optimized hyperparameters  
**Expected Improvement**: 85% → 90%+ F1

### **Step 3.1: Update Training Configuration**

**File**: `training/colab_train.py`

```python
# Improved hyperparameters
training_args = TrainingArguments(
    output_dir="./models/resume-ner-deberta",
    num_train_epochs=20,  # Increased from 15
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=3e-5,  # Optimized
    warmup_ratio=0.1,
    weight_decay=0.01,
    logging_steps=100,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    fp16=True,  # Mixed precision training
    gradient_accumulation_steps=2,  # Effective batch size = 32
    lr_scheduler_type="cosine",  # Better than linear
    max_grad_norm=1.0,  # Gradient clipping
    dataloader_num_workers=2,
    seed=42
)
```

### **Step 3.2: Add Early Stopping**

```python
from transformers import EarlyStoppingCallback

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)
```

### **Step 3.3: Train in Google Colab**

1. Upload fixed training data to Colab
2. Run training script
3. Monitor F1 score per epoch
4. Save best checkpoint to Google Drive

**Expected Training Time**: ~60-75 minutes on T4 GPU

---

## 📋 **Implementation Checklist**

### **Phase 1: Quick Wins** (Do this NOW)
- [x] Fix aggregation strategy (DONE)
- [ ] Add company filtering (`_filter_invalid_companies`)
- [ ] Add deduplication (`_deduplicate_experiences`)
- [ ] Add institution fallback extraction
- [ ] Test with sample resumes
- [ ] Expected result: 72-75% F1

### **Phase 2: Data Quality** (Do this NEXT)
- [ ] Run `analyze_training_data.py`
- [ ] Review incomplete entities
- [ ] Run `fix_training_data.py`
- [ ] Verify fixed data quality
- [ ] Create new training ZIP

### **Phase 3: Retrain** (Do this LAST)
- [ ] Update `colab_train.py` with new hyperparameters
- [ ] Upload fixed data to Colab
- [ ] Run training (60-75 min)
- [ ] Monitor F1 score progression
- [ ] Save best model to Google Drive
- [ ] Download and test locally
- [ ] Expected result: 85-90% F1

---

## 🎯 **Success Metrics**

| Phase | F1 Score | Time | Effort |
|-------|----------|------|--------|
| **Current** | 67.55% | - | - |
| **Phase 1** | 72-75% | 1-2 hours | Low |
| **Phase 2** | 82-85% | 2-3 hours | Medium |
| **Phase 3** | 85-90% | 3-4 hours | High |

---

## 💡 **Quick Start: Phase 1 Implementation**

Run these commands NOW to get immediate improvements:

```bash
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser/ai-service

# Create the filter functions
cat >> parsers/deberta_experience_builder.py << 'EOF'

    def _filter_invalid_companies(self, companies: List[str]) -> List[str]:
        """Remove technology names mistakenly extracted as companies."""
        tech_keywords = ['react', 'node', 'angular', 'vue', 'python', 'java', 
                         'javascript', 'typescript', 'software', 'web', 'api',
                         'redux', 'mysql', 'mongodb', 'aws', 'docker']
        
        filtered = []
        for company in companies:
            company_lower = company.lower().strip()
            if company_lower in tech_keywords:
                continue
            if company_lower in ['software', 'developer', 'engineer', 'web pages']:
                continue
            if len(company) < 3:  # Skip very short names
                continue
            filtered.append(company)
        
        return filtered
    
    def _deduplicate_experiences(self, experiences: List[Dict]) -> List[Dict]:
        """Remove duplicate job entries."""
        seen = set()
        unique = []
        
        for exp in experiences:
            key = (exp['company_name'], exp['start_date'], exp['end_date'])
            if key not in seen:
                seen.add(key)
                unique.append(exp)
        
        return unique
EOF

# Restart server
pkill -f "python.*main.py"
source venv/bin/activate && python main.py &
```

Then update the `build_experiences_from_entities` method to use these filters.

---

## 📞 **Need Help?**

If you get stuck on any phase:
1. Check the logs in `ai-service/logs/`
2. Test with `comprehensive_test.py`
3. Review training metrics in Colab

**Remember**: Phase 1 gives you 70-75% F1 with minimal effort. Do that first! 🚀
