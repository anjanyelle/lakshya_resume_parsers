# Training Steps - Get All Labels Working

## 🎯 Current Situation

Your `train.json` has **8 labels** but you need **12 labels** from Label Studio.

**What's in train.json:**
- ✅ COMPANY, CLIENT, ROLE, LOCATION
- ✅ START_DATE, END_DATE (but you labeled as DATE_START, DATE_END)
- ✅ EDUCATION (but you labeled as INSTITUTION)
- ✅ DEGREE

**What's missing:**
- ❌ FIELD (field of study)
- ❌ EDU_YEAR_START
- ❌ EDU_YEAR_END
- ❌ GRADE

---

## 🚀 Two Options

### **Option 1: Train with Current 8 Labels (QUICK - 30 min)**

Use existing `train.json` to get dates and institutions working immediately.

**Pros:**
- ✅ Quick (30-60 min training)
- ✅ Ready to use now
- ✅ Fixes missing dates and institutions

**Cons:**
- ❌ Won't extract FIELD, EDU_YEAR_START, EDU_YEAR_END, GRADE

---

### **Option 2: Regenerate train.json with All 12 Labels (COMPLETE - 2 hours)**

Re-export from Label Studio and convert with all 12 labels.

**Pros:**
- ✅ All 12 labels working
- ✅ Complete education data (field, years, grades)
- ✅ Uses all your Label Studio work

**Cons:**
- ❌ Need to re-export from Label Studio
- ❌ Need to update conversion script
- ❌ Longer process

---

## 📋 OPTION 1: Quick Training (Recommended to Start)

### Step 1: Upload Files to Google Colab

Create a new Colab notebook and upload these files:
```
ai-service/training/data/colab_train.py
ai-service/training/data/train.json
ai-service/training/data/test.json
```

### Step 2: Install Dependencies

```python
# In Colab cell 1
!pip install transformers datasets torch scikit-learn accelerate
```

### Step 3: Run Training

```python
# In Colab cell 2
!python colab_train.py
```

**Expected time:** 30-60 minutes with GPU (2-4 hours without GPU)

### Step 4: Download Model Files

After training completes, download these files from Colab:
- `models/resume-ner-deberta/pytorch_model.bin` (or `model.safetensors`)
- `models/resume-ner-deberta/config.json`
- `models/resume-ner-deberta/tokenizer_config.json`
- `models/resume-ner-deberta/vocab.txt`
- `models/resume-ner-deberta/special_tokens_map.json`
- `models/resume-ner-deberta/label_mappings.json`

### Step 5: Replace Model Locally

```bash
# Backup old model
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser/ai-service
mv models/resume-ner-deberta models/resume-ner-deberta.backup

# Create new directory
mkdir -p models/resume-ner-deberta

# Copy downloaded files to models/resume-ner-deberta/
```

### Step 6: Restart AI Service

```bash
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser/ai-service
source venv/bin/activate
python main.py
```

### Step 7: Test

Upload a resume and verify:
- ✅ Start dates extracted
- ✅ End dates extracted
- ✅ Institutions extracted
- ✅ Degrees extracted

---

## 📋 OPTION 2: Complete Training with All 12 Labels

### Step 1: Export from Label Studio

1. Go to Label Studio
2. Export your project as JSON
3. Save as `datalabel_full.json`

### Step 2: Update Conversion Script

The conversion script needs to preserve all 12 labels. Check if `convert_to_training_format.py` is mapping labels correctly.

### Step 3: Convert to Training Format

```bash
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser/ai-service/training/data

# Run conversion
python convert_to_training_format.py
```

### Step 4: Verify All Labels Present

```bash
python3 -c "
import json
from collections import Counter

with open('train.json', 'r') as f:
    data = json.load(f)

all_tags = []
for item in data:
    all_tags.extend(item['ner_tags'])

label_counts = Counter(all_tags)
print('Labels in train.json:')
for label in sorted(label_counts.keys()):
    print(f'  {label}: {label_counts[label]}')
"
```

**Expected labels:**
- B-COMPANY, I-COMPANY
- B-CLIENT, I-CLIENT
- B-ROLE, I-ROLE
- B-LOCATION, I-LOCATION
- B-DATE_START, I-DATE_START
- B-DATE_END, I-DATE_END
- B-INSTITUTION, I-INSTITUTION
- B-DEGREE, I-DEGREE
- B-FIELD, I-FIELD
- B-EDU_YEAR_START, I-EDU_YEAR_START
- B-EDU_YEAR_END, I-EDU_YEAR_END
- B-GRADE, I-GRADE

### Step 5: Update Training Script

Update `colab_train.py` to include all 12 labels:

```python
LABELS = [
    "O",
    "B-COMPANY", "I-COMPANY",
    "B-CLIENT", "I-CLIENT",
    "B-ROLE", "I-ROLE",
    "B-LOCATION", "I-LOCATION",
    "B-DATE_START", "I-DATE_START",
    "B-DATE_END", "I-DATE_END",
    "B-INSTITUTION", "I-INSTITUTION",
    "B-DEGREE", "I-DEGREE",
    "B-FIELD", "I-FIELD",
    "B-EDU_YEAR_START", "I-EDU_YEAR_START",
    "B-EDU_YEAR_END", "I-EDU_YEAR_END",
    "B-GRADE", "I-GRADE"
]
```

### Step 6: Update Inference Code

Update `deberta_ner_parser.py` to extract all 12 labels (I can help with this after training).

### Step 7: Train in Colab

Same as Option 1, steps 1-7.

---

## 💡 My Recommendation

**Start with Option 1** to get dates and institutions working immediately (30-60 min).

**Then do Option 2** later if you need field of study, education years, and grades.

---

## 🚀 Quick Start (Option 1)

1. Open Google Colab: https://colab.research.google.com
2. Upload these 3 files:
   - `colab_train.py`
   - `train.json`
   - `test.json`
3. Run:
   ```python
   !pip install transformers datasets torch scikit-learn accelerate
   !python colab_train.py
   ```
4. Wait 30-60 minutes
5. Download model files
6. Replace local model
7. Restart AI service
8. Test!

---

## ✅ After Training (Option 1)

You'll have:
- ✅ Companies extracted
- ✅ Clients extracted
- ✅ Job titles extracted
- ✅ Locations extracted
- ✅ **Start dates extracted** (NEW!)
- ✅ **End dates extracted** (NEW!)
- ✅ **Institutions extracted** (NEW!)
- ✅ Degrees extracted

Still missing (need Option 2):
- ❌ Field of study
- ❌ Education start year
- ❌ Education end year
- ❌ Grades

---

## 📞 Need Help?

If you get stuck during training, let me know at which step and I'll help troubleshoot!
