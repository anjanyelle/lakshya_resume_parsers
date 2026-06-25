# NER Post-Processor Integration Guide

## Overview

This guide shows how to integrate the production-grade NER post-processing pipeline into your existing Lakshya Resume Parser codebase.

---

## Quick Integration (Recommended)

### Step 1: Update `master_parser.py`

Add the integrated NER pipeline to your master parser:

```python
# In ai-service/parsers/master_parser.py

from parsers.integrated_ner_pipeline import IntegratedNERPipeline

class MasterParser:
    def __init__(self):
        # ... existing initialization ...
        
        # Add integrated NER pipeline
        try:
            self.integrated_ner = IntegratedNERPipeline()
            self.logger.info("✅ Integrated NER Pipeline initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Integrated NER: {e}")
            self.integrated_ner = None
    
    def parse_file(self, file_path: str, llm_provider: str = None) -> Dict[str, Any]:
        """Parse resume file with integrated NER pipeline."""
        
        # ... existing text extraction code ...
        
        # Use integrated NER pipeline for entity extraction
        if self.integrated_ner and self.integrated_ner.is_available():
            self.logger.info("Using Integrated NER Pipeline for entity extraction")
            
            ner_entities = self.integrated_ner.extract_entities(text)
            
            # Extract work experience and education separately
            work_exp = self.integrated_ner.extract_work_experience(text)
            education = self.integrated_ner.extract_education(text)
            
            # Merge with existing parsing results
            result = {
                **ner_entities,
                'work_experience': self._build_work_experience(work_exp),
                'education': self._build_education(education),
                # ... rest of your parsing logic ...
            }
        else:
            # Fallback to existing NER logic
            self.logger.warning("Integrated NER not available, using fallback")
            result = self._parse_with_existing_logic(text)
        
        return result
    
    def _build_work_experience(self, work_exp: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build structured work experience from NER entities."""
        experiences = []
        
        # Combine entities into structured work experience entries
        for i, role in enumerate(work_exp.get('roles', [])):
            exp_entry = {
                'job_title': role,
                'company_name': work_exp['companies'][i] if i < len(work_exp['companies']) else None,
                'location': work_exp['locations'][i] if i < len(work_exp['locations']) else None,
                'start_date': work_exp['date_start'][i] if i < len(work_exp['date_start']) else None,
                'end_date': work_exp['date_end'][i] if i < len(work_exp['date_end']) else None,
                'is_current': work_exp['date_end'][i] == 'Present' if i < len(work_exp['date_end']) else False
            }
            experiences.append(exp_entry)
        
        return experiences
    
    def _build_education(self, education: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build structured education from NER entities."""
        edu_entries = []
        
        for i, degree in enumerate(education.get('degrees', [])):
            edu_entry = {
                'degree': degree,
                'institution': education['institutions'][i] if i < len(education['institutions']) else None,
                'field_of_study': education['fields'][i] if i < len(education['fields']) else None,
                'start_year': education['edu_year_start'][i] if i < len(education['edu_year_start']) else None,
                'end_year': education['edu_year_end'][i] if i < len(education['edu_year_end']) else None,
                'gpa': education['grades'][i] if i < len(education['grades']) else None
            }
            edu_entries.append(edu_entry)
        
        return edu_entries
```

---

## Alternative: Add as Validation Layer

If you want to keep your existing NER logic and add post-processing as a validation layer:

### Update `deberta_ner_parser.py`

```python
# In ai-service/parsers/deberta_ner_parser.py

from parsers.ner_postprocessor import NERPostProcessor

class DeBERTaNerParser:
    def __init__(self, model_path: str = None):
        # ... existing initialization ...
        
        # Add post-processor
        try:
            self.post_processor = NERPostProcessor()
            self.logger.info("✅ NER Post-Processor initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize post-processor: {e}")
            self.post_processor = None
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse text with DeBERTa NER + post-processing."""
        
        # Step 1: Run existing DeBERTa NER
        raw_entities = self._extract_entities_with_model(text)
        
        # Step 2: Convert to standard format for post-processor
        standardized_entities = []
        for entity_type, entity_list in raw_entities.items():
            if entity_type.startswith('_'):
                continue  # Skip metadata
            
            for entity_value in entity_list:
                standardized_entities.append({
                    'entity_group': entity_type.upper(),
                    'word': entity_value if isinstance(entity_value, str) else entity_value.get('text', ''),
                    'score': 1.0 if isinstance(entity_value, str) else entity_value.get('confidence', 1.0)
                })
        
        # Step 3: Apply post-processing
        if self.post_processor:
            validated_entities = self.post_processor.process(
                entities=standardized_entities,
                full_text=text
            )
            return validated_entities
        else:
            # Fallback to raw entities
            return raw_entities
```

---

## Configuration Options

### Custom Confidence Thresholds

Create a configuration file for your thresholds:

```python
# In ai-service/config/ner_config.py

NER_CONFIDENCE_THRESHOLDS = {
    'ROLE': 0.95,           # Stricter for roles
    'COMPANY': 0.88,        # More lenient for companies
    'CLIENT': 0.90,
    'LOCATION': 0.90,
    'DEGREE': 0.92,
    'INSTITUTION': 0.90,
    'FIELD': 0.88,
    'PERSON_NAME': 0.96,
    'DATE_START': 0.85,
    'DATE_END': 0.85,
    'EDU_YEAR_START': 0.85,
    'EDU_YEAR_END': 0.85,
    'GRADE': 0.85
}
```

Then use in your code:

```python
from config.ner_config import NER_CONFIDENCE_THRESHOLDS
from parsers.integrated_ner_pipeline import IntegratedNERPipeline

pipeline = IntegratedNERPipeline(
    confidence_thresholds=NER_CONFIDENCE_THRESHOLDS
)
```

---

## Testing Your Integration

### Test Script

Create a test script to validate the integration:

```python
# test_integration.py

import logging
from parsers.integrated_ner_pipeline import IntegratedNERPipeline

logging.basicConfig(level=logging.INFO)

# Sample resume
sample_resume = """
JOHN DOE
Senior Full Stack Developer
john.doe@email.com | +1-555-123-4567

WORK EXPERIENCE

Senior Full Stack Developer
TechMahindra Pvt Ltd | Hyderabad, Telangana
January 2020 - Present
• Led team of 5 developers
• Developed REST APIs using Node.js
• Worked with business analysts

Software Engineer
Infosys Limited | Bangalore
June 2017 - December 2019
• Implemented microservices
• Performed unit testing and integration test cases

EDUCATION

Bachelor of Technology in Computer Science
JNTU Hyderabad | 2013 - 2017
GPA: 3.8/4.0

SKILLS
React, Node.js, Python, AWS, Docker
"""

# Test pipeline
pipeline = IntegratedNERPipeline()

if pipeline.is_available():
    print("✅ Pipeline is available")
    
    result = pipeline.extract_entities(sample_resume)
    
    print("\n" + "=" * 80)
    print("EXTRACTED ENTITIES")
    print("=" * 80)
    
    print(f"\nCompanies: {result['companies']}")
    print(f"Roles: {result['roles']}")
    print(f"Locations: {result['locations']}")
    print(f"Institutions: {result['institutions']}")
    print(f"Degrees: {result['degrees']}")
    
    print("\n" + "=" * 80)
    print("VALIDATION CHECKS")
    print("=" * 80)
    
    # Check that invalid entities were filtered
    assert 'React' not in result['companies'], "❌ Tech keyword accepted as company"
    assert 'Node.js' not in result['companies'], "❌ Tech keyword accepted as company"
    assert 'unit testing' not in result['roles'], "❌ Task accepted as role"
    assert 'integration test cases' not in result['roles'], "❌ Task accepted as role"
    assert 'business analysts' not in result['roles'], "❌ Plural form accepted as role"
    
    print("✅ All validation checks passed!")
    
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total raw entities: {result['metadata']['total_raw_entities']}")
    print(f"Total validated entities: {result['metadata']['total_validated_entities']}")
    
else:
    print("❌ Pipeline not available (DeBERTa model not loaded)")
```

Run the test:

```bash
cd ai-service
python test_integration.py
```

---

## API Endpoint Integration

### Update FastAPI Endpoint

```python
# In ai-service/main.py

from parsers.integrated_ner_pipeline import IntegratedNERPipeline

# Initialize at startup
ner_pipeline = None

@app.on_event("startup")
async def startup_event():
    global ner_pipeline
    try:
        ner_pipeline = IntegratedNERPipeline()
        logger.info("✅ NER Pipeline initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize NER pipeline: {e}")

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Parse resume with integrated NER pipeline."""
    
    # Extract text from file
    text = await extract_text_from_file(file)
    
    # Use integrated NER pipeline
    if ner_pipeline and ner_pipeline.is_available():
        result = ner_pipeline.extract_entities(text)
        
        return {
            "status": "success",
            "entities": result,
            "metadata": result.get('metadata', {})
        }
    else:
        return {
            "status": "error",
            "message": "NER pipeline not available"
        }

@app.post("/extract-work-experience")
async def extract_work_experience(file: UploadFile = File(...)):
    """Extract work experience only."""
    
    text = await extract_text_from_file(file)
    
    if ner_pipeline and ner_pipeline.is_available():
        work_exp = ner_pipeline.extract_work_experience(text)
        return {"status": "success", "work_experience": work_exp}
    else:
        return {"status": "error", "message": "NER pipeline not available"}

@app.post("/extract-education")
async def extract_education(file: UploadFile = File(...)):
    """Extract education only."""
    
    text = await extract_text_from_file(file)
    
    if ner_pipeline and ner_pipeline.is_available():
        education = ner_pipeline.extract_education(text)
        return {"status": "success", "education": education}
    else:
        return {"status": "error", "message": "NER pipeline not available"}
```

---

## Monitoring & Logging

### Add Logging Configuration

```python
# In ai-service/config/logging_config.py

import logging
from logging.handlers import RotatingFileHandler

def setup_ner_logging():
    """Setup logging for NER pipeline."""
    
    # Create logger
    logger = logging.getLogger('parsers.ner_postprocessor')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        'logs/ner_postprocessor.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

Use in your application:

```python
from config.logging_config import setup_ner_logging

# Setup logging at startup
setup_ner_logging()
```

---

## Performance Optimization

### Batch Processing

For processing multiple resumes:

```python
from parsers.integrated_ner_pipeline import IntegratedNERPipeline

pipeline = IntegratedNERPipeline()

def process_batch(resume_texts: List[str]) -> List[Dict[str, Any]]:
    """Process multiple resumes efficiently."""
    results = []
    
    for text in resume_texts:
        try:
            result = pipeline.extract_entities(text)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process resume: {e}")
            results.append(None)
    
    return results

# Usage
resumes = [resume1, resume2, resume3, ...]
results = process_batch(resumes)
```

### Caching

Cache processed results to avoid re-processing:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def extract_entities_cached(text_hash: str, text: str) -> Dict[str, Any]:
    """Extract entities with caching."""
    return pipeline.extract_entities(text)

def process_with_cache(text: str) -> Dict[str, Any]:
    """Process resume with caching."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return extract_entities_cached(text_hash, text)
```

---

## Troubleshooting

### Issue 1: Pipeline not available

**Error:** `NER pipeline not available (DeBERTa model not loaded)`

**Solution:**
1. Check if DeBERTa model files exist in `ai-service/models/resume-ner-deberta/`
2. Verify model files: `config.json`, `pytorch_model.bin`, `tokenizer.json`
3. Check logs for model loading errors

### Issue 2: Low entity extraction

**Problem:** Very few entities extracted

**Solution:**
1. Lower confidence thresholds
2. Check if text preprocessing is removing too much content
3. Verify section identification is not blocking valid sections

### Issue 3: Too many false positives

**Problem:** Invalid entities being accepted

**Solution:**
1. Increase confidence thresholds
2. Add custom validation rules
3. Review and update blocked sections list

---

## Migration Checklist

- [ ] Install dependencies (`torch`, `transformers`)
- [ ] Copy new files to `ai-service/parsers/`:
  - [ ] `ner_postprocessor.py`
  - [ ] `integrated_ner_pipeline.py`
- [ ] Update `master_parser.py` or `deberta_ner_parser.py`
- [ ] Create configuration file for thresholds
- [ ] Run integration tests
- [ ] Update API endpoints (if applicable)
- [ ] Setup logging
- [ ] Deploy and monitor

---

## Support

For issues or questions:
- Check the [NER_POSTPROCESSING_README.md](ai-service/parsers/NER_POSTPROCESSING_README.md)
- Run tests: `python tests/test_ner_postprocessor.py`
- Enable debug logging to see detailed processing steps

---

## Next Steps

1. **Test with real resumes** - Run the integration test script with your actual resume data
2. **Tune thresholds** - Adjust confidence thresholds based on your validation results
3. **Monitor performance** - Track processing time and accuracy metrics
4. **Iterate** - Add custom validation rules as needed for your specific use case

Good luck with your integration! 🚀
