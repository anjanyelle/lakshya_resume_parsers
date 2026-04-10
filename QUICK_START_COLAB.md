# 🚀 Quick Start: Train DeBERTa v3 on Google Colab

## Your Files Ready ✅

```
ai-service/training/data/
├── datalabel.json   (2.4 MB)
├── datalabel1.json  (2.5 MB)
└── datalabel2.json  (2.3 MB)
```

**Total: ~1,500-1,800 annotated resumes**

---

## 🎯 Method 1: Direct Upload (RECOMMENDED)

### Step-by-Step:

**1. Open Google Colab**
- Go to: https://colab.research.google.com/
- Upload: `Train_DeBERTa_Team_Workflow.ipynb`

**2. Enable GPU** ⚡
- Runtime → Change runtime type → GPU (T4)
- Click Save

**3. Run First 2 Cells**
- Check GPU availability
- Install dependencies

**4. Upload Your 3 JSON Files**
- When prompted, click "Choose Files"
- Select: `datalabel.json`, `datalabel1.json`, `datalabel2.json`
- Upload

**5. Run All Cells**
- Runtime → Run all
- Wait 20-30 minutes

**6. Download Model**
- File `resume-ner-final.zip` will auto-download
- Extract and copy to: `ai-service/models/resume-ner-deberta/`

---

## 🎯 Method 2: Zip & Upload (Your Previous Method)

### Step 1: Create Zip File

```bash
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser

# Zip only the data files
zip -r label_studio_data.zip ai-service/training/data/datalabel*.json

# OR zip entire training folder
zip -r training_data.zip ai-service/training/
```

### Step 2: Upload to Google Colab

In Colab, add this cell at the beginning:

```python
# Upload zip file
from google.colab import files
uploaded = files.upload()

# Unzip
!unzip label_studio_data.zip -d ./data/
```

### Step 3: Modify Upload Cell

Change the upload cell to read from unzipped folder:

```python
import os
import json

# Instead of uploading, read from unzipped folder
json_files = [
    './data/datalabel.json',
    './data/datalabel1.json', 
    './data/datalabel2.json'
]

uploaded = {}
for file_path in json_files:
    with open(file_path, 'rb') as f:
        uploaded[os.path.basename(file_path)] = f.read()

print(f"✅ Loaded {len(uploaded)} files")
```

### Step 4: Continue Normally

Run all remaining cells as usual.

---

## ⚡ Quick Commands

### Zip Your Data Files

```bash
# Navigate to project
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser"

# Zip only JSON files
zip -r label_data.zip \
  ai-service/training/data/datalabel.json \
  ai-service/training/data/datalabel1.json \
  ai-service/training/data/datalabel2.json

# Check zip file
ls -lh label_data.zip
```

### Extract Downloaded Model

```bash
# Extract model
unzip resume-ner-final.zip

# Copy to project
cp -r resume-ner-final/* \
  "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service/models/resume-ner-deberta/"

# Verify
ls -lh ai-service/models/resume-ner-deberta/
```

---

## 📊 Expected Results

| Metric | Value |
|--------|-------|
| Total Resumes | ~1,500-1,800 |
| Training Examples | ~1,350-1,620 |
| Test Examples | ~150-180 |
| Training Time (GPU) | 20-30 min |
| Training Time (CPU) | 4-6 hours ⚠️ |
| Expected F1 Score | 85-95% |
| Model Size | ~500 MB |

---

## ✅ Checklist

Before starting:
- [ ] 3 JSON files ready
- [ ] Google Colab account
- [ ] `Train_DeBERTa_Team_Workflow.ipynb` uploaded to Colab
- [ ] GPU enabled in Colab

During training:
- [ ] GPU is available (check first cell)
- [ ] All 3 files uploaded successfully
- [ ] Merge shows ~1,500-1,800 examples
- [ ] Training loss decreasing
- [ ] No errors in cells

After training:
- [ ] Model downloaded as zip
- [ ] Zip extracted
- [ ] Files copied to `ai-service/models/resume-ner-deberta/`
- [ ] AI service restarted
- [ ] Test resume uploaded and working

---

## 🔧 Troubleshooting

### GPU Not Available
**Solution:** Runtime → Change runtime type → GPU → Save → Restart runtime

### Upload Failed
**Solution:** Use zip method instead - upload zip, then unzip in Colab

### Out of Memory
**Solution:** Reduce batch size to 8 in training args

### Low F1 Score (<70%)
**Solution:** Check annotation quality, add more examples, or retrain

---

## 📞 Need Help?

1. Check cell outputs for error messages
2. Verify GPU is enabled
3. Ensure all 3 JSON files uploaded
4. Review `TEAM_TRAINING_GUIDE.md` for detailed troubleshooting

---

## 🎉 Success!

Once complete, you'll have:
- ✅ Custom DeBERTa v3 model trained on your data
- ✅ Better accuracy than base model
- ✅ Production-ready resume parser
- ✅ Downloadable model for deployment

**Training time: ~30 minutes total** ⚡
