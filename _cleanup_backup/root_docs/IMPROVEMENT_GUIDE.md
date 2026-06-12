# 🚀 Model Improvement Guide - Increase Accuracy to 99%+

## 📊 Current Status Analysis

### What's Working Well ✅
- **DEGREE:** 99.48% F1 (389 examples) - Excellent!
- **ROLE:** 98.86% F1 (1,186 examples) - Very Good
- **CLIENT:** 97.90% F1 (329 examples) - Good
- **COMPANY:** 97.86% F1 (770 examples) - Good
- **LOCATION:** 96.43% F1 (713 examples) - Acceptable

### Critical Issues ⚠️
- **PERSON:** 0% F1 (0 examples) - **NO TRAINING DATA**
- **EDUCATION:** 0% F1 (0 examples) - **NO TRAINING DATA**
- **START_DATE:** 0% F1 (0 examples) - **NO TRAINING DATA**
- **END_DATE:** 0% F1 (0 examples) - **NO TRAINING DATA**

---

## 🎯 Step-by-Step Improvement Plan

### Phase 1: Add Missing Entity Types (Priority: HIGH)

#### Step 1.1: Create Training Data for Missing Entities

**You need to annotate at least 500-1000 examples for each missing entity type.**

**Example annotation format:**

```json
{
  "tokens": ["John", "Doe", "worked", "at", "Google", "from", "Jan", "2020", "to", "Dec", "2023"],
  "ner_tags": ["B-PERSON", "I-PERSON", "O", "O", "B-COMPANY", "O", "B-START_DATE", "I-START_DATE", "O", "B-END_DATE", "I-END_DATE"]
}
```

**Create file:** `ai-service/training/data/additional_annotations.json`

```json
[
  {
    "tokens": ["Rajesh", "Kumar", "graduated", "from", "IIT", "Delhi", "with", "B.Tech", "in", "Computer", "Science"],
    "ner_tags": ["B-PERSON", "I-PERSON", "O", "O", "B-EDUCATION", "I-EDUCATION", "O", "B-DEGREE", "I-DEGREE", "I-DEGREE", "I-DEGREE"]
  },
  {
    "tokens": ["Sarah", "Johnson", "worked", "at", "Microsoft", "as", "Senior", "Developer", "from", "March", "2019", "to", "Present"],
    "ner_tags": ["B-PERSON", "I-PERSON", "O", "O", "B-COMPANY", "O", "B-ROLE", "I-ROLE", "O", "B-START_DATE", "I-START_DATE", "O", "B-END_DATE"]
  }
]
```

#### Step 1.2: Annotation Tools

**Option A: Manual Annotation (Recommended for small datasets)**

Create a simple annotation script:

```python
# ai-service/training/tools/annotate.py
import json

def annotate_resume(text):
    """Interactive annotation tool"""
    print("Resume Text:")
    print(text)
    print("\n" + "="*50)
    
    tokens = text.split()
    ner_tags = []
    
    entity_types = ["PERSON", "COMPANY", "CLIENT", "ROLE", "LOCATION", 
                    "START_DATE", "END_DATE", "EDUCATION", "DEGREE"]
    
    print("\nEntity Types:")
    for i, et in enumerate(entity_types, 1):
        print(f"{i}. {et}")
    print("0. O (Outside)")
    
    i = 0
    while i < len(tokens):
        print(f"\nToken {i+1}/{len(tokens)}: '{tokens[i]}'")
        choice = input("Select entity type (0-9) or 's' to skip: ")
        
        if choice == 's':
            ner_tags.append("O")
            i += 1
        elif choice.isdigit() and 0 <= int(choice) <= len(entity_types):
            if choice == '0':
                ner_tags.append("O")
                i += 1
            else:
                entity = entity_types[int(choice)-1]
                span = input(f"How many tokens for {entity}? ")
                span_len = int(span)
                
                ner_tags.append(f"B-{entity}")
                for j in range(1, span_len):
                    if i + j < len(tokens):
                        ner_tags.append(f"I-{entity}")
                
                i += span_len
    
    return {
        "tokens": tokens,
        "ner_tags": ner_tags
    }

# Usage
if __name__ == "__main__":
    resume_texts = [
        "John Doe worked at Google as Software Engineer in Bangalore from Jan 2020 to Dec 2023",
        # Add more resume sentences
    ]
    
    annotations = []
    for text in resume_texts:
        annotation = annotate_resume(text)
        annotations.append(annotation)
    
    # Save
    with open('../data/additional_annotations.json', 'w') as f:
        json.dump(annotations, f, indent=2)
```

**Option B: Use Label Studio (Recommended for large datasets)**

```bash
# Install Label Studio
pip install label-studio

# Start Label Studio
label-studio start

# Import your resume texts
# Configure NER labeling interface
# Export as JSON in the required format
```

#### Step 1.3: Merge New Data with Existing Data

```python
# ai-service/training/tools/merge_data.py
import json

# Load existing data
with open('../data/train.json', 'r') as f:
    existing_data = json.load(f)

# Load new annotations
with open('../data/additional_annotations.json', 'r') as f:
    new_data = json.load(f)

# Merge
merged_data = existing_data + new_data

# Split into train/test (80/20)
from sklearn.model_selection import train_test_split

train_data, test_data = train_test_split(merged_data, test_size=0.2, random_state=42)

# Save
with open('../data/train_v2.json', 'w') as f:
    json.dump(train_data, f, indent=2)

with open('../data/test_v2.json', 'w') as f:
    json.dump(test_data, f, indent=2)

print(f"✅ Created train_v2.json with {len(train_data)} examples")
print(f"✅ Created test_v2.json with {len(test_data)} examples")
```

---

### Phase 2: Improve Data Quality

#### Step 2.1: Data Augmentation

Create variations of existing examples:

```python
# ai-service/training/tools/augment_data.py
import random

def augment_resume_data(examples, num_augmentations=3):
    """Create variations of resume examples"""
    augmented = []
    
    # Synonym replacements
    synonyms = {
        "worked": ["employed", "served", "engaged"],
        "developed": ["created", "built", "designed"],
        "managed": ["led", "supervised", "directed"],
        "Software Engineer": ["Developer", "Programmer", "Software Developer"],
        "Senior": ["Lead", "Principal", "Staff"]
    }
    
    for example in examples:
        augmented.append(example)  # Keep original
        
        for _ in range(num_augmentations):
            new_tokens = example["tokens"].copy()
            new_tags = example["ner_tags"].copy()
            
            # Random synonym replacement
            for i, token in enumerate(new_tokens):
                if token in synonyms and random.random() > 0.7:
                    new_tokens[i] = random.choice(synonyms[token])
            
            augmented.append({
                "tokens": new_tokens,
                "ner_tags": new_tags
            })
    
    return augmented

# Usage
with open('../data/train.json', 'r') as f:
    train_data = json.load(f)

augmented_data = augment_resume_data(train_data, num_augmentations=2)

with open('../data/train_augmented.json', 'w') as f:
    json.dump(augmented_data, f, indent=2)

print(f"✅ Augmented from {len(train_data)} to {len(augmented_data)} examples")
```

#### Step 2.2: Fix Inconsistent Annotations

```python
# ai-service/training/tools/validate_annotations.py
import json
from collections import Counter

def validate_annotations(data_file):
    """Check for annotation inconsistencies"""
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    issues = []
    
    for i, example in enumerate(data):
        tokens = example["tokens"]
        tags = example["ner_tags"]
        
        # Check 1: Length mismatch
        if len(tokens) != len(tags):
            issues.append(f"Example {i}: Token/tag length mismatch")
        
        # Check 2: Invalid B-I sequences
        for j in range(len(tags)):
            if tags[j].startswith("I-"):
                if j == 0 or not tags[j-1].endswith(tags[j][2:]):
                    issues.append(f"Example {i}, token {j}: Invalid I- tag without B-")
        
        # Check 3: Duplicate consecutive B- tags
        for j in range(len(tags)-1):
            if tags[j].startswith("B-") and tags[j+1].startswith("B-"):
                if tags[j][2:] == tags[j+1][2:]:
                    issues.append(f"Example {i}, token {j}: Consecutive B- tags for same entity")
    
    if issues:
        print("⚠️ Found annotation issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        print(f"\nTotal issues: {len(issues)}")
    else:
        print("✅ All annotations are valid!")
    
    return issues

# Run validation
validate_annotations('../data/train.json')
validate_annotations('../data/test.json')
```

---

### Phase 3: Optimize Training Parameters

#### Step 3.1: Increase Training Epochs

Current: 10 epochs → Recommended: 15-20 epochs

Edit `ai-service/training/data/colab_train.py`:

```python
def setup_training_arguments(self) -> TrainingArguments:
    return TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=15,  # Changed from 10
        learning_rate=3e-5,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=8,
        warmup_steps=500,  # Increased from 200
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=50,
        eval_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='f1',
        dataloader_num_workers=0,
        fp16=False,
        report_to=[],
        save_total_limit=3,  # Keep more checkpoints
        use_cpu=True,
    )
```

#### Step 3.2: Learning Rate Scheduling

Add learning rate scheduler:

```python
from transformers import get_linear_schedule_with_warmup

# In train_model method, add:
num_training_steps = len(self.train_dataset) * training_args.num_train_epochs
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=500,
    num_training_steps=num_training_steps
)
```

#### Step 3.3: Class Weighting for Imbalanced Data

```python
from torch import nn
import torch

# Calculate class weights
def compute_class_weights(train_dataset):
    label_counts = {}
    for example in train_dataset:
        for label in example['labels']:
            if label != -100:
                label_counts[label] = label_counts.get(label, 0) + 1
    
    total = sum(label_counts.values())
    weights = {label: total / count for label, count in label_counts.items()}
    
    return torch.tensor([weights.get(i, 1.0) for i in range(len(LABELS))])

# Use in training
class_weights = compute_class_weights(self.train_dataset)
loss_fct = nn.CrossEntropyLoss(weight=class_weights)
```

---

### Phase 4: Advanced Techniques

#### Step 4.1: Use Larger Model

Current: `microsoft/deberta-v3-base` (184M parameters)  
Upgrade to: `microsoft/deberta-v3-large` (434M parameters)

```python
MODEL_NAME = "microsoft/deberta-v3-large"
```

**Note:** This will increase model size to ~1.7 GB and training time by 2-3x.

#### Step 4.2: Ensemble Models

Train multiple models and combine predictions:

```python
# ai-service/training/ensemble.py
from transformers import pipeline

# Load multiple models
model1 = pipeline("ner", model="./models/resume-ner-deberta-v1")
model2 = pipeline("ner", model="./models/resume-ner-deberta-v2")
model3 = pipeline("ner", model="./models/resume-ner-roberta")

def ensemble_predict(text):
    """Combine predictions from multiple models"""
    predictions = [
        model1(text),
        model2(text),
        model3(text)
    ]
    
    # Majority voting
    entity_votes = {}
    for pred_set in predictions:
        for entity in pred_set:
            key = (entity['word'], entity['entity_group'])
            entity_votes[key] = entity_votes.get(key, 0) + 1
    
    # Keep entities with 2+ votes
    final_entities = [
        {'word': word, 'entity_group': entity_type}
        for (word, entity_type), votes in entity_votes.items()
        if votes >= 2
    ]
    
    return final_entities
```

#### Step 4.3: Active Learning

Identify difficult examples for manual review:

```python
# ai-service/training/tools/active_learning.py
import torch

def find_uncertain_predictions(model, tokenizer, texts, threshold=0.7):
    """Find predictions with low confidence for manual review"""
    uncertain = []
    
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        outputs = model(**inputs)
        
        probs = torch.softmax(outputs.logits, dim=-1)
        max_probs = torch.max(probs, dim=-1).values
        
        # Find tokens with low confidence
        low_confidence_tokens = (max_probs < threshold).sum().item()
        
        if low_confidence_tokens > 0:
            uncertain.append({
                'text': text,
                'low_confidence_count': low_confidence_tokens,
                'avg_confidence': max_probs.mean().item()
            })
    
    # Sort by uncertainty
    uncertain.sort(key=lambda x: x['avg_confidence'])
    
    return uncertain

# Review and re-annotate these examples
uncertain_examples = find_uncertain_predictions(model, tokenizer, test_texts)
print(f"Found {len(uncertain_examples)} uncertain examples for review")
```

---

### Phase 5: Domain-Specific Fine-tuning

#### Step 5.1: Pre-train on Resume Corpus

Before NER training, pre-train on unlabeled resumes:

```python
# ai-service/training/pretrain_mlm.py
from transformers import AutoModelForMaskedLM, DataCollatorForLanguageModeling

# Load base model
model = AutoModelForMaskedLM.from_pretrained("microsoft/deberta-v3-base")

# Prepare resume corpus (no labels needed)
resume_texts = [
    "Experienced software engineer with 5 years in backend development...",
    # Add 10,000+ resume texts
]

# Train with masked language modeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,
    mlm_probability=0.15
)

# Train for 3-5 epochs
# Then use this model for NER fine-tuning
```

#### Step 5.2: Multi-task Learning

Train on related tasks simultaneously:

```python
# Train on:
# 1. NER (entity recognition)
# 2. Sentence classification (section detection: experience, education, skills)
# 3. Relation extraction (company-role relationships)
```

---

## 📈 Expected Improvements

| Phase | Expected F1 Improvement | Time Required |
|-------|------------------------|---------------|
| Phase 1: Add missing entities | +5-10% | 2-3 days |
| Phase 2: Data quality | +2-3% | 1-2 days |
| Phase 3: Training optimization | +1-2% | 1 day |
| Phase 4: Advanced techniques | +2-4% | 3-5 days |
| Phase 5: Domain fine-tuning | +1-2% | 5-7 days |
| **Total** | **+11-21%** | **12-18 days** |

**Target:** 98.90% → **99.5-99.9%** F1 Score

---

## 🔄 Retraining Workflow

### Quick Retrain (After adding data)

```bash
cd ai-service

# 1. Merge new data
python training/tools/merge_data.py

# 2. Validate annotations
python training/tools/validate_annotations.py

# 3. Retrain model
source venv/bin/activate
python training/data/colab_train.py

# 4. Evaluate
python training/tools/evaluate_model.py
```

### Full Retrain (With all improvements)

```bash
# 1. Augment data
python training/tools/augment_data.py

# 2. Pre-train on resume corpus
python training/pretrain_mlm.py

# 3. Fine-tune NER
python training/data/colab_train.py

# 4. Ensemble training
python training/train_ensemble.py

# 5. Evaluate and compare
python training/tools/compare_models.py
```

---

## 📊 Monitoring Training

### TensorBoard

```bash
# Start TensorBoard
tensorboard --logdir=ai-service/logs

# Open browser: http://localhost:6006
```

### Track Metrics

```python
# Add to training script
import wandb

wandb.init(project="resume-ner", name="deberta-v3-improved")

# Automatically logs metrics
training_args = TrainingArguments(
    ...
    report_to=["wandb"],
    logging_steps=10
)
```

---

## 🎯 Recommended Priority Order

1. **URGENT:** Add training data for PERSON, EDUCATION, START_DATE, END_DATE (Phase 1)
2. **HIGH:** Validate and fix existing annotations (Phase 2.2)
3. **MEDIUM:** Increase training epochs to 15-20 (Phase 3.1)
4. **MEDIUM:** Data augmentation (Phase 2.1)
5. **LOW:** Try larger model (Phase 4.1)
6. **LOW:** Ensemble methods (Phase 4.2)

---

## 📝 Quick Wins (Can do today)

1. **Increase epochs:** Change `num_train_epochs=10` to `15` → +1-2% F1
2. **Add warmup steps:** Change `warmup_steps=200` to `500` → +0.5-1% F1
3. **Validate data:** Run validation script and fix issues → +1-2% F1

**Total quick wins:** +2.5-5% improvement in 1-2 hours!

---

## 🔍 Debugging Low Performance

### Check Entity Distribution

```python
from collections import Counter

def analyze_entity_distribution(data_file):
    with open(data_file) as f:
        data = json.load(f)
    
    entity_counts = Counter()
    for example in data:
        for tag in example['ner_tags']:
            if tag != 'O':
                entity_type = tag.split('-')[1]
                entity_counts[entity_type] += 1
    
    print("Entity Distribution:")
    for entity, count in entity_counts.most_common():
        print(f"  {entity}: {count}")

analyze_entity_distribution('ai-service/training/data/train.json')
```

### Visualize Predictions

```python
def visualize_predictions(text, entities):
    """Highlight entities in text"""
    from colorama import Fore, Style
    
    colors = {
        'PERSON': Fore.RED,
        'COMPANY': Fore.BLUE,
        'ROLE': Fore.GREEN,
        'LOCATION': Fore.YELLOW,
        'DEGREE': Fore.MAGENTA
    }
    
    for entity in entities:
        color = colors.get(entity['entity_group'], Fore.WHITE)
        text = text.replace(
            entity['word'],
            f"{color}{entity['word']}{Style.RESET_ALL}"
        )
    
    print(text)
```

---

## 📞 Next Steps

1. **Start with Phase 1:** Create at least 500 annotations for each missing entity type
2. **Run validation:** Fix any annotation errors
3. **Retrain:** Use the improved dataset
4. **Evaluate:** Compare new F1 scores
5. **Iterate:** Repeat until target accuracy achieved

**Goal:** Achieve 99%+ F1 score within 2-3 weeks of focused work.
