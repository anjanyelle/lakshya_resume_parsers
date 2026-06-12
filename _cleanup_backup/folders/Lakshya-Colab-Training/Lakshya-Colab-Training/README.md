# Lakshya Resume NER - Google Colab Training Package

## 📦 Package Contents

```
Lakshya-Colab-Training/
├── ai-service/
│   ├── training/
│   │   ├── data/
│   │   │   ├── simple_dataset_train.conll  (15,433 sentences)
│   │   │   └── simple_dataset_test.conll   (1,930 sentences)
│   │   └── train_colab_standalone.py
│   └── models/  (output directory)
└── README.md
```

## 🎯 What This Package Does

Trains a **DeBERTa-v3-base** model for Named Entity Recognition (NER) on resume data.

### Labels (29 total):
- **Person**: PERSON_NAME
- **Experience**: COMPANY, CLIENT, ROLE, LOCATION, DATE_START, DATE_END
- **Education**: DEGREE, FIELD, INSTITUTION, EDU_YEAR_START, EDU_YEAR_END, GRADE

## 🚀 How to Use in Google Colab

### Step 1: Upload This ZIP File
```python
from google.colab import files
uploaded = files.upload()  # Select Lakshya-Colab-Training.zip
```

### Step 2: Extract
```python
!unzip -q Lakshya-Colab-Training.zip
%cd Lakshya-Colab-Training/ai-service
```

### Step 3: Install Dependencies
```python
!pip install -q transformers==4.44.0 datasets==2.19.0 accelerate==0.33.0 \
              evaluate==0.4.1 seqeval scikit-learn torch==2.4.0
```

### Step 4: Train
```python
!python training/train_colab_standalone.py
```

### Step 5: Download Model
```python
!zip -r resume-ner-deberta.zip models/resume-ner-deberta
files.download('resume-ner-deberta.zip')
```

## ⏱️ Training Time
- **T4 GPU**: ~60-70 minutes
- **8 epochs**
- **Expected F1 Score**: ~96%

## 📊 Training Configuration
- Model: microsoft/deberta-v3-base
- Batch size: 8
- Learning rate: 3e-5
- Max length: 512 tokens
- FP16: Enabled (on GPU)

## 🎯 Expected Results
```
Precision: ~0.97
Recall:    ~0.96
F1 Score:  ~0.96
```

## 📥 After Training

The trained model will be saved in:
```
models/resume-ner-deberta/
├── config.json
├── model.safetensors
├── tokenizer_config.json
├── vocab.txt
└── label_mappings.json
```

## 🔧 Troubleshooting

### GPU Not Available
```python
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
# If False: Runtime > Change runtime type > T4 GPU
```

### Out of Memory
Reduce batch size in `train_colab_standalone.py`:
```python
per_device_train_batch_size=4  # Change from 8 to 4
```

### File Not Found
Make sure you're in the correct directory:
```python
!pwd  # Should show: /content/Lakshya-Colab-Training/ai-service
!ls training/data/  # Should show .conll files
```

## 📝 Data Format (CoNLL)

```
John	B-PERSON_NAME
Doe	I-PERSON_NAME
works	O
at	O
Google	B-COMPANY

```
(Empty line separates sentences)

## 🎓 Model Architecture

- **Base**: DeBERTa-v3-base (184M parameters)
- **Task**: Token Classification (NER)
- **Output**: 29 labels (BIO tagging)

## 📞 Support

For issues or questions, check the main repository documentation.

---
**Created**: 2026
**Version**: 1.0
