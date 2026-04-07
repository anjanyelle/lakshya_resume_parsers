# 🎓 Model Training Guide

## 📋 Overview

You have new labeled training data and want to retrain your DeBERTa NER model to improve resume parsing accuracy.

---

## 📁 Your New Training Data

You have labeled data in these files:
1. `292_label.json` - 1.4 MB of labeled examples
2. `project-11-at-2026-04-06-17-21-de2eb7d3.json` - 1.2 MB
3. `project-12-at-2026-04-06-17-29-f3ec51ec.json` - 1.4 MB

**Total:** ~4 MB of new labeled training data!

---

## 🚀 Step-by-Step Training Process

### **Step 1: Prepare the Data**

Convert your Label Studio JSON format to the training format:

```bash
cd ai-service
source venv/bin/activate
python training/prepare_new_data.py
```

This will:
- ✅ Load all your labeled JSON files
- ✅ Convert Label Studio format to NER format
- ✅ Split into train (80%) and test (20%) sets
- ✅ Save as `train.json` and `test.json`

**Expected output:**
```
📁 Loading 292_label.json...
   ✅ Converted XXX examples
📁 Loading project-11-at-2026-04-06-17-21-de2eb7d3.json...
   ✅ Converted XXX examples
📊 Total examples: XXX
📊 Train examples: XXX
📊 Test examples: XXX
✅ Saved train data to: training/data/train.json
✅ Saved test data to: training/data/test.json
```

---

### **Step 2: Train the Model**

Run the training script:

```bash
python training/train.py
```

**Training Configuration:**
- **Model:** DeBERTa-v3-base
- **Epochs:** 5
- **Learning Rate:** 2e-5
- **Batch Size:** 1 (with gradient accumulation of 8)
- **Labels:** COMPANY, ROLE, LOCATION, START_DATE, END_DATE, PERSON, CLIENT, EDUCATION, DEGREE

**Expected Duration:** 
- ~30-60 minutes depending on data size and hardware
- GPU recommended but works on CPU/MPS

**Training Progress:**
```
🚀 Starting DeBERTa-v3 NER training pipeline
📁 Loading training data...
✅ Loaded XXX training examples
✅ Loaded XXX test examples
🤖 Initializing DeBERTa-v3 model and tokenizer...
🔧 Preparing datasets...
🚀 Starting model training...
Epoch 1/5: [████████████████████] 100%
Epoch 2/5: [████████████████████] 100%
...
📊 FINAL EVALUATION RESULTS
Test Precision: 0.XXXX
Test Recall: 0.XXXX
Test F1 Score: 0.XXXX
💾 Saving model to models/resume-ner-deberta...
✅ Model saved!
🎉 Training completed successfully!
```

---

### **Step 3: Verify the Model**

After training, verify the model works:

```bash
python test_model_loading.py
```

This will:
- ✅ Load the newly trained model
- ✅ Test it on sample text
- ✅ Show extracted entities

---

### **Step 4: Restart the Service**

Restart the AI service to use the new model:

```bash
python main.py
```

The parser will automatically use your newly trained model!

---

## 📊 What Gets Trained

Your model will learn to extract:

| Entity Type | Example |
|-------------|---------|
| **COMPANY** | TCS, Infosys, Accenture |
| **ROLE** | Senior Software Engineer, Lead Developer |
| **LOCATION** | Bangalore, Mumbai, New York |
| **START_DATE** | 2019, Jan 2020 |
| **END_DATE** | Present, 2023 |
| **PERSON** | John Doe, Anahita Zahl |
| **CLIENT** | Microsoft, Google |
| **EDUCATION** | Bachelor of Technology |
| **DEGREE** | B.Tech, MBA |

---

## 🎯 Expected Improvements

After training with your new data:

**Before:**
- ❌ Missing some companies
- ❌ Incorrect role extraction
- ❌ Date parsing issues

**After:**
- ✅ Better company name recognition
- ✅ Improved role/title extraction
- ✅ More accurate date parsing
- ✅ Better handling of your specific resume formats

---

## 📈 Monitoring Training

During training, watch for:

1. **F1 Score:** Should be > 0.85 for good performance
2. **Loss:** Should decrease over epochs
3. **Per-Entity Scores:** Check which entities need more data

**Good Training:**
```
Epoch 1: Loss 0.45, F1: 0.72
Epoch 2: Loss 0.28, F1: 0.81
Epoch 3: Loss 0.18, F1: 0.87
Epoch 4: Loss 0.12, F1: 0.89
Epoch 5: Loss 0.09, F1: 0.91  ✅ Great!
```

**Needs More Data:**
```
COMPANY  : 0.9200 (support: 450)  ✅ Good
ROLE     : 0.8800 (support: 380)  ✅ Good
LOCATION : 0.6500 (support: 120)  ⚠️ Needs more examples
START_DATE: 0.5200 (support: 80)   ⚠️ Needs more examples
```

---

## 🔧 Troubleshooting

### **Issue: Out of Memory**
```bash
# Reduce batch size in train.py line 185:
per_device_train_batch_size=1  # Already set to minimum
```

### **Issue: Training Too Slow**
- Use GPU if available
- Reduce epochs from 5 to 3
- Use smaller dataset for testing

### **Issue: Low F1 Score**
- Add more labeled examples
- Check label quality
- Increase training epochs

---

## 💾 Model Files

After training, your model will be saved to:
```
ai-service/models/resume-ner-deberta/
├── config.json
├── model.safetensors (or pytorch_model.bin)
├── tokenizer_config.json
├── vocab.txt
└── special_tokens_map.json
```

**Size:** ~700 MB

---

## 🎉 Quick Start Commands

```bash
# 1. Prepare data
cd ai-service
source venv/bin/activate
python training/prepare_new_data.py

# 2. Train model
python training/train.py

# 3. Test model
python test_model_loading.py

# 4. Restart service
python main.py
```

---

## 📝 Notes

- **Backup:** Your old model is automatically backed up
- **Training Time:** ~30-60 minutes
- **GPU:** Recommended but not required
- **Data Quality:** More important than quantity
- **Incremental Training:** You can add more data and retrain anytime

---

## ✅ Success Checklist

- [ ] Data preparation completed
- [ ] Training finished without errors
- [ ] F1 score > 0.85
- [ ] Model saved successfully
- [ ] Test script shows good results
- [ ] Service restarted with new model
- [ ] Resume parsing improved

---

**Ready to train? Run the commands above!** 🚀
