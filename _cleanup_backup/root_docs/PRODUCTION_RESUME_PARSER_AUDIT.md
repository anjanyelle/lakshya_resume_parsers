# Production Resume Parser — Technical Audit & Improvement Plan

**Document Version:** 1.0  
**Target:** Enterprise-grade, 90%+ accuracy, Zoho Recruit / Lever ATS–level architecture  
**Author:** Senior Resume Parsing Architect & ATS System Engineer

---

## Executive Summary

This document provides a root cause analysis of 10 critical issues, industry-standard architecture design, performance optimization strategy, and an actionable production improvement plan. It includes a logging strategy to trace where data is lost.

---

## Part 1: Root Cause Analysis

### Issue 1: Candidate Name Missing

| Root Cause                    | Location               | Explanation                                                                 |
| ----------------------------- | ---------------------- | --------------------------------------------------------------------------- |
| Name on line 2–4, not line 1  | `contact_extractor.py` | Parser historically checked only line 1; many resumes put email/phone first |
| ALL CAPS names not recognized | `contact_extractor.py` | "JOHN SMITH" was not matched by Firstname Lastname pattern                  |
| Name in header/footer         | `extract_text.py`      | PDF extraction may drop or misorder header text                             |
| LLM returns empty             | `llm_service.py`       | When LLM is used, empty name overwrites deterministic result                |

**Fix applied:** Extended to lines 1–4, ALL CAPS fallback, regex fallback, never return `None`. Additional: DOCX header/footer prepended to text for name extraction; LLM merge guard prevents empty name from overwriting deterministic name in structured merge.

---

### Issue 2: Summary Section Partially Extracted or Missing

| Root Cause                              | Location                                     | Explanation                                                     |
| --------------------------------------- | -------------------------------------------- | --------------------------------------------------------------- |
| Section header not detected             | `section_parser.py`, `fallback_segmenter.py` | "Professional Summary", "Career Overview" may not match aliases |
| Summary merged with skills              | `section_parser._canonicalize_sections`      | Overlap between summary and skills keywords                     |
| Content in wrong section                | `section_boundary_extractor.py`              | Date-based heuristics assign summary lines to experience        |
| Summary from `sections.summary.content` | `pipeline.py`                                | If section confidence < threshold, summary block may be skipped |

**Data flow:** `sections.summary.content` → `inferred_summary` → `candidate.summary` (only if `not candidate.summary`).

**Fix applied:** Added "Career Overview", "Executive Summary", "Profile", "Professional Profile" to section detection (section_parser, fallback_segmenter, section_boundary_extractor); expanded `_guess_summary_from_raw_text` and `_guess_name_from_raw_text` headings; added `career_overview` to `_canonical_section_key` mapping.

---

### Issue 3: Work History Incomplete (5 Companies → 2 Parsed)

| Root Cause                     | Location                                         | Explanation                                                         |
| ------------------------------ | ------------------------------------------------ | ------------------------------------------------------------------- |
| Single chunk returned          | `work_experience_parser.extract_individual_jobs` | No date boundaries found → entire section = 1 chunk → 1 job         |
| Section header not detected    | `section_parser`                                 | "Professional Experience" vs "Employment" — key mismatch            |
| Client names in bullets        | `extract_clients_task`                           | Clients extracted separately; not always merged into `company_name` |
| Placeholder/skillish filtering | `work_experience_sanitizer`                      | Entries dropped if company/title look like skills                   |
| `_is_plausible_job` too strict | `work_experience_parser`                         | Jobs without dates rejected unless 2+ bullets                       |

**Fix applied:** 1-chunk fallback splitting by company/title patterns, EXPERIENCE_KEYS expansion, LLM fallback when >300 chars but 0 jobs. Additional: client used as company_name when company empty (save to DB).

---

### Issue 4: Skills Missing

| Root Cause                   | Location                | Explanation                                                |
| ---------------------------- | ----------------------- | ---------------------------------------------------------- |
| Skills section not detected  | `section_parser`        | "Technical Skills", "Core Competencies" may not match      |
| Skills in experience bullets | `skill_extractor`       | Bullet skills not always extracted                         |
| Normalization fails          | `skill_extractor`       | Unknown skill → not matched to taxonomy → dropped          |
| Skill–WorkHistory join       | `task_save_to_database` | Skills require `Skill` record; insert may fail on conflict |

**Fix applied:** Added `_extract_freeform_skills` to `extract_from_work_history` (bullet skills now extracted); added "Core Competencies", "Key Competencies" to fallback segmenter; pre-lookup by `normalized_name` before Skill insert to avoid duplicates.

---

### Issue 5: Certifications Missing

| Root Cause                      | Location                               | Explanation                                              |
| ------------------------------- | -------------------------------------- | -------------------------------------------------------- |
| Section header not detected     | `section_parser`, `fallback_segmenter` | "Licenses", "Credentials" map to certs but may be missed |
| False positive filtering        | `certification_validator`              | "Certificate of Completion" dropped as training          |
| Duplicates removed aggressively | `deduplicate_certificates`             | Fuzzy match may over-merge                               |

**Fix applied:** Added "Credentials", "Professional Credentials" to fallback segmenter; removed "certificate of completion" from TRAINING_FALSE_POSITIVES (keeps certs like "AWS - Certificate of Completion"); raised deduplicate fuzzy threshold from 90% to 95% to reduce over-merge.

---

### Issue 6: Education Section Not Detected

| Root Cause                 | Location           | Explanation                                  |
| -------------------------- | ------------------ | -------------------------------------------- |
| Non-English headers        | `section_parser`   | "Formación", "Studium" need to be in aliases |
| Education mixed with certs | `section_parser`   | Overlap in keywords                          |
| Table layout               | `education_parser` | Dates in separate columns not parsed         |

**Fix applied:** Added "Formación", "Studium", "Ausbildung" to fallback segmenter for non-English education headers. Education parser already handles table layout via YEAR_RE fallback (multiple years → first=start, last=end).

---

### Issue 7: PDF Upload Takes Very Long

| Root Cause                  | Location          | Explanation                                                     |
| --------------------------- | ----------------- | --------------------------------------------------------------- |
| OCR fallback for PDF        | `extract_text.py` | When text extraction fails, PDF → images → Tesseract OCR (slow) |
| No parallel page processing | `extract_text.py` | Pages processed sequentially                                    |
| pdf2image + Tesseract       | External deps     | Image conversion + OCR are CPU-heavy                            |
| Large file size             | —                 | Multi-page PDFs = many images                                   |

**DOC/DOCX faster:** Direct `python-docx` parsing, no OCR path.

**Fix applied:** Parallel page processing (ThreadPoolExecutor, max 4 workers) for OCR path; OCR_MAX_PAGES=15 config to limit OCR to first 15 pages on very long PDFs.

---

### Issue 8: DOC/DOCX Inconsistent

| Root Cause                    | Location           | Explanation                               |
| ----------------------------- | ------------------ | ----------------------------------------- |
| Table extraction              | `extract_text.py`  | Tables in DOCX may be read in wrong order |
| .doc (legacy) → .docx convert | `doc_convert_task` | Conversion can alter layout               |
| Style-based headers           | `extract_text`     | Headings not always detected              |

**Fix applied:** Expanded style-based header detection: Subtitle, Titre, Section Header, Resume Section, etc.; added outline level (outlineLvl) check; relaxed text fallback to accept short ALL CAPS section headers (e.g. "EXPERIENCE") without requiring bold.

---

### Issue 9: Section-Wise Mapping Fails Despite Correct Raw Text

| Root Cause                    | Location         | Explanation                                             |
| ----------------------------- | ---------------- | ------------------------------------------------------- |
| Confidence threshold          | `section_parser` | Low confidence → section content discarded              |
| Key mismatch                  | `pipeline`       | `sections.experience` vs `EXPERIENCE_KEYS` — must align |
| `_apply_llm_resume` overwrite | `pipeline`       | LLM merge can overwrite good deterministic data         |

**Fix applied:** Lowered section confidence threshold from 0.6 to 0.45 (task_detect_sections merge, skill_extractor); added LLM overwrite guards for education/skills (don't overwrite non-empty deterministic with empty LLM).

---

### Issue 10: Data Extracted But Not Displayed in UI

| Root Cause                             | Location                  | Explanation                                                                                                                        |
| -------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **UI reads from DB, not parsed_data**  | `CandidateDetailPage.tsx` | `WorkHistoryTimeline` uses `candidate.work_history` (DB). Parsed data in `latestJob.parsed_data` is only for debug/mismatch banner |
| **task_save_to_database must succeed** | `pipeline.py`             | If this task fails or is skipped, nothing is written to WorkHistory, Education, Certification                                      |
| **Field mapping**                      | `task_save_to_database`   | `parsed.work_experience[].company` → `WorkHistory.company_name`; `parsed.work_experience[].title` → `WorkHistory.job_title`        |
| **Relationship loading**               | API                       | `Candidate` must include `work_history`, `education`, `certifications` in response                                                 |

**Critical:** The UI shows `candidate.work_history`, not `parsed_data.work_experience`. If `task_save_to_database` fails, runs before parsing completes, or drops entries (sanitizer), the UI will be empty.

---

## Part 2: Data Flow Diagram

```
[Upload] → extract_text_task → raw_text
                ↓
         task_clean_text → normalized text
                ↓
         task_detect_sections → sections { experience, summary, skills, education, certifications }
                ↓
         task_extract_contact_info → contact { name, emails, phones }
                ↓
         task_parse_work_experience → parsed_data.work_experience
                ↓
         task_extract_clients → parsed_data.work_experience (client promoted to company)
                ↓
         task_parse_education → parsed_data.education
                ↓
         task_parse_certifications → parsed_data.certifications
                ↓
         task_extract_achievements → parsed_data.achievements
                ↓
         task_extract_skills → parsed_data.skills
                ↓
         [LLM path if enabled: task_detect_resume_sections, task_extract_personal_info,
          task_extract_structured_resume, task_extract_work_experience_details, task_extract_experience_skills]
                ↓
         task_save_to_database
           ├─ _apply_llm_resume (merge LLM if applicable)
           ├─ sanitize_final_output (dedup guard)
           └─ DB writes
                ↓
         WorkHistory, Education, Certification, CandidateSkill, Candidate (DB)
                ↓
         API GET /candidates/{id} → CandidatePublicRead (includes work_history, education, certifications)
                ↓
         UI: WorkHistoryTimeline, EducationSection, CertificationsSection
```

**Where data can be lost:**

| #   | Stage                     | Location                                                                                 | Failure modes                                                                                                                                                | Mitigation                                                                                     |
| --- | ------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| 1   | **Section detection**     | `section_parser.py`, `fallback_segmenter.py`, `pipeline.task_detect_sections`            | Heading not in aliases; non-standard wording; conf under 0.45 discarded when merging with fallback (LLM_PROVIDER=none)                                       | Add aliases in `SECTION_HEADINGS`; lower threshold; fallback when avg_sec_conf under 0.6       |
| 2   | **Parser segmentation**   | `work_experience_parser.py`, `education_parser.py`, `certification_parser.py`            | Date regex misses format; table layout misread; chunk boundaries wrong; entries merged incorrectly                                                           | Date format fallbacks; table-aware extraction; layout heuristics                               |
| 3   | **Sanitizer filters**     | `work_experience_sanitizer.py`, `structured_sanitizers.py`, `certification_validator.py` | Work: placeholder/skillish company/title dropped. Education: all placeholder (inst+degree+field) → dropped. Certs: bad keywords, over 200 chars, fuzzy dedup | Relax `_PLACEHOLDER_RE`; tune `_CERT_BAD_RE`; log dropped entries                              |
| 4   | **task_save_to_database** | `pipeline.py` (lines ~3624+)                                                             | Exception before commit; rollback; `company` empty but `client` present not mapped; FK constraint                                                            | Use `company or client` when saving; retry on transient errors                                 |
| 5   | **API / schema**          | `app/schemas/public.py` (`CandidatePublicRead`), `app/api/.../candidates.py`             | Relationships lazy-loaded; session closed before access; field omitted from schema                                                                           | Eager-load (`joinedload`) work_history, education, certifications in GET; verify schema fields |

---

## Part 3: Industry-Standard Architecture (Zoho/Lever-Style)

### Section Detection

- **Primary:** Regex + keyword aliases (`section_parser.py`, SpaCy)
- **Fallback:** Keyword-based (`fallback_segmenter.py`) when avg_sec_conf under 0.6 and LLM_PROVIDER=none — uses `_KNOWN_HEADERS` + hint regexes (date, degree, cert, tech)
- **Confidence:** Per-section score; low avg → try fallback segmenter; sections with conf under 0.45 discarded when merging

### Experience Segmentation

- **Primary:** Date-range boundaries (`DATE_RANGE_RE`, `work_experience_parser.py`)
- **Fallback:** Company/title from `COMPANY_LINE_RE`, `TITLE_AT_COMPANY_RE`; job title keywords (`TITLE_SPLIT_KEYWORDS`)
- **LLM fallback:** When experience text >300 chars but 0 jobs (`work_experience_parser.py` line ~518)

### Client Extraction

- **Patterns:** `Client:`, `End Client:`, `Project:` (`work_experience_parser.CLIENT_PATTERNS`); `extract_clients_task`: `client[s]? :`, `worked for`, `project for`, `on-site at`, etc.
- **Merge:** Promote client to company when company empty or placeholder (`work_experience_parser` lines 908–915); `task_save_to_database` uses `company or client` for `company_name`

### Skills Detection

- **Taxonomy match:** `skill_extractor` normalizes via `normalized_map`, `SKILL_ALIASES`, `synonym_map`
- **Bullet extraction:** `extract_from_work_history` from job descriptions/bullets (base_conf 0.6/0.55)
- **Confidence:** Skills section conf under 0.45 discarded; low-conf skills require 2+ mentions in combined text

### Summary Extraction

- **Source:** `sections.summary.content` (`pipeline` line ~3775)
- **Fallback:** `_guess_summary_from_raw_text` — lines before experience/skills heading, up to 40 words
- **Clean:** `clean_summary` — dedup lines/sentences, trim to 800 chars / 3 sentences (`pipeline._dedup_text_lines`)

### Certifications

- **Patterns:** Exam codes (AZ-104, CKA), "Certified", "License" (`certification_parser`, `KNOWN_CERT_KEYWORDS`)
- **Deduplication:** Fuzzy match 95% + issuer (`certification_validator`, raised from 90%)

---

## Part 4: Performance Optimization

| Area          | Strategy                                                                              | Status      |
| ------------- | ------------------------------------------------------------------------------------- | ----------- |
| PDF speed     | PyMuPDF primary → pypdf fallback → pdfplumber tables only → pdfplumber full if needed | Implemented |
| Memory        | `PDF_MAX_PAGES` (50) limits non-OCR extraction; `OCR_MAX_PAGES` (15) limits OCR       | Implemented |
| Parallel      | ThreadPoolExecutor for OCR pages (max 4 workers)                                      | Implemented |
| Large resumes | Page limit applied; section parser receives truncated text                            | Implemented |

---

## Part 5: Technical Audit Checklist

- [x] All EXPERIENCE_KEYS checked when resolving experience section (`pipeline.task_parse_work_experience` lines 2296–2359)
- [x] Name extraction checks lines 1–4, ALL CAPS fallback (`contact_extractor.extract_name` lines 901–910, 975)
- [x] Summary from sections.summary.content with fallback (`_guess_summary_from_raw_text`, `pipeline` ~3775)
- [x] extract_individual_jobs has 1-chunk fallback splitting (`work_experience_parser._split_single_chunk_fallback` lines 735, 784, 794)
- [x] LLM fallback when >300 chars experience but 0 jobs (`work_experience_parser` ~518)
- [x] sanitize_final_output runs before save (`pipeline.task_save_to_database` lines 3649–3650)
- [x] task_save_to_database logs pre/post counts (`pipeline` lines 4090–4111: "Saving to DB", "DIAG pre-sanitize", "DIAG post-sanitize")
- [x] UI mismatch banner when parsed exists but DB empty (`CandidateDetailPage.tsx` showMismatchBanner: dbHistory.length === 0 && parsedExperience.length > 0)
- [x] Parsing debug endpoint available (`GET /candidates/{id}/parsing-debug`, `GET /jobs/{id}/debug` admin)

---

## Part 6: Logging Strategy — Where to Log

| Stage                      | Log Message                                                      | Purpose                   | Location                                          |
| -------------------------- | ---------------------------------------------------------------- | ------------------------- | ------------------------------------------------- |
| extract_text               | `Extracted text: N chars, method=X, ocr=Y`                       | Trace extraction path     | `extract_text_task`                               |
| task_detect_sections       | `Sections detected: keys=..., experience_conf=X`                 | Section detection success | `pipeline.task_detect_sections`                   |
| task_parse_work_experience | `Work experience: N chunks, M jobs`                              | Chunk/job count           | `work_experience_parser.parse_experience_section` |
| task_save_to_database      | `Saving to DB: work_experience=N, certifications=M, education=K` | Pre-save counts           | `pipeline.task_save_to_database`                  |
| sanitize_final_output      | `Final output: X jobs, Y certs, name=Z, summary_len=N`           | Post-dedup guard          | `pipeline.sanitize_final_output`                  |
| API get_candidate          | `Candidate X: work_history_count=N`                              | UI data availability      | `candidates.get_candidate`                        |

---

## Part 7: Validation Rules to Prevent Missing Data

| Rule                | Implementation                                                            | Location                                                                  |
| ------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Name**            | If empty after parsing, log warning; do not overwrite with empty from LLM | `sanitize_final_output` (log); `_apply_llm_resume` (guard)                |
| **Work experience** | If sections.experience has content but 0 jobs, trigger LLM fallback       | `work_experience_parser.parse_experience_section` (len(text)>300, 0 jobs) |
| **Summary**         | If sections.summary empty, try first N paragraphs                         | `_guess_summary_from_raw_text` in `task_save_to_database`                 |
| **Save guard**      | If sanitize_final_output reduces count significantly, log                 | `sanitize_final_output` (warn when work/cert count drops)                 |

---

## Part 8: Accuracy Roadmap to 90%+

| Phase | Target | Actions                                                   |
| ----- | ------ | --------------------------------------------------------- |
| 1     | 85%    | Ground truth dataset, fix known issues                    |
| 2     | 88%    | Multi-column PDF, OCR quality check                       |
| 3     | 90%    | LLM for ambiguous cases, human-in-loop for low confidence |

---

## Part 9: Issues Summary Table

| #   | Issue             | Root Cause                | Status  | Fix Location                                                                                          |
| --- | ----------------- | ------------------------- | ------- | ----------------------------------------------------------------------------------------------------- |
| 1   | Name missing      | Line 1 only, no ALL CAPS  | Fixed   | `contact_extractor`, `extract_text` (header/footer), `_apply_llm_resume` (guard)                      |
| 2   | Summary missing   | Section detection, merge  | Partial | `section_parser`, `fallback_segmenter`, `_guess_summary_from_raw_text`                                |
| 3   | Work incomplete   | 1 chunk, section keys     | Fixed   | `work_experience_parser._split_single_chunk_fallback`, `EXPERIENCE_KEYS`, `company or client`         |
| 4   | Skills missing    | Section, taxonomy         | Partial | `skill_extractor._extract_freeform_skills`, fallback segmenter, 2+ mentions, `normalized_name` lookup |
| 5   | Certs missing     | Section, false positives  | Partial | `fallback_segmenter`, `certification_parser`, `certification_validator` (95% dedup)                   |
| 6   | Education missing | Section aliases           | Partial | `fallback_segmenter` (FORMACIÓN, STUDIUM, AUSBILDUNG)                                                 |
| 7   | PDF slow          | OCR, sequential           | Fixed   | `extract_text`: ThreadPoolExecutor OCR, `OCR_MAX_PAGES`, `PDF_MAX_PAGES`, pypdf→pdfplumber tables     |
| 8   | DOC inconsistent  | Table extraction, headers | Partial | `extract_text._is_heading_paragraph` (style, outlineLvl, ALL CAPS)                                    |
| 9   | Mapping fails     | Confidence, key mismatch  | Partial | Confidence 0.45, LLM overwrite guards (education, skills)                                             |
| 10  | UI empty          | DB not populated          | Fixed   | `CandidateDetailPage` mismatch banner; `company or client` in save                                    |

---

## Part 10: Logging Added (Implemented)

| Location                         | Log                                                                                                         | When                            |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `extract_text_task`              | `Extracted text: N chars, method=X, ocr=Y`                                                                  | After extraction                |
| `task_extract_contact_info`      | `Contact extracted: name=X, emails=N, phones=N`                                                             | After contact parse             |
| `task_detect_sections`           | `Sections detected: keys=..., experience_conf=X`, `Section detection completed`, `DIAG sections keys=...`   | After section detection         |
| `task_parse_work_experience`     | `DIAG primary_jobs count=N`, `Work experience: N chunks, M jobs` (parser)                                   | After work parse                |
| `sanitize_final_output`          | `Final output: X jobs, Y certs, name=Z, summary_len=N`                                                      | Before save                     |
| `task_save_to_database`          | `Saving to DB: work_experience=N, certifications=M, education=K`, `DIAG pre-sanitize`, `DIAG post-sanitize` | Before DB write                 |
| `get_candidate` (API)            | `Candidate X: work_history_count=N`                                                                         | On candidate fetch              |
| `CandidateDetailPage` (frontend) | `[CandidateDetail] Data loaded: {...}`                                                                      | When candidate loads (dev only) |

---

## Part 11: Step-by-Step Production Improvement Plan

1. **Logging** — Implemented at key pipeline stages (see Part 10)
2. **Run ground truth evaluation** — measure baseline
3. **Fix PDF performance** — prefer PyMuPDF, parallel OCR
4. **Expand section aliases** — add missing headers
5. **Add UI fallback** — show parsed_data when DB empty (read-only)
6. **Implement generate_accuracy_report** — automated accuracy tracking
7. **Add health check** — `/health/parsing` with last N job success rate
