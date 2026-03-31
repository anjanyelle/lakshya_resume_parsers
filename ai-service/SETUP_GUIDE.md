# AI Service Setup Guide

## ✅ **Quick Start**

The AI service is now running successfully on `http://localhost:8000`

### **What's Working**
- ✅ **Health Endpoint**: `GET /health`
- ✅ **Parse Endpoint**: `POST /parse`
- ✅ **Basic Resume Parsing**: Name, Email, Phone extraction
- ✅ **Confidence Scoring**: Field-level confidence scores
- ✅ **Mock Parser**: Simplified parser for testing

---

## 🚀 **How to Use**

### **Start the Service**
```bash
cd ai-service
source venv/bin/activate
uvicorn main_simple:app --host 0.0.0.0 --port 8000 --reload
```

### **Test Health Check**
```bash
curl http://localhost:8000/health
```

### **Test Resume Parsing**
```bash
curl -X POST "http://localhost:8000/parse" \
-H "Content-Type: application/json" \
-d '{
  "text": "John Smith\nEmail: john.smith@example.com\nPhone: +1-555-123-4567\nSoftware Engineer"
}'
```

---

## 📊 **API Endpoints**

### **GET /health**
Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "All systems operational (simplified mode)",
  "timestamp": "2026-03-28 20:51:30"
}
```

### **POST /parse**
Parse resume text and extract information.

**Request:**
```json
{
  "text": "John Smith\nEmail: john.smith@example.com\nPhone: +1-555-123-4567",
  "options": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "John Smith",
    "email": "john.smith@example.com", 
    "phone": "+1-555-123-4567",
    "confidence": {
      "overall": 0.85,
      "fields": {
        "name": 0.9,
        "email": 0.9,
        "phone": 0.8
      }
    }
  },
  "processing_time": 0.003
}
```

### **GET /stats**
Get parser statistics and capabilities.

**Response:**
```json
{
  "parser_type": "mock_simple",
  "status": "running",
  "supported_formats": ["text"],
  "features": [
    "basic_text_extraction",
    "email_detection",
    "phone_detection", 
    "confidence_scoring"
  ]
}
```

---

## 🔧 **Current Setup**

### **Virtual Environment**
- **Python Version**: 3.13.7
- **Location**: `ai-service/venv`
- **Installed Packages**: 
  - fastapi==0.135.2
  - uvicorn[standard]==0.42.0
  - pydantic==2.12.5
  - python-multipart==0.0.22

### **Service Configuration**
- **Host**: 0.0.0.0 (accessible from any IP)
- **Port**: 8000
- **Mode**: Development with auto-reload
- **CORS**: Enabled for all origins

---

## 📝 **Notes**

### **Current Limitations**
- This is a **simplified mock parser** for testing
- No advanced NLP/AI features (requires additional dependencies)
- No PDF/DOCX file parsing (text only)
- No LLM integration (requires API keys and models)

### **Next Steps**
1. **Install additional dependencies** for full parsing:
   ```bash
   pip install pymupdf pdfplumber python-docx transformers torch
   ```

2. **Switch to full parser**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Configure API keys** in `.env` file for LLM features

---

## 🎯 **Testing**

The service is ready for testing with:
- Frontend applications
- API integration tests
- Resume parsing workflows
- Development and debugging

**Server Status**: ✅ **RUNNING** on `http://localhost:8000`

**Last Started**: 2026-03-28 20:51:13

**Mode**: Simplified mock parser for testing
