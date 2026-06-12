# Lakshya LLM Resume Parser - Knowledge Sharing Session

## 🎯 Session Overview

**Project:** Lakshya LLM Resume Parser  
**Duration:** 30-45 minutes  
**Audience:** Technical & Non-technical teams  
**Focus:** From rule-based parsing to custom AI model training

---

## 1. Introduction 📋

### What is the Project?
**Lakshya LLM Resume Parser** is an intelligent system that automatically extracts structured information from resumes using custom-trained AI models.

### Why We Built It?
**Problem Statement:** Recruiters and HR teams spend hours manually reading resumes to extract:
- Work experience details
- Education information  
- Skills and qualifications
- Contact information
- Employment dates

**Business Impact:**
- ⏰ Saves 80% of resume processing time
- 🎯 Improves candidate matching accuracy
- 📊 Enables better talent analytics
- 💰 Reduces operational costs

### Challenges with Earlier Approach
**Rule-based + Basic HuggingFace Models:**
- ❌ Limited entity recognition
- ❌ Poor accuracy on complex resume formats
- ❌ Couldn't distinguish between similar entities
- ❌ Required constant manual rule updates

---

## 2. Previous Approach (Problems) ❌

### Models We Used
- **dslim/bert-base-NER** - General purpose NER
- **jobbert** - Job-specific but limited

### What They Could Extract
```json
{
  "entities": [
    {"text": "John Doe", "label": "PERSON"},
    {"text": "Google", "label": "ORG"}, 
    {"text": "San Francisco", "label": "LOCATION"}
  ]
}
```

### Critical Limitations
**❌ Could Not Identify:**
- **Client vs Company**: "Consulting for ABC Corp (client) at XYZ Inc (company)"
- **Role Details**: "Senior Software Engineer" vs just "Engineer"
- **Date Ranges**: "Jan 2020 - Present" vs just dates
- **Education Specifics**: "Master's in Computer Science" vs generic

**Real-world Impact:**
```
Input: "Senior Data Scientist at Acme Corp (client: Fortune 500)"
Old Output: {"ORG": "Acme Corp", "PERSON": "Fortune 500"} ❌
Expected: {"ROLE": "Senior Data Scientist", "COMPANY": "Acme Corp", "CLIENT": "Fortune 500"} ✅
```

**Accuracy:** Only ~60-70% for work experience extraction

---

## 3. New Approach (Solution) ✅

### Model Choice: microsoft/deberta-v3-base

**Why DeBERTa-v3?**
- 🧠 **Better Context Understanding**: Superior attention mechanisms
- 🎯 **Custom Label Support**: Train for specific resume entities
- 📈 **Higher Accuracy**: State-of-the-art performance
- 🔄 **Transfer Learning**: Leverages pre-trained knowledge
- 🛠️ **HuggingFace Integration**: Easy deployment and fine-tuning

### Key Improvements
- ✅ **Custom Entity Types**: Tailored for resume parsing
- ✅ **Context-Aware**: Understands resume structure
- ✅ **High Precision**: 90%+ accuracy on key entities
- ✅ **Scalable**: Easy to retrain with new data

---

## 4. Labeling Process 🏷️

### Tool: Doccano
**Open-source annotation tool** for creating high-quality training data

### Custom Labels Created
| Label | Purpose | Example |
|-------|---------|---------|
| **PERSON** | Candidate name | "John Doe" |
| **COMPANY** | Employer | "Google Inc" |
| **CLIENT** | Consulting client | "Fortune 500" |
| **ROLE** | Job title | "Senior Engineer" |
| **LOCATION** | Work location | "San Francisco, CA" |
| **START_DATE** | Employment start | "Jan 2020" |
| **END_DATE** | Employment end | "Present" |
| **EDUCATION** | Institution | "Stanford University" |
| **DEGREE** | Qualification | "Master of Science" |

### Labeling Process
1. **Resume Collection**: 100+ diverse resume samples
2. **Guideline Creation**: Clear annotation rules
3. **Team Training**: Ensured consistent labeling
4. **Quality Checks**: Double-annotation for 20% of data
5. **Iterative Refinement**: Updated guidelines based on edge cases

### Example Annotation
```
"Senior Software Engineer at Microsoft from Jan 2020 to Present"
└─ROLE──────────┘    └─COMPANY─┘   └─START─┘   └─END───┘
```

---

## 5. Training Process 🚀

### Data Flow
```
Doccano (JSONL) → BIO Format → HuggingFace Dataset → DeBERTa Training
```

### Step-by-Step Training

#### 1. **Data Preparation**
```python
# Doccano export format
{"text": "Senior Engineer at Google", "labels": [[0, 6, "ROLE"], [10, 16, "COMPANY"]]}

# Convert to BIO format
{"tokens": ["Senior", "Engineer", "at", "Google"], "tags": ["B-ROLE", "I-ROLE", "O", "B-COMPANY"]}
```

#### 2. **Model Setup**
```python
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")
model = AutoModelForTokenClassification.from_pretrained(
    "microsoft/deberta-v3-base",
    num_labels=19,  # 9 entities × 2 (B/I) + O
    label2id=label_mapping,
    id2label=reverse_mapping
)
```

#### 3. **Training Configuration**
```python
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./models/resume-ner-deberta",
    learning_rate=2e-5,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=5,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch"
)
```

#### 4. **Training Execution**
- **Dataset**: 100+ annotated resumes
- **Validation**: 20% holdout set
- **Hardware**: GPU-enabled training
- **Monitoring**: Loss tracking and F1-score evaluation

#### 5. **Model Evaluation**
```python
# Results after 5 epochs
- Overall F1 Score: 0.91
- Entity-specific scores:
  - COMPANY: 0.94
  - ROLE: 0.89  
  - DATES: 0.87
  - EDUCATION: 0.92
```

---

## 6. Model Usage (Inference) 🔍

### Architecture Overview
```
Resume Text → Section Splitter → DeBERTa Model → Entity Extractor → Structured JSON
```

### Inference Pipeline
```python
from transformers import pipeline

# Load trained model
ner_pipeline = pipeline(
    "token-classification",
    model="./models/resume-ner-deberta",
    aggregation_strategy="simple"
)

# Extract entities
def extract_entities(text):
    entities = ner_pipeline(text)
    return structure_entities(entities)
```

### Real-world Example

**Input Resume Text:**
```
John Doe
Senior Data Scientist at Acme Corporation
San Francisco, CA | Jan 2020 - Present
• Led ML team of 5 engineers
• Improved model accuracy by 40%

Education:
Master of Science in Computer Science
Stanford University | 2018-2020
```

**Structured Output:**
```json
{
  "person": "John Doe",
  "role": "Senior Data Scientist", 
  "company": "Acme Corporation",
  "location": "San Francisco, CA",
  "start_date": "Jan 2020",
  "end_date": "Present",
  "education": "Stanford University",
  "degree": "Master of Science in Computer Science",
  "description": "Led ML team of 5 engineers. Improved model accuracy by 40%."
}
```

### Key Features
- 🎯 **Partial Text Support**: Works on sections or full resumes
- 🔄 **Context Awareness**: Understands resume structure
- 📊 **Confidence Scoring**: Quality assessment for each extraction
- 🛡️ **Error Handling**: Graceful fallbacks for edge cases

---

## 7. Improvements Achieved 📈

### Accuracy Comparison
| Metric | Old Approach | New Approach | Improvement |
|--------|--------------|--------------|-------------|
| **Overall Accuracy** | 60-70% | 90%+ | +30% |
| **Company Extraction** | 65% | 94% | +29% |
| **Role Detection** | 55% | 89% | +34% |
| **Date Parsing** | 40% | 87% | +47% |
| **Education Details** | 50% | 92% | +42% |

### Business Impact
- ⚡ **Processing Speed**: 5x faster resume processing
- 🎯 **Matching Accuracy**: Better candidate-job fit
- 💼 **Client Satisfaction**: Higher quality candidate profiles
- 📊 **Analytics**: Richer talent insights

### Real-world Success Stories
```
Case 1: Consulting Firm
- Challenge: Distinguish client vs company names
- Solution: Custom CLIENT label training
- Result: 95% accurate client identification

Case 2: Tech Recruiting
- Challenge: Extract complex role hierarchies  
- Solution: Enhanced ROLE label training
- Result: 90% accurate seniority detection
```

---

## 8. Architecture Overview 🏗️

### System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Resume File   │ →  │  Section Splitter │ →  │  DeBERTa Model  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │ ←  │ Entity Processor │ ←  │ Entity Extractor │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Component Breakdown

#### 1. **Section Splitter**
- Identifies resume sections (Experience, Education, Skills)
- Enables focused extraction per section
- Handles various resume formats

#### 2. **DeBERTa Model** 
- Custom-trained NER model
- 19 label classes (B-I-O format)
- Optimized for resume text

#### 3. **Entity Processor**
- Converts model output to structured format
- Handles entity merging and validation
- Applies business rules

#### 4. **Database Integration**
- Saves structured data to work_history table
- Maintains candidate profiles
- Enables search and analytics

### Data Flow Example
```
1. Upload: resume.pdf
2. Extract: Raw text using OCR/document parser
3. Split: Identify experience section
4. Process: "Senior Engineer at Google from 2020-2023"
5. Extract: {"ROLE": "Senior Engineer", "COMPANY": "Google", "DATES": "2020-2023"}
6. Save: Store in candidate.work_history table
```

---

## 9. Conclusion & Future Work 🎯

### Key Learnings

#### Technical Insights
- 🎯 **Data Quality > Model Complexity**: Clean labeled data is crucial
- 🔄 **Iterative Training**: Continuous improvement with new data
- 🏷️ **Label Design**: Good taxonomy drives accuracy
- 📊 **Evaluation Metrics**: F1-score more informative than accuracy

#### Business Insights
- 💡 **Domain-Specific Models**: Outperform generic models
- 🎯 **User Feedback**: Essential for model improvement
- 📈 **Measurable Impact**: Quantify ROI of AI improvements

### Future Improvements

#### Short-term (3-6 months)
- 📚 **More Training Data**: Expand to 1000+ annotated resumes
- 🌐 **Multi-language Support**: Handle international resumes
- 📱 **Mobile Resumes**: Optimize for different formats

#### Long-term (6-12 months)  
- 🤖 **LLM Integration**: Combine with GPT for complex cases
- 🔍 **Active Learning**: Automatic data labeling suggestions
- 📊 **Explainability**: Show confidence scores and reasoning

#### Technical Enhancements
- ⚡ **Model Optimization**: Faster inference, smaller footprint
- 🔄 **Continuous Training**: Automated model retraining
- 🛡️ **Privacy**: On-premise deployment options

### Success Metrics
- 🎯 **Accuracy**: Maintain 90%+ on key entities
- ⚡ **Speed**: Sub-second processing per resume
- 📈 **Adoption**: 100+ resumes processed daily
- 💼 **Business Impact**: 50% reduction in manual processing

---

## 🎤 Presentation Tips

### For Technical Audience
- Focus on model architecture and training details
- Discuss evaluation metrics and optimization techniques
- Share code examples and implementation challenges

### For Non-technical Audience  
- Emphasize business problems and solutions
- Use real-world examples and success stories
- Focus on impact and ROI rather than technical details

### Interactive Elements
- 📝 **Live Demo**: Show real resume parsing
- 📊 **Before/After**: Compare old vs new approach
- ❓ **Q&A**: Address specific use cases

---

## 📚 Additional Resources

### Code Repository
- **AI Service**: `/ai-service/`
- **Training Scripts**: `/ai-service/training/`
- **Model Files**: `/ai-service/models/`

### Documentation
- **README**: Complete setup instructions
- **API Docs**: Integration guidelines  
- **Training Guide**: Model customization

### Contact
- **Project Lead**: [Your Name]
- **Technical Questions**: [Dev Team]
- **Business Inquiries**: [Product Team]

---

## 🎉 Thank You!

**Questions?**  
**Feedback Welcome!**  
**Let's Build the Future of Resume Parsing Together!** 🚀
