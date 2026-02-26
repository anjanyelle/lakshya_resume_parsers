# Lakshya Resume Parser — Technical Architecture Analysis

**Document Version:** 1.0  
**Audience:** Product Owner / Technical Stakeholders  
**Purpose:** Full architectural clarity from upload to final JSON output

---

## 1. End-to-End Flow: Upload → Final JSON Output

### 1.1 High-Level Pipeline

```
[API Upload] → ParsingJob created → start_parsing_workflow(job_id)
    ↓
[extract_text_task] → raw_text stored in ParsingJob.raw_text
    ↓
[task_clean_text] → normalize_resume_text() → raw_text overwritten
    ↓
[task_detect_sections] → sections dict (experience, summary, skills, education, certifications, etc.)
    ↓
[task_extract_contact_info] → contact { name, emails, phones, urls, location }
    ↓
[task_parse_work_experience] → work_experience []
    ↓
[task_extract_clients] → client promoted to company when company empty
    ↓
[task_parse_education] → education []
    ↓
[task_parse_certifications] → certifications []
    ↓
[task_extract_achievements] → achievements []
    ↓
[task_extract_skills] → skills []
    ↓
[task_taxonomy_mapping] → taxonomy enrichment
    ↓
[task_calculate_confidence] → confidence_score, confidence_breakdown
    ↓
[task_save_to_database] → _apply_llm_resume() → sanitize_final_output() → DB writes
    ↓
[Candidate, WorkHistory, Education, Certification, CandidateSkill] persisted
```

**Three parsing modes** (controlled by `PARSING_MODE`):

| Mode | Tasks Run |
|------|-----------|
| `text_only` | extract_text → clean_text → finalize_text_only (saves raw text only) |
| `deterministic` | Full pipeline above, **no LLM tasks** |
| `full` | Full pipeline + LLM tasks (task_detect_resume_sections, task_extract_personal_info, task_extract_structured_resume, etc.) |

---

## 2. Module/File Responsibilities

### 2.1 Entry Points & Orchestration

| File | Responsibility |
|------|----------------|
| `app/api/v1/endpoints/upload.py` | Receives file upload, creates `Candidate` + `ParsingJob`, calls `start_parsing_workflow(job_id)` via background task |
| `app/workers/pipeline.py` | Orchestrates Celery chain; defines all `task_*` functions; `_apply_llm_resume`, `sanitize_final_output`, `_parse_date_str`, confidence logic |
| `app/workers/celery_app.py` | Celery app config; queues: `extract`, `doc_convert`, `parse`, `llm`, `persist` |

### 2.2 Text Extraction

| File | Responsibility |
|------|----------------|
| `app/workers/extract_text_task.py` | Loads job, calls `extract_text()`, applies table normalization for DOCX, stores `raw_text` in `ParsingJob` |
| `app/services/parser/extract_text.py` | **Multi-format extraction**: PDF (PyMuPDF → pypdf → pdfplumber → OCR), DOCX (python-docx), TXT/RTF, PNG/JPG (Tesseract). Returns `ExtractedText(text, ocr_confidence, used_ocr, method)` |
| `app/services/parser/normalize.py` | `normalize_resume_text()`, `normalize_table_lines()`, `clean_summary_and_skills_sections()`; NFKC, bullet substitution, URL repair |

### 2.3 Section Detection

| File | Responsibility |
|------|----------------|
| `app/services/parser/section_parser.py` | **Primary section detector**: 300+ `SECTION_ALIASES`, regex + spaCy PhraseMatcher (`spacy.blank("xx")`), inline sections ("Skills: Python, Java"), `_slice_sections()`, `_canonicalize_sections()` |
| `app/services/parser/fallback_segmenter.py` | **Fallback** when `avg_section_confidence < 0.6` and `LLM_PROVIDER=none`: `_KNOWN_HEADERS` (ALL CAPS), date/tech/degree/cert hints in 10-line windows |
| `app/services/parser/section_boundary_extractor.py` | Strict boundary extraction for **summary** and **certifications**; `SUMMARY_HEADINGS`, `CERTIFICATION_HEADINGS`, `STOP_HEADINGS` |

### 2.4 Entity Extraction

| File | Responsibility |
|------|----------------|
| `app/services/parser/contact_extractor.py` | Name (lines 1–4, ALL CAPS fallback, NAME_LABEL_REGEX), emails, phones, URLs, location via regex |
| `app/services/parser/work_experience_parser.py` | `extract_individual_jobs()` (date anchors, CLIENT blocks, `_split_single_chunk_fallback`), `_parse_chunk()`, `_parse_table_formatted_experience()`, company/title normalization |
| `app/services/parser/education_parser.py` | `_split_blocks()` by year/institution, `_extract_institution()`, `_extract_degree()`, `DEGREE_ALIASES` |
| `app/services/parser/certification_parser.py` | Regex for cert names, exam codes (AZ-104, CKA), `KNOWN_CERT_KEYWORDS` |
| `app/services/parser/certification_validator.py` | `remove_false_positives`, `deduplicate_certifications` (95% fuzzy), `normalize_providers` |
| `app/services/parser/achievements_extractor.py` | Achievements/awards section extraction |
| `app/workers/extract_clients_task.py` | Client patterns (`client:`, `worked for`, `project for`); promotes client to company when company empty |

### 2.5 Skills

| File | Responsibility |
|------|----------------|
| `app/services/parser/skill_extractor.py` | Taxonomy-based (`skills_master`), PhraseMatcher, `extract_from_skills_section`, `extract_from_work_history`, `extract_from_raw_text`, `_canonicalize_token`, `SKILL_ALIASES`, `RELATED_SKILLS` |
| `app/data/skills/skills_master.py` | JSON taxonomy of skills with `name`, `normalized_name`, `category` |

### 2.6 Sanitization & Quality

| File | Responsibility |
|------|----------------|
| `app/services/parser/work_experience_sanitizer.py` | `sanitize_work_experience_entries`, `deduplicate_work_entries`; filters placeholder/skillish entries |
| `app/services/parser/structured_sanitizers.py` | `sanitize_certifications_entries`, `sanitize_education_entries`, `sanitize_skill_entries` |
| `app/services/parser/quality_scoring.py` | `score_work_experience_jobs()`, `score_certifications()` |

### 2.7 LLM Integration

| File | Responsibility |
|------|----------------|
| `app/services/llm_service.py` | `LLMParsingService`: `extract_work_experience`, `extract_certifications`, `extract_all_skills_grouped`, `extract_personal_info`, `extract_structured_resume`, `verify_structured_resume`; OpenAI/Anthropic/Ollama via config |

### 2.8 Confidence & Persistence

| File | Responsibility |
|------|----------------|
| `app/workers/task_calculate_confidence.py` | `build_per_field_confidence()`, `record_quality_metrics()` |
| `app/workers/pipeline.py` (task_calculate_confidence) | Weighted score: section (0.35), extraction (0.35), pattern (0.2), llm (0.1); field importance: contact 22%, work 28%, skills 18%, education 16%, certs 8%, achievements 8% |
| `app/workers/pipeline.py` (task_save_to_database) | `_apply_llm_resume()`, `sanitize_final_output()`, DB writes to `Candidate`, `WorkHistory`, `Education`, `Certification`, `CandidateSkill` |

---

## 3. Internal Pipeline Flow (Data Passing)

- **State carrier:** `ParsingJob` (PostgreSQL) — `raw_text`, `parsed_data` (JSONB), `confidence_score`
- **Each task:** `_load_job(job_id)` → read `job.parsed_data` → compute updates → `_update_job(job_id, parsed_data=_merge_parsed(job, updates))`
- **Merge semantics:** `_merge_parsed` does `base.update(updates)` — later tasks overwrite keys
- **Idempotency:** Tasks check `if "sections" in parsed: return job_id` (or equivalent) to skip if already done

---

## 4. Deterministic vs AI/LLM Parts

### 4.1 Fully Deterministic (Regex/Rule-Based)

| Stage | Implementation |
|-------|----------------|
| **Text extraction** | PyMuPDF, pypdf, pdfplumber, python-docx, Tesseract — no ML |
| **Text normalization** | `normalize_resume_text`, `normalize_table_lines` — regex, NFKC |
| **Section detection (primary)** | `SectionParser`: regex + `SECTION_ALIASES` + spaCy PhraseMatcher with `spacy.blank("xx")` (tokenization only, **no pretrained NER**) |
| **Fallback segmenter** | `FallbackSegmenter`: `_KNOWN_HEADERS`, `_DATE_HINT_RE`, `_TECH_HINT_RE`, `_DEGREE_HINT_RE`, `_CERT_HINT_RE` |
| **Contact extraction** | `ContactExtractor`: regex for email, phone, NAME_LABEL_REGEX, lines 1–4 |
| **Work experience (primary)** | `WorkExperienceParser`: `DATE_RANGE_RE`, `COMPANY_LINE_RE`, `TITLE_AT_COMPANY_RE`, `extract_individual_jobs`, `_parse_chunk` |
| **Education** | `EducationParser`: year/institution regex, `DEGREE_ALIASES` |
| **Certifications (primary)** | `section_boundary_extractor.extract_certifications`, `CertificationParser` |
| **Skills (primary)** | `SkillExtractor`: taxonomy match, PhraseMatcher, `_split_skills`, `_canonicalize_token` |
| **Client extraction** | Regex patterns in `extract_clients_task` |
| **Confidence calculation** | Rule-based: `_contact_pattern_strength`, `_work_pattern_strength`, `_skills_pattern_strength`, etc. |

### 4.2 AI/LLM (Conditional)

| Stage | Trigger | Implementation |
|-------|---------|----------------|
| **Work experience LLM fallback** | `exp_conf < 0.55` OR `primary_score < 1.2` OR `ambiguous_headers >= 2` | `LLMParsingService.extract_work_experience()` |
| **Work experience in-chunk LLM** | `job.confidence < 0.8` inside `_parse_chunk` | `_llm_fallback(chunk)` |
| **Work experience 0 jobs** | `len(text) > 300` and `len(jobs) == 0` | `llm.extract_work_experience(text)` |
| **Skills LLM fallback** | `payload` empty after deterministic | `llm.extract_all_skills_grouped(raw_text)` |
| **Certifications LLM fallback** | `payload` empty or `best_score < 1.0` | `llm.extract_certifications(cert_text)` |
| **Full-mode LLM tasks** | `PARSING_MODE=full` | `task_extract_personal_info`, `task_extract_structured_resume`, `task_extract_work_experience_details`, `task_extract_experience_skills`, `task_evaluate_extraction_confidence`, `task_verify_extracted_data` |
| **LLM merge** | `_apply_llm_resume()` | Fills gaps only; guards prevent overwriting non-empty deterministic with empty LLM |

---

## 5. Section Detection — How It Works

### 5.1 SectionParser Flow

1. **`_prepare_lines()`** — Split by `\n`, strip, `_normalize_table_row()` (2+ spaces → ` | `)
2. **`_detect_headers()`** — For each line:
   - **Inline:** `_try_split_inline(line)` — e.g. `"Skills: Python, Java"` → key `skills`, content `"Python, Java"`
   - **Regex:** `_match_header_line()` — match against `SECTION_ALIASES` with `re.match(rf"^\s*[^A-Za-z0-9]*?{re.escape(alias)}(?P<rest>.*)$", line)`
   - **spaCy PhraseMatcher:** `doc = nlp("\n".join(lines))`, `matcher(doc)` — exact token match (no NER)
3. **`_slice_sections()`** — Content between consecutive headers
4. **`_canonicalize_sections()`** — Map aliases to canonical keys (e.g. `profile` → `summary`)
5. **`_postprocess_sections()`** — Truncate by stop headings, length heuristics
6. **`_score_sections()`** — Per-section confidence from header match quality

### 5.2 FallbackSegmenter (when avg_sec_conf < 0.6)

- Scans for ALL CAPS lines (3–50 chars) in `_KNOWN_HEADERS`
- Density hints: `_DATE_HINT_RE`, `_TECH_HINT_RE`, `_DEGREE_HINT_RE`, `_CERT_HINT_RE` in 10-line windows
- Merges with primary: keeps primary sections with conf ≥ 0.45, adds fallback sections not in primary

### 5.3 Confidence Thresholds

- Sections with conf < 0.45 are **discarded** when merging with fallback
- Skills section conf < 0.45 → `section_text = ""` in `SkillExtractor.extract_all`

---

## 6. Work Experience Parsing — How It Works

### 6.1 Experience Section Resolution

- Pipeline checks **40+ `EXPERIENCE_KEYS`** (experience, work_experience, professional_experience, projects, internship, etc.)
- Takes the **longest** content block among matching keys

### 6.2 extract_individual_jobs()

1. **Pre-split:** If `CLIENT:` or `project:` blocks exist, split by those first
2. **Boundary detection:** For each line:
   - `CLIENT_HEADER_RE` → boundary
   - `DATE_ANCHOR_RE` + `PRESENT_RE` on adjacent lines → boundary
   - `_has_date_anchor(line)` → boundary (DATE_RANGE_RE, DATE_ANCHOR_RE, OCR lenient for `20xx`)
3. **Start adjustment:** Walk back 1–4 lines to find company/title line (skip bullets, environment lines)
4. **Chunk assembly:** Content between consecutive starts
5. **1-chunk fallback:** If only 1 chunk and `len(lines) >= 4` and `len(text) > 200`:
   - `_split_single_chunk_fallback()` — split by `CLIENT_HEADER_RE`, company name + date, `TITLE_HINT_RE` at line start

### 6.3 _parse_chunk()

- **Company/title:** `COMPANY_LINE_RE` (Company - Title), `TITLE_AT_COMPANY_RE`, `LABELED_ORG_RE`, `LABELED_TITLE_RE`
- **Dates:** `DATE_RANGE_RE`, `dateparser` fallback
- **Client:** `CLIENT_PATTERNS`
- **Bullets:** Lines starting with `-`, `•`, `*`
- **Plausibility:** `_is_plausible_job()` — rejects placeholder, phone, email, skillish headers

### 6.4 Table-Formatted Experience

- If >40% of lines contain `|`, use `_parse_table_formatted_experience()`
- Split by `|`, find date column, map remaining cols to company/title/location via `_looks_like_company`, `_looks_like_title`

### 6.5 Quality Score (score_work_experience_jobs)

- +1.0 per job, +0.6 company, +0.4 title, +0.8 dates, +0.1 per bullet (max 0.6), +0.2 description
- -1.5 if skillish header
- -0.8 if ≥12 jobs (over-extraction)

---

## 7. Skills Extraction and Mapping

### 7.1 Sources

1. **Skills section** — `sections["skills"]["content"]` (if conf ≥ 0.45)
2. **Work history** — `job.description` + `job.bullets` per `JobEntry`
3. **Raw text fallback** — When no section matches; `extract_from_raw_text()`

### 7.2 extract_from_skills_section

- `_extract_skills(text, base_confidence=0.85)` — PhraseMatcher + taxonomy
- `_extract_freeform_skills(text, base_confidence=0.7)` — Split by comma/pipe/bullet, canonicalize

### 7.3 extract_from_work_history

- `_extract_skills(text, base_confidence=0.6)` + `_extract_freeform_skills(text, base_confidence=0.55)` per job

### 7.4 extract_from_raw_text

- Lines with `:` and label containing "skill", "tools", "technolog", "environment"
- Or lines with 2+ delimiters (`,`, `|`, `•`, `-`, `;`)
- Or `_extract_from_token_line()` for space-separated skills
- `_expand_and_canonicalize()` → taxonomy lookup, `SKILL_ALIASES`, `synonym_map`

### 7.5 Filtering & Enrichment

- **2+ mentions:** Skills with conf < 0.6 require 2+ mentions in combined text
- **Proficiency:** `SKILL_CONTEXT_KEYWORDS` (e.g. "expert" → 0.95, "developed" → 0.8)
- **Years:** `calculate_skill_years()` from job durations
- **Related skills:** `infer_related_skills()` from `RELATED_SKILLS` dict
- **Categorization:** `normalized_map` → category from taxonomy

---

## 8. Confidence Score Calculation

### 8.1 Formula

```
overall = Σ (field_importance[name] / total_importance) * field_score[name]
```

**Field importance:** contact 22%, work_experience 28%, skills 18%, education 16%, certifications 8%, achievements 8%

### 8.2 Per-Field Score

```
field_score = (section_weight * section_conf) + (extraction_weight * extraction_conf) + (pattern_weight * pattern_strength) + (llm_weight * llm_validation)
```

**Weights (normalized):** section 0.35, extraction 0.35, pattern 0.2, llm 0.1 (when LLM enabled)

### 8.3 Component Definitions

| Component | Definition |
|-----------|-------------|
| **section_conf** | `sections[section_key].confidence` from SectionParser |
| **extraction_conf** | Mean of per-item `confidence` in contact/work/skills/education/certs |
| **pattern_strength** | Rule-based: e.g. contact = (name+email+phone+location+linkedin+github)/6; work = mean of (company+title+start+end)/4 per job; skills = tiered by count (≥12→1.0, ≥6→0.85, etc.) |
| **llm_validation** | 1.0 if `llm_structured_verified` has non-empty data for that field |

### 8.4 build_per_field_confidence (task_calculate_confidence.py)

- **name:** `_cap_words_score` (2+ capitalized words → 0.95)
- **email:** 1.0 if valid regex, else 0
- **phone:** 1.0 if E.164, 0.7 if raw pattern, else 0
- **work_experience:** `primary_quality_score / 2.0` from debug
- **skills:** `min(1.0, skill_count / 10)`
- **certifications:** `(cert_count / 3) * 0.8`

---

## 9. Where Accuracy Fails and Why

### 9.1 Section Detection Failures

| Failure | Root Cause |
|---------|------------|
| **Experience section missed** | Header not in `SECTION_ALIASES` or `_KNOWN_HEADERS`; non-English ("Erfahrung", "Expérience"); inline format without colon |
| **Summary merged with skills** | `_canonicalize_sections` maps both to same key; `clean_summary_and_skills_sections` moves lines; overlap in keywords |
| **Skills section discarded** | conf < 0.45 → `section_text = ""` |
| **Certifications missed** | "Licenses", "Credentials" not matched; inline "Certifications: X, Y" not in section parser path |

### 9.2 Work Experience Failures

| Failure | Root Cause |
|---------|------------|
| **Single chunk → 1 job** | No date boundaries found; `_split_single_chunk_fallback` heuristics fail (e.g. "Title at Company" format, table layout) |
| **Company/title swapped** | `COMPANY_LINE_RE` assumes "Company - Title"; "Title at Company" handled by `TITLE_AT_COMPANY_RE` but order-dependent |
| **Dates not parsed** | `DATE_TOKEN` misses `'20`, `20.01`, regional formats; `dateparser` fails on ambiguous input |
| **Entries dropped by sanitizer** | `_is_plausible_job` rejects; `_has_any_date and _has_any_body` filter; placeholder/skillish filtering |
| **Table layout** | >40% pipe lines triggers table parse; column order (company/title/date) guessed; wrong mapping |

### 9.3 Contact Failures

| Failure | Root Cause |
|---------|------------|
| **Name missing** | Name beyond line 30; no "Name:" label; ALL CAPS not matched by Firstname Lastname pattern |
| **Name in header/footer** | DOCX header/footer prepended but PDF extraction may drop or misorder |

### 9.4 Skills Failures

| Failure | Root Cause |
|---------|------------|
| **Skills not in taxonomy** | Dropped or low confidence; `_canonicalize_token` returns raw token with category None |
| **Section misdetected** | Skills in summary or experience → wrong bucket |
| **extract_from_raw_text** | Requires `:` with skill-like label OR 2+ delimiters; "Python Java SQL" with 1 delimiter may use `_extract_from_token_line` which can miss |

### 9.5 Certification Failures

| Failure | Root Cause |
|---------|------------|
| **Section not detected** | Header not in CERTIFICATION_HEADINGS or section parser |
| **False positive removal** | "Certificate of Completion" in TRAINING_FALSE_POSITIVES (relaxed but still filters some) |
| **Over-deduplication** | 95% fuzzy match merges distinct certs |
| **DB truncation** | `len(name) > 200` → `StringDataRightTruncation` (cert name stored in description-like field) |

### 9.6 PDF/DOCX Extraction Failures

| Failure | Root Cause |
|---------|------------|
| **Multi-column PDF** | Text order wrong; `reconstruct_multicolumn_layout` exists but not always applied |
| **DOCX bullets lost** | Bullets in numbering defs; extraction may flatten |
| **Table order** | DOCX tables read in arbitrary order |
| **OCR quality** | Tesseract eng-only; low confidence on scanned docs |

---

## 10. Technical Bottlenecks

### 10.1 Performance

| Bottleneck | Location | Impact |
|------------|----------|--------|
| **OCR sequential** | `extract_text.py` | Now parallel (ThreadPoolExecutor, 4 workers) but still slow for 10+ pages |
| **LLM latency** | `llm_service.py` | 90s timeout; chunked prompts for long text |
| **Section parser** | `section_parser.py` | 3000+ lines; spaCy `nlp("\n".join(lines))` on full text |
| **DB writes** | `task_save_to_database` | Single transaction; no bulk insert optimization |

### 10.2 Memory

| Bottleneck | Location | Impact |
|------------|----------|--------|
| **PDF page limit** | `PDF_MAX_PAGES=50`, `OCR_MAX_PAGES=15` | Truncation on long resumes |
| **LLM chunk size** | `LLM_MAX_CHARS=12000`, `LLM_CHUNK_CHARS=9000` | Chunking may lose context |

### 10.3 Accuracy Cascade

- **Section detection** is the root: if experience section is wrong or empty, work_experience and skills both suffer
- **Date parsing** gates work_experience quality; bad dates → sanitizer drops entries
- **Taxonomy** gates skills; unknown skills get low confidence or dropped

---

## 11. Improvements Needed for 85%+ Accuracy

### 11.1 Short-Term (Weeks)

| Improvement | File | Action |
|-------------|------|--------|
| **Date format fallbacks** | `pipeline._parse_date_str`, `work_experience_parser` | Add `20.01`, `20/01`, `'20`, `Jan 20` |
| **Section aliases** | `section_parser.SECTION_ALIASES`, `fallback_segmenter._KNOWN_HEADERS` | Add non-English, inline variants |
| **Experience keys** | `pipeline.EXPERIENCE_KEYS` | Already 40+; verify coverage |
| **Skills section conf** | `skill_extractor.extract_all` | Consider 0.4 threshold for edge cases |
| **Cert name truncation** | DB schema, `task_save_to_database` | Truncate cert name to 200 before insert |
| **Ground truth** | `scripts/build_ground_truth.py`, `tests/eval_resume_regression.py` | 50–100 resumes with expected JSON |

### 11.2 Medium-Term (Months)

| Improvement | File | Action |
|-------------|------|--------|
| **Pretrained NER** | `contact_extractor`, `work_experience_parser` | Use `en_core_web_sm` for PERSON, ORG, DATE |
| **Multi-column PDF** | `extract_text.py` | Apply `reconstruct_multicolumn_layout` when columns detected |
| **Source format propagation** | `extract_text_task` → `normalize_resume_text`, parsers | Pass `source_format` (pdf, docx, ocr) for format-specific rules |
| **LLM gating** | `task_parse_work_experience` | Lower threshold (e.g. 0.5) for LLM trigger |
| **Skills taxonomy expansion** | `skills_master.py` | Add missing skills from failure analysis |
| **Block segmentation** | `work_experience_parser._split_single_chunk_fallback` | Add company regex for "Inc", "LLC", "Ltd" at line start |

### 11.3 Long-Term (Quarters)

| Improvement | Area | Action |
|-------------|------|--------|
| **Fine-tuned NER** | Resume-specific entities | Train on resume corpus |
| **Multilingual** | OCR + section + parsing | Tesseract lang, SECTION_ALIASES per language |
| **Semantic matching** | Skills | Embeddings for skill similarity |
| **Layout model** | PDF | Document layout analysis (e.g. layoutlm-style) |

---

## 12. Summary Diagram

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    UPLOAD (upload.py)                     │
                    │  Candidate + ParsingJob created → start_parsing_workflow  │
                    └────────────────────────────┬──────────────────────────────┘
                                                 │
                    ┌────────────────────────────▼──────────────────────────────┐
                    │  EXTRACT (extract_text_task → extract_text.py)             │
                    │  PDF: PyMuPDF→pypdf→pdfplumber→OCR  DOCX: python-docx      │
                    │  Output: raw_text                                         │
                    └────────────────────────────┬──────────────────────────────┘
                                                 │
                    ┌────────────────────────────▼──────────────────────────────┐
                    │  CLEAN (task_clean_text → normalize.py)                    │
                    │  normalize_resume_text, NFKC, table lines                  │
                    └────────────────────────────┬──────────────────────────────┘
                                                 │
                    ┌────────────────────────────▼──────────────────────────────┐
                    │  SECTIONS (task_detect_sections)                          │
                    │  SectionParser (regex+PhraseMatcher) → FallbackSegmenter   │
                    │  Output: sections { experience, summary, skills, ... }     │
                    └────────────────────────────┬──────────────────────────────┘
                                                 │
         ┌───────────────────────────────────────┼───────────────────────────────────────┐
         │                                       │                                       │
         ▼                                       ▼                                       ▼
┌─────────────────┐                 ┌─────────────────────┐                 ┌─────────────────────┐
│ CONTACT         │                 │ WORK EXPERIENCE     │                 │ EDUCATION           │
│ contact_extractor│                 │ work_experience_    │                 │ education_parser    │
│ regex, lines 1-4│                 │ parser              │                 │ DEGREE_ALIASES      │
└────────┬────────┘                 │ date anchors,      │                 └──────────┬──────────┘
         │                          │ _parse_chunk       │                              │
         │                          └──────────┬──────────┘                              │
         │                                     │                                         │
         │                          ┌──────────▼──────────┐                              │
         │                          │ extract_clients     │                              │
         │                          │ client→company      │                              │
         │                          └──────────┬──────────┘                              │
         │                                     │                                         │
         └─────────────────────────────────────┼─────────────────────────────────────────┘
                                              │
                    ┌─────────────────────────▼──────────────────────────────┐
                    │  CERTIFICATIONS (section_boundary + certification_     │
                    │  parser + validator)                                   │
                    └────────────────────────────┬───────────────────────────┘
                                                 │
                    ┌────────────────────────────▼──────────────────────────────┐
                    │  SKILLS (skill_extractor)                                  │
                    │  taxonomy + PhraseMatcher + work_history + raw_text        │
                    └────────────────────────────┬──────────────────────────────┘
                                                 │
                    ┌────────────────────────────▼──────────────────────────────┐
                    │  CONFIDENCE (task_calculate_confidence)                    │
                    │  section + extraction + pattern + llm → weighted score        │
                    └────────────────────────────┬──────────────────────────────┘
                                                 │
                    ┌────────────────────────────▼──────────────────────────────┐
                    │  SAVE (task_save_to_database)                             │
                    │  _apply_llm_resume → sanitize_final_output → DB            │
                    └───────────────────────────────────────────────────────────┘
```

---

*End of Technical Architecture Analysis*
