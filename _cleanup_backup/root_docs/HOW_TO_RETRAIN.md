# How to Retrain the Model (Step-by-Step)

## Step 1: Verify Labels are Correct ✅

Before training, check that your labels are correct:

```bash
cd ai-service/training
python3 verify_labels.py
```

**Expected output:**
```
✅ NO BIO TAGGING ERRORS FOUND!
✅ ALL CHECKS PASSED - READY TO TRAIN!
```

If you see errors, fix them in the `.conll` files before proceeding.

---

## Step 2: Choose Training Environment

### Option A: Train on Google Colab (Recommended - FREE GPU)

1. **Upload files to Google Drive:**
   - Upload `ai-service/training/` folder to Google Drive
   - Make sure `dataset_train.conll` and `dataset_test.conll` are in `training/data/`

2. **Open Google Colab:**
   - Go to https://colab.research.google.com/
   - Click "New Notebook"

3. **Enable GPU:**
   - Runtime → Change runtime type → GPU (T4)

4. **Run training:**
   ```python
   # Mount Google Drive
   from google.colab import drive
   drive.mount('/content/drive')
   
   # Navigate to your training folder
   %cd /content/drive/MyDrive/your-folder/ai-service/training
   
   # Install dependencies
   !pip install transformers datasets evaluate seqeval torch accelerate
   
   # Run training with class weights
   !python3 train_with_class_weights.py
   ```

5. **Download trained model:**
   - Model will be saved in `ai-service/models/resume-ner-deberta-weighted/`
   - Download the entire folder to your local machine

### Option B: Train Locally (Requires Good CPU/GPU)

```bash
cd ai-service/training

# Make sure you have dependencies
pip install transformers datasets evaluate seqeval torch

# Run training (will take 2-4 hours on CPU, 30-40 min on GPU)
python3 train_with_class_weights.py
```

---

## Step 3: Monitor Training

You'll see output like:

```
📊 STATISTICS
   Total tokens: 69,257
   B- tags: 8,234 tokens
   I- tags: 4,567 tokens
   Applied 2.0x weight to I- tags

🏋️  Starting training...
Epoch 1/15: [████████████████] 100%
   eval_f1: 0.8234
Epoch 2/15: [████████████████] 100%
   eval_f1: 0.9012
...
Epoch 15/15: [████████████████] 100%
   eval_f1: 0.9733

✅ Training complete!
   F1 Score: 0.9733
```

**Good signs:**
- F1 score increasing each epoch
- Final F1 > 0.95
- No errors or warnings

**Bad signs:**
- F1 score decreasing (overfitting)
- Out of memory errors (reduce batch size)
- Loss not decreasing (learning rate too high/low)

---

## Step 4: Test the New Model

After training completes, test it:

```bash
cd ai-service

# Test the new model
python3 << 'EOF'
from transformers import pipeline

# Load new model
ner = pipeline(
    "ner",
    model="models/resume-ner-deberta-weighted",
    aggregation_strategy="simple"
)

# Test
text = "I worked as a Junior Full Stack Developer at Google from Jan 2020 to Dec 2022"
result = ner(text)

print("\n🔍 Test Results:")
for entity in result:
    print(f"   {entity['entity_group']:15s}: {entity['word']}")

EOF
```

**Expected output (GOOD):**
```
🔍 Test Results:
   ROLE           : Junior Full Stack Developer
   COMPANY        : Google
   DATE_START     : Jan 2020
   DATE_END       : Dec 2022
```

**If you see this (BAD - model still has issue):**
```
   ROLE           : Junior
   ROLE           : Full
   ROLE           : Stack
   ROLE           : Developer
```

---

## Step 5: Replace Old Model

If the new model works better:

```bash
# Backup old model
mv ai-service/models/resume-ner-deberta ai-service/models/resume-ner-deberta-old

# Use new model
mv ai-service/models/resume-ner-deberta-weighted ai-service/models/resume-ner-deberta

# Restart AI service
# (It will automatically load the new model)
```

---

## Step 6: Verify in Application

1. **Restart AI service:**
   ```bash
   cd ai-service
   source venv/bin/activate
   python3 -m uvicorn main:app --reload --port 8000
   ```

2. **Test via API:**
   ```bash
   curl -X POST http://localhost:8000/parse-sections \
     -H 'Content-Type: application/json' \
     -d '{
       "experience_text": "I worked as a Senior Software Engineer at Microsoft",
       "education_text": ""
     }'
   ```

3. **Check output:**
   - Role should be "Senior Software Engineer" (not "Senior", "Software", "Engineer" separately)
   - Company should be "Microsoft"

---

## Troubleshooting

### Out of Memory Error
**Solution:** Reduce batch size in `train_with_class_weights.py`:
```python
CONFIG = {
    "per_device_train_batch_size": 4,  # Reduced from 8
    "gradient_accumulation_steps": 2,  # Add this line
}
```

### Training Too Slow
**Solution:** Use Google Colab with GPU (30-40 minutes vs 2-4 hours on CPU)

### F1 Score Not Improving
**Solutions:**
1. Increase epochs to 20
2. Adjust learning rate: try `1e-5` or `3e-5`
3. Increase I- tag weight to `3.0` instead of `2.0`

### Model Still Predicts All B- Tags
**Solutions:**
1. Increase I- tag weight to `3.0` or `4.0`
2. Train for more epochs (20-25)
3. Add CRF layer (advanced - see `RETRAINING_RECOMMENDATIONS.md`)

---

## Quick Reference

### Files You Need:
- ✅ `ai-service/training/data/dataset_train.conll` - Training data
- ✅ `ai-service/training/data/dataset_test.conll` - Test data
- ✅ `ai-service/training/verify_labels.py` - Label verification
- ✅ `ai-service/training/train_with_class_weights.py` - Training script

### Commands:
```bash
# 1. Verify labels
cd ai-service/training && python3 verify_labels.py

# 2. Train model
python3 train_with_class_weights.py

# 3. Test model
cd ../.. && python3 test_new_model.py

# 4. Replace old model
mv models/resume-ner-deberta models/resume-ner-deberta-old
mv models/resume-ner-deberta-weighted models/resume-ner-deberta
```

### Expected Timeline:
- **Verification**: 1-2 minutes
- **Training (Colab GPU)**: 30-40 minutes
- **Training (Local CPU)**: 2-4 hours
- **Testing**: 2-3 minutes
- **Total**: ~1 hour (Colab) or ~3-5 hours (Local)

---

## Summary

1. ✅ **Verify labels** - Run `verify_labels.py`
2. 🚀 **Train model** - Run `train_with_class_weights.py` (preferably on Colab GPU)
3. 🧪 **Test model** - Check if it predicts I- tags correctly
4. 🔄 **Replace model** - Swap old model with new one
5. ✅ **Done!** - Enjoy better entity extraction

**Current model works fine with manual aggregation, so retraining is optional but recommended for best results!**
