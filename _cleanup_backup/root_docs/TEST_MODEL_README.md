# 🧪 NER Model Performance Testing

Test your trained DeBERTa NER model with real resume examples and get detailed performance metrics.

## 📋 Prerequisites

```bash
pip install -r requirements_test.txt
```

Or install individually:
```bash
pip install transformers==4.44.0 torch colorama
```

## 🚀 Quick Start

### Option 1: Visual Testing (Colorful Output)
```bash
python test_model_performance.py
```

**Features:**
- ✨ Color-coded entity highlighting
- 🎯 Confidence scores for each prediction
- 📊 5 diverse test cases (work experience, education, etc.)
- 🌈 Visual text highlighting

### Option 2: Detailed Accuracy Testing
```bash
python test_model_detailed.py
```

**Features:**
- ✅ Compares predictions vs expected entities
- 📈 Precision, Recall, F1 metrics per test
- ❌ Shows incorrect extractions
- ⚠️ Shows missed entities
- 📊 Overall performance summary

## 📁 Model Location

Both scripts expect the model at:
```
models/resume-ner-deberta/
```

If your model is elsewhere, update the `MODEL_PATH` variable in the scripts.

## 🎨 Understanding the Output

### Color Coding (test_model_performance.py)
- **Cyan**: Person names
- **Green**: Companies
- **Magenta**: Clients
- **Yellow**: Roles
- **Blue**: Locations
- **Red**: Dates
- **Light colors**: Education entities

### Confidence Scores
- 🟢 **Green (>90%)**: High confidence
- 🟡 **Yellow (70-90%)**: Medium confidence
- 🔴 **Red (<70%)**: Low confidence

### Metrics (test_model_detailed.py)
- **Precision**: % of extracted entities that are correct
- **Recall**: % of expected entities that were found
- **F1 Score**: Harmonic mean of precision and recall

## 📊 Your Model Performance

**Training F1 Score**: 66.92%  
**Target F1 Score**: 98.5-99%

The gap suggests the model needs:
1. More diverse training data
2. Better label quality
3. Longer training or hyperparameter tuning

## 🧪 Test Cases Included

### test_model_performance.py
1. Work Experience (single role)
2. Education (multiple degrees)
3. Complex Work History (multiple roles)
4. Multiple Roles with clients
5. Education with distinctions

### test_model_detailed.py
1. Work Experience with clients
2. Education Background (multiple degrees)
3. Multiple Roles (career progression)
4. Consulting Experience

## 🔧 Customizing Tests

Add your own test cases by modifying the scripts:

```python
# In test_model_performance.py
custom_text = """
Your resume text here...
"""
tester.test_resume(custom_text, "My Custom Test")

# In test_model_detailed.py
custom_expected = [
    {'type': 'PERSON_NAME', 'text': 'John Doe'},
    {'type': 'COMPANY', 'text': 'Acme Corp'},
    # ... more expected entities
]
extracted = tester.extract_entities(custom_text)
metrics = tester.display_comparison(custom_text, extracted, custom_expected, "My Test")
```

## 📝 Supported Entity Types

- `PERSON_NAME`: Full names
- `COMPANY`: Organization names
- `CLIENT`: Client/customer names
- `ROLE`: Job titles/positions
- `LOCATION`: Cities, states, countries
- `DATE_START`: Start dates
- `DATE_END`: End dates
- `DEGREE`: Academic degrees
- `FIELD`: Field of study
- `INSTITUTION`: Universities/schools
- `EDU_YEAR_START`: Education start dates
- `EDU_YEAR_END`: Education end dates
- `GRADE`: GPA/grades

## 🐛 Troubleshooting

**Model not found:**
```bash
# Check if model exists
ls -la models/resume-ner-deberta/

# If model is in Google Drive, download it first
```

**Import errors:**
```bash
# Reinstall dependencies
pip install --upgrade transformers torch colorama
```

**CUDA errors:**
```bash
# Model will automatically use CPU if CUDA unavailable
# No action needed
```

## 💡 Next Steps

1. **Run the tests** to see current performance
2. **Analyze the results** - which entity types perform well/poorly?
3. **Improve training data** based on missed entities
4. **Retrain the model** with enhanced data
5. **Re-test** to measure improvement

## 📧 Questions?

Review the test output carefully - it shows exactly what the model extracts vs what's expected!
