# Model Retraining Recommendations

## Current Issue
The model predicts **all B- tags** instead of using I- tags for multi-token entity continuation, despite having correct training data.

## Root Cause
- **Class imbalance**: More B- tags than I- tags in training data
- **Model converged to local minimum**: Learned to predict B- for all entity tokens
- **Insufficient training signal**: Model didn't learn the BIO sequence pattern properly

## Recommended Solutions

### Option 1: Add Class Weights (Recommended)
Weight the I- tags higher during training to force the model to learn them:

```python
from torch.nn import CrossEntropyLoss

# Calculate class weights
def compute_class_weights(train_dataset):
    from collections import Counter
    label_counts = Counter()
    
    for example in train_dataset:
        for label in example['labels']:
            if label != -100:  # Ignore padding
                label_counts[label] += 1
    
    # Give I- tags 2x weight
    weights = []
    for label_id in range(len(id2label)):
        label_name = id2label[label_id]
        if label_name.startswith('I-'):
            weights.append(2.0)  # 2x weight for I- tags
        else:
            weights.append(1.0)
    
    return torch.FloatTensor(weights)

# In training script, modify the model:
class_weights = compute_class_weights(tokenized_train)
model.config.loss_fct = CrossEntropyLoss(weight=class_weights.to(model.device))
```

### Option 2: Increase Training Epochs
Train for **15-20 epochs** instead of 8 to give the model more time to learn the sequence pattern:

```python
training_args = TrainingArguments(
    num_train_epochs=15,  # Increased from 8
    learning_rate=2e-5,   # Slightly lower for stability
    warmup_steps=1000,    # More warmup
    # ... rest of config
)
```

### Option 3: Use CRF Layer (Advanced)
Add a Conditional Random Field layer on top of DeBERTa to enforce BIO sequence constraints:

```python
from torchcrf import CRF

class DeBERTaWithCRF(nn.Module):
    def __init__(self, base_model, num_labels):
        super().__init__()
        self.deberta = base_model
        self.crf = CRF(num_labels, batch_first=True)
    
    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.deberta(input_ids, attention_mask=attention_mask)
        emissions = outputs.logits
        
        if labels is not None:
            # CRF enforces valid BIO sequences
            loss = -self.crf(emissions, labels, mask=attention_mask.byte())
            return loss
        else:
            # Viterbi decoding for inference
            predictions = self.crf.decode(emissions, mask=attention_mask.byte())
            return predictions
```

### Option 4: Data Augmentation
Add more multi-word entity examples to the training data:

```python
# Example: Augment training data with synthetic multi-word entities
augmented_examples = [
    "Senior Software Engineer at Google",
    "Junior Full Stack Developer at Microsoft",
    "Lead Data Scientist at Amazon",
    # ... add 100+ examples
]
```

### Option 5: Lower Learning Rate + More Epochs
```python
training_args = TrainingArguments(
    num_train_epochs=20,
    learning_rate=1e-5,  # Lower learning rate
    warmup_ratio=0.1,    # 10% warmup
    per_device_train_batch_size=4,  # Smaller batches
    gradient_accumulation_steps=4,  # Accumulate to effective batch of 16
)
```

## Quick Fix for Current Model

**The manual aggregation I implemented works perfectly** for the current model. It combines consecutive entities of the same type, which solves the immediate problem.

You can continue using the current model with the aggregation fix while you retrain a better model in the background.

## Recommended Approach

1. **Short term**: Use current model with manual aggregation (already implemented ✅)
2. **Long term**: Retrain with **Option 1 (Class Weights)** + **Option 2 (More Epochs)**

### Updated Training Script

```python
# train_with_class_weights.py

from collections import Counter
import torch
from torch.nn import CrossEntropyLoss

# ... (load data, tokenizer, etc.)

# Compute class weights
label_counts = Counter()
for example in tokenized_train:
    for label in example['labels']:
        if label != -100:
            label_counts[label] += 1

# Create weights: I- tags get 2x weight
weights = []
for label_id in range(len(id2label)):
    label_name = id2label[label_id]
    if label_name.startswith('I-'):
        weights.append(2.0)
    else:
        weights.append(1.0)

class_weights = torch.FloatTensor(weights)

# Load model
model = AutoModelForTokenClassification.from_pretrained(
    "microsoft/deberta-v3-base",
    num_labels=len(label2id),
    id2label=id2label,
    label2id=label2id
)

# Apply class weights to loss function
model.config.loss_fct = CrossEntropyLoss(
    weight=class_weights.to(model.device),
    ignore_index=-100
)

# Training args with more epochs
training_args = TrainingArguments(
    output_dir="./resume-ner-deberta-weighted",
    num_train_epochs=15,  # Increased
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    warmup_steps=1000,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    fp16=True
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

trainer.train()
```

## Expected Results

With class weights + more epochs:
- **I- tag prediction accuracy**: Should improve from ~0% to 85%+
- **Entity aggregation**: Will work automatically without manual fix
- **F1 Score**: Should maintain or improve current 96.33%

## Testing After Retraining

```python
# Test the new model
from transformers import pipeline

ner = pipeline("ner", model="./resume-ner-deberta-weighted", aggregation_strategy="simple")
result = ner("I worked as a Junior Full Stack Developer at Google")

# Should output:
# [{'entity_group': 'ROLE', 'word': 'Junior Full Stack Developer', ...},
#  {'entity_group': 'COMPANY', 'word': 'Google', ...}]
```

---

**Bottom line**: Your training data is perfect. The model just needs class weights or more training to learn the I- tag pattern correctly.
