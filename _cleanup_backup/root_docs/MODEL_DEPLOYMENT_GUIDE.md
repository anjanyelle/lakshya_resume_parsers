# Model Deployment Guide

## Training Complete ✅

**Final Model Performance:**
- F1 Score: **96.33%**
- Precision: **96.94%**
- Recall: **95.73%**
- Training Time: 69 minutes on T4 GPU
- Dataset: 17,363 samples

---

## Download Model from Google Drive

### Option 1: Download All Files (Recommended)

1. Go to Google Drive: `/MyDrive/Resume-NER-Models/resume-ner-deberta`
2. Select the entire `resume-ner-deberta` folder
3. Right-click → Download
4. Google Drive will create a ZIP file

### Option 2: Download Required Files Only

Download these 8 files:
- `config.json`
- `model.safetensors`
- `tokenizer.json`
- `tokenizer_config.json`
- `spm.model`
- `special_tokens_map.json`
- `label_mappings.json`
- `added_tokens.json`

**Skip these (not needed for production):**
- `checkpoint-9650/` folder
- `checkpoint-15440/` folder
- `training_args.bin`

---

## Install Model Locally

### Step 1: Extract ZIP

```bash
cd ~/Downloads
unzip resume-ner-deberta.zip
```

### Step 2: Move to AI Service

```bash
# Navigate to project
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser"

# Remove old model (if exists)
rm -rf ai-service/models/resume-ner-deberta

# Copy new model
cp -r ~/Downloads/resume-ner-deberta ai-service/models/
```

### Step 3: Verify Installation

```bash
ls -lh ai-service/models/resume-ner-deberta/
```

**Expected output:**
```
config.json
model.safetensors
tokenizer.json
tokenizer_config.json
spm.model
special_tokens_map.json
label_mappings.json
added_tokens.json
```

---

## Test the Model

### Start AI Service

```bash
cd ai-service
python -m uvicorn main:app --reload --port 8000
```

### Test with Sample Resume

```bash
curl -X POST http://localhost:8000/parse-sections \
  -H "Content-Type: application/json" \
  -d '{
    "experience_text": "John Smith worked at Google as Senior Data Engineer in Hyderabad from Jan 2021 to Mar 2023. Client was Microsoft.",
    "education_text": "B.Tech in Computer Science from JNTU Hyderabad, 2015-2019, Grade 8.2"
  }'
```

**Expected response:**
```json
{
  "work_experience": [
    {
      "person_name": "John Smith",
      "company": "Google",
      "role": "Senior Data Engineer",
      "location": "Hyderabad",
      "date_start": "Jan 2021",
      "date_end": "Mar 2023",
      "client": "Microsoft"
    }
  ],
  "education": [
    {
      "degree": "B.Tech",
      "field": "Computer Science",
      "institution": "JNTU Hyderabad",
      "edu_year_start": "2015",
      "edu_year_end": "2019",
      "grade": "8.2"
    }
  ]
}
```

---

## Full Application Testing

### 1. Start Backend

```bash
cd backend
source venv/bin/activate  # or your virtual environment
python -m uvicorn app.main:app --reload --port 3001
```

### 2. Start AI Service

```bash
cd ai-service
python -m uvicorn main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm run dev
```

### 4. Test Resume Upload

1. Open browser: http://localhost:5173
2. Login with admin credentials
3. Upload a test resume (PDF/DOCX)
4. Verify parsed data displays correctly

---

## Model Files Explained

| File | Purpose | Required |
|------|---------|----------|
| `config.json` | Model architecture config | ✅ Yes |
| `model.safetensors` | Trained model weights | ✅ Yes |
| `tokenizer.json` | Fast tokenizer | ✅ Yes |
| `tokenizer_config.json` | Tokenizer settings | ✅ Yes |
| `spm.model` | SentencePiece model | ✅ Yes |
| `special_tokens_map.json` | Special tokens | ✅ Yes |
| `label_mappings.json` | 29 NER labels | ✅ Yes |
| `added_tokens.json` | Additional tokens | ✅ Yes |
| `checkpoint-*/` | Training checkpoints | ❌ No (only for retraining) |
| `training_args.bin` | Training config | ❌ No (only for retraining) |

---

## Troubleshooting

### Model Not Loading

```python
# Check if files exist
import os
model_path = "ai-service/models/resume-ner-deberta"
print(os.listdir(model_path))
```

### Low Accuracy on Real Resumes

- Model trained on IT/tech resumes
- May need fine-tuning for other domains
- Check if resume format matches training data

### Slow Inference

- **CPU**: 5-8 seconds per resume (normal)
- **GPU**: 1-2 seconds per resume
- Consider batch processing for multiple resumes

---

## Production Deployment Checklist

- [ ] Model files copied to production server
- [ ] AI service running on port 8000
- [ ] Backend connected to AI service
- [ ] Test with 10+ real resumes
- [ ] Monitor accuracy and errors
- [ ] Set up logging for failed parses
- [ ] Configure GPU if available
- [ ] Set up model versioning

---

## Model Retraining (Future)

To retrain with new data:

1. Add new labeled data to `ai-service/training/data/`
2. Update `train_colab_standalone.py` if needed
3. Run training on Google Colab
4. Download new model
5. Replace old model files
6. Test thoroughly before production

---

## Support

For issues or questions:
1. Check training logs in Colab
2. Verify all 8 required files present
3. Test with simple examples first
4. Check AI service logs for errors
