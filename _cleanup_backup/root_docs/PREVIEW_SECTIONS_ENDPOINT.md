# Preview Sections Endpoint - Complete Implementation

## Overview

Created a new endpoint chain that allows previewing resume sections without running DeBERTa entity extraction:

**Frontend → Node.js Backend → Python AI Service**

---

## Implementation Details

### **1. Python AI Service Endpoint**

**File:** `ai-service/main.py`

**Endpoint:** `POST /preview-sections`

**What it does:**
- Accepts file upload (field name: `file`)
- Runs text extraction (PDF/DOCX/TXT)
- Runs section splitting (regex + font metadata)
- Runs section validation (spaCy NLP)
- **Does NOT run DeBERTa or entity extraction**

**Response:**
```json
{
  "filename": "resume.pdf",
  "extraction_method": "pdfplumber",
  "raw_text_length": 7591,
  "raw_text": "Full extracted text...",
  "total_sections": 6,
  "sections": {
    "experience": {
      "text": "Section content...",
      "char_count": 2345
    },
    "education": {...},
    "skills": {...}
  },
  "detected_sections": ["experience", "education", "skills", "summary"],
  "missing_sections": ["certifications", "projects"]
}
```

---

### **2. Node.js Backend Route**

**File:** `backend/src/routes/upload.routes.ts`

**Endpoint:** `POST /api/upload/preview-sections`

**Authentication:** Requires Bearer token (uses `authenticateToken` middleware)

**What it does:**
- Accepts file upload using multer (field name: `file` or `resume`)
- Validates file upload
- Forwards file to Python AI service using FormData
- Returns Python service response directly to frontend
- Cleans up temporary file after processing
- Handles errors gracefully

**Controller:** `backend/src/controllers/upload.controller.ts` - `previewSections()`

**Console Logging:**
```
🔍 Preview sections endpoint called for file: resume.pdf
📤 Forwarding to Python AI service: http://localhost:8000/preview-sections
✅ Preview sections completed for: resume.pdf
```

---

## Error Handling

### **AI Service Unavailable**
```json
{
  "error": "AI service unavailable",
  "message": "The Python AI service is currently unreachable. Please try again later.",
  "code": "AI_SERVICE_UNAVAILABLE"
}
```
**HTTP Status:** 503

### **No File Uploaded**
```json
{
  "error": "No file uploaded",
  "message": "Please upload a resume file",
  "code": "NO_FILE_UPLOADED"
}
```
**HTTP Status:** 400

### **Preview Failed**
```json
{
  "error": "Preview sections failed",
  "message": "Failed to preview sections",
  "code": "PREVIEW_FAILED"
}
```
**HTTP Status:** 500

---

## Files Modified

### **Python AI Service**
1. **`ai-service/main.py`**
   - Added `UploadFile` and `File` imports (line 1)
   - Added `SectionPreviewResponse` model (lines 235-243)
   - Added `/preview-sections` endpoint (lines 714-836)
   - Updated root endpoint documentation (line 257)

### **Node.js Backend**
1. **`backend/src/controllers/upload.controller.ts`**
   - Added imports: `FormData`, `fs`, `axios` (lines 11-13)
   - Added `previewSections()` function (lines 293-387)

2. **`backend/src/routes/upload.routes.ts`**
   - Added `previewSections` import (line 6)
   - Added route with Swagger documentation (lines 101-157)

---

## Usage Examples

### **cURL**
```bash
# Direct to Python service
curl -X POST http://localhost:8000/preview-sections \
  -F "file=@resume.pdf"

# Through Node.js backend
curl -X POST http://localhost:3001/api/upload/preview-sections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf"
```

### **JavaScript/Fetch**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:3001/api/upload/preview-sections', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const data = await response.json();
console.log('Sections:', data.sections);
console.log('Detected:', data.detected_sections);
console.log('Missing:', data.missing_sections);
```

---

## Environment Variables

**Node.js Backend** (`backend/src/.env`):
```
AI_SERVICE_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`

---

## Dependencies

### **Node.js Backend**
- `form-data` - For creating multipart/form-data requests
- `axios` - For HTTP requests to Python service
- `fs` - For file stream operations

These should already be installed. If not:
```bash
cd backend/src
npm install form-data axios
```

### **Python AI Service**
No new dependencies required. Uses existing:
- `fastapi`
- `python-multipart` (for file uploads)

---

## Testing

### **1. Start Python AI Service**
```bash
cd ai-service
source venv/bin/activate
python main.py
```

### **2. Start Node.js Backend**
```bash
cd backend/src
npm run dev
```

### **3. Test Endpoint**
```bash
curl -X POST http://localhost:3001/api/upload/preview-sections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_resume.pdf"
```

---

## Benefits

1. **Fast Preview** - No DeBERTa processing (saves 2-3 seconds per resume)
2. **Debugging** - See exactly what sections are detected before entity extraction
3. **Quality Check** - Verify text extraction and section splitting quality
4. **Error Isolation** - Identify if issues are in extraction/splitting vs entity extraction

---

## Console Output Example

**Python AI Service:**
```
INFO:     127.0.0.1:52341 - "POST /preview-sections HTTP/1.1" 200 OK
Processing file for section preview: resume.pdf
Text extracted: 7591 chars using pdfplumber
Sections detected: 6
Sections after validation: 6
Section preview complete for resume.pdf
```

**Node.js Backend:**
```
🔍 Preview sections endpoint called for file: resume.pdf
📤 Forwarding to Python AI service: http://localhost:8000/preview-sections
✅ Preview sections completed for: resume.pdf
```

---

## Next Steps

This endpoint is now ready to use for:
- Frontend debugging tools
- Section quality analysis
- Resume upload preview before full parsing
- Testing section detection improvements
