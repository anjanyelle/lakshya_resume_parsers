# 🚀 Team Training Guide - DeBERTa v3 Resume NER

## Overview

This guide explains how to combine Label Studio annotations from multiple team members and train a DeBERTa v3 model on Google Colab with GPU acceleration.

---

## 📋 Workflow Summary

```
Team Members → Label Studio → Export JSON → Merge Files → Upload to Colab → Train on GPU → Download Model
```

---

## 👥 Step 1: Team Annotation (Label Studio)

### For Each Team Member:

1. **Access Label Studio**
   - Each employee works on their assigned resumes (400-600 resumes each)
   - Use consistent labels across the team

2. **Annotation Labels**
   - **Work Experience:**
     - `COMPANY` - Company name
     - `ROLE` - Job title/position
     - `DATE_START` - Start date
     - `DATE_END` - End date
     - `LOCATION` - Work location
     - `CLIENT` - Client name (if applicable)
   
   - **Education:**
     - `DEGREE` - Degree name
     - `INSTITUTION` - University/college
     - `FIELD` - Field of study
     - `GRADE` - GPA/percentage
     - `EDU_YEAR_START` - Start year
     - `EDU_YEAR_END` - End year

3. **Export Annotations**
   - After completing annotations, go to: **Export → JSON**
   - Save as: `employee_name_annotations.json` or `project-XX.json`
   - Send the JSON file to the team lead

---

## 📦 Step 2: Collect All JSON Files

### Team Lead Tasks:

1. **Collect Files**
   - Gather all JSON export files from team members
   - Typical files:
     ```
     548_label.json
     project-11-at-2026-04-08-15-38-a8419544.json
     project-12-at-2026-04-08-15-46-22c9eaca.json
     employee1_annotations.json
     employee2_annotations.json
     ...
     ```

2. **Organize Files**
   - Create a folder: `label_studio_exports/`
   - Place all JSON files in this folder
   - Total expected: 2000-3000+ annotated resumes

---

## 🔄 Step 3: Merge Files (Optional - Local)

You can merge files locally before uploading to Colab, or let Colab handle it.

### Option A: Merge Locally

```bash
# Navigate to project directory
cd /path/to/Lakshya-LLM-Resume-Parser

# Run merge script
python merge_label_studio_files.py \
  --input-dir ./label_studio_exports \
  --output merged_annotations.json \
  --stats

# This will:
# - Combine all JSON files
# - Remove duplicates
# - Show statistics
```

### Option B: Upload All Files to Colab

Skip local merging and upload all files directly to Colab (recommended for simplicity).

---

## 🌐 Step 4: Google Colab Setup

### 4.1 Open the Notebook

1. **Upload Notebook to Google Drive**
   - Upload `Train_DeBERTa_Team_Workflow.ipynb` to your Google Drive

2. **Open in Colab**
   - Right-click → Open with → Google Colaboratory

### 4.2 Enable GPU

**CRITICAL: You MUST enable GPU for fast training!**

1. Click: **Runtime → Change runtime type**
2. Select: **Hardware accelerator → GPU**
3. Choose: **T4 GPU** (free tier) or **A100** (paid)
4. Click: **Save**

### 4.3 Verify GPU

Run the first cell to check:

```python
import torch
if torch.cuda.is_available():
    print("✅ GPU is available!")
else:
    print("⚠️ GPU not available - go enable it!")
```

---

## 📤 Step 5: Upload JSON Files to Colab

### Method 1: Upload Multiple Files (Recommended)

1. Run the upload cell in the notebook
2. Click **Choose Files**
3. **Select ALL JSON files** from your team (Ctrl+A or Cmd+A)
4. Click **Open**
5. Wait for upload to complete

### Method 2: Upload Merged File

If you merged locally:
1. Upload only `merged_annotations.json`
2. Faster upload, same result

---

## 🚀 Step 6: Train the Model

### 6.1 Run All Cells

Click: **Runtime → Run all**

The notebook will:
1. ✅ Check GPU availability
2. ✅ Install dependencies
3. ✅ Merge all JSON files
4. ✅ Remove duplicates
5. ✅ Analyze dataset quality
6. ✅ Convert to NER format
7. ✅ Create train/test split
8. ✅ Load DeBERTa v3 model
9. ✅ Train on GPU (20-30 minutes)
10. ✅ Evaluate performance
11. ✅ Save model

### 6.2 Monitor Training

Watch the training progress:
- **Loss** should decrease
- **F1 Score** should increase
- **GPU utilization** should be high

Expected metrics:
- **Precision:** 85-95%
- **Recall:** 85-95%
- **F1 Score:** 85-95%

---

## 📥 Step 7: Download Trained Model

### 7.1 Download from Colab

The last cell will:
1. Create a zip file: `resume-ner-final.zip`
2. Automatically download it to your computer

### 7.2 Extract Model

```bash
# Extract the zip file
unzip resume-ner-final.zip

# You'll get:
resume-ner-final/
├── config.json
├── model.safetensors
├── tokenizer_config.json
├── vocab.txt
├── label_mappings.json
└── training_metadata.json
```

---

## 🔧 Step 8: Deploy Model to Your System

### 8.1 Copy Model Files

```bash
# Copy to your AI service
cp -r resume-ner-final/* \
  /path/to/Lakshya-LLM-Resume-Parser/ai-service/models/resume-ner-deberta/
```

### 8.2 Update Configuration

Edit: `ai-service/config/deberta_config.py`

```python
DEBERTA_CONFIG = {
    "model_path": "models/resume-ner-deberta",  # Your new model
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "max_length": 512,
    "batch_size": 8
}
```

### 8.3 Restart AI Service

```bash
# Stop current service
# Ctrl+C or kill the process

# Start with new model
cd ai-service
python -m uvicorn main:app --reload --port 8000
```

---

## 🧪 Step 9: Test the Model

### 9.1 Upload Test Resume

1. Go to: `http://localhost:5174/upload`
2. Upload a test resume
3. Check extracted information

### 9.2 Verify Extraction

The model should now extract:
- ✅ All work experiences (company, role, dates, location)
- ✅ Education details
- ✅ Better accuracy than before

---

## 📊 Expected Results

### Dataset Size

| Team Members | Resumes Each | Total Resumes |
|--------------|--------------|---------------|
| 5            | 500          | 2,500         |
| 10           | 400          | 4,000         |
| 15           | 600          | 9,000         |

### Training Time (GPU)

| Dataset Size | Training Time | GPU Type |
|--------------|---------------|----------|
| 2,000        | 15-20 min     | T4       |
| 5,000        | 25-35 min     | T4       |
| 10,000       | 45-60 min     | T4       |

### Model Performance

| Metric    | Expected Range |
|-----------|----------------|
| Precision | 85-95%         |
| Recall    | 85-95%         |
| F1 Score  | 85-95%         |

---

## ⚠️ Common Issues & Solutions

### Issue 1: GPU Not Available

**Problem:** Training is very slow (4-6 hours)

**Solution:**
1. Runtime → Change runtime type → GPU
2. Restart runtime
3. Re-run all cells

### Issue 2: Out of Memory

**Problem:** "CUDA out of memory" error

**Solution:**
1. Reduce batch size in training args:
   ```python
   per_device_train_batch_size=8  # Instead of 16
   ```
2. Restart runtime
3. Re-run

### Issue 3: Duplicate Annotations

**Problem:** Same resume annotated by multiple people

**Solution:**
- The notebook automatically removes duplicates
- Check merge statistics to see how many were removed

### Issue 4: Inconsistent Labels

**Problem:** Different team members used different label names

**Solution:**
- Standardize labels before export
- Or manually edit JSON files to fix label names

### Issue 5: Low F1 Score (<70%)

**Possible Causes:**
- Inconsistent annotations
- Too few examples
- Poor quality annotations

**Solution:**
1. Review annotation quality
2. Add more examples
3. Retrain with corrected data

---

## 🔄 Retraining Workflow

When you get new annotations:

1. **Collect new JSON files**
2. **Merge with existing data** (optional)
3. **Upload to Colab**
4. **Train new model**
5. **Compare performance** with old model
6. **Deploy if better**

---

## 📝 Best Practices

### For Team Members:

1. ✅ **Be consistent** with label usage
2. ✅ **Annotate completely** - don't skip entities
3. ✅ **Double-check** dates and locations
4. ✅ **Use exact text** from resume
5. ✅ **Export regularly** to avoid data loss

### For Team Lead:

1. ✅ **Review samples** from each team member
2. ✅ **Check label consistency** across team
3. ✅ **Backup JSON files** before merging
4. ✅ **Track model versions** and performance
5. ✅ **Document improvements** over time

---

## 📞 Support

### Need Help?

1. **Check notebook output** for error messages
2. **Review this guide** for solutions
3. **Check Label Studio docs** for annotation issues
4. **Contact team lead** for coordination

### Useful Links

- Label Studio: https://labelstud.io/guide/
- DeBERTa v3: https://huggingface.co/microsoft/deberta-v3-base
- Google Colab: https://colab.research.google.com/
- Transformers Docs: https://huggingface.co/docs/transformers/

---

## ✅ Checklist

Before starting training:

- [ ] All team members completed annotations
- [ ] All JSON files collected
- [ ] Files organized in one folder
- [ ] Google Colab notebook uploaded
- [ ] GPU enabled in Colab
- [ ] Backup of all JSON files created

During training:

- [ ] All files uploaded successfully
- [ ] Merge statistics look correct
- [ ] No duplicate removal errors
- [ ] GPU is being used
- [ ] Training loss decreasing
- [ ] F1 score improving

After training:

- [ ] Model downloaded successfully
- [ ] Model files extracted
- [ ] Model copied to correct directory
- [ ] Configuration updated
- [ ] Service restarted
- [ ] Test resume uploaded
- [ ] Extraction working correctly

---

## 🎉 Success!

Once completed, you'll have:
- ✅ A custom DeBERTa v3 model trained on your team's data
- ✅ Better accuracy than the base model
- ✅ Production-ready resume parser
- ✅ Reusable workflow for future updates

**Congratulations on building your AI-powered resume parser!** 🚀
