# NER Post-Processor Testing Guide

## Quick Start

### 1. Start the AI Service

```bash
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/lakshya_resume_parsers/ai-service
source venv/bin/activate
python main.py
```

The service should start on `http://localhost:8000`

### 2. Test the New Endpoint

#### Option A: Using the Test Script

```bash
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/lakshya_resume_parsers
chmod +x test_ner_endpoint.sh
./test_ner_endpoint.sh
```

#### Option B: Using curl directly

```bash
curl -X POST 'http://localhost:8000/test-ner-postprocessor' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "model": "own-model",
    "experience_text": "Software Engineer\n\nTata Consultancy Services\nJuly 2023 – Present\n\nClient: Banking & Financial Services\n\nRoles & Responsibilities:\n\nDeveloped enterprise-level web applications using React.js, TypeScript, and Redux Toolkit.",
    "education_text": "Bachelor of Technology (B.Tech)\n\nComputer Science and Engineering\n\nJawaharlal Nehru Technological University Hyderabad\n\n2018 – 2022"
  }' | jq '.'
```

#### Option C: Using Python

```python
import requests
import json

url = "http://localhost:8000/test-ner-postprocessor"

data = {
    "model": "own-model",
    "experience_text": """
Software Engineer

Tata Consultancy Services
July 2023 – Present

Client: Banking & Financial Services

Roles & Responsibilities:

Developed enterprise-level web applications using React.js, TypeScript, and Redux Toolkit.
Designed reusable UI components and integrated RESTful APIs.
""",
    "education_text": """
Bachelor of Technology (B.Tech)

Computer Science and Engineering

Jawaharlal Nehru Technological University Hyderabad

2018 – 2022
"""
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

---

## Expected Response Format

```json
{
  "status": "success",
  "model_used": "own-model",
  "processing_time_ms": 234.56,
  "raw_entities": {
    "raw_predictions": [
      {
        "entity_group": "ROLE",
        "word": "Software Engineer",
        "score": 0.98
      },
      {
        "entity_group": "COMPANY",
        "word": "Tata Consultancy Services",
        "score": 0.96
      },
      {
        "entity_group": "ROLE",
        "word": "business analysts",
        "score": 0.89
      },
      {
        "entity_group": "COMPANY",
        "word": "React",
        "score": 0.85
      }
    ]
  },
  "validated_entities": {
    "companies": ["Tata Consultancy Services", "Infosys"],
    "roles": ["Software Engineer", "Associate Software Engineer"],
    "clients": ["Banking & Financial Services", "Retail & E-Commerce"],
    "locations": [],
    "degrees": ["Bachelor of Technology (B.Tech)"],
    "institutions": ["Jawaharlal Nehru Technological University Hyderabad"],
    "fields": ["Computer Science and Engineering"],
    "date_start": ["July 2023", "May 2022"],
    "date_end": ["Present", "June 2023"],
    "edu_year_start": ["2018"],
    "edu_year_end": ["2022"],
    "grades": [],
    "person_names": []
  },
  "statistics": {
    "total_raw_entities": 45,
    "total_validated_entities": 12,
    "filtering_rate": 73.3,
    "preprocessing_enabled": true,
    "model_available": true
  },
  "work_experience": [
    {
      "job_title": "Software Engineer",
      "company_name": "Tata Consultancy Services",
      "client": "Banking & Financial Services",
      "location": null,
      "start_date": "July 2023",
      "end_date": "Present",
      "is_current": true
    },
    {
      "job_title": "Associate Software Engineer",
      "company_name": "Infosys",
      "client": "Retail & E-Commerce",
      "location": null,
      "start_date": "May 2022",
      "end_date": "June 2023",
      "is_current": false
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Technology (B.Tech)",
      "institution": "Jawaharlal Nehru Technological University Hyderabad",
      "field_of_study": "Computer Science and Engineering",
      "start_year": "2018",
      "end_year": "2022",
      "gpa": null
    }
  ]
}
```

---

## What to Look For

### ✅ Validation Success Indicators

1. **Invalid Roles Filtered:**
   - ❌ "business analysts" (plural form) should be REJECTED
   - ❌ "integration test cases" (task) should be REJECTED
   - ❌ "Sprint Planning" (activity) should be REJECTED
   - ✅ "Software Engineer" should be ACCEPTED
   - ✅ "Associate Software Engineer" should be ACCEPTED

2. **Tech Keywords Filtered from Companies:**
   - ❌ "React" should be REJECTED as company
   - ❌ "TypeScript" should be REJECTED as company
   - ❌ "Redux Toolkit" should be REJECTED as company
   - ❌ "Material UI" should be REJECTED as company
   - ✅ "Tata Consultancy Services" should be ACCEPTED
   - ✅ "Infosys" should be ACCEPTED

3. **Clients Extracted:**
   - ✅ "Banking & Financial Services" should be extracted as CLIENT
   - ✅ "Retail & E-Commerce" should be extracted as CLIENT

4. **Education Validated:**
   - ✅ "Bachelor of Technology (B.Tech)" should be extracted as DEGREE
   - ✅ "Jawaharlal Nehru Technological University Hyderabad" should be extracted as INSTITUTION
   - ✅ "Computer Science and Engineering" should be extracted as FIELD
   - ❌ "React.js" (from project description) should NOT be extracted as education

5. **Dates Normalized:**
   - "July 2023" should remain as "July 2023"
   - "Present" should remain as "Present"
   - "2018 – 2022" should be split into start_year and end_year

---

## Common Issues & Debugging

### Issue 1: DeBERTa Model Not Available

**Error:**
```json
{
  "detail": "NER pipeline initialization failed: DeBERTa model not loaded"
}
```

**Solution:**
1. Check if model files exist:
```bash
ls -la ai-service/models/resume-ner-deberta/
```

2. Required files:
   - `config.json`
   - `pytorch_model.bin` or `model.safetensors`
   - `tokenizer.json`
   - `tokenizer_config.json`

3. If missing, download or train the model first

### Issue 2: Too Many Entities Filtered

**Problem:** `filtering_rate` is > 90%

**Possible Causes:**
- Confidence thresholds too high
- Text preprocessing removing too much content
- Section identification blocking valid sections

**Solution:**
1. Check raw_predictions to see what was extracted
2. Lower confidence thresholds in the code
3. Disable preprocessing temporarily to test

### Issue 3: Invalid Entities Accepted

**Problem:** Tech keywords appearing in companies list

**Solution:**
1. Check if entity is in `TECH_KEYWORDS_NOT_COMPANIES` list
2. Add missing keywords to the list in `ner_postprocessor.py`
3. Increase confidence threshold for COMPANY entities

---

## Comparing with Existing Endpoint

### Old Endpoint: `/parse-sections`

```bash
curl -X POST 'http://localhost:8000/parse-sections' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "experience_text": "...",
    "education_text": "..."
  }'
```

### New Endpoint: `/test-ner-postprocessor`

```bash
curl -X POST 'http://localhost:8000/test-ner-postprocessor' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "model": "own-model",
    "experience_text": "...",
    "education_text": "..."
  }'
```

### Key Differences

| Feature | `/parse-sections` | `/test-ner-postprocessor` |
|---------|-------------------|---------------------------|
| **Post-Processing** | Basic filtering | 13-phase production pipeline |
| **Raw Predictions** | Not returned | Included for comparison |
| **Statistics** | Limited | Detailed filtering stats |
| **Validation** | Basic | Comprehensive (role/company/education) |
| **Tech Keyword Filtering** | Limited | Extensive list |
| **Entity Merging** | No | Yes (fragments merged) |
| **Deduplication** | No | Yes (smart deduplication) |
| **Normalization** | No | Yes (dates, names, locations) |

---

## Performance Benchmarks

Expected processing times (on typical hardware):

- **Text Pre-processing:** ~10-20ms
- **DeBERTa NER Inference:** ~100-200ms
- **Post-Processing Pipeline:** ~50-100ms
- **Total:** ~160-320ms per resume

For your test data (~2000 chars):
- Expected time: ~200-300ms
- If > 500ms: Check model loading or hardware

---

## Integration with Frontend

### Update Frontend API Call

```typescript
// In frontend/src/services/api.ts

export const testNERPostProcessor = async (
  experienceText: string,
  educationText: string
) => {
  const response = await fetch('http://localhost:8000/test-ner-postprocessor', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'own-model',
      experience_text: experienceText,
      education_text: educationText,
    }),
  });
  
  if (!response.ok) {
    throw new Error('NER post-processor test failed');
  }
  
  return response.json();
};
```

### Display Results in UI

```typescript
// In ModelTestPage.tsx

const handleTest = async () => {
  try {
    const result = await testNERPostProcessor(experienceText, educationText);
    
    console.log('Raw Entities:', result.raw_entities);
    console.log('Validated Entities:', result.validated_entities);
    console.log('Statistics:', result.statistics);
    
    // Display in UI
    setResults({
      companies: result.validated_entities.companies,
      roles: result.validated_entities.roles,
      workExperience: result.work_experience,
      education: result.education,
      filteringRate: result.statistics.filtering_rate,
    });
  } catch (error) {
    console.error('Test failed:', error);
  }
};
```

---

## Next Steps

1. **Test with Your Data:**
   ```bash
   ./test_ner_endpoint.sh
   ```

2. **Review Results:**
   - Check `validated_entities` for correct filtering
   - Verify `work_experience` structure
   - Confirm `statistics.filtering_rate` is reasonable (50-80%)

3. **Tune Thresholds:**
   - If too many false positives: Increase thresholds
   - If too many false negatives: Decrease thresholds
   - Edit `ner_postprocessor.py` → `DEFAULT_CONFIDENCE_THRESHOLDS`

4. **Compare with Old Endpoint:**
   - Run both `/parse-sections` and `/test-ner-postprocessor`
   - Compare entity extraction quality
   - Measure performance difference

5. **Integrate into Production:**
   - Once satisfied, replace old logic with new pipeline
   - Update frontend to use new endpoint
   - Monitor performance and accuracy

---

## Support & Documentation

- **Full Documentation:** `ai-service/parsers/NER_POSTPROCESSING_README.md`
- **Integration Guide:** `INTEGRATION_GUIDE.md`
- **Test Suite:** `ai-service/tests/test_ner_postprocessor.py`
- **Source Code:**
  - `ai-service/parsers/ner_postprocessor.py` (13-phase pipeline)
  - `ai-service/parsers/integrated_ner_pipeline.py` (integration layer)

---

## Troubleshooting Checklist

- [ ] AI service running on port 8000
- [ ] DeBERTa model files present in `models/resume-ner-deberta/`
- [ ] Virtual environment activated
- [ ] Dependencies installed (`torch`, `transformers`)
- [ ] Test endpoint accessible: `curl http://localhost:8000/health`
- [ ] Logs showing no errors: Check console output
- [ ] Test data properly formatted (JSON with `experience_text` and `education_text`)

---

Good luck with your testing! 🚀

If you encounter any issues, check the logs in the terminal where the AI service is running for detailed debugging information.
