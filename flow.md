I'll analyze your Resume Parser application and provide a comprehensive technical explanation of the entire flow. Let me first explore the codebase structure to understand the implementation.

# Complete Technical Architecture Documentation: Resume Parser Application

Based on my analysis of your Lakshya Resume Parser codebase, here's a comprehensive end-to-end technical explanation of how the system works internally.

## 1. Resume Upload Flow

### What happens when a user uploads a resume?

**Frontend Flow:**
1. User selects a file (PDF/DOCX) via React dropzone in `<UploadPage.tsx>`
2. File is validated for type and size
3. WebSocket connection is established for real-time progress updates
4. File is uploaded to backend via POST `/api/upload` endpoint

**Backend Flow:**
1. **uploadResume()** function in <ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/backend/src/controllers/upload.controller.ts" lines="285-350" /> is triggered
2. File validation via `validateUploadedFile()` middleware
3. Immediate text extraction via AI service `/preview-sections` endpoint
4. Database transaction begins - creates candidate record with 'pending' status
5. AI service is called for full parsing
6. Results are stored and candidate status updated to 'success'

**Key Functions Called:**
```typescript
uploadResume()           // Main controller function
validateUploadedFile()   // File validation middleware
extractTextFromPDF()     // Text extraction (via AI service)
parseResume()            // Full AI parsing via master parser
storeAllParsedData()     // Database storage
```

## 2. Text Extraction

### How text is extracted from PDF/DOCX files

**Multi-Tier Extraction Strategy** (from <ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/ai-service/parsers/text_extractor.py" lines="64-100" />):

**Tier 1: pdfplumber** - Best for text-based PDFs
- Extracts text layer directly from PDF
- Preserves layout and formatting
- Fast and accurate for digital PDFs

**Tier 2: AWS Textract** - Cloud-based OCR
- Used for scanned PDFs and table-heavy layouts
- Handles complex layouts and forms
- Requires AWS credentials

**Tier 3: pymupdf (fitz)** - Fallback digital text
- Alternative PDF text extraction
- Good backup when pdfplumber fails

**Tier 4: Tesseract OCR** - Local OCR fallback
- Last resort for scanned documents
- Runs locally, no cloud dependency
- Slower but works offline

**Example Extracted Text:**
```
JOHN DOE
Senior Software Engineer
john.doe@email.com | (555) 123-4567 | San Francisco, CA

SUMMARY
Experienced software engineer with 8+ years in full-stack development...

EXPERIENCE
Senior Software Engineer | Google
2020 - Present
• Led team of 5 developers on cloud infrastructure project
• Implemented microservices architecture reducing latency by 40%

Software Engineer | Microsoft
2017 - 2020
• Developed REST APIs using Node.js and Express
• Worked on Azure cloud migration project
```

**Common Libraries Used:**
- `pdfplumber` - PDF text extraction
- `pymupdf/fitz` - Alternative PDF extraction
- `python-docx` - DOCX file handling
- `pytesseract` - OCR for scanned PDFs
- `boto3` - AWS Textract integration

**Potential Extraction Issues:**
- Scanned PDFs with poor image quality
- Multi-column layouts causing text scrambling
- Tables and forms losing structure
- Encoded characters (â€™ instead of ')
- Password-protected PDFs
- Corrupted file formats

## 3. Section Splitting

### How extracted text is split into sections

**Section Splitter** (<ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/ai-service/parsers/section_splitter.py" lines="19-99" />) uses regex patterns to identify sections:

**Section Patterns:**
```python
SECTION_PATTERNS = {
    'experience': re.compile(r'(?i)^\s*(work experience|professional experience|employment history|...)'),
    'education': re.compile(r'(?i)^\s*(education|academic background|educational qualifications|...)'),
    'skills': re.compile(r'(?i)^\s*(skills|key skills|core skills|technical skills|...)'),
    'summary': re.compile(r'(?i)^\s*(summary|professional summary|career summary|profile|...)'),
    'certifications': re.compile(r'(?i)^\s*(certifications|certificates|professional certifications|...)'),
    'projects': re.compile(r'(?i)^\s*(projects|project experience|key projects|...)')
}
```

**Example Implementation:**
```python
class SectionSplitter:
    def split_sections(self, text: str) -> Dict[str, str]:
        sections = {}
        lines = text.split('\n')
        current_section = 'header'
        current_content = []
        
        for line in lines:
            matched = False
            for section_name, pattern in SECTION_PATTERNS.items():
                if pattern.match(line):
                    sections[current_section] = '\n'.join(current_content)
                    current_section = section_name
                    current_content = []
                    matched = True
                    break
            if not matched:
                current_content.append(line)
        
        sections[current_section] = '\n'.join(current_content)
        return sections
```

**Example Input:**
```
JOHN DOE
Senior Software Engineer

SUMMARY
Experienced developer...

EXPERIENCE
Senior Engineer at Google...
```

**Example Output:**
```json
{
  "header": "JOHN DOE\nSenior Software Engineer",
  "summary": "Experienced developer...",
  "experience": "Senior Engineer at Google..."
}
```

## 4. Pre-Processing

### What preprocessing happens before sending data to AI model

**ResumePreprocessor** (<ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/ai-service/parsers/preprocessor.py" lines="25-45" />) applies multiple normalization steps:

**Text Cleaning:**
```python
def preprocess(self, raw_text: str) -> str:
    text = self._reconstruct_reading_order(raw_text)  # Fix multi-column layouts
    text = self._normalize_bullets(text)              # Standardize bullet points
    text = self._fix_broken_lines(text)               # Fix hyphenated words
    text = self._normalize_section_headers(text)      # Standardize headers
    text = self._fix_encoding_artifacts(text)         # Fix special characters
    text = self._normalize_whitespace(text)           # Remove extra spaces
    return text.strip()
```

**Specific Operations:**

1. **Reading Order Reconstruction**
   - Detects multi-column layouts (3+ spaces between text)
   - Reconstructs columns sequentially instead of line-by-line
   - Prevents text scrambling from side-by-side layouts

2. **Bullet Normalization**
   - Converts all bullet variants to plain dash: • ● ◦ ▪ → -
   - Ensures consistent list formatting

3. **Encoding Fixes**
   - Fixes common encoding issues: â€™ → ', â€œ → ", Ã© → é
   - Handles Unicode characters properly

4. **Whitespace Normalization**
   - Removes excessive spaces and newlines
   - Standardizes line breaks

5. **Section Header Normalization**
   - Standardizes section header formats
   - Removes extra formatting around headers

**Token Optimization:**
- Removes redundant text to reduce token count
- Preserves semantic meaning
- Optimizes for LLM context limits

**Validation Checks:**
- Minimum text length validation (200 chars)
- Character set validation
- Language detection
- Quality scoring

## 5. Prompt Engineering

### Exact prompt sent to LLM

**System Prompt** (<ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/ai-service/parsers/llm_full_parser.py" lines="32-43" />):

```python
system_prompt = """You are an expert AI Resume Parser with advanced text understanding capabilities.

Your ONLY job is to extract structured data from resume text and return VALID JSON.

CRITICAL RULES:
1. Output ONLY JSON - no markdown, no explanation, no extra text
2. Follow the exact schema provided
3. NEVER put locations, dates, or "Present" in job_title field
4. ALWAYS extract the actual job role/position as job_title
5. ALWAYS extract the company/organization name as company_name
6. If company name appears in the text, extract it - NEVER leave it empty
7. Clean and normalize all data intelligently"""
```

**User Prompt** with detailed extraction rules:

```python
user_prompt = f"""WORK EXPERIENCE PARSING RULES (CRITICAL):

⚠️ COMMON PATTERNS TO FIX:

Pattern 1: "Company Name – Job Title"
Example: "JPMorgan Chase – Cloud Solutions Engineer"
→ job_title: "Cloud Solutions Engineer"
→ company_name: "JPMorgan Chase"

Pattern 2: "Job Title at Company Name"
Example: "Senior Data Engineer at DataWorks Inc."
→ job_title: "Senior Data Engineer"
→ company_name: "DataWorks Inc."

[... more patterns and rules ...]

EXPECTED JSON FORMAT:
{{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "summary": "",
  "work_history": [
    {{
      "job_title": "",
      "company_name": "",
      "start_date": "",
      "end_date": "",
      "is_current": false,
      "description": ""
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "field_of_study": "",
      "start_year": "",
      "end_year": ""
    }}
  ],
  "skills": [],
  "certifications": [],
  "projects": []
}}

Resume text to parse:
{resume_text}"""
```

**Prompt Components:**

1. **System Prompt** - Defines role and constraints
2. **Context** - Explains the hybrid parsing system
3. **Instructions** - Specific extraction rules with examples
4. **Pattern Recognition** - Common resume format patterns
5. **Expected JSON Schema** - Complete output structure
6. **Input Text** - The actual resume text

## 6. Model Processing

### How the LLM reads and processes the prompt

**LLM Processing Steps:**

1. **Tokenization**
   - Prompt is broken into tokens
   - Resume text is tokenized
   - Total tokens counted against context limit

2. **Pattern Recognition**
   - LLM identifies section headers (EXPERIENCE, EDUCATION, etc.)
   - Recognizes common resume patterns
   - Detects job title/company name relationships

3. **Entity Extraction**
   - **Skills**: Identifies technical skills, tools, technologies
   - **Experience**: Extracts job titles, companies, dates, descriptions
   - **Job Titles**: Recognizes role patterns (Engineer, Manager, Developer)
   - **Companies**: Identifies organization names
   - **Education**: Extracts degrees, institutions, dates
   - **Certifications**: Identifies professional certificates

4. **Reasoning Process**
   - Applies extraction rules from prompt
   - Handles ambiguous cases using context clues
   - Normalizes data formats (dates, locations)
   - Validates extracted entities against patterns

5. **Structured Output Generation**
   - Constructs JSON response
   - Ensures all required fields are present
   - Applies data cleaning rules
   - Validates JSON structure

**Internal Reasoning Example:**
```
Input: "Senior Data Engineer at DataWorks Inc. (2020-Present)"
Reasoning:
- "Senior Data Engineer" matches job title pattern
- "at" indicates company separator
- "DataWorks Inc." is the company name
- "(2020-Present)" contains date information
- "Present" indicates current position
Output: {
  "job_title": "Senior Data Engineer",
  "company_name": "DataWorks Inc.",
  "start_date": "2020",
  "end_date": null,
  "is_current": true
}
```

## 7. AI Response Example

### Raw response returned by the model

**Sample JSON Response:**
```json
{
  "name": "John Doe",
  "email": "john.doe@email.com",
  "phone": "(555) 123-4567",
  "location": "San Francisco, CA",
  "linkedin": "linkedin.com/in/johndoe",
  "github": "github.com/johndoe",
  "summary": "Experienced software engineer with 8+ years in full-stack development...",
  "work_history": [
    {
      "job_title": "Senior Software Engineer",
      "company_name": "Google",
      "start_date": "2020-01",
      "end_date": null,
      "is_current": true,
      "description": "Led team of 5 developers on cloud infrastructure project...",
      "location": "Mountain View, CA"
    },
    {
      "job_title": "Software Engineer",
      "company_name": "Microsoft",
      "start_date": "2017-06",
      "end_date": "2020-01",
      "is_current": false,
      "description": "Developed REST APIs using Node.js and Express...",
      "location": "Redmond, WA"
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "Stanford University",
      "field_of_study": "Computer Science",
      "start_year": "2013",
      "end_year": "2017",
      "gpa": "3.8"
    }
  ],
  "skills": [
    "JavaScript",
    "Python",
    "React",
    "Node.js",
    "AWS",
    "Docker",
    "Kubernetes",
    "PostgreSQL"
  ],
  "certifications": [
    "AWS Solutions Architect",
    "Google Cloud Professional"
  ],
  "projects": [
    {
      "name": "Cloud Migration Project",
      "description": "Led migration of monolithic application to microservices"
    }
  ],
  "extraction_quality": {
    "extraction_quality_percentage": 95,
    "missing_fields": [],
    "confidence_score": 0.92
  },
  "confidence": {
    "overall": 0.92,
    "name": 0.98,
    "email": 0.99,
    "experience": 0.90,
    "education": 0.95,
    "skills": 0.88
  }
}
```

## 8. Post-Processing

### How raw model response is validated and processed

**ParsedDataValidator** (<ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/ai-service/parsers/validator.py" lines="23-49" />) applies validation rules:

**Validation Pipeline:**
```python
def validate_and_fix(self, data: dict) -> Tuple[dict, List[str]]:
    warnings = []
    fixed_data = data.copy()
    
    fixed_data = self._fix_name(fixed_data, warnings)      # Validate name
    fixed_data = self._fix_email(fixed_data, warnings)    # Validate email
    fixed_data = self._fix_phone(fixed_data, warnings)    # Validate phone
    fixed_data = self._fix_years_experience(fixed_data, warnings)  # Fix experience
    fixed_data = self._fix_skills(fixed_data, warnings)   # Clean skills
    fixed_data = self._fix_dates(fixed_data, warnings)    # Validate dates
    
    return fixed_data, warnings
```

**Specific Validations:**

1. **Name Validation**
   - Removes emails mistakenly classified as names
   - Rejects names > 60 characters
   - Removes names containing numbers

2. **Email Validation**
   - Regex pattern matching
   - Removes invalid formats
   - Standardizes domain names

3. **Phone Validation**
   - Removes non-numeric characters
   - Validates length
   - Standardizes format

4. **Date Validation**
   - Parses various date formats
   - Validates date ranges
   - Handles "Present" values

5. **Skills Cleaning**
   - Removes duplicates
   - Standardizes formatting
   - Removes non-skill items

6. **Experience Calculation**
   - Calculates total years from work history
   - Handles overlapping dates
   - Validates date ranges

**Error Handling:**
- Missing fields are set to null
- Invalid data is removed
- Warnings are collected for review
- Confidence scores are adjusted

**Duplicate Removal:**
- Skills are deduplicated
- Companies are normalized
- Certifications are consolidated

**Data Enrichment:**
- Location geocoding
- Company domain lookup
- Skill categorization
- Industry classification

## 9. Candidate Analysis

### How candidate metrics are calculated

**Experience Calculation** (<ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/backend/src/controllers/upload.controller.ts" lines="165-200" />):

```typescript
const { total, processed } = calculateTotalExperience(workItems);
// Returns: { years: 5, months: 8, formatted_string: "5 Years 8 Months" }
```

**Skills Categorization:**
- Skills are classified as technical/non-technical
- Mapped to standard skill taxonomy
- Proficiency levels estimated from context

**Matching Score Generation:**
- Compares candidate skills against job requirements
- Calculates weighted score based on:
  - Skill match percentage
  - Experience relevance
  - Education compatibility
  - Industry alignment

**Strengths and Weaknesses:**
- **Strengths**: High-demand skills, relevant experience, strong education
- **Weaknesses**: Missing key skills, gaps in experience, outdated technologies

**Quality Scoring:**
- Extraction quality percentage (0-100)
- Confidence scores per field
- Overall confidence score

## 10. Database Storage

### Database schema and storage

**Main Tables** (<ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/backend/src/database/schema.sql" lines="150-200" />):

**candidates table:**
```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY,
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    linkedin_url TEXT,
    github_url TEXT,
    summary TEXT,
    status candidate_status,
    review_status review_status,
    total_experience_years DOUBLE PRECISION,
    email_hash VARCHAR(32),
    resume_hash VARCHAR(64),
    resume_quality_score INTEGER,
    confidence_score DOUBLE PRECISION,
    raw_resume_text TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**work_history table:**
```sql
CREATE TABLE work_history (
    id UUID PRIMARY KEY,
    candidate_id UUID REFERENCES candidates(id),
    job_title VARCHAR(255),
    company_name VARCHAR(255),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN,
    description TEXT,
    location VARCHAR(255),
    duration_string VARCHAR(100)
);
```

**education table:**
```sql
CREATE TABLE education (
    id UUID PRIMARY KEY,
    candidate_id UUID REFERENCES candidates(id),
    degree VARCHAR(255),
    institution VARCHAR(255),
    field_of_study VARCHAR(255),
    start_date DATE,
    end_date DATE,
    gpa DOUBLE PRECISION
);
```

**skills and candidate_skills tables:**
```sql
CREATE TABLE skills (
    id UUID PRIMARY KEY,
    name VARCHAR(200) UNIQUE,
    category VARCHAR(50)
);

CREATE TABLE candidate_skills (
    candidate_id UUID REFERENCES candidates(id),
    skill_id UUID REFERENCES skills(id),
    proficiency_level proficiency_level,
    PRIMARY KEY (candidate_id, skill_id)
);
```

**Example Candidate Object:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "John Doe",
  "email": "john.doe@email.com",
  "phone": "(555) 123-4567",
  "location": "San Francisco, CA",
  "total_experience_years": 5.8,
  "status": "success",
  "review_status": "pending",
  "work_history": [...],
  "education": [...],
  "skills": [...]
}
```

## 11. UI Rendering

### How parsed data is displayed in frontend

**React Component Flow** (<ref_file file="/Users/anjanyelle/Desktop/untitled folder 3/lakshya_resume_parsers/frontend/src/pages/UploadPage.tsx" lines="1-100" />):

1. **UploadPage.tsx** - Main upload interface
   - Handles file selection via dropzone
   - Manages upload state and progress
   - Displays real-time parsing progress via WebSocket
   - Shows parsed results in cards

2. **ParsedResultCard** - Displays individual candidate results
   - Shows candidate summary information
   - Displays key metrics (experience, skills count)
   - Provides action buttons (view details, edit)

3. **CandidateDetailPage** - Detailed view
   - Shows complete parsed information
   - Displays work history timeline
   - Lists education, skills, certifications
   - Provides editing capabilities

**API Response Flow:**
```
Frontend Upload → POST /api/upload
    ↓
Backend processes file → Calls AI service
    ↓
AI service returns parsed JSON
    ↓
Backend stores in PostgreSQL
    ↓
Backend returns candidate data to frontend
    ↓
Frontend displays in React components
```

**Real-time Updates:**
- WebSocket connection for progress updates
- Socket.io events: `parsing_progress`, `parsing_complete`, `parsing_failed`
- Progress bar updates during parsing
- Real-time error notifications

## 12. Existing Project Analysis

### File structure and organization

**Backend (Node.js/Express):**
```
backend/src/
├── controllers/
│   └── upload.controller.ts      # Main upload handler
├── services/
│   ├── openai-parser.service.ts  # OpenAI integration
│   └── experience.service.ts     # Experience calculation
├── middleware/
│   └── upload.middleware.ts      # File validation
├── database/
│   ├── db.ts                     # Database connection
│   └── schema.sql                # Database schema
└── utils/
    └── experienceCalculator.ts   # Experience utilities
```

**AI Service (Python/FastAPI):**
```
ai-service/
├── parsers/
│   ├── master_parser.py          # Main orchestrator
│   ├── text_extractor.py         # Text extraction
│   ├── section_splitter.py       # Section splitting
│   ├── preprocessor.py           # Text preprocessing
│   ├── llm_full_parser.py        # LLM parsing
│   ├── validator.py              # Post-processing validation
│   └── experience_extractor.py   # Experience extraction
├── prompts/
│   └── work_education_extraction_prompt.py  # Prompt templates
├── main.py                       # FastAPI application
└── resume_parser_pipeline.py     # Pipeline orchestration
```

**Frontend (React):**
```
frontend/src/
├── pages/
│   ├── UploadPage.tsx            # Upload interface
│   ├── CandidatesPage.tsx        # Candidates list
│   └── CandidateDetailPage.tsx   # Candidate details
├── components/
│   └── upload/
│       ├── ParsedResultCard.tsx  # Result display
│       └── DuplicateCandidateModal.tsx  # Duplicate handling
├── services/
│   ├── api.ts                    # API client
│   └── socket.ts                 # WebSocket client
└── utils/
    ├── experienceCalculator.ts   # Experience utilities
    └── validation.ts             # Validation utilities
```

**Recommended Placement:**

- **Preprocessing functions**: `ai-service/parsers/preprocessor.py` ✅ (already correct)
- **Prompt generation functions**: `ai-service/prompts/` ✅ (already correct)
- **Model calling functions**: `ai-service/parsers/llm_full_parser.py` ✅ (already correct)
- **Post-processing functions**: `ai-service/parsers/validator.py` ✅ (already correct)
- **Validation functions**: `ai-service/parsers/validator.py` ✅ (already correct)

## 13. Debugging Guide

### Common issues and solutions

**If skills are missing:**

1. **Check text extraction quality**
   ```python
   # Add logging in text_extractor.py
   logger.info(f"Extracted text length: {len(text)}")
   logger.info(f"Text sample: {text[:500]}")
   ```

2. **Verify section splitter identified skills section**
   ```python
   # In section_splitter.py
   sections = splitter.split_sections(text)
   logger.info(f"Found sections: {list(sections.keys())}")
   logger.info(f"Skills section: {sections.get('skills', 'NOT FOUND')}")
   ```

3. **Check LLM prompt includes skills**
   ```python
   # In llm_full_parser.py
   logger.info(f"Prompt includes skills extraction: {'skills' in user_prompt}")
   ```

4. **Verify post-processing doesn't filter skills**
   ```python
   # In validator.py
   logger.info(f"Skills before validation: {len(data.get('skills', []))}")
   logger.info(f"Skills after validation: {len(fixed_data.get('skills', []))}")
   ```

**If experience is incorrect:**

1. **Check date parsing**
   ```python
   # In experience_extractor.py
   logger.info(f"Raw dates: {start_date}, {end_date}")
   logger.info(f"Parsed dates: {parsed_start}, {parsed_end}")
   ```

2. **Verify experience calculation logic**
   ```typescript
   // In experienceCalculator.ts
   console.log("Work history items:", workItems);
   console.log("Calculated experience:", totalExperience);
   ```

3. **Check for overlapping dates**
   ```python
   # Add validation for date ranges
   if start_date > end_date:
       logger.warning(f"Invalid date range: {start_date} > {end_date}")
   ```

**If sections are not extracted:**

1. **Check section patterns**
   ```python
   # In section_splitter.py
   for line in text.split('\n'):
       for section_name, pattern in SECTION_PATTERNS.items():
           if pattern.match(line):
               logger.info(f"Matched {section_name}: {line}")
   ```

2. **Verify text preprocessing**
   ```python
   # In preprocessor.py
   logger.info(f"Text before preprocessing: {raw_text[:200]}")
   logger.info(f"Text after preprocessing: {processed_text[:200]}")
   ```

3. **Check for encoding issues**
   ```python
   # Add encoding detection
   logger.info(f"Text encoding: {detected_encoding}")
   ```

**If local works but production fails:**

1. **Check environment variables**
   ```bash
   # Verify API keys are set
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

2. **Check network connectivity**
   ```python
   # Test API connectivity
   import requests
   response = requests.get("https://api.openai.com/v1/models")
   logger.info(f"API connectivity: {response.status_code}")
   ```

3. **Verify file paths**
   ```python
   # Check if files exist
   import os
   logger.info(f"File exists: {os.path.exists(file_path)}")
   ```

4. **Check database connection**
   ```typescript
   // In db.ts
   pool.query('SELECT NOW()', (err, res) => {
     console.log("Database connection:", err ? "FAILED" : "OK");
   });
   ```

**How to identify the exact failing function:**

1. **Add comprehensive logging**
   ```python
   logger.info("=== Starting function_name ===")
   logger.info(f"Input: {input_data}")
   # ... function code ...
   logger.info(f"Output: {output_data}")
   logger.info("=== Completed function_name ===")
   ```

2. **Use try-catch blocks with specific error messages**
   ```python
   try:
       result = some_function()
   except Exception as e:
       logger.error(f"Function some_function failed: {str(e)}", exc_info=True)
       raise
   ```

3. **Add timing metrics**
   ```python
   import time
   start_time = time.time()
   result = some_function()
   logger.info(f"Function took {time.time() - start_time:.2f}s")
   ```

4. **Use request tracing**
   ```python
   request_id = generate_request_id()
   logger.info(f"[{request_id}] Starting request processing")
   # Include request_id in all log messages
   ```

## 14. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        RESUME UPLOAD                             │
│                  (React Frontend - UploadPage)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ POST /api/upload
                         │ multipart/form-data
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                          │
│                   (Express.js - upload.controller)               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  1. File Validation (validateUploadedFile)              │   │
│  │  2. Text Extraction (AI Service /preview-sections)      │   │
│  │  3. Create Candidate Record (PostgreSQL)                │   │
│  │  4. Call AI Parsing Service                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ POST /parse-resume
                         │ FormData + text
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AI SERVICE (FastAPI)                         │
│                      (main.py - endpoints)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   MASTER PARSER ORCHESTRATOR                     │
│                 (parsers/master_parser.py)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  1. Text Extraction (text_extractor.py)                  │   │
│  │     ├─ pdfplumber (Tier 1)                               │   │
│  │     ├─ AWS Textract (Tier 2)                             │   │
│  │     ├─ pymupdf (Tier 3)                                  │   │
│  │     └─ Tesseract OCR (Tier 4)                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  2. Text Preprocessing (preprocessor.py)                 │   │
│  │     ├─ Reading order reconstruction                      │   │
│  │     ├─ Bullet normalization                              │   │
│  │     ├─ Encoding fixes                                    │   │
│  │     └─ Whitespace normalization                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  3. Section Splitting (section_splitter.py)              │   │
│  │     ├─ Experience section                                │   │
│  │     ├─ Education section                                 │   │
│  │     ├─ Skills section                                    │   │
│  │     ├─ Summary section                                   │   │
│  │     └─ Projects section                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  4. Prompt Building (prompts/*.py)                       │   │
│  │     ├─ System prompt construction                        │   │
│  │     ├─ User prompt with rules                            │   │
│  │     ├─ JSON schema definition                            │   │
│  │     └─ Context injection                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  5. LLM API Call (llm_full_parser.py)                    │   │
│  │     ├─ OpenAI GPT                                        │   │
│  │     ├─ Anthropic Claude                                  │   │
│  │     ├─ Google Gemini                                     │   │
│  │     └─ DeepSeek                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  6. Model Processing                                     │   │
│  │     ├─ Tokenization                                      │   │
│  │     ├─ Pattern recognition                              │   │
│  │     ├─ Entity extraction                                │   │
│  │     ├─ Reasoning                                         │   │
│  │     └─ JSON generation                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  7. Post-Processing (validator.py)                       │   │
│  │     ├─ JSON parsing                                      │   │
│  │     ├─ Data validation                                   │   │
│  │     ├─ Error handling                                    │   │
│  │     ├─ Missing field handling                            │   │
│  │     ├─ Duplicate removal                                 │   │
│  │     ├─ Skill normalization                               │   │
│  │     └─ Experience calculation                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  8. Confidence Scoring (confidence_scorer.py)            │   │
│  │     ├─ Field-level confidence                           │   │
│  │     ├─ Overall confidence                                │   │
│  │     └─ Quality assessment                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ JSON Response
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                          │
│              (upload.controller.ts - storeAllParsedData)        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  1. Update candidates table                              │   │
│  │  2. Insert work_history records                          │   │
│  │  3. Insert education records                             │   │
│  │  4. Insert skills and candidate_skills                   │   │
│  │  5. Insert certifications                                │   │
│  │  6. Update experience metrics                            │   │
│  │  7. Calculate matching scores                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQL Transactions
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  candidates  │  │ work_history │  │  education   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    skills    │  │candidate_    │  │certification│          │
│  │              │  │   skills     │  │     s        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Query Results
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND RESPONSE                            │
│                   JSON API Response                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ WebSocket + REST
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      REACT FRONTEND                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  UploadPage.tsx - Real-time progress                     │   │
│  │  ParsedResultCard - Result display                       │   │
│  │  CandidateDetailPage - Detailed view                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 15. Code-Level Explanation

### Function-by-function breakdown

#### 1. Text Extraction

**Function:** `extract_from_pdf()`
**File:** `ai-service/parsers/text_extractor.py`
**Input:** `file_path: str, force_ocr: bool = False`
**Output:** `Dict[str, any]` with text, method_used, char_count, quality_score

**Sample Code:**
```python
def extract_from_pdf(self, file_path: str, force_ocr: bool = False) -> Dict[str, any]:
    MIN_CHAR_THRESHOLD = 200
    
    if force_ocr:
        if TEXTRACT_AVAILABLE:
            result = _textract_extractor.extract_from_pdf(file_path)
            return {
                'text': result['text'],
                'method_used': 'aws_textract',
                'char_count': result['char_count'],
                'quality_score': self._calculate_quality_score(text, len(text.split()))
            }
    
    # Try pdfplumber first
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            if len(text) > MIN_CHAR_THRESHOLD:
                return {'text': text, 'method_used': 'pdfplumber', 'char_count': len(text)}
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")
    
    # Fallback to other methods...
```

**Common Bugs:**
- Empty text from scanned PDFs (fix: use OCR)
- Text scrambling from multi-column layouts (fix: preprocessing)
- Encoding issues (fix: encoding normalization)

**Debugging Logs:**
```python
logger.info(f"Extracting text from: {file_path}")
logger.info(f"Method used: {method_used}")
logger.info(f"Character count: {char_count}")
logger.info(f"Text sample: {text[:200]}")
```

#### 2. Section Splitting

**Function:** `split_sections()`
**File:** `ai-service/parsers/section_splitter.py`
**Input:** `text: str`
**Output:** `Dict[str, str]` mapping section names to content

**Sample Code:**
```python
def split_sections(self, text: str) -> Dict[str, str]:
    sections = {'header': ''}
    lines = text.split('\n')
    current_section = 'header'
    current_content = []
    
    for line in lines:
        matched = False
        for section_name, pattern in SECTION_PATTERNS.items():
            if pattern.match(line):
                sections[current_section] = '\n'.join(current_content)
                current_section = section_name
                current_content = []
                matched = True
                break
        if not matched:
            current_content.append(line)
    
    sections[current_section] = '\n'.join(current_content)
    return sections
```

**Common Bugs:**
- Sections not detected due to unusual formatting
- False positives (regular text matched as section headers)
- Empty sections due to aggressive filtering

**Debugging Logs:**
```python
logger.info(f"Detected sections: {list(sections.keys())}")
for section_name, content in sections.items():
    logger.info(f"Section {section_name}: {len(content)} chars")
```

#### 3. Preprocessing

**Function:** `preprocess()`
**File:** `ai-service/parsers/preprocessor.py`
**Input:** `raw_text: str`
**Output:** `str` cleaned and normalized text

**Sample Code:**
```python
def preprocess(self, raw_text: str) -> str:
    if not raw_text:
        return ""
    
    text = self._reconstruct_reading_order(raw_text)
    text = self._normalize_bullets(text)
    text = self._fix_broken_lines(text)
    text = self._normalize_section_headers(text)
    text = self._fix_encoding_artifacts(text)
    text = self._normalize_whitespace(text)
    
    return text.strip()
```

**Common Bugs:**
- Over-aggressive text removal
- Breaking valid formatting
- Character encoding corruption

**Debugging Logs:**
```python
logger.info(f"Original text length: {len(raw_text)}")
logger.info(f"Processed text length: {len(text)}")
logger.info(f"Text sample before: {raw_text[:100]}")
logger.info(f"Text sample after: {text[:100]}")
```

#### 4. LLM Parsing

**Function:** `parse_resume_with_llm()`
**File:** `ai-service/parsers/llm_full_parser.py`
**Input:** `resume_text: str, llm_provider: str`
**Output:** `Optional[Dict[str, Any]]` parsed resume data

**Sample Code:**
```python
def parse_resume_with_llm(resume_text: str, llm_provider: str) -> Optional[Dict[str, Any]]:
    logger.info(f"🤖 FULL LLM PARSING - Provider: {llm_provider}")
    
    system_prompt = """You are an expert AI Resume Parser..."""
    
    user_prompt = f"""Extract structured data from this resume:
    {resume_text}
    
    Return ONLY valid JSON."""
    
    try:
        if llm_provider == "openai":
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"LLM parsing failed: {e}")
        return None
```

**Common Bugs:**
- Invalid JSON response from LLM
- Missing required fields
- Incorrect data types
- API rate limits

**Debugging Logs:**
```python
logger.info(f"Sending prompt to {llm_provider}")
logger.info(f"Prompt length: {len(user_prompt)}")
logger.info(f"Response received: {response is not None}")
logger.info(f"Parsed JSON keys: {list(result.keys()) if result else 'None'}")
```

#### 5. Post-Processing Validation

**Function:** `validate_and_fix()`
**File:** `ai-service/parsers/validator.py`
**Input:** `data: dict`
**Output:** `Tuple[dict, List[str]]` fixed data and warnings

**Sample Code:**
```python
def validate_and_fix(self, data: dict) -> Tuple[dict, List[str]]:
    warnings = []
    fixed_data = data.copy()
    
    fixed_data = self._fix_name(fixed_data, warnings)
    fixed_data = self._fix_email(fixed_data, warnings)
    fixed_data = self._fix_phone(fixed_data, warnings)
    fixed_data = self._fix_years_experience(fixed_data, warnings)
    fixed_data = self._fix_skills(fixed_data, warnings)
    fixed_data = self._fix_dates(fixed_data, warnings)
    
    fixed_data['_validation_warnings'] = warnings
    return fixed_data, warnings
```

**Common Bugs:**
- Over-aggressive data removal
- False positives in validation
- Incorrect data type conversions

**Debugging Logs:**
```python
logger.info(f"Validation warnings: {warnings}")
logger.info(f"Fields before: {list(data.keys())}")
logger.info(f"Fields after: {list(fixed_data.keys())}")
```

#### 6. Database Storage

**Function:** `storeAllParsedData()`
**File:** `backend/src/controllers/upload.controller.ts`
**Input:** `client: any, candidateId: string, ai: any, filePath?: string`
**Output:** `Promise<void>`

**Sample Code:**
```typescript
async function storeAllParsedData(client: any, candidateId: string, ai: any, filePath?: string) {
  // Update candidates table
  await client.query(
    `UPDATE candidates
     SET full_name = COALESCE($1, full_name),
         email = COALESCE($2, email),
         ...
     WHERE id = $14`,
    [ai.name, ai.email, ..., candidateId]
  );
  
  // Store work history
  for (const w of workItems) {
    await client.query(
      `INSERT INTO work_history (...) VALUES (...)`,
      [uuidv4(), candidateId, w.job_title, ...]
    );
  }
  
  // Store education, skills, certifications...
}
```

**Common Bugs:**
- Constraint violations (duplicate keys)
- Data type mismatches
- Missing required fields
- Transaction rollbacks

**Debugging Logs:**
```typescript
console.log(`✅ Candidate profile updated`);
console.log(`✅ Work history: ${workItems.length} entries stored`);
console.log(`✅ Education: ${eduItems.length} entries stored`);
console.log(`✅ Skills: ${rawSkills.length} entries stored`);
```

---

This comprehensive documentation covers the entire resume parsing pipeline from upload to database storage, with real examples from your codebase and practical debugging guidance for each component.