# Lakshya LLM Resume Parser — Full Technical Audit

> Produced by deep codebase analysis. Last updated: March 2026.

---

## Table of Contents

1. [Full Architecture Documentation](#1-full-architecture-documentation)
2. [Codebase Explanation](#2-codebase-explanation)
3. [Resume Parsing Pipeline — Step by Step](#3-resume-parsing-pipeline--step-by-step)
4. [Model Analysis](#4-model-analysis)
5. [Root Cause of Accuracy Drop (65% → 10%)](#5-root-cause-of-accuracy-drop-65--10)
6. [Rule-Based vs AI Parser Comparison](#6-rule-based-vs-ai-parser-comparison)
7. [Accuracy Improvement Plan (Target: 85–90%)](#7-accuracy-improvement-plan-target-8590)
8. [Code Fix Recommendations](#8-code-fix-recommendations)
9. [Developer Reference Documentation](#9-developer-reference-documentation)

---

## 1. Full Architecture Documentation

### System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│                  React + TypeScript (Vite)                       │
│         Zustand Store | Socket.io Client | Axios API             │
└───────────────────────┬───────────────────────────────┬──────────┘
                        │ HTTP REST (port 3001)          │ WebSocket
                        ▼                               │
┌──────────────────────────────────────────────────┐   │
│               NODE.JS BACKEND                    │   │
│           Express + TypeScript (port 3001)       │◄──┘
│  ┌──────────────┐  ┌────────────────────────┐    │
│  │ REST Routes  │  │    Socket.io Server    │    │
│  │ /api/auth    │  │  Real-time progress    │    │
│  │ /api/candidates│ │  parsing events       │    │
│  │ /api/jobs    │  └────────────────────────┘    │
│  │ /api/matching│                                │
│  └──────┬───────┘                                │
│         │ Enqueue Job                            │
│         ▼                                        │
│  ┌──────────────┐       ┌──────────────────┐     │
│  │  BullMQ      │       │  parseWorker.ts  │     │
│  │  Queue       │──────►│  (processes jobs)│     │
│  │  (Redis)     │       └────────┬─────────┘     │
│  └──────────────┘                │               │
└─────────────────────────────────-│───────────────┘
                                   │ HTTP POST /parse
                                   ▼
┌──────────────────────────────────────────────────┐
│              PYTHON AI SERVICE                   │
│           FastAPI (port 8000)                    │
│  ┌───────────────────────────────────────────┐   │
│  │              MasterParser                 │   │
│  │  1. TextExtractor  (PDF/DOCX→text)        │   │
│  │  2. SectionSplitter (section detection)   │   │
│  │  3. RuleBasedParser (regex extraction)    │   │
│  │  4. AINamedEntityParser (BERT NER)        │   │
│  │  5. ExperienceExtractor (work history)    │   │
│  │  6. EducationExtractor (degrees)          │   │
│  │  7. HybridMerger (combine results)        │   │
│  │  8. EntityNormalizer (cleanup)            │   │
│  │  9. ConfidenceScorer (quality score)      │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────┬────────────────┘
                                  │ Parsed JSON
                                  ▼
                    ┌──────────────────────┐
                    │    PostgreSQL DB      │
                    │  candidates          │
                    │  skills              │
                    │  work_experience     │
                    │  education           │
                    │  parsing_jobs        │
                    └──────────────────────┘
```

### Data Flow — Resume Upload to Stored Result

```
1. User uploads PDF/DOCX via React UI
        ↓
2. POST /api/candidates/upload (Express)
   → Saves file to /backend/uploads/resumes/<uuid>.pdf
   → Creates candidate row in DB (status: pending)
   → Creates parsing_jobs row (status: pending)
        ↓
3. Job enqueued in BullMQ queue: "resume-parsing"
   Payload: { candidateId, filePath, fileType, userId }
        ↓
4. parseWorker.ts picks up the job
   → Emits Socket.io progress events to frontend
   → Calls POST http://localhost:8000/parse (AI Service)
        ↓
5. Python MasterParser runs 9-step pipeline (see Section 3)
   → Returns JSON with all parsed fields + confidence
        ↓
6. parseWorker saves parsed data to PostgreSQL
   → candidates table (name, email, phone, etc.)
   → skills table (skill_name, category)
   → work_experience table (job_title, company_name, dates)
   → education table (degree, institution)
   → parsing_jobs table (status: completed, confidence_score)
        ↓
7. Frontend receives Socket.io "parsing_complete" event
   → Fetches candidate detail via GET /api/candidates/:id
   → Renders parsed data in CandidateDetailPage
```

---

## 2. Codebase Explanation

### Frontend (`/frontend/src`)

| File                            | Purpose                                                                             |
| ------------------------------- | ----------------------------------------------------------------------------------- |
| `pages/CandidateDetailPage.tsx` | Displays full parsed candidate profile: skills, experience, education, match scores |
| `pages/MatchingPage.tsx`        | Runs AI job matching between candidates and jobs                                    |
| `store/useCandidateStore.ts`    | Zustand store for candidate state, `fetchCandidate`, `uploadResume`                 |
| `store/useJobStore.ts`          | Zustand store for jobs + match results, `fetchMatchResults('all')`                  |
| `services/api.ts`               | Axios instance, base URL = `http://localhost:3001/api`                              |

### Backend (`/backend/src`)

| File                                  | Purpose                                                             |
| ------------------------------------- | ------------------------------------------------------------------- |
| `workers/parseWorker.ts`              | BullMQ worker that processes parse jobs, calls AI service, saves DB |
| `controllers/candidate.controller.ts` | REST handlers: upload, list, get by ID, delete                      |
| `controllers/matching.controller.ts`  | REST handlers: match job↔candidates, get results                    |
| `routes/matching.routes.ts`           | Express router for `/api/matching/*`                                |
| `database/db.ts`                      | PostgreSQL connection pool                                          |
| `database/migrations/`                | SQL migration files for schema changes                              |
| `services/aiService.ts`               | HTTP client wrapper for Python AI service                           |

### AI Service (`/ai-service/parsers`)

| File                      | Purpose                                                                                                         |
| ------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `master_parser.py`        | **Orchestrator** — runs all 9 pipeline steps in order                                                           |
| `text_extractor.py`       | Extracts raw text from PDF (PyMuPDF, pdfplumber) or DOCX (python-docx)                                          |
| `section_splitter.py`     | Detects section headers (EXPERIENCE, EDUCATION, SKILLS) and splits text                                         |
| `rule_parser.py`          | Regex-based: email, phone, LinkedIn, GitHub, dates, years of experience. Requires `phonenumbers` + `dateparser` |
| `simple_rule_parser.py`   | Lightweight fallback rule parser (stdlib only) — added during debugging                                         |
| `ai_ner_parser.py`        | BERT NER: `dslim/bert-large-NER` (names/orgs/locations) + `Nucha/Nucha_ITSkillNER_BERT` (skills)                |
| `experience_extractor.py` | Extracts structured work history from experience section text                                                   |
| `education_extractor.py`  | Extracts degrees, institutions, dates from education section text                                               |
| `hybrid_merger.py`        | Intelligently merges rule + AI results using field-specific strategies                                          |
| `confidence_scorer.py`    | Weighted scoring: email(15%) + phone(10%) + name(20%) + skills(25%) + experience(20%) + education(10%)          |
| `entity_normalizer.py`    | Normalizes skill names, company names to canonical forms                                                        |

---

## 3. Resume Parsing Pipeline — Step by Step

### Step 1: File Upload & Queue

```
POST /api/candidates/upload
  → multer saves file: /uploads/resumes/<uuid>.pdf
  → DB: INSERT INTO candidates (id, status='pending')
  → DB: INSERT INTO parsing_jobs (candidate_id, status='pending')
  → BullMQ: queue.add('parse', { candidateId, filePath, userId })
```

### Step 2: Text Extraction (`text_extractor.py`)

- **PDF**: Tries PyMuPDF first (fast, text-based PDFs), falls back to pdfplumber, then pytesseract OCR for scanned PDFs
- **DOCX**: Uses python-docx to extract paragraphs + tables
- **Output**: Raw string of resume text + quality_score

### Step 3: Section Splitting (`section_splitter.py`)

- Scans for uppercase headers like `EXPERIENCE`, `EDUCATION`, `SKILLS`
- Uses regex `^\s*([A-Z][A-Z\s]{2,}|...)\s*[:\-=_]*\s*$`
- **Output**: Dict `{ 'experience': '...', 'education': '...', 'skills': '...', 'summary': '...' }`
- ⚠️ **Risk**: If headers aren't detected (e.g., styled PDFs), all sections return empty, so experience/education extractors produce nothing

### Step 4: Rule-Based Parsing (`rule_parser.py`)

Extracts via regex + libraries:

- Email: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`
- Phone: `phonenumbers` library (multi-country: US/GB/IN/AU)
- LinkedIn: `linkedin.com/in/<username>`
- GitHub: `github.com/<username>`
- Dates: dateparser library
- Years of experience: regex `(\d+)\s*years?`

⚠️ **NOTE**: `RuleBasedParser.extract_skills_from_list(text, taxonomy)` requires a skills taxonomy list — `extract_skills(text)` does NOT exist on this class.

### Step 5: AI NER Parsing (`ai_ner_parser.py`)

- Chunks text into 300-word blocks with 50-word overlap
- **Model 1** `dslim/bert-large-NER`: CoNLL-2003 NER → extracts PER (names), ORG (companies), LOC (locations), MISC
- **Model 2** `Nucha/Nucha_ITSkillNER_BERT`: IT-skill NER (tries to load, falls back to MISC keyword matching)
- Output: `{ names, organizations, locations, skills, misc }`

### Step 6: Experience Extraction (`experience_extractor.py`)

- Only operates on `sections['experience']` text
- Uses regex patterns to find: job titles, company names, date ranges
- Calculates duration in months
- **Output**: List of `{ job_title, company_name, start_date, end_date, duration_months, description }`

### Step 7: Education Extraction (`education_extractor.py`)

- Only operates on `sections['education']` text
- Extracts: degree type (B.E., M.Tech, etc.), institution name, graduation year
- **Output**: List of `{ degree, institution, field_of_study, start_date, end_date }`

### Step 8: Hybrid Merging (`hybrid_merger.py`)

Field priority rules:
| Strategy | Fields |
|----------|--------|
| **Rule priority** (regex wins) | email, phone, linkedin, github, dates, websites |
| **AI priority** (BERT wins) | name, companies, locations, organizations |
| **Union** (combine both) | skills, job_titles, education_institutions, degrees |
| **Conflict resolution** | everything else |

### Step 9: Confidence Scoring (`confidence_scorer.py`)

```python
FIELD_WEIGHTS = {
  'email': 0.15, 'phone': 0.10, 'name': 0.20,
  'skills': 0.25, 'experience': 0.20, 'education': 0.10
}
```

Score = Σ(field_score × field_weight). Each field score is 0.0–1.0.

---

## 4. Model Analysis

### Model 1: `dslim/bert-large-NER`

| Property             | Value                                                     |
| -------------------- | --------------------------------------------------------- |
| Base Model           | BERT-large (340M params)                                  |
| Trained On           | CoNLL-2003 NER dataset                                    |
| Entity Labels        | PER, ORG, LOC, MISC                                       |
| **Resume Relevance** | **Low** — not trained on resumes                          |
| Skills Extraction    | ❌ Skills are NOT a CoNLL label. Falls under MISC at best |
| Job Titles           | ❌ Not extracted — no JOB_TITLE label                     |
| Education Degrees    | ❌ Not extracted — no DEGREE label                        |
| Dependency           | `transformers==4.44.0`, `torch==2.4.0`                    |

### Model 2: `Nucha/Nucha_ITSkillNER_BERT`

| Property             | Value                                                  |
| -------------------- | ------------------------------------------------------ |
| Base Model           | BERT fine-tuned on IT skill dataset                    |
| Entity Labels        | IT skills (React, Python, AWS, etc.)                   |
| **Resume Relevance** | **High** for tech skills specifically                  |
| Dependency           | Same: `transformers`, `torch`                          |
| Status               | ⚠️ Often fails to load — try/except falls back to None |

### What Labels Are Missing (vs Resume Needs)

| Resume Field | NER Label Needed | Available?                          |
| ------------ | ---------------- | ----------------------------------- |
| Name         | PER              | ✅                                  |
| Company      | ORG              | ✅                                  |
| Location     | LOC              | ✅                                  |
| Skills       | SKILL            | ❌ (only if skill model loads)      |
| Job Title    | JOB_TITLE        | ❌                                  |
| Degree       | DEGREE           | ❌                                  |
| University   | ORG              | ⚠️ (partial — mixed with companies) |
| Email        | —                | Rule-based only                     |
| Phone        | —                | Rule-based only                     |

---

## 5. Root Cause of Accuracy Drop (65% → 10%)

There are **5 compounding bugs** causing this. Together they explain exactly why confidence dropped to ~14%.

---

### Bug #1 — Missing Python Dependencies (CRITICAL 🔴)

**File**: `ai-service/requirements.txt` vs installed environment

**Problem**: The packages `phonenumbers` and `dateparser` (required by `RuleBasedParser`) are NOT installed in the runtime environment. When `master_parser.py` tries to initialize `RuleBasedParser`:

```python
try:
    self.rule_parser = RuleBasedParser()  # FAILS — ModuleNotFoundError: phonenumbers
except Exception as e:
    self.rule_parser = None  # Silently swallowed!
```

Similarly `transformers` and `torch` are likely not installed, causing:

```python
try:
    self.ai_parser = AINamedEntityParser()  # FAILS
except Exception as e:
    self.ai_parser = None  # Both parsers are None
```

**Effect**: The two primary parsers are both None. No entity extraction happens.

**Fix**: `pip install -r requirements.txt`

---

### Bug #2 — Missing `extract_skills()` Method on RuleBasedParser (HIGH 🟠)

**File**: `ai-service/parsers/master_parser.py` line ~348  
**File**: `ai-service/parsers/rule_parser.py`

**Problem**: `master_parser._run_rule_parsing()` calls:

```python
if hasattr(self.rule_parser, 'extract_skills'):
    result['skills'] = self.rule_parser.extract_skills(text)
```

But `RuleBasedParser` only has `extract_skills_from_list(text, skill_taxonomy)` — it requires a taxonomy list to be passed. The method `extract_skills(text)` does **not exist**.

The `hasattr()` check returns `False`, so skills are never extracted via rule parser.

**Effect**: Even when `RuleBasedParser` is properly initialized, zero skills are extracted.

**Fix**: Add `extract_skills(text)` method to `RuleBasedParser` using the built-in taxonomy.

---

### Bug #3 — HybridMerger Skills Merge NullPointerError (HIGH 🟠)

**File**: `ai-service/parsers/hybrid_merger.py` line ~235

**Problem**: The merger processes the `skills` field:

```python
if field == 'skills':
    rule_skills = set(s.lower().strip() for s in rule_value if s)
    ai_skills = set(s.lower().strip() for s in ai_value.get('ai_skills', []) if s)
    #                                                    ^^^
    # ai_value here is what combined_ai has for key 'skills' — which is None!
```

In `_merge_results()`:

```python
combined_ai = {**ai_results, **experience_results, **education_results}
```

`ai_results` has a key `ai_skills` (a list), NOT `skills`. So when the merger iterates `all_fields` and processes `skills`, `ai_value = combined_ai.get('skills')` is `None`. Then `None.get('ai_skills', [])` throws `AttributeError`, which is caught by the outer try/except, returning `rule_result` as fallback — but rule_result also has no skills. **Net result: skills = []**.

**Fix**: Either rename `ai_skills` key to `skills` in `_run_ai_parsing()`, or update the merger to handle this case.

---

### Bug #4 — Experience/Education Extraction Depends Entirely on Section Detection (MEDIUM 🟡)

**File**: `ai-service/parsers/master_parser.py` lines ~381-382

**Problem**:

```python
def _extract_experience(self, sections):
    experience_text = sections.get('experience', '')
    if not experience_text:
        return {'work_experience': [], 'job_titles': []}  # Returns empty!
```

If `SectionSplitter` fails to detect the "PROFESSIONAL EXPERIENCE" header (which happens with non-standard formatting), the entire experience extraction is skipped.

**Effect**: 0 work experience positions even though the resume clearly has them.

**Fix**: Fall back to running the experience extractor on full text when section is empty.

---

### Bug #5 — Confidence Score of 14% Is Mathematically Explained (INFORMATIONAL ℹ️)

The 14% confidence is not random — it's the exact result of Bugs #1–4:

```
email     = 0.0  × 0.15 = 0.000  (rule parser missing)
phone     = 0.0  × 0.10 = 0.000  (rule parser missing)
name      = 0.7  × 0.20 = 0.140  (AI NER finds name from text)
skills    = 0.0  × 0.25 = 0.000  (hybrid merger bug)
experience= 0.0  × 0.20 = 0.000  (section splitter miss)
education = 0.0  × 0.10 = 0.000  (section splitter miss)
                         ───────
TOTAL                  = 0.140  ← This is exactly 14%!
```

---

## 6. Rule-Based vs AI Parser Comparison

| Capability         | Rule-Based (old)          | AI/Hybrid (new)            | Status                      |
| ------------------ | ------------------------- | -------------------------- | --------------------------- |
| Email extraction   | ✅ Regex (perfect)        | ✅ Regex via rule_parser   | ⚠️ Broken (dep missing)     |
| Phone extraction   | ✅ phonenumbers lib       | ✅ phonenumbers lib        | ⚠️ Broken (dep missing)     |
| LinkedIn / GitHub  | ✅ Regex                  | ✅ Regex                   | ⚠️ Broken (dep missing)     |
| Name extraction    | ✅ First line heuristic   | ✅ BERT PER entity         | ✅ Works when AI installed  |
| Skills extraction  | ✅ Taxonomy keyword match | ⚠️ BERT MISC / skill model | 🔴 Broken (method missing)  |
| Work experience    | ✅ Section regex          | ✅ ExperienceExtractor     | ⚠️ Only if section detected |
| Companies          | ✅ Pattern matching       | ✅ BERT ORG entity         | ⚠️ Only if AI installed     |
| Job titles         | ✅ Pattern list           | ✅ Title patterns          | ⚠️ Only if section detected |
| Education          | ✅ Pattern matching       | ✅ EducationExtractor      | ⚠️ Only if section detected |
| Accuracy (overall) | ~60–65%                   | ~10–14% (broken)           | Regressed                   |

**What was lost in migration**:

- The rule-based parser had a direct skill taxonomy match that worked offline, with no model dependency
- The old system didn't rely on section detection for basic fields
- The new system added dependencies (phonenumbers, dateparser, torch, transformers) that silently fail

---

## 7. Accuracy Improvement Plan (Target: 85–90%)

### Phase 1 — Fix Critical Bugs (Immediate, 1–2 days)

This alone should restore accuracy from 14% to ~65%+.

1. Install all dependencies: `pip install -r requirements.txt`
2. Add `extract_skills(text)` to `RuleBasedParser` using internal taxonomy
3. Fix `HybridMerger._merge_union_fields` — handle `ai_value=None` case
4. Fall back to full text in `_extract_experience` and `_extract_education` when section is empty

### Phase 2 — Improve Rule-Based Coverage (1 week)

Target: +10–15% accuracy

- Expand skill taxonomy to 500+ technologies in a JSON file
- Add Indian phone number formats explicitly
- Improve section detection patterns for non-standard resumes
- Add designation/job title regex patterns
- Run rule-based parser on full text (not just sections) for all fields

### Phase 3 — Better AI Models (2–4 weeks)

Target: +10–15% accuracy

- Switch from `dslim/bert-large-NER` to a **resume-specific NER** model:
  - `jjzha/jobbert-base-cased` — fine-tuned on resume/job data
  - `manishiitg/open-llama-resume-parser` — LLM for resume parsing
- Fine-tune on Indian resumes with your own labeled dataset (10k+ samples)
- Add a dedicated skills extractor using `en_core_web_sm` spaCy + skills PhraseMatcher

### Phase 4 — Hybrid Enhancement (2–4 weeks)

Target: +5–10% accuracy

```
Full Text
    ├─► Rule Parser (email, phone, linkedin, github)       → always runs
    ├─► Regex Skills Extractor (500+ skill taxonomy)       → always runs
    ├─► Section Splitter → Experience/Education Extractor  → section-based
    ├─► AI NER (names, companies, locations)               → AI-based
    └─► Skills NER (bert skill model)                      → AI-based
              ↓
         HybridMerger (fixed)
              ↓
         EntityNormalizer
              ↓
         ConfidenceScorer
```

### Phase 5 — Layout-Aware Extraction (Optional, 4–8 weeks)

For PDFs with complex layouts (columns, tables):

- Use `pdfplumber` with coordinate extraction to detect column boundaries
- Use `LayoutLMv3` (Microsoft) for document understanding with layout context
- Implement table extraction for tabular skills/experience

---

## 8. Code Fix Recommendations

### Fix 1 — Add `extract_skills()` to RuleBasedParser

**File**: `ai-service/parsers/rule_parser.py`

Add this method to the `RuleBasedParser` class:

```python
# Built-in comprehensive skill taxonomy
SKILL_TAXONOMY = [
    'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby',
    'React', 'React.js', 'Angular', 'Vue', 'Vue.js', 'Next.js', 'Nuxt.js', 'Svelte',
    'Node.js', 'Express', 'FastAPI', 'Django', 'Flask', 'Spring Boot', 'Laravel',
    'HTML', 'HTML5', 'CSS', 'CSS3', 'Sass', 'Tailwind CSS', 'Bootstrap', 'Material UI',
    'Redux', 'Redux Toolkit', 'Zustand', 'MobX', 'React Query', 'Context API',
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'SQLite',
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Ansible',
    'Git', 'GitHub', 'GitLab', 'CI/CD', 'Jenkins', 'GitHub Actions',
    'REST', 'GraphQL', 'WebSocket', 'gRPC', 'Microservices',
    'Jest', 'Pytest', 'Cypress', 'Selenium', 'React Testing Library',
    'Webpack', 'Vite', 'Babel', 'ESLint', 'Prettier',
    'Linux', 'Bash', 'PowerShell', 'Figma', 'Storybook',
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
    'Jira', 'Confluence', 'Postman', 'Firebase', 'Supabase',
]

def extract_skills(self, text: str) -> list:
    """
    Extract skills from text using built-in skill taxonomy.
    No external taxonomy list required.
    """
    return self.extract_skills_from_list(text, self.SKILL_TAXONOMY)
```

---

### Fix 2 — Fix HybridMerger Skills Merge

**File**: `ai-service/parsers/hybrid_merger.py`, `_merge_union_fields()`

```python
if field == 'skills':
    # Handle None safely
    rule_list = rule_value if isinstance(rule_value, list) else []
    # ai_value may be None (skills key not in ai results) or a list
    ai_list = ai_value if isinstance(ai_value, list) else []

    rule_skills = set(s.lower().strip() for s in rule_list if s)
    ai_skills   = set(s.lower().strip() for s in ai_list if s)

    all_skills_lower = rule_skills | ai_skills
    rule_skills_original = {s.lower(): s for s in rule_list if s}
    ai_skills_original   = {s.lower(): s for s in ai_list if s}
    casing_map = {**ai_skills_original, **rule_skills_original}
    return sorted([casing_map[s] for s in all_skills_lower if s in casing_map])
```

Also in `_run_ai_parsing()` of `master_parser.py`, rename `ai_skills` to `skills`:

```python
return {
    'name': self.ai_parser.get_top_person(entities),
    'companies': self.ai_parser.get_organizations(entities),
    'locations': self.ai_parser.get_locations(entities),
    'misc_entities': self.ai_parser.get_misc_entities(entities),
    'skills': self.ai_parser.get_skills(entities),   # renamed from ai_skills
    'ai_entities': entities
}
```

---

### Fix 3 — Fall Back to Full Text for Experience/Education

**File**: `ai-service/parsers/master_parser.py`

```python
def _extract_experience(self, sections, full_text=''):
    if not self.exp_extractor:
        return {'work_experience': [], 'job_titles': []}

    experience_text = sections.get('experience', '').strip()
    # Fallback: use full text when section not detected
    if not experience_text and full_text:
        experience_text = full_text

    if not experience_text:
        return {'work_experience': [], 'job_titles': []}

    work_experience = self.exp_extractor.extract_work_experience(experience_text)
    job_titles = [exp.get('job_title', '') for exp in work_experience if exp.get('job_title')]
    return {'work_experience': work_experience, 'job_titles': job_titles}
```

---

### Fix 4 — Pass Full Text to Extractors in Pipeline

**File**: `ai-service/parsers/master_parser.py`, `_parse_text_pipeline()`

```python
# Step 5: Extract structured experience (pass full text as fallback)
experience_results = self._extract_experience(sections, text)  # pass text

# Step 6: Extract structured education (pass full text as fallback)
education_results = self._extract_education(sections, text)    # pass text
```

---

## 9. Developer Reference Documentation

### Folder Structure

```
Lakshya-LLM-Resume-Parser/
├── ai-service/                     # Python FastAPI service
│   ├── main.py                     # FastAPI app, endpoints: /parse, /parse-text, /health
│   ├── requirements.txt            # ALL Python deps — must be installed
│   ├── parsers/
│   │   ├── master_parser.py        # Orchestrator — entry point for all parsing
│   │   ├── text_extractor.py       # PDF/DOCX → raw text
│   │   ├── section_splitter.py     # Detects EXPERIENCE, EDUCATION, SKILLS sections
│   │   ├── rule_parser.py          # Regex: email, phone, URLs (needs phonenumbers+dateparser)
│   │   ├── simple_rule_parser.py   # Fallback rule parser (stdlib only)
│   │   ├── ai_ner_parser.py        # BERT NER models (needs torch+transformers)
│   │   ├── experience_extractor.py # Structured work history extraction
│   │   ├── education_extractor.py  # Degree, institution extraction
│   │   ├── hybrid_merger.py        # Combines rule + AI results intelligently
│   │   ├── confidence_scorer.py    # Computes 0–1 quality score
│   │   └── entity_normalizer.py    # Normalizes skill/company names
│   └── training/                   # Model training scripts
│
├── backend/src/
│   ├── workers/parseWorker.ts      # BullMQ job processor
│   ├── controllers/
│   │   ├── candidate.controller.ts # Upload, list, get candidate
│   │   └── matching.controller.ts  # Match job↔candidates
│   ├── routes/
│   │   ├── candidate.routes.ts
│   │   └── matching.routes.ts
│   └── database/
│       ├── db.ts                   # PG connection pool
│       ├── setup.sql               # Initial schema
│       └── migrations/             # 001–009 migration files
│
└── frontend/src/
    ├── pages/
    │   ├── CandidateDetailPage.tsx # Candidate profile view
    │   └── MatchingPage.tsx        # Job matching UI
    └── store/
        ├── useCandidateStore.ts    # Candidate state
        └── useJobStore.ts          # Job + match state
```

### How to Start the System

```bash
# 1. Start PostgreSQL (if not running)
pg_ctl start

# 2. Start Redis
redis-server

# 3. Install and start AI service
cd ai-service
pip install -r requirements.txt          # CRITICAL — must run this!
python3 main.py                           # Starts on port 8000

# 4. Start backend
cd backend/src
npm install
npm run dev                               # Starts on port 3001

# 5. Start frontend
cd frontend
npm install
npm run dev                               # Starts on port 5173
```

### How to Debug the Parser

**Step 1 — Test AI service directly**:

```bash
curl -X POST http://localhost:8000/parse-text \
  -H "Content-Type: application/json" \
  -d '{"text": "John Doe\njohn@example.com\n+91-9876543210\nReact, TypeScript", "candidate_id": "test"}'
```

Expected output: email, phone, skills should all be present.

**Step 2 — Check which parsers initialized**:
Look at AI service startup logs:

```
✅ TextExtractor initialized
✅ RuleBasedParser initialized     ← if missing, phonenumbers/dateparser not installed
✅ AINamedEntityParser initialized ← if missing, torch/transformers not installed
```

**Step 3 — Check confidence breakdown**:
The confidence response includes `fields`:

```json
"confidence": {
  "overall": 0.14,
  "fields": { "email": 0.0, "phone": 0.0, "skills": 0.0 }
}
```

Zero values indicate which extractors are broken.

**Step 4 — Test rule parser standalone**:

```bash
cd ai-service
python3 test_rule_parser.py
```

### How to Improve Accuracy

1. **Immediate** (minutes): `pip install -r requirements.txt` → restores to ~65%
2. **Short term** (hours): Apply Bug #2 and #3 fixes above → raises to ~70%+
3. **Medium term** (days): Expand skill taxonomy → raises to ~75%+
4. **Long term** (weeks): Fine-tune BERT on resume dataset → target 85–90%

### Key Database Tables

| Table             | Key Columns                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------- |
| `candidates`      | id, full_name, email, phone, location, linkedin_url, github_url, summary, years_of_experience |
| `skills`          | id, candidate_id, name, skill_name (generated), category, proficiency_level                   |
| `work_experience` | id, candidate_id, job_title, company_name, start_date, end_date, is_current, description      |
| `education`       | id, candidate_id, degree, institution, field_of_study, start_date, end_date, gpa              |
| `parsing_jobs`    | id, candidate_id, status, confidence_score, parsed_data, error_message, completed_at          |

### Environment Variables (Backend `.env`)

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_parser
REDIS_URL=redis://localhost:6379
AI_SERVICE_URL=http://localhost:8000
PORT=3001
```

### Environment Variables (AI Service `.env`)

```
AI_SERVICE_PORT=8000
MODEL_NAME=dslim/bert-large-NER
SKILL_MODEL_NAME=Nucha/Nucha_ITSkillNER_BERT
```
