# 🔄 Complete Resume Upload Flow & JSON Output Guide

## 📋 **Step-by-Step Upload Flow**

### **Step 1: Frontend Upload**
```
User uploads resume.pdf → POST /api/v1/upload/upload
```

**What happens:**
- File validation (size, type, virus scan)
- File stored in S3 or local storage
- Parsing job created in database
- Background task starts

### **Step 2: Backend Processing Pipeline**
```
File → Text Extraction → ML/Rule-based Parsing → Database Storage
```

**Processing Stages:**
1. **Text Extraction** (`task_extract_text`)
2. **Text Cleaning** (`task_clean_text`)
3. **Section Detection** (`task_detect_sections`)
4. **Entity Extraction** (`task_extract_contact_info`, `task_parse_work_experience`, etc.)
5. **ML Enhancement** (LayoutLM + spaCy if available)
6. **Database Storage** (`task_save_to_database`)

---

## 🔍 **Where to Observe the JSON Output**

### **Option 1: API Endpoint (Recommended)**
```bash
GET /api/v1/candidates/{candidate_id}/parsing-debug
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/candidates/123e4567-e89b-12d3-a456-426614174000/parsing-debug"
```

### **Option 2: Database Direct Access**
```sql
-- View parsing job with JSON
SELECT id, status, parsed_data, parsed_json_path 
FROM parsing_jobs 
WHERE id = 'your-job-id';
```

### **Option 3: File System (Local Storage)**
```bash
# JSON file location
uploads/{year}/{month}/candidate_id/job_id/resume.json

# Example path
uploads/2024/03/123e4567-e89b-12d3-a456-426614174000/456e7890-e12b-34d5-a678-537714285111/resume.json
```

---

## 📊 **JSON Output Structure**

### **Complete Parsed Resume JSON:**
```json
{
  "contact": {
    "name": {
      "name": "John Doe",
      "confidence": 0.95
    },
    "email": {
      "email": "john.doe@email.com",
      "confidence": 0.98
    },
    "phone": {
      "phone": "+1-555-123-4567",
      "confidence": 0.90
    },
    "location": {
      "location": "Mountain View, CA",
      "confidence": 0.85
    },
    "linkedin": {
      "url": "linkedin.com/in/johndoe",
      "confidence": 0.92
    }
  },
  "summary": {
    "text": "Senior Software Engineer with 5+ years of experience...",
    "confidence": 0.88
  },
  "work_experience": [
    {
      "company": {
        "name": "Google",
        "confidence": 0.95
      },
      "title": {
        "title": "Senior Software Engineer",
        "confidence": 0.93
      },
      "location": "Mountain View, CA",
      "start_date": "2020-01-01",
      "end_date": "2023-12-31",
      "is_current": true,
      "description": "Developed microservices using Python and AWS...",
      "bullet_points": [
        "Led team of 5 engineers",
        "Improved system performance by 40%",
        "Built REST APIs with Node.js"
      ],
      "confidence": 0.91
    }
  ],
  "education": [
    {
      "institution": {
        "name": "Stanford University",
        "confidence": 0.96
      },
      "degree": {
        "degree": "Bachelor of Science in Computer Science",
        "confidence": 0.94
      },
      "start_date": "2014-09-01",
      "end_date": "2018-06-01",
      "gpa": "3.8",
      "confidence": 0.89
    }
  ],
  "skills": {
    "technical_skills": [
      {"skill": "Python", "confidence": 0.95},
      {"skill": "AWS", "confidence": 0.88},
      {"skill": "Docker", "confidence": 0.85},
      {"skill": "Kubernetes", "confidence": 0.82}
    ],
    "soft_skills": [
      {"skill": "Leadership", "confidence": 0.78},
      {"skill": "Communication", "confidence": 0.75}
    ],
    "certifications": [
      {"certification": "AWS Certified Developer", "confidence": 0.90}
    ]
  },
  "parsing_metadata": {
    "processing_time": 2.34,
    "models_used": ["spaCy", "rule_based"],
    "overall_confidence": 0.89,
    "parsing_mode": "full"
  }
}
```

---

## 🎯 **How to Test the Complete Flow**

### **Step 1: Upload Resume**
```bash
# Using curl
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf" \
  "http://localhost:8000/api/v1/upload/upload"

# Response:
{
  "message": "Upload successful",
  "jobs": [
    {
      "job_id": "456e7890-e12b-34d5-a678-537714285111",
      "status": "pending"
    }
  ]
}
```

### **Step 2: Check Parsing Status**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/parsing/456e7890-e12b-34d5-a678-537714285111"

# Response:
{
  "job_id": "456e7890-e12b-34d5-a678-537714285111",
  "status": "success",
  "last_stage": "save_to_database",
  "task_id": "celery-task-id",
  "celery_state": "SUCCESS"
}
```

### **Step 3: Get Parsed JSON**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/candidates/123e4567-e89b-12d3-a456-426614174000/parsing-debug"

# This returns the complete parsed JSON!
```

---

## 🔧 **Debugging & Monitoring**

### **View Processing Logs**
```bash
# Check Celery logs
docker-compose logs worker

# Check application logs
docker-compose logs app
```

### **Database Queries**
```sql
-- Check parsing job status
SELECT id, status, last_stage, error_message 
FROM parsing_jobs 
ORDER BY created_at DESC;

-- Check parsed data
SELECT candidate_id, parsed_data::text 
FROM parsing_jobs 
WHERE status = 'SUCCESS';
```

### **File System Check**
```bash
# Check if JSON file exists
ls -la uploads/2024/03/*/*/resume.json

# View JSON content
cat uploads/2024/03/candidate_id/job_id/resume.json | jq .
```

---

## 📈 **What to Observe in the JSON**

### **Key Metrics to Check:**
1. **Confidence Scores** - Look for values > 0.7
2. **Completeness** - All sections should be populated
3. **ML Model Usage** - Check `models_used` field
4. **Processing Time** - Should be < 5 seconds
5. **Error Handling** - Check for missing fields

### **Quality Indicators:**
- ✅ **High Confidence**: > 0.8 for most fields
- ✅ **Complete Sections**: Contact, Experience, Education, Skills
- ✅ **ML Enhancement**: `models_used` includes "spaCy" or "layoutlm"
- ✅ **Reasonable Time**: < 3 seconds processing

### **Common Issues:**
- ❌ **Low Confidence**: < 0.5 indicates parsing problems
- ❌ **Missing Sections**: Empty arrays or null values
- ❌ **Long Processing**: > 10 seconds indicates issues
- ❌ **Error Messages**: Check `error_message` field

---

## 🚀 **Production Monitoring**

### **API Endpoints for Monitoring:**
```bash
# List all candidates with their parsing status
GET /api/v1/candidates

# Get detailed parsing information
GET /api/v1/candidates/{candidate_id}/parsing-debug

# Get parsing job status
GET /api/v1/parsing/{job_id}
```

### **Performance Metrics:**
- **Upload Success Rate**: % of successful uploads
- **Processing Time**: Average time per resume
- **Accuracy**: Confidence scores across fields
- **Error Rate**: % of failed parsing jobs

---

## 🎯 **Quick Test Script**

```python
import requests
import time

# Test the complete flow
def test_resume_upload():
    # 1. Upload resume
    with open('resume.pdf', 'rb') as f:
        upload_response = requests.post(
            'http://localhost:8000/api/v1/upload/upload',
            files={'file': f},
            headers={'Authorization': 'Bearer YOUR_TOKEN'}
        )
    
    job_id = upload_response.json()['jobs'][0]['job_id']
    print(f"Uploaded with job_id: {job_id}")
    
    # 2. Wait for processing
    for i in range(30):  # Wait max 30 seconds
        status_response = requests.get(
            f'http://localhost:8000/api/v1/parsing/{job_id}',
            headers={'Authorization': 'Bearer YOUR_TOKEN'}
        )
        
        if status_response.json()['status'] == 'success':
            break
        time.sleep(1)
    
    # 3. Get parsed JSON
    candidate_id = "get-from-upload-response"
    json_response = requests.get(
        f'http://localhost:8000/api/v1/candidates/{candidate_id}/parsing-debug',
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
    
    parsed_json = json_response.json()
    print(f"Parsed JSON: {parsed_json}")
    
    return parsed_json

# Run test
result = test_resume_upload()
```

---

## 🏆 **Summary**

**Upload Flow**: File → Validation → Background Processing → JSON Output

**JSON Output Locations**:
1. **API**: `/api/v1/candidates/{id}/parsing-debug` (Easiest)
2. **Database**: `parsing_jobs.parsed_data` column
3. **File System**: `uploads/year/month/candidate_id/job_id/resume.json`

**What You'll See**: Complete structured JSON with contact info, experience, education, skills, and confidence scores!

Your ML-enhanced parser will automatically use spaCy and LayoutLM (when available) to provide the highest accuracy parsing! 🚀
