# Section Parsing Flow - Complete Guide

## Overview
This document explains the complete flow for extracting resume sections and parsing them with AI models.

## Architecture

### Step 1: Section Extraction (Frontend → Backend → AI Service)
**Endpoint:** `POST /api/resume/preview-sections`

**Flow:**
1. User uploads resume (PDF/DOCX) on frontend
2. Frontend sends file to backend
3. Backend forwards to AI service `/preview-sections`
4. AI service extracts text and splits into sections
5. Returns raw section text (e.g., Experience: 1,726 chars, Education: 79 chars)

**Response:**
```json
{
  "sections": {
    "experience": {
      "text": "React\n- Built a drag-and-drop resume builder...",
      "char_count": 1726
    },
    "education": {
      "text": "Bachelor of Engineering in Computer Science...",
      "char_count": 79
    }
  },
  "detected_sections": ["summary", "experience", "education", "skills"],
  "missing_sections": ["certifications", "projects"]
}
```

### Step 2: AI Model Parsing (Frontend → AI Service)
**Endpoint:** `POST http://localhost:8000/parse-sections`

**Flow:**
1. User clicks "Parse Sections" button
2. Frontend sends extracted section text to AI service
3. AI service uses ExperienceExtractor and EducationExtractor
4. Returns structured/parsed data

**Request:**
```json
{
  "experience_text": "React\n- Built a drag-and-drop resume builder...",
  "education_text": "Bachelor of Engineering in Computer Science..."
}
```

**Response:**
```json
{
  "status": "success",
  "work_experience": [
    {
      "job_title": "Frontend Developer",
      "company_name": "OxyLoans",
      "location": "Hyderabad",
      "duration": "Oct 2022 - Nov 2024",
      "responsibilities": [
        "Built a drag-and-drop resume builder with live preview",
        "Integrated resume parsing APIs and AI-based candidate scoring"
      ],
      "technologies": ["React", "Redux", "TypeScript"]
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Engineering",
      "institution": "MVSR Engineering College",
      "field_of_study": "Computer Science",
      "graduation_date": "Hyderabad"
    }
  ],
  "processing_time_ms": 245.3,
  "message": "Successfully parsed 1 experience entries and 1 education entries"
}
```

## Frontend Display

### Before Parsing
Shows raw section text:
```
EXPERIENCE          1,726 characters    ✓ Detected
React
- Built a drag-and-drop resume builder with live preview
- Integrated resume parsing APIs and AI-based candidate scoring
...
```

### After Parsing
Shows structured data in cards:

**Work Experience (1 entries)**
```
┌─────────────────────────────────────────────┐
│ Job Title: Frontend Developer              │
│ Company: OxyLoans (P2P Lending Platform)   │
│ Location: Hyderabad                         │
│ Duration: Oct 2022 - Nov 2024               │
│                                             │
│ Responsibilities:                           │
│ • Built a drag-and-drop resume builder     │
│ • Integrated resume parsing APIs           │
│                                             │
│ Technologies:                               │
│ [React] [Redux] [TypeScript] [Context API] │
└─────────────────────────────────────────────┘
```

**Education (1 entries)**
```
┌─────────────────────────────────────────────┐
│ Degree: Bachelor of Engineering            │
│ Institution: MVSR Engineering College      │
│ Field: Computer Science                     │
│ Graduation: Hyderabad                       │
└─────────────────────────────────────────────┘
```

## How to Use

### 1. Upload Resume
- Go to `http://localhost:5173/section-preview`
- Upload PDF or DOCX file
- Click "Analyze Sections"

### 2. View Extracted Sections
- See which sections were detected (Summary, Experience, Education, Skills, etc.)
- View raw text for each section
- Check character counts

### 3. Parse with AI Model
- Click "Parse Sections" button
- Wait for AI model to process (usually < 1 second)
- View structured results with:
  - Job titles, companies, dates, responsibilities
  - Degrees, institutions, graduation dates
  - Technologies and skills

## Technical Details

### Backend Files Modified
- `ai-service/main.py`:
  - Added `ParseSectionsRequest` model
  - Added `ParseSectionsResponse` model
  - Added `/parse-sections` endpoint

### Frontend Files Modified
- `frontend/src/pages/SectionPreviewPage.tsx`:
  - Added `ParsedSectionsResponse` interface
  - Added `parsedData` state
  - Added `handleParseSections()` function
  - Added "Parse Sections" button
  - Added structured data display section

### AI Models Used
- **ExperienceExtractor**: Parses work experience into structured entries
- **EducationExtractor**: Parses education into structured entries

## API Endpoints

### 1. Preview Sections (via Backend)
```
POST http://localhost:3001/api/resume/preview-sections
Content-Type: multipart/form-data

file: <resume.pdf>
```

### 2. Parse Sections (Direct to AI Service)
```
POST http://localhost:8000/parse-sections
Content-Type: application/json

{
  "experience_text": "...",
  "education_text": "..."
}
```

## Testing

1. **Start AI Service:**
   ```bash
   cd ai-service
   source venv/bin/activate
   python main.py
   # Running on http://0.0.0.0:8000
   ```

2. **Start Backend:**
   ```bash
   cd backend
   npm run dev
   # Running on http://localhost:3001
   ```

3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   # Running on http://localhost:5173
   ```

4. **Test Flow:**
   - Upload resume → Click "Analyze Sections" → Click "Parse Sections"
   - Verify structured data appears with job titles, companies, etc.

## Benefits

✅ **Two-Step Process**: First extract sections, then parse with AI
✅ **Visual Feedback**: See raw text before parsing
✅ **Structured Output**: Get clean JSON with job titles, companies, dates
✅ **Fast Processing**: < 1 second for most resumes
✅ **Error Handling**: Clear error messages if parsing fails

## Next Steps

- Add more sections (Skills, Projects, Certifications)
- Add export to JSON button for parsed data
- Add edit functionality for parsed results
- Integrate with main resume parser pipeline
