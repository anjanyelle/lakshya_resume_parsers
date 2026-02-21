# Resume Parser Audit & Accuracy Roadmap (Code-Based)

This document is a **technical audit** of the current backend in `Lakshya-LLM-Resume-Parser/backend` and a **production-focused roadmap** to improve:

- `.doc/.docx` consistency vs PDF
- experience parsing quality
- client name extraction coverage
- section-wise extraction correctness (summary/skills mixing)
- scalability to **10,000+ resumes/day**

It is **strictly grounded** in the current codebase (FastAPI + Celery + SQLAlchemy + parsers + optional LLM).

---

## 1) Current Architecture Overview (End-to-End Flow)

### 1.1 API → Ingestion
- **Endpoint:** `backend/app/api/v1/endpoints/upload.py`
- **What happens:**
  - Validates file extension + magic bytes (`validate_magic`).
  - Virus scan (`scan_file`).
  - Stores file in S3 or local storage (`services/storage.py`).
  - Creates:
    - `Candidate` row (`models/candidate.py`)
    - `ParsingJob` row (`models/parsing_job.py`) with `file_path`.
  - Starts parsing via `start_parsing_workflow(job_id)`.

### 1.2 Storage
- **S3/local abstraction:** `backend/app/services/storage.py`
- Canonical copy is also attempted (`original_file_copy_path`).

### 1.3 Worker/Queue Execution
- **Celery app:** `backend/app/workers/celery_app.py`
- **Workflow orchestration:** `backend/app/workers/pipeline.py`
  - Uses Celery `chain(...)` for multi-stage parsing.
  - Supports `PARSING_MODE`:
    - `text_only`
    - `deterministic`
    - default (hybrid multi-pass w/ LLM)

### 1.4 Text Extraction
- **Task:** `extract_text_task` (`backend/app/workers/extract_text_task.py`)
- **Extractor:** `backend/app/services/parser/extract_text.py`
  - `pdf`: PyMuPDF layout → pdfplumber → pypdf fallback → OCR fallback.
  - `docx`: `python-docx` paragraphs + tables.
  - `doc`: converted to docx via `soffice --headless --convert-to docx` then docx extraction.

### 1.5 Normalization
- `backend/app/services/parser/normalize.py`
  - Unicode normalization (NFKC)
  - bullet normalization
  - whitespace repair
  - basic OCR error repair

### 1.6 Section Detection
- **Deterministic sectioning:** `task_detect_sections` → `SectionParser(use_spacy=True)`
  - Stores:
    - `parsed_data["sections"] = {section: {content, confidence}}`
    - `parsed_data["detected_headers"]`
    - debug bundle: `parsed_data["debug"]["sections"]`

### 1.7 Structured Extraction (Deterministic + Optional LLM)
- **Contact:** `ContactExtractor().extract_all(raw_text)`
- **Experience:** `WorkExperienceParser().parse_experience_section(...)`
  - Has a quality-scored gating path that can invoke LLM extraction **only if** enabled and low confidence/quality.
- **Skills:** `SkillExtractor.extract_all(skills_section, jobs, raw_text=...)` with optional LLM fallback for grouped skills.
- **Education/Certifications/Achievements:** deterministic parsers + sanitizers.

### 1.8 Validation / Confidence / Review
- **Confidence score:** `task_calculate_confidence`
  - Combines:
    - section confidence
    - extraction confidence (when present)
    - pattern strength
    - optional LLM verification strength
- **Validation / verification:** `task_verify_extracted_data`
  - Only runs when `LLM_PROVIDER != none`.
  - Merges deterministic contact back into verified contact if LLM misses emails/phones/name/location/URLs.
- **Human review flags:** in `task_save_to_database` via:
  - `compute_review_flags(...)`
  - thresholds: `REVIEW_FIELD_THRESHOLD`, `REVIEW_CONFIDENCE_THRESHOLD`
  - auto-corrections: `apply_correction_patterns(...)`

### 1.9 Persistence
- **DB save:** `task_save_to_database`
  - Writes:
    - `Candidate` fields (name, email, phone, summary, current title/company, years exp)
    - `WorkHistory`, `Education`, `Certification`, `CandidateSkill`, `CandidateAchievement`
  - Stores `resume.txt` and `resume.json` to S3/local if missing.

---

## 2) Implemented Features (What You Already Have)

### 2.1 PDF extraction is already production-grade compared to DOCX
- Multi-strategy extraction.
- Layout reconstruction for 2-column PDFs.
- Header/footer stripping.
- OCR fallback if extracted text is small.
- Debug capture in `parsed_data["debug"]["text_extraction"]`.

### 2.2 Deterministic parsing pipeline (works without LLM)
Based on your README environment sample:
- `PARSING_MODE=deterministic`
- `LLM_PROVIDER=none`

In this mode you already have:
- Contact extraction
- Section detection (SectionParser)
- Experience parsing (WorkExperienceParser)
- Education parsing (EducationParser)
- Skills extraction (SkillExtractor)
- Certifications parsing + validation logic
- Confidence scoring (purely deterministic weighting)
- DB persistence + review flagging

### 2.3 Hybrid multi-pass pipeline exists (but only when LLM is enabled)
When LLM is enabled (not `none`), you have:
- LLM-based section detection fallback `task_detect_resume_sections` (gated by deterministic confidence)
- LLM structured resume extraction + normalization
- LLM verification of extracted payload
- LLM-based extraction confidence scoring

### 2.4 Observability
- Prometheus metrics (API, parsing totals, stage durations, DB query latency, queue depth)
- Structured logging (`structlog`)
- Sentry integration

---

## 3) Accuracy Gaps (What’s Weak and Why — Based on Code)

### 3.1 DOC/DOCX inconsistency root cause (structure loss)
**Current DOCX extraction** (`_extract_docx` in `services/parser/extract_text.py`) only does:
- `paragraph.text` (plain text)
- `table.rows[].cells[].text` and joins with `" | "`

This causes predictable enterprise failures:
- **Bullets and numbering metadata are lost** (DOCX stores bullets in numbering definitions; `paragraph.text` doesn’t preserve them).
  - Impact: experience responsibilities collapse into a blob.
- **Heading/style metadata is lost** (DOCX headings are often `Heading 1/2` styles).
  - Impact: section detection confidence drops; summary/skills/experience mix.
- **Multi-column layouts and text boxes are lost** (Word resumes frequently use columns, tables, floating text boxes, headers).
  - Impact: order is wrong; sidebar skills appear in the middle; “contact header” gets mixed into experience.
- **Table semantics are flattened**.
  - Impact: experience rows with (Company | Title | Dates) become hard to align.

### 3.2 Experience parsing is already quite sophisticated, but still vulnerable
Your `task_parse_work_experience` does:
- uses section slice if present
- quality scoring (`score_work_experience_jobs`)
- creates an alternate `date_anchor_excerpt` window and prefers it if it yields better parse score
- has LLM gating (only when enabled)

Why experience still fails at ~60%:
- If DOCX loses bullets/headings, the experience section boundary becomes weak (`exp_conf` low), and deterministic parser sees noisy lines.
- Work history in tables (common in DOCX) becomes `" | "` lines; your experience parser likely expects more natural line breaks.

### 3.3 Client names are often missed (confirmed by code)
- DB persistence supports `WorkHistory.client_name`.
- Experience LLM path maps `client` / `client_name` into payload.
- **But in deterministic mode (`LLM_PROVIDER=none`) there is no explicit client extraction stage**.

Therefore:
- If `LLM_PROVIDER=none`, clients will only appear if `WorkExperienceParser` deterministically populates `client` (not guaranteed).

### 3.4 Summary and skills mixing
- Candidate summary is set from `sections["summary"].content` or guessed from top-of-document heuristics.
- If section detection is weak (DOCX structure loss), summary may be wrong or bleed into other content.

---

## 4) Missing Core Layers (What’s Missing/Incomplete in Your Implementation)

### 4.1 DOCX-aware structure-preserving extraction layer (missing)
You need a DOCX extraction layer that emits a richer intermediate representation:
- paragraph text **with bullet/number markers**
- heading detection from styles
- stable ordering for tables (and table row/column semantics)

Your PDF extractor already does layout reconstruction; DOCX needs a comparable “layout-aware to plain-text” strategy.

### 4.2 Field-level provenance (evidence) storage (mostly missing)
You store debug bundles, but you don’t persist per-field evidence like:
- which lines produced the candidate name
- which line matched the email
- which excerpt produced the job header

This blocks enterprise debugging and systematic improvement.

### 4.3 Deterministic client extraction module (missing)
To support `LLM_PROVIDER=none` (or to reduce LLM dependency), add a deterministic client extractor:
- scan experience bullets for patterns:
  - `Client:` / `Clients:`
  - `Worked for <ORG>` / `On-site at <ORG>`
  - `Project for <ORG>`
- use org-phrase heuristics or lightweight NER (spaCy if already used for SectionParser) **only on experience/projects sections**.

### 4.4 Adaptive multi-pass (partial)
You do have gating (e.g., `task_detect_resume_sections` runs only when deterministic sectioning is weak), but it is only active when LLM is enabled.
For enterprise accuracy, you need deterministic adaptive passes too:
- if experience parse score is low, attempt an alternate “table-line normalization” pass before parsing.

---

## 5) Performance & Scalability Gaps (10k/day)

### 5.1 External DOC conversion cost
- `.doc` conversion uses `soffice` subprocess and a temp directory per conversion.
- At scale, this must be isolated in its own worker pool/queue.

### 5.2 Queue topology is not separated by workload class
Currently the pipeline is a single chain. For 10k/day you should split queues:
- `extract_text` queue
- `doc_convert` queue
- `ocr` queue
- `parse_deterministic` queue
- `llm` queue
- `persist` queue

This prevents OCR/DOC conversion jobs from starving normal resumes.

### 5.3 LLM overhead (only relevant when LLM is enabled)
In hybrid mode, multiple LLM calls per resume can become the main bottleneck.
Your code already includes good gating patterns; next step is:
- caching by hash of normalized section text
- token budgeting / chunking

### 5.4 DB write pattern
`task_save_to_database` deletes and reinserts all child entities each run.
That is safe but can be heavy at high throughput.
At 10k/day it’s acceptable with proper indexing and batch operations, but for enterprise scale you may want:
- upsert strategies
- differential updates

---

## 6) Advanced Enterprise Enhancements (Specific to Your Code)

### 6.1 Upgrade DOCX extraction (highest ROI for accuracy)
Add a DOCX extraction strategy that:
- emits bullets (prefix `- `) when paragraph is list item
- uses paragraph styles to mark headings (e.g., `## EXPERIENCE`)
- treats tables as structured blocks (e.g., row-wise with controlled separators)

Expected impact:
- improves `SectionParser` header detection confidence
- improves experience parsing quality score
- reduces summary/skills mixing

### 6.2 Add deterministic client extraction stage (works even with LLM disabled)
- Implement a new stage after `task_parse_work_experience`:
  - `task_extract_clients`
- Use:
  - extracted `work_experience[*].description/bullets`
  - plus `sections["projects"].content` (if present)

Persist into:
- `parsed_data["clients"] = [...]`
- and/or populate `work_experience[*].client` when detected.

### 6.3 Strengthen section segmentation contract
Today you store `sections = {key: {content, confidence}}`.
Enterprise upgrade:
- also store:
  - `start_line`, `end_line`
  - `evidence_heading`
  - `method` (spacy/dict/llm)

This makes debugging DOCX issues much easier.

### 6.4 Field-level confidence and validation
You already compute an overall confidence score.
Add per-field confidence fields inside `parsed_data["confidence_breakdown"]["fields"]` and tie them to:
- pattern checks (email regex exact match, date parsing success)
- section confidence
- parser quality score

### 6.5 Monitoring upgrades
Add Prometheus counters/gauges:
- doc/docx/pdf counts and failure rates
- doc conversion time + failure count
- OCR trigger rate
- experience parse quality distribution (from `debug_bundle["work_experience"]["primary_quality_score"]`)

---

## 7) Step-by-Step Improvement Roadmap (Practical)

### Phase 1 — Make DOCX extraction structure-preserving (1–2 weeks)
- Preserve bullets
- Preserve headings
- Add docx-specific debug stats

### Phase 2 — Fix experience & client extraction deterministically (2–3 weeks)
- Add deterministic `task_extract_clients`
- Add table-line normalization for experience parsing
- Improve experience validation (date ordering, overlap heuristics)

### Phase 3 — Improve section segmentation stability (2–4 weeks)
- Store boundaries + evidence
- Add deterministic fallback segmenter when headers are weak

### Phase 4 — Scale to 10k/day (ongoing)
- Split Celery queues by workload class
- Isolate `.doc` conversion and OCR workers
- Add caching and chunking if/when LLM is enabled

---

## Notes About Your Current Env Settings
Your README shows:
- `PARSING_MODE=deterministic`
- `LLM_PROVIDER=none`

In this mode:
- All LLM-based accuracy boosters (LLM section detection fallback, LLM verification, LLM confidence evaluation, structured resume extraction) are **disabled** by design.
- Therefore, improving accuracy from ~60% to 85%+ will depend heavily on:
  - **DOCX extraction fidelity**
  - deterministic segmentation + extraction improvements
  - hybrid (LLM) enabling for the hardest fields (optional, but typically needed for 85%+ across diverse templates)
