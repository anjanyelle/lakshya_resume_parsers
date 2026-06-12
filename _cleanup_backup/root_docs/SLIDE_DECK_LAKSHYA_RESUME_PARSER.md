# Lakshya LLM Resume Parser - Slide Deck

---

## Slide 1: Title Slide
**Lakshya LLM Resume Parser**  
From Rule-Based to Custom AI Model Training  
*Knowledge Sharing Session*  
[Your Name] | [Date]

---

## Slide 2: What We Built
### Project Overview
- **Intelligent Resume Parser** using custom-trained AI
- **Automates extraction** of key resume information
- **Saves 80% processing time** for HR teams
- **90%+ accuracy** on critical entities

### Key Features
- Work experience extraction (company, role, dates)
- Education details (institution, degree)
- Contact information and skills
- Client vs company identification

---

## Slide 3: Why We Built It
### The Problem
- **Manual resume processing** takes hours
- **Inconsistent data extraction** across formats
- **Poor candidate matching** due to incomplete data
- **High operational costs** in recruitment

### Business Impact
- ⏰ **Time Savings**: 80% reduction in processing time
- 🎯 **Better Matching**: Improved candidate-job fit
- 📊 **Rich Analytics**: Better talent insights
- 💰 **Cost Reduction**: Lower operational overhead

---

## Slide 4: Previous Approach Problems
### Old Models Used
- dslim/bert-base-NER
- jobbert
- Rule-based parsing

### Critical Limitations
- ❌ **Generic entities only** (PERSON, ORG, LOCATION)
- ❌ **No client vs company distinction**
- ❌ **Poor date extraction** (40% accuracy)
- ❌ **Limited role understanding**
- ❌ **60-70% overall accuracy**

### Real Example
```
Input: "Senior Data Scientist at Acme Corp (client: Fortune 500)"
Old: {"ORG": "Acme Corp", "PERSON": "Fortune 500"} ❌
Need: {"ROLE": "Senior Data Scientist", "COMPANY": "Acme Corp", "CLIENT": "Fortune 500"} ✅
```

---

## Slide 5: New Solution - DeBERTa-v3
### Why microsoft/deberta-v3-base?
- 🧠 **Superior context understanding**
- 🎯 **Custom label support**
- 📈 **State-of-the-art accuracy**
- 🔄 **Transfer learning capabilities**
- 🛠️ **Easy deployment**

### Key Improvements
- ✅ **9 custom entity types**
- ✅ **Context-aware extraction**
- ✅ **90%+ accuracy**
- ✅ **Resume-specific training**

---

## Slide 6: Custom Labels Created
### Our Label Set
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

### Labeling Tool: Doccano
- Open-source annotation platform
- Team collaboration features
- Quality control mechanisms

---

## Slide 7: Training Process Overview
### Data Pipeline
```
Doccano (JSONL) → BIO Format → HuggingFace Dataset → DeBERTa Training
```

### Training Steps
1. **Data Collection**: 100+ diverse resumes
2. **Annotation**: Consistent labeling with guidelines
3. **Format Conversion**: Span labels → BIO format
4. **Model Training**: 5 epochs, custom labels
5. **Evaluation**: F1-score metrics
6. **Deployment**: Pipeline integration

### Key Metrics
- **Training Time**: ~2 hours on GPU
- **Model Size**: 400MB (compressed)
- **Inference Speed**: <1 second per resume
- **F1 Score**: 0.91 overall

---

## Slide 8: Technical Architecture
### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Resume File   │ →  │  Section Splitter │ →  │  DeBERTa Model  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │ ←  │ Entity Processor │ ←  │ Entity Extractor │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Flow
1. **Upload**: Resume file processing
2. **Extract**: Text extraction (OCR/docs)
3. **Split**: Section identification
4. **Process**: Entity extraction with DeBERTa
5. **Structure**: Format to JSON
6. **Save**: Database storage

---

## Slide 9: Real-World Example
### Input Resume
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

### Structured Output
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

---

## Slide 10: Results & Improvements
### Accuracy Comparison
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Overall** | 65% | 91% | **+26%** |
| **Company** | 65% | 94% | **+29%** |
| **Role** | 55% | 89% | **+34%** |
| **Dates** | 40% | 87% | **+47%** |
| **Education** | 50% | 92% | **+42%** |

### Business Impact
- ⚡ **5x faster** processing
- 🎯 **Better candidate matching**
- 💼 **Higher client satisfaction**
- 📊 **Richer talent analytics**

---

## Slide 11: Key Learnings
### Technical Insights
- 🎯 **Data Quality > Model Complexity**
- 🔄 **Iterative training** with new data
- 🏷️ **Label design** drives accuracy
- 📊 **F1-score** over accuracy for NER

### Business Insights
- 💡 **Domain-specific models** win
- 🎯 **User feedback** essential
- 📈 **Measure ROI** of AI improvements
- 🛡️ **Privacy matters** for HR data

### Success Factors
- Clean, consistent training data
- Clear business requirements
- Iterative improvement process
- Cross-team collaboration

---

## Slide 12: Future Roadmap
### Short-term (3-6 months)
- 📚 **More training data** (1000+ resumes)
- 🌐 **Multi-language support**
- 📱 **Mobile resume formats**
- 🔍 **Confidence scoring**

### Long-term (6-12 months)
- 🤖 **LLM integration** for complex cases
- 🔄 **Active learning** automation
- 📊 **Explainability** features
- ⚡ **Model optimization**

### Technical Goals
- Maintain 90%+ accuracy
- Sub-second processing
- Continuous improvement
- Privacy-first design

---

## Slide 13: Demo Highlights
### Live Demo Flow
1. **Upload Resume**: PDF/DOCX file
2. **Real-time Processing**: Show extraction
3. **Results Display**: Structured JSON
4. **Database Storage**: Verify persistence
5. **Quality Metrics**: Confidence scores

### Key Features to Showcase
- Partial text processing
- Error handling
- Confidence scoring
- Section-based extraction

---

## Slide 14: Q&A
### Discussion Points
- **Technical**: Model architecture, training details
- **Business**: ROI, use cases, integration
- **Future**: Roadmap, improvements
- **General**: Best practices, lessons learned

### Contact Information
- **Project Lead**: [Your Name]
- **Email**: [your.email@company.com]
- **Repository**: [GitHub link]
- **Documentation**: [Docs link]

---

## Slide 15: Thank You
### Key Takeaways
- ✅ **Custom training** beats generic models
- ✅ **Quality data** is the foundation
- ✅ **Iterative improvement** drives success
- ✅ **Business impact** validates effort

### Next Steps
- 📧 **Feedback collection**
- 🔄 **Model improvements**
- 📊 **Performance monitoring**
- 🚀 **Feature expansion**

## Thank You! 🎉
**Questions?**  
**Let's Build the Future of Resume Parsing Together!**
