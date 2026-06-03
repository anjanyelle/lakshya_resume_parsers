# Skill Extraction API Integration

## Overview

The Resume Parser now integrates with an external Skill Extraction API to automatically extract and categorize skills from uploaded resumes.

## Architecture

```
User Upload Resume (localhost:5173/upload)
         ↓
Frontend calls: POST localhost:3001/api/upload/preview-sections
         ↓
Backend extracts full text from PDF/DOCX
         ↓
Backend parses sections (existing logic - unchanged)
         ↓
Backend calls: POST localhost:8000/extract-skills
         ↓
Skills API returns extracted skills with categories
         ↓
Response includes: sections + raw_text + extracted_skills_from_text
         ↓
Frontend displays skills in dedicated UI section
```

## API Endpoints

### 1. Upload & Preview Sections (Modified)

**Endpoint:** `POST /api/upload/preview-sections`

**Request:**
```bash
curl -X POST http://localhost:3001/api/upload/preview-sections \
  -F "file=@resume.pdf" \
  -F "force_ocr=false"
```

**Response:**
```json
{
  "filename": "resume.pdf",
  "extraction_method": "auto",
  "raw_text_length": 5432,
  "raw_text": "FULL RESUME TEXT HERE...",
  "total_sections": 7,
  "sections": {
    "summary": {
      "text": "Experienced developer...",
      "char_count": 234
    },
    "experience": {
      "text": "Senior Developer at...",
      "char_count": 1234
    },
    "skills": {
      "text": "React.js, Python, AWS...",
      "char_count": 456
    }
  },
  "detected_sections": ["summary", "experience", "education", "skills"],
  "missing_sections": ["certifications", "projects"],
  "validation_metadata": {
    "spacy_available": false,
    "warnings": []
  },
  "extracted_skills_from_text": {
    "total_skills": 45,
    "skills_by_category": {
      "Programming Languages": [
        {
          "name": "Python",
          "normalized_name": "python",
          "category": "Programming Languages",
          "confidence": 0.95,
          "source": "technical_skills_section"
        }
      ],
      "Cloud Platforms": [
        {
          "name": "AWS",
          "normalized_name": "aws",
          "category": "Cloud Platforms",
          "confidence": 0.92,
          "source": "experience"
        }
      ]
    },
    "all_skills": [
      {
        "name": "Python",
        "normalized_name": "python",
        "category": "Programming Languages",
        "confidence": 0.95,
        "source": "technical_skills_section"
      }
    ],
    "categories": ["Programming Languages", "Cloud Platforms", "Databases"]
  }
}
```

### 2. External Skill Extraction API

**Endpoint:** `POST http://localhost:8000/extract-skills`

**Request:**
```bash
curl -X POST http://localhost:8000/extract-skills \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FULL RESUME TEXT INCLUDING ALL SECTIONS..."
  }'
```

**Response:**
```json
{
  "total_skills": 45,
  "skills_by_category": {
    "Programming Languages": [...],
    "Cloud Platforms": [...],
    "Databases": [...]
  },
  "all_skills": [...],
  "categories": [...]
}
```

## Implementation Details

### Backend Changes

**File:** `backend/app/api/v1/endpoints/upload.py`

1. **Full Text Extraction:**
   ```python
   extracted = extract_text(temp_path)
   text = extracted.text  # Complete resume text
   ```

2. **Section Parsing (Unchanged):**
   ```python
   parser = SectionParser()
   parsed_sections = parser.parse(text)
   ```

3. **External API Call:**
   ```python
   import httpx
   async with httpx.AsyncClient(timeout=30.0) as client:
       response = await client.post(
           "http://localhost:8000/extract-skills",
           json={"text": text},  # FULL resume text
           headers={"Content-Type": "application/json"}
       )
       if response.status_code == 200:
           extracted_skills_from_text = response.json()
   ```

4. **Response Structure:**
   ```python
   return SectionPreviewResponse(
       filename=file.filename,
       raw_text=text,  # Full resume text
       sections=sections_dict,  # Parsed sections
       extracted_skills_from_text=extracted_skills_from_text  # Skills from API
   )
   ```

### Frontend Changes

**File:** `frontend/src/pages/UploadPage.tsx`

1. **State Management:**
   ```typescript
   const [extractedSkillsFromText, setExtractedSkillsFromText] = useState<any>(null);
   ```

2. **Capture API Response:**
   ```typescript
   const skillsData = response.data.extracted_skills_from_text || null;
   setExtractedSkillsFromText(skillsData);
   ```

3. **Display Skills UI:**
   - Skills grouped by category
   - Confidence scores displayed
   - Color-coded badges
   - Hover tooltips with details

## UI Features

### Extracted Skills Section

- **Header:** Shows total skills count with "AI Extracted" badge
- **Category View:** Skills organized by technical categories
- **Confidence Scores:** Each skill shows extraction confidence percentage
- **All Skills View:** Flat list sorted by confidence (top 50 displayed)
- **Responsive Design:** Modern card-based layout with gradients

### Example Display

```
🎯 EXTRACTED SKILLS (45)                    [AI Extracted]
Skills automatically extracted from resume using SkillExtractor

Programming Languages
  Python 95%  JavaScript 92%  TypeScript 88%

Cloud Platforms
  AWS 92%  Azure 85%  GCP 80%

Databases
  PostgreSQL 90%  MongoDB 87%  MySQL 85%

All Skills (Sorted by Confidence)
  Python 95%  JavaScript 92%  AWS 92%  PostgreSQL 90%  ...
```

## Testing

### 1. Test Skill Extraction API Directly

```bash
bash test_skill_api.sh
```

### 2. Test Full Upload Flow

```bash
bash test_upload_with_skills.sh
```

### 3. Manual Testing

1. Start backend: `cd backend && uvicorn app.main:app --reload --port 3001`
2. Start skill API: (ensure running on port 8000)
3. Start frontend: `cd frontend && npm run dev`
4. Navigate to: `http://localhost:5173/upload`
5. Upload a resume
6. Verify skills appear in the "EXTRACTED SKILLS" section

## Important Notes

### ✅ What Changed

- Added external API call to `http://localhost:8000/extract-skills`
- Full resume text is sent to the skill API
- Skills response is included in preview-sections response
- Frontend displays extracted skills in dedicated UI section

### ✅ What Stayed the Same

- Section parsing logic (unchanged)
- Existing response structure (only added new field)
- All other endpoints and functionality
- Frontend section preview functionality

### ⚠️ Requirements

1. **Skill Extraction API must be running on port 8000**
2. **API must accept:** `POST /extract-skills` with `{"text": "..."}`
3. **API must return:** Skills data with categories and confidence scores

## Error Handling

- If skill API is unavailable: `extracted_skills_from_text` will be `null`
- Frontend gracefully handles missing skills data
- Logs errors for debugging
- Section parsing continues normally even if skill extraction fails

## Performance

- Skill extraction runs in parallel with section parsing
- Timeout: 30 seconds for API call
- No blocking of main upload flow
- Async/await for non-blocking execution

## Future Enhancements

1. Cache skill extraction results
2. Add skill confidence threshold filtering
3. Allow manual skill editing in UI
4. Export skills to different formats
5. Skill matching against job descriptions
