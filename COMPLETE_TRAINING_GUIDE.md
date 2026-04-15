# Complete Training Guide - All 12 Label Studio Labels

## ✅ **Code Updated for All 12 Labels**

I've updated all the training and inference code to use **all 12 labels** from your Label Studio screenshot:

**Work Experience (6 labels):**
- COMPANY
- CLIENT
- ROLE
- LOCATION
- DATE_START
- DATE_END

**Education (6 labels):**
- DEGREE
- FIELD
- INSTITUTION
- EDU_YEAR_START
- EDU_YEAR_END
- GRADE

---

## 📋 **Files Updated**

1. ✅ `ai-service/training/data/colab_train.py` - Training script with 12 labels
2. ✅ `ai-service/training/model_loader.py` - Model loader with 12 labels
3. ✅ `ai-service/parsers/deberta_ner_parser.py` - Inference code with 12 labels

---

## 🚀 **Step-by-Step Training Instructions**

### **Step 1: Prepare Training Data**

You need to regenerate `train.json` with all 12 labels from your Label Studio export.

**Option A: If you have Label Studio export file**

1. Export from Label Studio as JSON
2. Save as `datalabel_full.json` in `ai-service/training/data/`
3. Run conversion:
   ```bash
   cd ai-service/training/data
   python convert_to_training_format.py
   ```

**Option B: If your current train.json already has all 12 labels**

Check if your current `train.json` has all labels:
```bash
cd ai-service/training/data
python3 -c "
import json
from collections import Counter

with open('train.json', 'r') as f:
    data = json.load(f)

all_tags = set()
for item in data:
    all_tags.update(item['ner_tags'])

print('Labels in train.json:')
for label in sorted(all_tags):
    print(f'  {label}')
"
```

**Expected output should include:**
- B-DATE_START, I-DATE_START
- B-DATE_END, I-DATE_END
- B-INSTITUTION, I-INSTITUTION
- B-FIELD, I-FIELD
- B-EDU_YEAR_START, I-EDU_YEAR_START
- B-EDU_YEAR_END, I-EDU_YEAR_END
- B-GRADE, I-GRADE

---

### **Step 2: Upload to Google Colab**

1. Go to: https://colab.research.google.com
2. Create a new notebook
3. Upload these 3 files (drag & drop):
   - `colab_train.py` (from `ai-service/training/data/`)
   - `train.json` (from `ai-service/training/data/`)
   - `test.json` (from `ai-service/training/data/`)

---

### **Step 3: Install Dependencies in Colab**

In Colab cell 1, run:
```python
!pip install transformers datasets torch scikit-learn accelerate
```

---

### **Step 4: Run Training**

In Colab cell 2, run:
```python
!python colab_train.py
```

**Expected output:**
```
==================================================
🎯 Resume NER Model Training (Colab Version)
==================================================
🖥️  Using device: cuda
GPU: Tesla T4 (or similar)
📂 Loading data from train.json and test.json...
✅ Loaded 7382 train and 820 test examples
🤖 Loading model and tokenizer: microsoft/deberta-v3-base
✅ Model initialized with 25 labels
🔧 Preparing datasets...
✅ Datasets prepared with 7382 train and 820 test examples
🚀 Starting model training...
```

**Training time:**
- With GPU (T4/V100): 30-60 minutes
- Without GPU (CPU): 2-4 hours

---

### **Step 5: Download Trained Model**

After training completes, download these files from Colab:

**Method 1: Using Colab file browser**
1. Click folder icon on left sidebar
2. Navigate to `models/resume-ner-deberta/`
3. Download each file:
   - `pytorch_model.bin` (or `model.safetensors`)
   - `config.json`
   - `tokenizer_config.json`
   - `vocab.txt`
   - `special_tokens_map.json`
   - `label_mappings.json`

**Method 2: Using code in Colab**
```python
# In Colab cell 3
from google.colab import files
import os

model_dir = 'models/resume-ner-deberta'
for filename in os.listdir(model_dir):
    filepath = os.path.join(model_dir, filename)
    if os.path.isfile(filepath):
        files.download(filepath)
```

---

### **Step 6: Replace Local Model Files**

On your Mac:

```bash
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser/ai-service

# Backup old model
mv models/resume-ner-deberta models/resume-ner-deberta.backup.$(date +%Y%m%d)

# Create new directory
mkdir -p models/resume-ner-deberta

# Copy downloaded files to models/resume-ner-deberta/
# (Drag files from Downloads folder to models/resume-ner-deberta/)
```

**Required files in `models/resume-ner-deberta/`:**
- ✅ `pytorch_model.bin` (or `model.safetensors`)
- ✅ `config.json`
- ✅ `tokenizer_config.json`
- ✅ `vocab.txt`
- ✅ `special_tokens_map.json`
- ✅ `label_mappings.json`

---

### **Step 7: Restart AI Service**

```bash
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser/ai-service
source venv/bin/activate
python main.py
```

**Expected output:**
```
✅ DeBERTa model loaded successfully
   Model: models/resume-ner-deberta
   Labels: 25 (12 entity types)
   Device: cpu
```

---

### **Step 8: Test Extraction**

Upload a resume through your web interface and verify all fields are extracted:

**Work Experience:**
- ✅ COMPANY: "Infosys"
- ✅ CLIENT: "Google"
- ✅ ROLE: "Senior Data Engineer"
- ✅ LOCATION: "Hyderabad"
- ✅ **DATE_START: "Jan 2021"** (NEW!)
- ✅ **DATE_END: "Mar 2023"** (NEW!)

**Education:**
- ✅ **INSTITUTION: "JNTU Hyderabad"** (NEW!)
- ✅ DEGREE: "B.Tech"
- ✅ **FIELD: "Computer Science"** (NEW!)
- ✅ **EDU_YEAR_START: "2015"** (NEW!)
- ✅ **EDU_YEAR_END: "2019"** (NEW!)
- ✅ **GRADE: "8.2"** (NEW!)

---

## 🎯 **What You'll Get After Training**

### **Before (Current Model - 8 labels):**
```json
{
  "work_experience": [
    {
      "company": "Infosys",
      "role": "Senior Data Engineer",
      "location": "Hyderabad",
      "start_date": null,  // ❌ Missing
      "end_date": null     // ❌ Missing
    }
  ],
  "education": [
    {
      "institution": "",   // ❌ Missing
      "degree": "B.Tech",
      "field_of_study": null,  // ❌ Missing
      "start_year": null,      // ❌ Missing
      "end_year": null,        // ❌ Missing
      "grade": null            // ❌ Missing
    }
  ]
}
```

### **After (New Model - 12 labels):**
```json
{
  "work_experience": [
    {
      "company": "Infosys",
      "role": "Senior Data Engineer",
      "location": "Hyderabad",
      "start_date": "Jan 2021",  // ✅ Extracted
      "end_date": "Mar 2023"     // ✅ Extracted
    }
  ],
  "education": [
    {
      "institution": "JNTU Hyderabad",  // ✅ Extracted
      "degree": "B.Tech",
      "field_of_study": "Computer Science",  // ✅ Extracted
      "start_year": "2015",                  // ✅ Extracted
      "end_year": "2019",                    // ✅ Extracted
      "grade": "8.2"                         // ✅ Extracted
    }
  ]
}
```

---

## ⚠️ **Important Notes**

1. **Training data must have all 12 labels** - Check your `train.json` first
2. **Use GPU in Colab** - Training on CPU takes 2-4 hours
3. **Download ALL model files** - Missing files will cause errors
4. **Backup old model** - In case you need to revert
5. **Test thoroughly** - Upload multiple resumes to verify extraction

---

## 🐛 **Troubleshooting**

### **Issue: train.json doesn't have all 12 labels**

**Solution:** Re-export from Label Studio and regenerate train.json

### **Issue: Training fails with "CUDA out of memory"**

**Solution:** Reduce batch size in `colab_train.py`:
```python
per_device_train_batch_size=1,  # Changed from 2
gradient_accumulation_steps=16,  # Changed from 8
```

### **Issue: Model doesn't extract new labels**

**Solution:** 
1. Verify model files were copied correctly
2. Check `label_mappings.json` has all 12 labels
3. Restart AI service
4. Clear browser cache

### **Issue: "Model not found" error**

**Solution:** Check file paths:
```bash
ls -la ai-service/models/resume-ner-deberta/
```

Should show all 6 required files.

---

## ✅ **Checklist**

- [ ] Verified `train.json` has all 12 label types
- [ ] Uploaded 3 files to Google Colab
- [ ] Installed dependencies in Colab
- [ ] Started training (30-60 min with GPU)
- [ ] Downloaded all 6 model files
- [ ] Backed up old model
- [ ] Copied new model files to `models/resume-ner-deberta/`
- [ ] Restarted AI service
- [ ] Tested with sample resumes
- [ ] Verified all 12 entity types extract correctly

---

## 🎉 **Success!**

After completing these steps, your resume parser will extract **all 12 entity types** from your Label Studio labels, giving you complete work experience and education data!

Your 2,000+ labeled resumes will finally be fully utilized! 🚀
