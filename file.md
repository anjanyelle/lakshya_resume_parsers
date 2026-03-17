Feedback submitted




1. Resume Upload (Frontend)
   ↓
2. File Upload API (POST /api/upload)
   ↓
3. File Storage (uploads/ folder)
   ↓
4. Candidate Record Creation (PostgreSQL)
   ↓
5. Parsing Job Queue (Redis/BullMQ)
   ↓
6. Parse Worker Processing:
   a. Text Extraction (PDF/DOCX → plain text)
   b. AI Service Call (POST http://localhost:8001/parse)
      - Section Detection (experience, education, skills, etc.)
      - AI NER Parsing (names, companies, locations)
      - Rule-based Parsing (dates, emails, phones)
      - Experience Extraction (job blocks → structured data)
      - Education Extraction
      - Skills Extraction
   c. Data Merging & Validation
   d. Confidence Scoring
   ↓
7. Database Update:
   - candidates table (name, email, phone, summary)
   - skills table + candidate_skills junction
   - work_experience table
   - education table
   ↓
8. WebSocket Event Emission:
   - Event: "parsing:complete"
   - Payload: { candidateId, data: <full_parsed_json> }
   ↓
9. Frontend Reception & Display
   - UploadPage receives WebSocket event
   - Stores in currentUpload.result
   - ParsedDataDebugView renders JSON




📋 COMPLETE RESUME PARSING PIPELINE - DEEP DIVE
Let me explain each step in detail with the actual code flow, data transformations, and technical implementation.

STEP 1: Resume Upload (Frontend)
Component: UploadPage.tsx
User Action:

typescript
// User drags/drops or selects a file
<input type="file" accept=".pdf,.docx,.doc" />
What Happens:

File validation (size, type)
FormData creation with file + metadata
State management:
typescript
setUploadFiles([{
  id: uuid(),
  file: selectedFile,
  status: 'uploading',
  progress: 0
}])
STEP 2: File Upload API
Endpoint: POST /api/upload
File: backend/src/routes/upload.ts
Request Flow:

typescript
// Multer middleware processes multipart/form-data
upload.single('resume') → saves to /uploads/
 
// Request body:
{
  file: <binary_data>,
  fileName: "resume.pdf",
  tenantId: "default"
}
Response:

json
{
  "success": true,
  "candidateId": "uuid-here",
  "message": "File uploaded successfully"
}
Code Path:

typescript
router.post('/upload', upload.single('resume'), async (req, res) => {
  // 1. File saved by multer to disk
  const filePath = req.file.path;
  
  // 2. Create candidate record (Step 4)
  const candidate = await createCandidate({
    tenant_id: req.body.tenantId || 'default',
    status: 'pending'
  });
  
  // 3. Queue parsing job (Step 5)
  await parseQueue.add('parse-resume', {
    candidateId: candidate.id,
    filePath: filePath,
    fileName: req.file.originalname
  });
  
  res.json({ candidateId: candidate.id });
});
STEP 3: File Storage
Location: /backend/src/uploads/

File Naming:

{uuid}_{originalFileName}
Example: a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI.docx
Metadata Stored:

Original filename
File size
Upload timestamp
MIME type
STEP 4: Candidate Record Creation
Database: PostgreSQL
Table: candidates
SQL Insert:

sql
INSERT INTO candidates (
  id,
  tenant_id,
  status,
  created_at,
  updated_at
) VALUES (
  gen_random_uuid(),
  'default',
  'pending',
  NOW(),
  NOW()
) RETURNING *;
Initial Record:

json
{
  "id": "70817988-a32d-45fd-8f4f-5026969658da",
  "email": null,
  "full_name": null,
  "phone": null,
  "status": "pending",
  "review_status": "pending"
}
STEP 5: Parsing Job Queue
Technology: BullMQ + Redis
File: backend/src/queues/parseQueue.ts
Job Creation:

typescript
const parseQueue = new Queue('resume-parsing', {
  connection: redisConnection
});
 
await parseQueue.add('parse-resume', {
  candidateId: "70817988-...",
  filePath: "/uploads/a3475d4b_RAGHAVENDRA.docx",
  fileName: "RAGHAVENDRA_PRASAD_VEMURI.docx"
}, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 2000 }
});
Redis Storage:

Key: bull:resume-parsing:1
Value: {
  data: { candidateId, filePath, fileName },
  opts: { attempts: 3 },
  timestamp: 1710689990673
}
STEP 6: Parse Worker Processing
File: backend/src/workers/parseWorker.ts
This is the MOST COMPLEX step. Let me break it down in extreme detail:

6a. Text Extraction
Code:

typescript
const worker = new Worker('resume-parsing', async (job) => {
  const { candidateId, filePath } = job.data;
  
  // Progress: 10%
  await job.updateProgress(10);
  emitParsingProgress(userId, candidateId, 10, 'Extracting text...');
No actual extraction here - the backend delegates to AI service.

6b. AI Service Call
HTTP Request:

typescript
const response = await axios.post('http://localhost:8001/parse', {
  file_path: filePath,
  file_info: {
    filename: fileName,
    size: fileSize
  }
}, {
  timeout: 120000 // 2 minutes
});
AI Service Receives Request:

python
# ai-service/main.py
@app.post("/parse")
async def parse_resume(request: ParseRequest):
    file_path = request.file_path
    
    # Initialize master parser
    parser = MasterParser()
    
    # Parse the resume
    result = parser.parse_resume(file_path, request.file_info)
    
    return result
6b.1: MasterParser.parse_resume()
File: ai-service/parsers/master_parser.py

Complete Flow:

python
def parse_resume(self, file_path: str, file_info: Dict) -> Dict:
    """
    STEP 1: TEXT EXTRACTION
    """
    text_result = self.text_extractor.extract(file_path)
    # Returns: {
    #   'text': "RAGHAVENDRA PRASAD VEMURI\nSenior Cloud...",
    #   'method': 'python-docx',
    #   'word_count': 1425,
    #   'quality_score': 0.73
    # }
    
    text = text_result['text']
    
    """
    STEP 2: SECTION SPLITTING
    """
    sections = self.section_splitter.split_sections(text)
    # Returns: {
    #   'other': "RAGHAVENDRA PRASAD VEMURI\n...",
    #   'summary': "13+ years of IT experience...",
    #   'skills': "Cloud Platforms: AWS...\nInfrastructure as Code...",
    #   'experience': "Goldman Sachs – Senior Cloud Architect...",
    #   'education': "Master of Science – Cloud Computing...",
    #   'certifications': "AWS Certified Solutions Architect..."
    # }
    
    """
    STEP 3: RULE-BASED PARSING
    """
    rule_results = self._run_rule_parsing(text, sections)
    # Returns: {
    #   'email': 'raghav.vemuri.cloud@gmail.com',
    #   'phone': '+19725558432',
    #   'name': 'RAGHAVENDRA PRASAD VEMURI',
    #   'linkedin': 'linkedin.com/in/raghavendra-cloud',
    #   'github': 'github.com/raghav-cloud',
    #   'skills': ['AWS', 'Terraform', 'Docker', ...]
    # }
    
    """
    STEP 4: AI NER PARSING
    """
    ai_results = self._run_ai_parsing(text, sections)
    # Returns: {
    #   'name': 'RAGHAVENDRA PRASAD VEMURI',
    #   'companies': ['Goldman Sachs', 'JPMorgan Chase', ...],
    #   'locations': ['Dallas', 'Texas', 'Chicago', ...],
    #   'skills': ['AWS', 'Kubernetes', ...]
    # }
    
    """
    STEP 5: EXPERIENCE EXTRACTION
    """
    experience_results = self._extract_experience(sections, text)
    # Returns: {
    #   'work_experience': [
    #     {
    #       'job_title': 'Senior Cloud Architect',
    #       'company_name': 'Goldman Sachs',
    #       'start_date': '2020-04',
    #       'end_date': 'Present',
    #       'location': 'Dallas, TX',
    #       'description': '...',
    #       'skills_mentioned': ['AWS', 'Terraform', ...]
    #     },
    #     ...
    #   ],
    #   'job_titles': ['Senior Cloud Architect', ...]
    # }
    
    """
    STEP 6: EDUCATION EXTRACTION
    """
    education_results = self._extract_education(sections, text)
    # Returns: {
    #   'education': [
    #     {
    #       'degree': 'Master of Science',
    #       'field_of_study': 'Cloud Computing',
    #       'institution': 'University of Texas at Dallas',
    #       'start_year': 2015,
    #       'end_year': 2017
    #     },
    #     ...
    #   ]
    # }
    
    """
    STEP 7: SUMMARY EXTRACTION
    """
    summary = self._extract_summary(sections, text)
    # Returns: "13+ years of IT experience..."
    
    """
    STEP 8: HYBRID MERGING
    """
    merged_results = self.hybrid_merger.merge(
        rule_results,
        ai_results,
        experience_results,
        education_results
    )
    # Combines all results with priority rules:
    # - Rule-based priority: email, phone, linkedin, github, dates
    # - AI priority: companies, locations
    # - Union: skills (merge both sources)
    
    """
    STEP 9: CONFIDENCE SCORING
    """
    confidence = self.confidence_scorer.calculate_confidence(merged_results)
    # Returns: {
    #   'overall': 0.75,
    #   'fields': {
    #     'email': 1.0,
    #     'phone': 1.0,
    #     'name': 0.9,
    #     'skills': 0.8,
    #     'experience': 0.7
    #   },
    #   'needs_review': False,
    #   'quality_level': 'good'
    # }
    
    """
    STEP 10: FINAL ASSEMBLY
    """
    return {
        **merged_results,
        'summary': summary,
        'confidence': confidence,
        'source_info': text_result,
        'processing_metrics': metrics
    }
6b.2: Section Splitting (Deep Dive)
File: ai-service/parsers/section_splitter.py

python
def split_sections(self, text: str) -> Dict[str, str]:
    # Clean PDF artifacts
    text = self._clean_pdf_artifacts(text)
    
    # Split ALL CAPS headers merged with content
    text = re.sub(r'([a-z.!?])\s+([A-Z]{2,}(?:\s+[A-Z]{2,})+)\s*$', 
                  r'\1\n\2', text, flags=re.MULTILINE)
    
    sections = {}
    current_section = 'other'
    current_content = []
    
    for line in text.split('\n'):
        # Detect if line is a section header
        section_name = self.detect_section_header(line.strip())
        
        if section_name:
            # Save previous section
            if current_content:
                if current_section in sections:
                    sections[current_section] += '\n\n' + '\n'.join(current_content)
                else:
                    sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = section_name
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections
Header Detection Logic:

python
def detect_section_header(self, line: str) -> Optional[str]:
    # Exclude lines with colons + content (labels, not headers)
    if ':' in line and len(line.split(':', 1)[1].strip()) > 0:
        return None
    
    # Strategy 1: ALL CAPS (≤10 words)
    if line.isupper() and len(line.split()) <= 10:
        return self._match_section_keywords(line.lower())
    
    # Strategy 2: Short lines (≤6 words) matching keywords
    if len(line.split()) <= 6:
        return self._match_section_keywords(line.lower())
    
    # Strategy 3: Title Case (≤5 words)
    if line.istitle() and len(line.split()) <= 5:
        return self._match_section_keywords(line.lower())
    
    return None
6b.3: Experience Extraction (Deep Dive)
File: ai-service/parsers/experience_extractor.py

python
def extract_work_experience(self, text: str) -> Dict:
    # STEP 1: Split into job blocks
    job_blocks = self._split_into_job_blocks(text)
    # Uses date patterns to identify job boundaries
    # Example: "Apr 2020 – Present" triggers new block
    
    work_experience = []
    
    for block in job_blocks:
        job = {}
        
        # STEP 2: Extract job title
        job['job_title'] = self._extract_job_title(block)
        # Looks for patterns:
        # - "Senior Cloud Architect"
        # - "Goldman Sachs – Senior Cloud Architect"
        # - Pipe-separated: "Company | Job Title"
        
        # STEP 3: Extract company
        job['company_name'] = self._extract_company(block)
        # Patterns:
        # - "at Goldman Sachs"
        # - "Goldman Sachs –"
        # - First line before job title
        
        # STEP 4: Extract dates
        dates = self._extract_dates(block)
        job['start_date'] = dates.get('start')
        job['end_date'] = dates.get('end')
        job['duration_months'] = self._calculate_duration(dates)
        
        # STEP 5: Extract location
        job['location'] = self._extract_location(block)
        # Patterns: "Dallas, TX" | "Chicago, IL"
        
        # STEP 6: Extract description
        job['description'] = self._extract_description(block)
        # Everything after header lines
        
        # STEP 7: Extract skills mentioned
        job['skills_mentioned'] = self._extract_skills_from_description(
            job['description']
        )
        
        work_experience.append(job)
    
    return {
        'work_experience': work_experience,
        'job_titles': [j['job_title'] for j in work_experience]
    }
6c. Data Merging & Validation
Back in parseWorker.ts:

typescript
// AI service returns parsed data
const parsedData = response.data;
 
// Validate and clean
const validatedData = {
  email: validateEmail(parsedData.email),
  phone: validatePhone(parsedData.phone),
  full_name: parsedData.name?.trim() || null,
  summary: parsedData.summary?.substring(0, 1000) || null,
  work_experience: parsedData.work_experience || [],
  education: parsedData.education || [],
  skills: parsedData.skills || []
};
6d. Confidence Scoring
File: ai-service/parsers/confidence_scorer.py

python
def calculate_confidence(self, parsed_data: Dict) -> Dict:
    field_scores = {}
    
    # Email confidence
    if parsed_data.get('email'):
        domain = parsed_data['email'].split('@')[-1]
        if domain in PROFESSIONAL_DOMAINS:
            field_scores['email'] = 1.0
        else:
            field_scores['email'] = 0.7
    else:
        field_scores['email'] = 0.0
    
    # Name confidence
    name = parsed_data.get('name', '')
    if len(name.split()) >= 2:
        field_scores['name'] = 0.9
    elif len(name) > 0:
        field_scores['name'] = 0.5
    else:
        field_scores['name'] = 0.0
    
    # Experience confidence
    exp_count = len(parsed_data.get('work_experience', []))
    if exp_count >= 3:
        field_scores['experience'] = 0.9
    elif exp_count >= 1:
        field_scores['experience'] = 0.7
    else:
        field_scores['experience'] = 0.0
    
    # Overall confidence (weighted average)
    overall = sum(
        field_scores[field] * FIELD_WEIGHTS[field]
        for field in field_scores
    )
    
    return {
        'overall': overall,
        'fields': field_scores,
        'needs_review': overall < 0.6,
        'quality_level': self._get_quality_level(overall)
    }
STEP 7: Database Update
File: backend/src/workers/parseWorker.ts
typescript
// Update candidate record
await db.query(`
  UPDATE candidates SET
    email = $1,
    full_name = $2,
    phone = $3,
    summary = $4,
    location = $5,
    linkedin_url = $6,
    github_url = $7,
    years_experience = $8,
    status = 'completed',
    updated_at = NOW()
  WHERE id = $9
`, [
  validatedData.email,
  validatedData.full_name,
  validatedData.phone,
  validatedData.summary,
  validatedData.location,
  validatedData.linkedin,
  validatedData.github,
  validatedData.years_of_experience,
  candidateId
]);
 
// Insert work experience
for (const exp of validatedData.work_experience) {
  await db.query(`
    INSERT INTO work_experience (
      candidate_id, job_title, company_name,
      start_date, end_date, location, description
    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
  `, [
    candidateId,
    exp.job_title,
    exp.company_name,
    exp.start_date,
    exp.end_date,
    exp.location,
    exp.description
  ]);
}
 
// Insert education
for (const edu of validatedData.education) {
  await db.query(`
    INSERT INTO education (
      candidate_id, degree, field_of_study,
      institution, start_date, end_date
    ) VALUES ($1, $2, $3, $4, $5, $6)
  `, [...]);
}
 
// Insert skills
for (const skill of validatedData.skills) {
  // Check if skill exists
  let skillId = await getOrCreateSkill(skill);
  
  // Link to candidate
  await db.query(`
    INSERT INTO candidate_skills (candidate_id, skill_id)
    VALUES ($1, $2)
    ON CONFLICT DO NOTHING
  `, [candidateId, skillId]);
}
STEP 8: WebSocket Event Emission
File: backend/src/socket.ts
typescript
export const emitParsingComplete = (
  userId: string,
  data: ParsingCompleteEvent
) => {
  if (io) {
    io.to(`user:${userId}`).emit("parsing:complete", {
      candidateId: data.candidateId,
      data: data.data
    });
    
    console.log(`✅ Emitted parsing complete to user ${userId}`);
  }
};
WebSocket Payload:

json
{
  "event": "parsing:complete",
  "data": {
    "candidateId": "70817988-a32d-45fd-8f4f-5026969658da",
    "data": {
      "name": "RAGHAVENDRA PRASAD VEMURI",
      "email": "raghav.vemuri.cloud@gmail.com",
      "phone": "+19725558432",
      "skills": [...],
      "work_experience": [...],
      "education": [...],
      "confidence": {...}
    }
  }
}
STEP 9: Frontend Reception & Display
File: frontend/src/pages/UploadPage.tsx
typescript
useEffect(() => {
  if (!socket) return;
  
  // Subscribe to parsing events
  socket.on("parsing:complete", (data: ParsingCompleteEvent) => {
    console.log("✅ Parsing complete:", data);
    
    // Update upload files state
    setUploadFiles((prev) =>
      prev.map((uploadFile) => {
        if (uploadFile.candidateId === data.candidateId) {
          return {
            ...uploadFile,
            status: "completed",
            progress: 100,
            message: "Complete!",
            result: data.data  // ← FULL PARSED JSON STORED HERE
          };
        }
        return uploadFile;
      })
    );
    
    // Update current upload
    setCurrentUpload((prev) => {
      if (prev?.candidateId === data.candidateId) {
        return {
          ...prev,
          status: "completed",
          result: data.data
        };
      }
      return prev;
    });
    
    toast.success("Resume parsing completed!");
  });
  
  return () => {
    socket.off("parsing:complete");
  };
}, [socket]);
Render:

tsx
{currentUpload?.status === "completed" && currentUpload.result && (
  <ParsedDataDebugView data={currentUpload.result} />
)}
COMPLETE DATA FLOW EXAMPLE
Input: RAGHAVENDRA_PRASAD_VEMURI.docx

Output at each stage:

Upload: File saved to /uploads/a3475d4b_RAGHAVENDRA.docx
DB: Candidate record created with id: 70817988...
Queue: Job added to Redis
AI Service: Text extracted (11,411 chars)
Sections: 7 sections detected
Parsing: All fields extracted
DB Update: 3 work experiences, 2 education records, 65 skills
WebSocket: Event emitted to frontend
Display: JSON rendered in debug view
Total Processing Time: ~9.2 seconds (from your metrics)

Text extraction: 23ms
Section splitting: 21ms
Rule parsing: 41ms
AI parsing: 9,073ms ← Slowest (AI model inference)
Experience extraction: 70ms
Merging: 0.5ms
This is the complete end-to-end flow! 🚀

Feedback submitted




Command Awaiting Approval







Drop to add to Cascade