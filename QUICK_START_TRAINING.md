# Quick Start - Train Your Model

## Copy-Paste These Commands

Open Terminal and run these commands **one by one**:

### 1. Navigate to Project
```bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser"
```

### 2. Verify Labels (Already Done ✅)
```bash
cd ai-service/training
python3 verify_labels.py
```

**Expected**: `✅ NO BIO TAGGING ERRORS FOUND!`

### 3. Train Model (Choose One Option)

#### Option A: Train on Google Colab (Recommended - FREE GPU)

1. Go to https://colab.research.google.com/
2. Click "New Notebook"
3. Runtime → Change runtime type → GPU (T4)
4. Copy-paste this into a cell:

```python
# Install dependencies
!pip install transformers datasets evaluate seqeval torch accelerate

# Clone or upload your code
# (Upload the ai-service/training folder to Colab)

# Run training
!python3 train_with_class_weights.py
```

#### Option B: Train Locally (2-4 hours on Mac)

```bash
# From: /Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service/training

python3 train_with_class_weights.py
```

### 4. Monitor Progress

You'll see:
```
📊 Training configuration:
   Epochs: 15
   Batch size: 8
   Learning rate: 2e-05
   
🏋️  Starting training...
Epoch 1/15: [████████] 100%
   eval_f1: 0.8234
Epoch 2/15: [████████] 100%
   eval_f1: 0.9012
...
```

**Wait for it to complete** (30-40 min on Colab GPU, 2-4 hours on Mac CPU)

### 5. Test New Model

```bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service"

python3 << 'EOF'
from transformers import pipeline

ner = pipeline(
    "ner",
    model="models/resume-ner-deberta-weighted",
    aggregation_strategy="simple"
)

text = "I worked as a Junior Full Stack Developer at Google"
result = ner(text)

print("\n🔍 Test Results:")
for entity in result:
    print(f"   {entity['entity_group']:15s}: {entity['word']}")
EOF
```

**Expected (GOOD)**:
```
   ROLE           : Junior Full Stack Developer
   COMPANY        : Google
```

### 6. Replace Old Model (If New Model Works Better)

```bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service"

# Backup old model
mv models/resume-ner-deberta models/resume-ner-deberta-old

# Use new model
mv models/resume-ner-deberta-weighted models/resume-ner-deberta

# Restart AI service
cd ..
pkill -f "uvicorn.*ai-service"
cd ai-service
source venv/bin/activate
python3 -m uvicorn main:app --reload --port 8000
```

---

## Troubleshooting

### "No such file or directory"
Make sure you're in the right directory:
```bash
pwd
# Should show: /Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service/training
```

### "Out of memory"
Reduce batch size in `train_with_class_weights.py`:
```python
CONFIG = {
    "per_device_train_batch_size": 4,  # Change from 8 to 4
}
```

### Training too slow
Use Google Colab with free GPU instead of local training.

---

## Summary

1. ✅ Labels verified - Ready to train!
2. 🚀 Run `python3 train_with_class_weights.py`
3. ⏱️ Wait 30-40 min (Colab) or 2-4 hours (Mac)
4. 🧪 Test the new model
5. 🔄 Replace old model if better

**Current model works fine, so training is optional but recommended!**
