# 🚀 Colab Training Workflow - No Data Loss

## 📦 Step 1: Upload Training Package

Upload `Lakshya-Colab-Training.zip` to your Colab notebook:

```python
from google.colab import files
print("\n📤 Upload Lakshya-Colab-Training.zip...")
uploaded = files.upload()
```

## 📂 Step 2: Extract Files

```python
!unzip -q "Lakshya-Colab-Training.zip"
!ls -lh
```

## ✅ Step 3: Verify GPU

```python
import torch
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
else:
    print("❌ Enable GPU: Runtime → Change runtime type → GPU")
```

## 💾 Step 4: Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')

import os
os.makedirs("/content/drive/MyDrive/file1/Resume-NER-Models", exist_ok=True)
print("✅ Google Drive mounted!")
```

## 🎯 Step 5: Start Training

```python
print("\n🚀 Starting training...")
!python colab_train.py
```

## 📊 Training Details

**Dataset:**
- Total examples: 11,949
- Train: 10,754 (90%)
- Test: 1,195 (10%)

**Labels (13 entity types):**
- COMPANY: 5,724
- ROLE: 5,875
- LOCATION: 7,935
- DATE_START: 4,635
- DATE_END: 5,457
- INSTITUTION: 3,838
- DEGREE: 3,724
- FIELD: 3,480
- EDU_YEAR_END: 3,618
- CLIENT: 3,615
- GRADE: 3,417
- EDU_YEAR_START: 1,181
- PERSON_NAME: 567

## 💾 Step 6: Save Model to Google Drive

After training completes, the model will automatically save to:
`/content/drive/MyDrive/file1/Resume-NER-Models/resume-ner-deberta_{timestamp}`

The script includes automatic timestamping and Google Drive backup!

## ✅ Expected Output

```
Training completed successfully!
Final F1 Score: 0.98XX
Model saved to: /content/drive/MyDrive/file1/Resume-NER-Models/resume-ner-deberta_YYYYMMDD_HHMMSS
✅ Saved to: MyDrive/file1/Resume-NER-Models/resume-ner-deberta_YYYYMMDD_HHMMSS
```

## 📥 Files Location

Your trained model will be in Google Drive at:
`MyDrive/file1/Resume-NER-Models/resume-ner-deberta_{timestamp}/`

Containing:
- model.safetensors (701 MB)
- config.json
- tokenizer files
- label_mappings.json

---

## 🎉 Complete Workflow Summary

1. ✅ Merged label1.json + label2.json + label3.json → 11,949 examples
2. ✅ Created train.json (10,754) + test.json (1,195)
3. ✅ Packaged into Lakshya-Colab-Training.zip
4. 📤 Upload to Colab
5. 🚀 Train on GPU
6. 💾 Auto-save to Google Drive with timestamp
7. 📥 Download from Google Drive anytime

**No data loss - all 11,949 examples preserved!**
