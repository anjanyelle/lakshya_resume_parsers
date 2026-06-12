Complete Resume Parsing Pipeline Explanation
🏗️ Architecture Overview
User Upload → Backend API → Redis Queue → Parse Worker → AI Service → Database
     ↓            ↓              ↓            ↓              ↓           ↓
  Frontend    Node.js/TS      BullMQ      TypeScript      Python     PostgreSQL
🔄 Complete Flow: Step-by-Step
PHASE 1: File Upload (Frontend → Backend)
1.1 Frontend Upload (frontend/src/pages/UploadPage.tsx)
typescript
// User selects file and LLM provider
- File: resume.docx
- LLM Provider: "gemini-2.0-flash-lite" or "own-model"
 
// Makes API call
POST /api/upload
Body: { file, llm_provider }
Technologies: React, TypeScript, Axios

1.2 Backend Upload Controller (backend/src/controllers/upload.controller.ts)
typescript
uploadResume() {
  1. Receives file upload
  2. Saves file to disk: /backend/src/uploads/[uuid]_[filename]
  3. Creates candidate record in PostgreSQL
  4. Adds parsing job to Redis queue
  5. Returns candidate_id to frontend
}
Technologies: Express.js, Multer (file upload), PostgreSQL

PHASE 2: Background Processing (Redis Queue)
2.1 Redis Queue (backend/src/workers/parseWorker.ts)
typescript
// BullMQ worker picks up job
parseQueue.process(async (job) => {
  1. Gets job data: { candidate_id, file_path, llm_provider }
  2. Calls AI service via HTTP
  3. Updates candidate status in database
  4. Emits progress via WebSocket
})
Technologies: BullMQ, Redis, Socket.IO

PHASE 3: AI Service Parsing (Python)
This is where the actual parsing happens. There are TWO MODES:

🎯 MODE 1: Full LLM Parsing (When Gemini/GPT/Claude/DeepSeek Selected)
Entry Point: ai-service/main.py
python
@app.post("/parse")
async def parse_resume(request: ParseRequest):
    # Receives: file_path, candidate_id, llm_provider
    result = master_parser.parse_file(
        file_path=request.file_path,
        candidate_id=request.candidate_id,
        llm_provider=request.llm_provider  # "gemini-2.0-flash-lite"
    )
    return result
Technologies: FastAPI, Uvicorn

Step 3.1: Master Parser (ai-service/parsers/master_parser.py)
python
class MasterParser:
    def parse_file(file_path, candidate_id, llm_provider):
        # Step 1: Extract text from file
        text = self._extract_text_from_file(file_path)
        
        # Step 2: Route to parsing pipeline
        result = self._parse_text_pipeline(
            text, 
            candidate_id, 
            llm_provider="gemini-2.0-flash-lite"
        )
        return result
Step 3.2: Text Extraction (ai-service/parsers/text_extractor.py)
python
class TextExtractor:
    def extract_text(file_path):
        if file_path.endswith('.pdf'):
            # Use PyPDF2 or pdfplumber
            return extract_from_pdf(file_path)
        
        elif file_path.endswith('.docx'):
            # Use python-docx
            doc = Document(file_path)
            text = '\n'.join([p.text for p in doc.paragraphs])
            return text
        
        elif file_path.endswith('.txt'):
            # Read plain text
            return open(file_path).read()
Technologies: PyPDF2, python-docx, pdfplumber

Step 3.3: Pipeline Router (master_parser._parse_text_pipeline())
python
def _parse_text_pipeline(text, candidate_id, llm_provider):
    
    # CHECK: Is LLM provider selected?
    if llm_provider and llm_provider != 'own-model':
        # ✅ OPTION 1: Full LLM Parsing
        return self._full_llm_parsing(text, llm_provider)
    else:
        # ⚠️ OPTION 2: Hybrid Pipeline
        return self._hybrid_parsing(text)
Step 3.4: Full LLM Parsing (ai-service/parsers/llm_full_parser.py)
python
def parse_resume_with_llm(resume_text, llm_provider):
    # Step 1: Build comprehensive prompt
    system_prompt = """You are an expert AI Resume Parser..."""
    
    user_prompt = f"""
    WORK EXPERIENCE PARSING RULES:
    - NEVER use "Duration:" as job_title
    - NEVER use locations as job_title
    - Extract actual role from "Role:" keyword
    
    Resume text: {resume_text}
    """
    
    # Step 2: Call LLM API
    if llm_provider == "gemini-2.0-flash-lite":
        result = _call_gemini(system_prompt, user_prompt)
    elif llm_provider == "deepseek-v3":
        result = _call_deepseek(system_prompt, user_prompt)
    # ... other providers
    
    # Step 3: Post-process and clean
    result = _post_process_result(result)
    
    return result  # Complete parsed resume
Key Function: _call_gemini()

python
def _call_gemini(system_prompt, user_prompt):
    import google.generativeai as genai
    
    # Configure API
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Create model with JSON response
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite",
        generation_config={"response_mime_type": "application/json"}
    )
    
    # Generate content
    response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
    
    # Parse JSON response
    result = json.loads(response.text)
    
    return result  # { name, email, skills, work_experience, ... }
Technologies: Google Generative AI SDK, OpenAI SDK, Anthropic SDK, DeepSeek API

Step 3.5: Post-Processing (llm_full_parser._post_process_result())
python
def _post_process_result(result):
    # Clean work experience
    for exp in result['work_experience']:
        # Remove invalid job titles
        if exp['job_title'] in ['Present', 'Duration:', 'Graduated:']:
            exp['job_title'] = None
        
        # Ensure is_current is boolean
        exp['is_current'] = bool(exp['is_current'])
    
    # Remove duplicate skills
    result['skills'] = list(dict.fromkeys(result['skills']))
    
    # Calculate years of experience
    result['years_of_experience'] = _calculate_years(result['work_experience'])
    
    return result
🔧 MODE 2: Hybrid Pipeline (When "Our Own Model" Selected)
Step 3.1: Section Splitting (ai-service/parsers/section_splitter.py)
python
class SectionSplitter:
    def split_sections(text):
        sections = {}
        
        # Detect section headers using regex
        patterns = {
            'experience': r'(EXPERIENCE|WORK HISTORY|EMPLOYMENT)',
            'education': r'(EDUCATION|ACADEMIC)',
            'skills': r'(SKILLS|TECHNICAL SKILLS)',
            'summary': r'(SUMMARY|OBJECTIVE)'
        }
        
        # Split text into sections
        for section_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sections[section_name] = extract_section_text(text, match)
        
        return sections
Technologies: Regular Expressions (regex)

Step 3.2: Rule-Based Parsing (ai-service/parsers/rule_parser.py)
python
class RuleBasedParser:
    def extract_email(text):
        # Regex pattern for email
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def extract_phone(text):
        # Regex pattern for phone
        pattern = r'\+?1?\d{9,15}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def extract_skills_from_dictionary(text):
        # Load 500+ skill keywords from dictionary
        skills_dict = load_skills_dictionary()
        
        # Match skills in text
        matched_skills = []
        for skill in skills_dict:
            if skill.lower() in text.lower():
                matched_skills.append(skill)
        
        return matched_skills
Technologies: Regular Expressions, Skill Dictionary (JSON)

Step 3.3: AI Entity Extraction (ai-service/parsers/ai_ner_parser.py)
python
class AINamedEntityParser:
    def __init__(self):
        # Load JobBERT model for NER
        self.model = AutoModelForTokenClassification.from_pretrained(
            "jjzha/jobbert-base-cased"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            "jjzha/jobbert-base-cased"
        )
        self.ner_pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer)
    
    def extract_entities(text):
        # Run NER on text
        entities = self.ner_pipeline(text)
        
        # Categorize entities
        result = {
            'names': [],
            'companies': [],
            'locations': [],
            'skills': [],
            'titles': []
        }
        
        for entity in entities:
            if 'PER' in entity['entity_group']:
                result['names'].append(entity['word'])
            elif 'ORG' in entity['entity_group']:
                result['companies'].append(entity['word'])
            # ... etc
        
        return result
Technologies: Transformers (Hugging Face), JobBERT model, PyTorch

Step 3.4: Experience Extraction (ai-service/parsers/experience_extractor.py)
python
class ExperienceExtractor:
    def extract_experience(sections, llm_provider=None):
        experience_text = sections.get('experience', '')
        
        if llm_provider:
            # Use LLM for experience extraction
            from parsers.llm_experience_extractor import extract_experience_with_llm
            return extract_experience_with_llm(experience_text, llm_provider)
        else:
            # Use regex-based extraction
            return self._extract_with_regex(experience_text)
    
    def _extract_with_regex(text):
        # Pattern: Company - Job Title (Dates)
        pattern = r'([A-Z][A-Za-z\s]+)\s*[-–]\s*([A-Z][A-Za-z\s]+)\s*\((\d{4})\s*-\s*(\d{4}|Present)\)'
        
        matches = re.findall(pattern, text)
        
        experiences = []
        for match in matches:
            experiences.append({
                'company_name': match[0],
                'job_title': match[1],
                'start_date': f"{match[2]}-01-01",
                'end_date': None if match[3] == 'Present' else f"{match[3]}-01-01",
                'is_current': match[3] == 'Present'
            })
        
        return experiences
Step 3.5: Education Extraction (ai-service/parsers/education_extractor.py)
python
class EducationExtractor:
    def extract_education(sections):
        education_text = sections.get('education', '')
        
        # Pattern: Degree in Field - Institution (Year)
        pattern = r'(Bachelor|Master|PhD|B\.S\.|M\.S\.)[^-]+-\s*([A-Za-z\s]+)\s*\((\d{4})\)'
        
        matches = re.findall(pattern, education_text)
        
        education = []
        for match in matches:
            education.append({
                'degree': match[0],
                'institution': match[1],
                'end_year': int(match[2])
            })
        
        return education
Step 3.6: Hybrid Merger (ai-service/parsers/hybrid_merger.py)
python
class HybridMerger:
    def merge(rule_results, ai_results, experience_results, education_results):
        merged = {}
        
        # Priority: Rule-based > AI > Default
        merged['email'] = rule_results.get('email') or ai_results.get('email')
        merged['phone'] = rule_results.get('phone') or ai_results.get('phone')
        merged['name'] = rule_results.get('name') or ai_results.get('names', [None])[0]
        
        # Merge skills (combine and deduplicate)
        rule_skills = rule_results.get('skills', [])
        ai_skills = ai_results.get('skills', [])
        merged['skills'] = list(dict.fromkeys(rule_skills + ai_skills))
        
        # Use extracted experience and education
        merged['work_experience'] = experience_results.get('experiences', [])
        merged['education'] = education_results.get('degrees', [])
        
        return merged
Step 3.7: Confidence Scoring (ai-service/parsers/confidence_scorer.py)
python
class ConfidenceScorer:
    def calculate_confidence(parsed_data):
        scores = {}
        
        # Email confidence
        if parsed_data.get('email') and '@' in parsed_data['email']:
            scores['email'] = 0.9
        else:
            scores['email'] = 0.0
        
        # Skills confidence
        if len(parsed_data.get('skills', [])) > 5:
            scores['skills'] = 1.0
        elif len(parsed_data.get('skills', [])) > 0:
            scores['skills'] = 0.7
        else:
            scores['skills'] = 0.0
        
        # Overall confidence (weighted average)
        weights = {
            'email': 0.15,
            'phone': 0.10,
            'name': 0.20,
            'skills': 0.25,
            'experience': 0.20,
            'education': 0.10
        }
        
        overall = sum(scores.get(field, 0) * weight 
                     for field, weight in weights.items())
        
        return {
            'overall': overall,
            'fields': scores,
            'quality_level': 'excellent' if overall > 0.9 else 'good' if overall > 0.7 else 'poor'
        }
Step 3.8: Quality Analysis (ai-service/parsers/text_quality_analyzer.py)
python
class TextQualityAnalyzer:
    def analyze_extraction_quality(original_text, parsed_data, sections):
        # Calculate text similarity
        reconstructed_text = self._reconstruct_text(parsed_data)
        similarity = self._calculate_similarity(original_text, reconstructed_text)
        
        # Find missing keywords
        original_keywords = extract_keywords(original_text)
        parsed_keywords = extract_keywords(reconstructed_text)
        missing_keywords = set(original_keywords) - set(parsed_keywords)
        
        # Calculate text loss
        text_loss = 100 - similarity
        
        return {
            'extraction_quality_percentage': similarity,
            'text_loss_percentage': text_loss,
            'missing_keywords': list(missing_keywords)[:20],
            'recommendation': self._get_recommendation(similarity)
        }
Technologies: TF-IDF, Cosine Similarity, NLTK

📊 Final Result Assembly
master_parser.py - Final Assembly
python
def _parse_text_pipeline(text, candidate_id, llm_provider):
    
    if llm_provider and llm_provider != 'own-model':
        # Full LLM Parsing
        llm_result = parse_resume_with_llm(text, llm_provider)
        
        # Add metadata
        llm_result['candidate_id'] = candidate_id
        llm_result['status'] = 'success'
        llm_result['confidence'] = calculate_confidence(llm_result)
        llm_result['extraction_quality'] = analyze_quality(text, llm_result)
        
        return llm_result  # ✅ Return immediately
    
    else:
        # Hybrid Pipeline
        sections = split_sections(text)
        rule_results = rule_based_parsing(text, sections)
        ai_results = ai_entity_extraction(text, sections)
        experience = extract_experience(sections)
        education = extract_education(sections)
        
        # Merge all results
        merged = hybrid_merger.merge(rule_results, ai_results, experience, education)
        
        # Add metadata
        merged['candidate_id'] = candidate_id
        merged['status'] = 'success'
        merged['confidence'] = calculate_confidence(merged)
        merged['extraction_quality'] = analyze_quality(text, merged)
        
        return merged
🔙 PHASE 4: Return to Backend
Step 4.1: Parse Worker Receives Result
typescript
// backend/src/workers/parseWorker.ts
const result = await callAIService(file_path, candidate_id, llm_provider);
 
// Update database
await db.query(`
    UPDATE candidates 
    SET 
        name = $1,
        email = $2,
        phone = $3,
        skills = $4,
        status = 'success',
        parsed_at = NOW()
    WHERE id = $5
`, [result.name, result.email, result.phone, result.skills, candidate_id]);
 
// Save work experience
for (const exp of result.work_experience) {
    await db.query(`
        INSERT INTO work_history (candidate_id, job_title, company_name, ...)
        VALUES ($1, $2, $3, ...)
    `, [candidate_id, exp.job_title, exp.company_name, ...]);
}
 
// Emit success via WebSocket
io.to(user_id).emit('parsing:complete', { candidate_id });
📱 PHASE 5: Frontend Display
Step 5.1: WebSocket Update
typescript
// frontend/src/pages/CandidatesPage.tsx
socket.on('parsing:complete', ({ candidate_id }) => {
    // Refresh candidates list
    fetchCandidates();
});
Step 5.2: Display Candidate
typescript
// Fetch candidate details
GET /api/candidates/:id
 
// Display in UI
<CandidateCard>
    <h2>{candidate.name}</h2>
    <p>{candidate.email}</p>
    <Skills>{candidate.skills.map(s => <Tag>{s}</Tag>)}</Skills>
    <WorkExperience>
        {candidate.work_experience.map(exp => (
            <div>
                <h3>{exp.job_title}</h3>
                <p>{exp.company_name}</p>
                <p>{exp.start_date} - {exp.end_date || 'Present'}</p>
            </div>
        ))}
    </WorkExperience>
</CandidateCard>
🛠️ Complete Technology Stack
Frontend
React + TypeScript
Zustand (state management)
Axios (HTTP client)
Socket.IO Client (WebSocket)
TailwindCSS (styling)
Backend
Node.js + Express.js + TypeScript
PostgreSQL (database)
Redis + BullMQ (job queue)
Socket.IO (WebSocket server)
Multer (file upload)
JWT (authentication)
AI Service
Python 3.9+
FastAPI (web framework)
Uvicorn (ASGI server)
LLM APIs:

Google Generative AI SDK (Gemini)
OpenAI SDK (GPT)
Anthropic SDK (Claude)
DeepSeek API
ML/NLP Libraries:

Transformers (Hugging Face)
PyTorch
JobBERT model
NLTK
Scikit-learn
Text Extraction:

PyPDF2 / pdfplumber (PDF)
python-docx (Word)
Utilities:

Regular Expressions
JSON
Logging
📈 Summary: Two Parsing Modes
Mode 1: Full LLM Parsing (Gemini/GPT/Claude/DeepSeek)
File → Text Extraction → LLM API Call → JSON Response → Post-Processing → Database
✅ High accuracy
✅ Handles complex formats
⚠️ Requires API key
⚠️ Costs money (or quota limits)
Mode 2: Hybrid Pipeline ("Our Own Model")
File → Text Extraction → Section Splitting → Rule-Based + AI NER → Merge → Database
✅ Free (no API costs)
✅ Fast
⚠️ Lower accuracy for complex resumes
⚠️ Needs improvement for non-standard formats
This is the complete end-to-end flow of how resume parsing works in your system! 🎉

Feedback submitted




Command Awaiting Approval







Drop to add to Cascade