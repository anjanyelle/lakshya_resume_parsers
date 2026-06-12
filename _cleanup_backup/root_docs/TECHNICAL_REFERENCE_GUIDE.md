# Technical Reference Guide - Lakshya LLM Resume Parser

## 🚀 Quick Start

### Installation
```bash
cd ai-service
pip install -r requirements.txt
python3 main.py  # Start AI service
```

### Basic Usage
```python
from training.predict import ResumeNERPredictor

# Initialize predictor
predictor = ResumeNERPredictor()

# Extract entities from resume text
entities = predictor.extract_entities(resume_text)

# Extract specific sections
experience = predictor.predict_experience_section(experience_text)
education = predictor.predict_education_section(education_text)
```

---

## 🏗️ Architecture Components

### 1. Model Loader (`training/model_loader.py`)
```python
from training.model_loader import ModelLoader, load_for_inference

# Load model for inference
model, tokenizer, device = load_for_inference("./models/resume-ner-deberta")

# Custom model loader
loader = ModelLoader(model_path="./models/resume-ner-deberta")
model = loader.load_model()
tokenizer = loader.load_tokenizer()
```

### 2. Training Pipeline (`training/train.py`)
```python
# Train custom model
python3 training/train.py

# With custom data path
python3 training/train.py --data-path ./custom_data.jsonl

# With specific epochs
python3 training/train.py --epochs 10 --learning-rate 3e-5
```

### 3. Prediction Pipeline (`training/predict.py`)
```python
from training.predict import ResumeNERPredictor

predictor = ResumeNERPredictor()

# Full resume parsing
result = predictor.predict(resume_text)

# Section-specific parsing
experience = predictor.predict_experience_section(experience_text)
education = predictor.predict_education_section(education_text)

# Batch processing
results = predictor.predict_batch([resume1, resume2, resume3])
```

---

## 📊 Data Formats

### Training Data (Doccano JSONL)
```json
{"text": "Senior Engineer at Google from Jan 2020 to Present", "labels": [[0, 6, "ROLE"], [10, 16, "COMPANY"], [22, 29, "START_DATE"], [33, 40, "END_DATE"]]}
```

### BIO Format (Converted)
```json
{"tokens": ["Senior", "Engineer", "at", "Google", "from", "Jan", "2020", "to", "Present"], "tags": ["B-ROLE", "I-ROLE", "O", "B-COMPANY", "O", "B-START_DATE", "I-START_DATE", "O", "B-END_DATE"]}
```

### Model Output (Structured)
```json
{
  "company": ["Google"],
  "role": ["Senior Engineer"],
  "start_date": ["Jan 2020"],
  "end_date": ["Present"],
  "confidence": {"overall": 0.91, "company": 0.94, "role": 0.89}
}
```

---

## 🏷️ Label Mapping

### Entity Types
```python
LABELS = [
    'O',  # Outside entity
    'B-PERSON', 'I-PERSON',
    'B-COMPANY', 'I-COMPANY', 
    'B-CLIENT', 'I-CLIENT',
    'B-ROLE', 'I-ROLE',
    'B-LOCATION', 'I-LOCATION',
    'B-START_DATE', 'I-START_DATE',
    'B-END_DATE', 'I-END_DATE',
    'B-EDUCATION', 'I-EDUCATION',
    'B-DEGREE', 'I-DEGREE'
]
```

### Label to ID Mapping
```python
LABEL_TO_ID = {
    'O': 0,
    'B-PERSON': 1, 'I-PERSON': 2,
    'B-COMPANY': 3, 'I-COMPANY': 4,
    'B-CLIENT': 5, 'I-CLIENT': 6,
    'B-ROLE': 7, 'I-ROLE': 8,
    'B-LOCATION': 9, 'I-LOCATION': 10,
    'B-START_DATE': 11, 'I-START_DATE': 12,
    'B-END_DATE': 13, 'I-END_DATE': 14,
    'B-EDUCATION': 15, 'I-EDUCATION': 16,
    'B-DEGREE': 17, 'I-DEGREE': 18
}
```

---

## 🔄 Data Conversion

### Doccano to BIO
```python
from training.convert_doccano_to_training import convert_doccano_to_bio

# Convert Doccano export to training format
convert_doccano_to_training(
    input_file="training/data/dataset.jsonl",
    output_file="training/data/train.json",
    test_split=0.2
)
```

### Custom Entity Mapping
```python
# Map Doccano labels to our entity types
ENTITY_MAPPING = {
    'PERSON_NAME': 'PERSON',
    'COMPANY_NAME': 'COMPANY', 
    'CLIENT_NAME': 'CLIENT',
    'JOB_TITLE': 'ROLE',
    'LOCATION': 'LOCATION',
    'START_DATE': 'START_DATE',
    'END_DATE': 'END_DATE',
    'UNIVERSITY': 'EDUCATION',
    'DEGREE': 'DEGREE'
}
```

---

## 🎯 Training Configuration

### Training Arguments
```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./models/resume-ner-deberta",
    learning_rate=2e-5,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=5,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    report_to="none"  # Disable wandb/tensorboard
)
```

### Model Configuration
```python
from transformers import AutoConfig

config = AutoConfig.from_pretrained(
    "microsoft/deberta-v3-base",
    num_labels=19,
    label2id=LABEL_TO_ID,
    id2label=ID_TO_LABEL,
    hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1
)
```

---

## 📈 Evaluation Metrics

### F1 Score Calculation
```python
from datasets import load_metric

metric = load_metric("seqeval")

def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)
    
    # Remove ignored index (-100)
    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    
    results = metric.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"]
    }
```

### Per-Entity Metrics
```python
# Entity-specific F1 scores
entity_metrics = {
    "COMPANY": {"precision": 0.94, "recall": 0.94, "f1": 0.94},
    "ROLE": {"precision": 0.89, "recall": 0.89, "f1": 0.89},
    "DATES": {"precision": 0.87, "recall": 0.87, "f1": 0.87},
    "EDUCATION": {"precision": 0.92, "recall": 0.92, "f1": 0.92}
}
```

---

## 🔧 API Integration

### FastAPI Endpoints
```python
# Parse text directly
@app.post("/parse-text")
async def parse_text(request: ParseTextRequest):
    result = master_parser.parse_text(request.text, request.candidate_id)
    return ParseResponse(**result)

# Parse file
@app.post("/parse")
async def parse_file(request: ParseRequest):
    result = master_parser.parse_file(request.file_path, request.candidate_id)
    return ParseResponse(**result)
```

### Response Format
```json
{
  "candidate_id": "uuid",
  "status": "success",
  "name": "John Doe",
  "email": "john@example.com",
  "work_experience": [...],
  "work_history": [...],  # Backend compatibility
  "education": [...],
  "skills": [...],
  "confidence": {"overall": 0.91, "fields": {...}},
  "processing_metrics": {"total_ms": 1500}
}
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Model Not Found
```bash
# Solution: Train model first
python3 training/train.py

# Or download pretrained model
wget https://example.com/models/resume-ner-deberta.zip
unzip resume-ner-deberta.zip -d models/
```

#### 2. Low Accuracy
```python
# Solutions:
# - Increase training epochs
# - Add more training data
# - Improve label consistency
# - Check data quality

python3 training/train.py --epochs 10 --learning-rate 1e-5
```

#### 3. Memory Issues
```python
# Reduce batch size
training_args.per_device_train_batch_size = 1
training_args.gradient_accumulation_steps = 16

# Use smaller model
# Replace microsoft/deberta-v3-base with microsoft/deberta-v3-small
```

#### 4. Slow Inference
```python
# Use GPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# Optimize model
model = model.to(device)
model.eval()

# Batch processing
results = predictor.predict_batch(resume_list)
```

---

## 📚 Advanced Usage

### Custom Training Loop
```python
from transformers import Trainer, DataCollatorForTokenClassification

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForTokenClassification(tokenizer),
    compute_metrics=compute_metrics
)

# Train with custom callbacks
trainer.train()
```

### Active Learning
```python
# Identify uncertain predictions
uncertain_samples = find_uncertain_predictions(model, dataset)

# Manual annotation loop
for sample in uncertain_samples:
    annotation = get_human_annotation(sample)
    add_to_training_data(sample, annotation)
    retrain_model()
```

### Model Optimization
```python
# Quantization for faster inference
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)

model = AutoModelForTokenClassification.from_pretrained(
    model_path,
    quantization_config=quantization_config
)
```

---

## 📊 Performance Monitoring

### Logging Setup
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log prediction metrics
logger.info(f"Processed resume in {processing_time}ms")
logger.info(f"Extracted {len(entities)} entities with confidence {confidence:.3f}")
```

### Metrics Collection
```python
# Track performance over time
metrics = {
    "total_processed": 0,
    "avg_processing_time": 0,
    "accuracy_by_entity": {},
    "error_rate": 0
}

# Update metrics
def update_metrics(processing_time, accuracy, entities_count):
    metrics["total_processed"] += 1
    metrics["avg_processing_time"] = (
        (metrics["avg_processing_time"] * (metrics["total_processed"] - 1) + processing_time) 
        / metrics["total_processed"]
    )
```

---

## 🔐 Security & Privacy

### Data Protection
```python
# Remove sensitive information
def sanitize_text(text):
    # Remove SSN patterns
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    # Remove phone numbers
    text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', text)
    return text

# Encrypt stored data
from cryptography.fernet import Fernet

def encrypt_data(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data, key
```

### Access Control
```python
# API key authentication
from fastapi import Depends, HTTPException, status

async def verify_api_key(api_key: str = Header(...)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key
```

---

## 📞 Support & Resources

### Documentation
- **Full Guide**: `README_DEBERTA_NER.md`
- **Quick Start**: `QUICK_START.md`
- **API Docs**: Available at `/docs` endpoint

### Troubleshooting
- **Common Issues**: See Troubleshooting section
- **Performance Tips**: Optimization section
- **Data Quality**: Labeling guidelines

### Contact
- **Technical Issues**: [dev-team@company.com]
- **Business Questions**: [product@company.com]
- **Support**: [support@company.com]

---

## 🎯 Best Practices

### Data Quality
- ✅ Consistent labeling guidelines
- ✅ Multiple annotators for validation
- ✅ Regular quality checks
- ✅ Handle edge cases explicitly

### Model Training
- ✅ Use validation set for early stopping
- ✅ Monitor overfitting
- ✅ Experiment with hyperparameters
- ✅ Save best model checkpoint

### Production Deployment
- ✅ Implement error handling
- ✅ Add monitoring and logging
- ✅ Use batch processing for efficiency
- ✅ Regular model retraining

---

**Happy Resume Parsing! 🚀**
