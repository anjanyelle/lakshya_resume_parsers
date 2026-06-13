I'll analyze your Resume Parser codebase to understand the text extraction flow. Let me inspect the key files:

















Now let me check the section extraction and parsing flow:



Now let me check the main API endpoint that handles the upload:



Now let me check the parsing workflow:

Perfect! Now I have enough information. Let me provide you with a comprehensive analysis:

---

## 📊 **RESUME PARSER CODEBASE ANALYSIS**

### **1. TEXT EXTRACTION LIBRARIES**

#### **DOCX Files:**
- **Library:** `python-docx` (imported as `from docx import Document`)
- **Location:** [/backend/app/services/parser/extract_text.py](cci:7://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:0:0-0:0) lines 23, 991
- **Function:** [_extract_docx(file_path: Path)](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:989:0-1287:67) at line 990

#### **PDF Files (Multi-tier fallback system):**
1. **Primary:** `PyMuPDF` (fitz) - Layout-aware, fastest
   - Import: `import fitz` (line 14)
   - Function: [extract_text_from_pdf_pymupdf_layout()](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:463:0-528:81) (line 318)
   
2. **Fallback 1:** `pypdf` (PdfReader) - Fast, simple
   - Import: `from pypdf import PdfReader` (line 22)
   - Used at line 331-338
   
3. **Fallback 2:** `pdfplumber` - For tables
   - Import: `import pdfplumber` (line 20)
   - Function: [_extract_tables_only_pdfplumber()](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:292:0-305:17) (line 293)
   - Full extraction: lines 356-373

#### **OCR Library (when "Force OCR" enabled):**
- **Library:** `Tesseract OCR` via `pytesseract`
- **Import:** `import pytesseract` (line 198)
- **Function:** [_ocr_pdf()](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:916:0-982:40) at line 917
- **Helper:** `_ocr_with_confidence()` for confidence scoring
- **Image conversion:** `pdf2image.convert_from_path()` (line 932)

---

### **2. COMPLETE UPLOAD & PARSING FLOW**

```
📤 RESUME UPLOAD
│
├─ File: /backend/app/api/v1/endpoints/upload.py
├─ Function: _process_uploads() (line 71)
├─ Validation: validate_magic(), scan_file()
├─ Storage: S3 or local filesystem
│
↓
📝 TEXT EXTRACTION
│
├─ Worker: /backend/app/workers/extract_text_task.py
├─ Task: extract_text_task() (line 42)
├─ Core Function: extract_text(file_path) from extract_text.py (line 194)
│
├─ PDF Extraction Flow (line 309):
│   1. Try PyMuPDF (fitz) → method="pymupdf"
│   2. Try pypdf → method="pypdf"
│   3. Try pdfplumber (tables) → method="pypdf+pdfplumber_tables"
│   4. Try pdfplumber (full) → method="pdfplumber"
│   5. If text < OCR_MIN_TEXT_CHARS → Trigger OCR → method="ocr"
│
├─ DOCX Extraction (line 990):
│   - python-docx Document()
│   - Extracts paragraphs, tables, headers, footers, textboxes
│   - Preserves structure with ## headings and - bullets
│
├─ OCR Trigger (line 375-403):
│   - Triggered when len(text) < OCR_MIN_TEXT_CHARS
│   - Uses Tesseract via pytesseract
│   - Parallel processing (ThreadPoolExecutor)
│   - DPI: 300 (initial), 400 (retry if confidence < 60)
│
↓
🔍 SECTION DETECTION
│
├─ File: /backend/app/services/parser/section_parser.py
├─ Class: SectionParser
├─ Detects: contact, summary, experience, education, skills, certifications, projects
├─ Method: Pattern matching + spaCy PhraseMatcher
│
↓
💼 EXPERIENCE EXTRACTION
│
├─ File: /backend/app/services/parser/work_experience_parser.py
├─ Class: WorkExperienceParser
├─ Function: parse_experience_section()
├─ Extracts: company, role, dates, location, responsibilities, technologies
├─ Confidence threshold: 0.95 (falls back to LLM if lower)
│
↓
🎓 EDUCATION EXTRACTION
│
├─ File: /backend/app/services/parser/education_parser.py
├─ Class: EducationParser
├─ Extracts: institution, degree, field_of_study, dates, GPA
│
↓
🤖 DeBERTa NER PARSER (Optional)
│
├─ Location: Python AI service (separate process)
├─ Port: 8000 (AI_SERVICE_URL)
├─ Endpoint: /parse-sections
├─ Uses: Fine-tuned DeBERTa model for NER
│
↓
📊 API RESPONSE
│
└─ Returns: work_experience, education, skills, contact, summary, certifications, projects
```

---

### **3. EXACT CODE LOCATIONS**

#### **Resume Upload:**
- **File:** [/backend/app/api/v1/endpoints/upload.py](cci:7://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/api/v1/endpoints/upload.py:0:0-0:0)
- **Function:** [_process_uploads()](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/api/v1/endpoints/upload.py:70:0-218:70) (line 71-178)
- **Creates:** Candidate + ParsingJob records
- **Triggers:** `start_parsing_workflow(job.id)` (line 27)

#### **Text Extraction:**
- **File:** [/backend/app/services/parser/extract_text.py](cci:7://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:0:0-0:0)
- **Main Function:** [extract_text(file_path: Path)](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:193:0-222:64) (line 194)
- **PDF:** [_extract_pdf()](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:308:0-426:5) (line 309)
- **DOCX:** [_extract_docx()](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:989:0-1287:67) (line 990)
- **OCR:** [_ocr_pdf()](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:916:0-982:40) (line 917)

#### **Section Extraction:**
- **File:** [/backend/app/services/parser/section_parser.py](cci:7://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/section_parser.py:0:0-0:0)
- **Class:** [SectionParser](cci:2://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/section_parser.py:2284:0-3252:18)
- **Sections:** contact, summary, experience, education, skills, certifications, projects

#### **Experience Extraction:**
- **File:** `/backend/app/services/parser/work_experience_parser.py`
- **Class:** `WorkExperienceParser`
- **Method:** `parse_experience_section()`

#### **Education Extraction:**
- **File:** `/backend/app/services/parser/education_parser.py`
- **Class:** `EducationParser`

---

### **4. GPT-4o-mini INTEGRATION ANALYSIS**

#### **What OpenAI Currently Receives:**
Based on your implementation in [/backend/src/controllers/upload.controller.ts](cci:7://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/src/controllers/upload.controller.ts:0:0-0:0):

```typescript
const experienceText = experience_text || "";
const educationText = education_text || "";
```

**OpenAI receives:**
- ✅ `experience_text` - Section-extracted experience text only
- ✅ `education_text` - Section-extracted education text only
- ❌ NOT `raw_text` - Full resume text is NOT sent to OpenAI

#### **Text Extraction Pipeline:**
**YES**, OpenAI uses the **SAME** text extraction pipeline:

1. **Frontend** uploads resume → **Node.js backend** (`backend/src`)
2. **Node.js** forwards to **Python AI service** (`backend/app`) via `/preview-sections`
3. **Python AI service** uses:
   - [extract_text()](cci:1://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/extract_text.py:193:0-222:64) → PyMuPDF/pdfplumber/pytesseract
   - [SectionParser](cci:2://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/app/services/parser/section_parser.py:2284:0-3252:18) → Detects sections
   - Returns `sections.experience.text` and `sections.education.text`
4. **Frontend** sends these section texts to **Node.js** `/parse-sections`
5. **Node.js** routes to:
   - **OpenAI** (if `model=gpt-4o-mini`) → Uses `experience_text` + `education_text`
   - **Python DeBERTa** (if `model=own-model`) → Uses all sections

---

### **5. HYBRID PARSING FLOW (Current Implementation)**

When `model = "gpt-4o-mini"`:

```
Step A: OpenAI Parser
├─ Input: experience_text, education_text
├─ Output: work_experience[], education[]
│
Step B: Existing Parser (Python DeBERTa)
├─ Input: ALL sections (experience, education, skills, contact, summary, etc.)
├─ Output: skills[], contact{}, summary, certifications[], projects[]
│
Step C: Merge Results
└─ Final: OpenAI (experience/education) + DeBERTa (everything else)
```

---

### **6. KEY FINDINGS**

✅ **Text Extraction Libraries:**
- DOCX: `python-docx`
- PDF: `PyMuPDF` (primary) → `pypdf` → `pdfplumber`
- OCR: `Tesseract` via `pytesseract`

✅ **Same Pipeline:**
- OpenAI uses the SAME text extraction as DeBERTa
- Both receive section-extracted text, NOT raw text

✅ **Hybrid Approach:**
- OpenAI: experience + education only
- DeBERTa: skills, contact, summary, certifications, projects

✅ **No Code Duplication:**
- Single text extraction pipeline
- Section detection happens once
- Results are routed based on model selection

---

**This is your complete codebase analysis. No files were created, only inspection and explanation as requested.**