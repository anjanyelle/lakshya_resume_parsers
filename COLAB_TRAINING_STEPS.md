# 🎯 Google Colab Training - Simple Steps

## Your Current Situation ✅

You have **3 Label Studio JSON files** from your team:
```
📁 ai-service/training/data/
   ├── datalabel.json   (2.4 MB) - Team Member 1
   ├── datalabel1.json  (2.5 MB) - Team Member 2
   └── datalabel2.json  (2.3 MB) - Team Member 3
```

**Total: ~1,500-1,800 annotated resumes** 🎉

---

## 🚀 EASIEST METHOD: Direct Upload

### Visual Flow:

```
┌─────────────────┐
│  Your Computer  │
│                 │
│  datalabel.json │
│  datalabel1.json│──────┐
│  datalabel2.json│      │
└─────────────────┘      │
                         │ Upload (30 sec)
                         ▼
┌─────────────────────────────────────┐
│        Google Colab (GPU)           │
│                                     │
│  1. Auto-merge 3 files             │
│  2. Remove duplicates              │
│  3. Train DeBERTa v3 (20-30 min)   │
│  4. Create resume-ner-final.zip    │
└─────────────────────────────────────┘
                         │
                         │ Download
                         ▼
┌─────────────────────────────────────┐
│  Your Computer                      │
│                                     │
│  resume-ner-final.zip (500 MB)     │
│  ↓ Extract                          │
│  ↓ Copy to ai-service/models/      │
│  ✅ Done!                           │
└─────────────────────────────────────┘
```

---

## 📝 Step-by-Step Instructions

### **STEP 1: Open Google Colab** (2 minutes)

1. Go to: **https://colab.research.google.com/**
2. Click: **File → Upload notebook**
3. Select: `Train_DeBERTa_Team_Workflow.ipynb`

**OR** (easier):
- Upload notebook to Google Drive
- Right-click → **Open with → Google Colaboratory**

---

### **STEP 2: Enable GPU** (1 minute) ⚡

**CRITICAL STEP - Don't skip!**

1. Click: **Runtime** (top menu)
2. Click: **Change runtime type**
3. Select: **Hardware accelerator → GPU**
4. Select: **GPU type → T4** (free)
5. Click: **Save**

**Why?** GPU trains in 30 min vs CPU takes 6 hours!

---

### **STEP 3: Run First Cell - Check GPU** (10 seconds)

Click the **▶ Play** button on Cell 1:

```python
import torch
if torch.cuda.is_available():
    print("✅ GPU is available!")
```

**You MUST see:** `✅ GPU is available!`

**If you see:** `⚠️ GPU not available`
→ Go back to Step 2 and enable GPU!

---

### **STEP 4: Install Dependencies** (1 minute)

Click **▶ Play** on Cell 2:

```python
!pip install -q transformers datasets accelerate evaluate seqeval
```

Wait for installation to complete.

---

### **STEP 5: Upload Your 3 JSON Files** (30 seconds)

When you reach the upload cell, you'll see:

```
📤 Upload ALL Label Studio JSON files from your team...
```

**Click the "Choose Files" button**

Then:
1. Navigate to: `ai-service/training/data/`
2. **Hold Ctrl (Windows) or Cmd (Mac)**
3. Click all 3 files:
   - `datalabel.json`
   - `datalabel1.json`
   - `datalabel2.json`
4. Click **Open**

**Upload progress will show** - wait until 100%

---

### **STEP 6: Run All Remaining Cells** (20-30 minutes)

Click: **Runtime → Run all**

**What happens automatically:**

```
⏳ Merging 3 JSON files...
✅ Merged! Total: ~1,500 examples

⏳ Removing duplicates...
✅ Removed X duplicates

⏳ Converting to NER format...
✅ Converted!

⏳ Creating train/test split...
✅ Train: 1,350 | Test: 150

⏳ Loading DeBERTa v3 model...
✅ Model loaded on GPU

⏳ Training... (20-30 minutes)
Epoch 1/5: Loss 0.234
Epoch 2/5: Loss 0.156
Epoch 3/5: Loss 0.098
Epoch 4/5: Loss 0.067
Epoch 5/5: Loss 0.045
✅ Training complete!

📊 Test Results:
   Precision: 89.5%
   Recall: 87.3%
   F1 Score: 88.4%

💾 Saving model...
✅ Model saved!

📦 Creating zip file...
✅ resume-ner-final.zip created!

📥 Downloading...
```

---

### **STEP 7: Download Completes Automatically**

The file `resume-ner-final.zip` (~500 MB) will download to your computer.

**Location:** Usually in your Downloads folder

---

### **STEP 8: Extract Model** (1 minute)

On your computer:

**Mac/Linux:**
```bash
cd ~/Downloads
unzip resume-ner-final.zip
```

**Windows:**
- Right-click `resume-ner-final.zip`
- Click "Extract All..."

You'll get folder: `resume-ner-final/`

---

### **STEP 9: Copy to Your Project** (1 minute)

**Mac/Linux:**
```bash
cp -r ~/Downloads/resume-ner-final/* \
  "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service/models/resume-ner-deberta/"
```

**Windows:**
- Copy all files from `resume-ner-final/`
- Paste into: `ai-service\models\resume-ner-deberta\`

---

### **STEP 10: Restart AI Service** (30 seconds)

```bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service"

# Stop current service (Ctrl+C if running)

# Start with new model
python -m uvicorn main:app --reload --port 8000
```

**Look for:** `✅ Model loaded successfully`

---

### **STEP 11: Test Your Model** (1 minute)

1. Open: http://localhost:5174/upload
2. Upload a test resume
3. Check extracted information

**You should see better accuracy!** 🎉

---

## ⏱️ Total Time Breakdown

| Step | Time |
|------|------|
| 1. Open Colab | 2 min |
| 2. Enable GPU | 1 min |
| 3. Check GPU | 10 sec |
| 4. Install deps | 1 min |
| 5. Upload files | 30 sec |
| 6. **Training** | **20-30 min** |
| 7. Download | 2 min |
| 8. Extract | 1 min |
| 9. Copy files | 1 min |
| 10. Restart service | 30 sec |
| 11. Test | 1 min |
| **TOTAL** | **~30-35 min** |

---

## 🎯 Alternative: Zip Method

If you prefer your previous approach:

### Create Zip File:

```bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser"

# Zip the 3 JSON files
zip -r label_data.zip \
  ai-service/training/data/datalabel.json \
  ai-service/training/data/datalabel1.json \
  ai-service/training/data/datalabel2.json

# Check size
ls -lh label_data.zip
```

### In Colab - Add Unzip Cell:

After cell 2 (install dependencies), add a new cell:

```python
# Upload zip file
from google.colab import files
print("📤 Upload your label_data.zip file...")
uploaded_zip = files.upload()

# Unzip
!unzip label_data.zip -d ./

# List files
!ls -lh ai-service/training/data/
```

Then modify the upload cell to read from unzipped location instead of uploading again.

---

## ✅ Success Indicators

### During Training:
- ✅ GPU shows as available
- ✅ Loss decreases each epoch
- ✅ F1 score increases
- ✅ No error messages

### After Training:
- ✅ F1 Score > 85%
- ✅ Model zip downloaded
- ✅ Files extracted successfully
- ✅ AI service starts without errors
- ✅ Test resume extracts correctly

---

## ⚠️ Common Issues

### Issue: "GPU not available"
**Fix:** Runtime → Change runtime type → GPU → Save → Restart runtime

### Issue: "Upload failed"
**Fix:** Use zip method - zip files first, upload zip, unzip in Colab

### Issue: "CUDA out of memory"
**Fix:** In training args, change `per_device_train_batch_size=8`

### Issue: "Model not loading"
**Fix:** Verify all files copied correctly to `ai-service/models/resume-ner-deberta/`

---

## 📊 What You'll Get

From your **~1,500-1,800 resumes**:

- ✅ **Custom DeBERTa v3 model** trained on your team's data
- ✅ **85-95% accuracy** on resume parsing
- ✅ **Better extraction** of companies, roles, dates, education
- ✅ **Production-ready** model
- ✅ **Reusable workflow** for future updates

---

## 🎉 You're Ready!

**Your approach is 100% correct!** Just follow these steps and you'll have a trained model in ~30 minutes.

**Questions?** Check `TEAM_TRAINING_GUIDE.md` for detailed explanations.

**Good luck!** 🚀
