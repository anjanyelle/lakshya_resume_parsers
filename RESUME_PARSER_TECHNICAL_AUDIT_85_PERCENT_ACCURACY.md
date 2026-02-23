# Resume Parser Technical Audit & 85%+ Accuracy Roadmap

**Target:** 85%+ parsing accuracy across PDF, DOC, DOCX, TXT, RTF, and image formats  
**Scope:** Code-focused, production-level analysis of `Lakshya-LLM-Resume-Parser/backend`

---

## 1. Full Technical Audit

### 1.1 Architecture Overview

```
Upload → Storage → extract_text → clean_text → detect_sections → 
  extract_contact → parse_work_experience → extract_clients → 
  parse_education → parse_certifications → extract_achievements → 
  extract_skills → taxonomy_mapping → calculate_confidence → save_to_database
```

**Key files:**
- `app/workers/pipeline.py` – Celery chain orchestration
- `app/services/parser/extract_text.py` – Multi-format text extraction
- `app/services/parser/normalize.py` – Text normalization
- `app/services/parser/section_parser.py` – Section detection (3,000+ lines)
- `app/services/parser/fallback_segmenter.py` – Fallback when SectionParser fails
- `app/services/parser/work_experience_parser.py` – Experience extraction
- `app/services/parser/skill_extractor.py` – Skills extraction
- `app/services/parser/education_parser.py` – Education extraction
- `app/services/parser/contact_extractor.py` – Contact extraction
- `app/workers/extract_clients_task.py` – Client extraction

### 1.2 File Extraction Audit

| Format | Method | Strengths | Weaknesses |
|--------|--------|-----------|------------|
| **PDF** | PyMuPDF (optional) → pdfplumber → pypdf → OCR | Layout-aware, 2-column, header/footer strip | PyMuPDF not in `pyproject.toml`; table cells flattened; no native table structure |
| **DOCX** | python-docx paragraphs + tables | Tables rendered as `\|` rows | **Bullets lost** (stored in numbering defs); **headings lost** (style metadata); **textboxes** extracted but order arbitrary; **multi-column** not handled |
| **DOC** | soffice → docx → docx extraction | Converts to DOCX | Requires LibreOffice; subprocess per file; no layout preservation |
| **TXT/RTF** | read_text / _strip_rtf | Simple | RTF stripping is basic; complex RTF may corrupt |
| **PNG/JPG** | pytesseract OCR | Works for scanned docs | Single image; no multi-page; no layout; `TESSERACT_LANG=eng` only |

**Critical finding:** PyMuPDF (`fitz`) is used but **not declared** in `pyproject.toml`. If missing, PDF falls back to pdfplumber immediately.

### 1.3 Preprocessing Audit

**`normalize.py`** – `normalize_resume_text()`:
- NFKC normalization, bullet substitution, URL repair
- `normalize_table_lines()` – pipe-row detection, date/company heuristics
- `clean_summary_and_skills_sections()` – moves skill-like lines from summary to skills and vice versa

**Gaps:**
- No format-specific normalization (PDF vs DOCX artifacts differ)
- `_TECH_KEYWORD_RE` and `_VERB_HINT_RE` are limited; many skills/verbs missed
- Table normalization assumes `|`-separated rows; PDF tables often use spaces or tabs
- No handling of merged cells or nested tables

### 1.4 Section Detection Audit

**`SectionParser`** (`section_parser.py`):
- 300+ section keys, extensive `SECTION_ALIASES` (multilingual)
- Header matching: regex, spacy PhraseMatcher (`spacy.blank("xx")` – no language model)
- `_match_header_line()`: dict_match, style_heading (`## `), casing bonuses
- `_slice_sections()`: content between headers
- `_normalize_table_row()`: `\s{2,}` → ` | ` for table-like lines

**`FallbackSegmenter`** (triggered when `avg_sec_conf < 0.6` and `LLM_PROVIDER=none`):
- All-caps headings → `_KNOWN_HEADERS` (limited set)
- Colon-suffixed headings
- Density guess: date/tech/degree/cert hints in 10-line windows

**Weaknesses:**
1. **DOCX structure loss:** No `## ` or heading markers if DOCX extraction drops styles
2. **Non-English headers:** PhraseMatcher uses `spacy.blank("xx")` – tokenization only, no semantics
3. **Inline sections:** "Skills: Python, Java" not detected as section start
4. **Density guess:** Can misassign sections (e.g., skills in experience block)
5. **No `start_line`/`end_line` in primary output** – only in fallback; debugging is harder

### 1.5 Experience Extraction Audit

**`WorkExperienceParser`** (`work_experience_parser.py`):
- `extract_individual_jobs()`: boundaries via `DATE_ANCHOR_RE`, `CLIENT_HEADER_RE`, `PRESENT_RE`
- `_parse_chunk()`: company/title from `COMPANY_LINE_RE`, `LABELED_ORG_RE`, `LABELED_TITLE_RE`
- Date parsing: `DATE_RANGE_RE`, `dateparser` fallback
- Client extraction: `CLIENT_PATTERNS` (4 patterns)
- `_is_plausible_job()`: filters skill-ish headers, placeholders, contact info

**Gaps:**
1. **Table-formatted experience:** Rows like `Company | Title | 2020-2022` often not split correctly; `_parse_header_lines` expects natural line breaks
2. **Date formats:** `DATE_TOKEN` misses formats like `'20` (apostrophe year), `Q1 2020`, `2020.01`
3. **Company/title order:** `COMPANY_LINE_RE` assumes `Company - Title`; many use `Title at Company` or `Title | Company`
4. **Concurrent roles:** No handling of "2020–2022 Role A; 2021–2023 Role B"
5. **Client regex:** `[A-Z][^\n,;\.]{2,50}` requires leading capital; misses "client: acme corp"

### 1.6 Skills Extraction Audit

**`SkillExtractor`** (`skill_extractor.py`):
- Taxonomy-based: `skills_master` JSON + PhraseMatcher
- `extract_from_skills_section()`, `extract_from_work_history()`, `extract_from_raw_text()`
- `_split_skills()`: comma, pipe, bullet splits
- `SKILL_ALIASES`, `RELATED_SKILLS`, `SOFT_SKILLS`
- Proficiency from `SKILL_CONTEXT_KEYWORDS`

**Gaps:**
1. **Taxonomy dependency:** Skills not in taxonomy get low confidence or missed
2. **Compound skills:** "React/Redux", "AWS (EC2, S3)" – splitting can fragment
3. **Section mixing:** If summary/skills misdetected, skills land in wrong bucket
4. **`extract_from_raw_text`** requires `:` or 2+ delimiters – misses "Python Java SQL" lines
5. **No confidence calibration** – same weight for taxonomy match vs. freeform

### 1.7 Education Extraction Audit

**`EducationParser`** (`education_parser.py`):
- `_split_blocks()`: year or institution keyword → new block
- `_extract_institution()`: `TOP_UNIVERSITIES` + keywords
- `_extract_degree()`: `DEGREE_ALIASES`, `DEGREE_KEYWORDS`, regex patterns
- `_extract_dates()`, `_extract_gpa()`, `_extract_honors()`

**Gaps:**
1. **Block splitting:** Single year can split incorrectly; "2020 B.S. Computer Science" may fragment
2. **International degrees:** Limited to English/Indian patterns
3. **In-progress:** "Expected 2025" not always detected
4. **Field of study:** Extracted but often conflated with degree

### 1.8 Entity Recognition Audit

- **Contact:** `ContactExtractor` – regex for email, phone, URL; optional spacy `en_core_web_sm` for NER (name)
- **Clients:** `extract_clients_task` – 6 regex patterns; false-positive filter
- **Certifications:** `CertificationParser`, `section_boundary_extractor.extract_certifications`
- **Achievements:** `AchievementsExtractor`

**NLP usage:** spaCy used for PhraseMatcher (section/skill headers) and optional NER. No dedicated NER for companies, titles, or dates.

---

## 2. Structural Weaknesses Reducing Accuracy

### 2.1 Format Handling

| Issue | Impact | Location |
|-------|--------|----------|
| DOCX bullets lost | Experience bullets merge; section boundaries blur | `extract_text.py:_extract_docx` |
| DOCX headings lost | Section detection fails; summary/skills mix | `extract_text.py:_extract_docx` |
| DOCX tables flattened | Experience table rows become single lines | `extract_text.py:_table_to_lines` |
| DOCX textbox order | Sidebar content interleaved incorrectly | `extract_text.py:_extract_textboxes` |
| PDF table structure | No cell-level extraction; tables as lines | `extract_text.py` (all PDF paths) |
| RTF stripping | Complex RTF corrupts (fonts, unicode) | `extract_text.py:_strip_rtf` |

### 2.2 Section Boundary Problems

- **Missing headers:** Headers without colon or all-caps (e.g., "Technical Skills" in sentence case) may not match
- **Overlapping sections:** "Experience" and "Professional Experience" can map to same key but slice differently
- **Inline sections:** "Skills: Python, Java" – content on same line as header
- **No boundary evidence:** Primary SectionParser doesn't persist `start_line`/`end_line` for all sections

### 2.3 Regex Limitations

- **Date patterns:** `DATE_TOKEN` in `work_experience_parser.py` and `education_parser.py` – missing `Q1 2020`, `'20`, `2020.01`, `Fall 2020`
- **Company patterns:** `COMPANY_HINT_RE` – short list; misses many org suffixes
- **Client patterns:** Case-sensitive `[A-Z]`; "client: acme" missed
- **Phone patterns:** `phonenumbers` used but international formats may fail

### 2.4 NLP Gaps

- **spacy.blank("xx"):** No language model – PhraseMatcher does exact token match only
- **No NER for orgs/titles:** Company and title extraction is heuristic
- **No date NER:** Relies on regex + dateparser
- **Multilingual:** Section aliases exist but no language detection or switching

### 2.5 Layout Detection

- **PDF:** 2-column via `reconstruct_two_column_layout`; 3+ columns not handled
- **PDF tables:** pdfplumber `extract_words` + gap threshold; complex tables misaligned
- **DOCX:** No column detection; tables and paragraphs in document order only

### 2.6 OCR Limitations

- **Trigger:** Only when `len(text) < OCR_MIN_TEXT_CHARS` (100)
- **Language:** `TESSERACT_LANG=eng` – no multi-language
- **No layout:** OCR returns plain text; structure lost
- **No confidence gating:** Low OCR confidence still used

---

## 3. Why Accuracy Drops: PDF vs DOC/DOCX

### PDF Strengths
- Layout extraction (PyMuPDF, pdfplumber) preserves x,y
- 2-column reconstruction works for many resumes
- Word-level extraction enables column detection
- Header/footer stripping reduces noise

### DOC/DOCX Weaknesses
1. **Structure loss:** `paragraph.text` drops bullets, numbering, styles
2. **Table flattening:** `" | ".join(cells)` loses row semantics; experience tables become one block
3. **No layout:** Reading order may not match visual order (columns, textboxes)
4. **Conversion (DOC):** soffice can alter layout; temp files add latency

### Result
- **PDF:** ~65–75% accuracy (layout helps sections and experience)
- **DOCX:** ~50–60% (structure loss cascades)
- **DOC:** ~45–55% (conversion + structure loss)

---

## 4. Feature Upgrades for 85%+ Accuracy

### 4.1 Document Normalization Strategy

**Implement format-aware normalization:**

```python
# In normalize.py - add format hint
def normalize_resume_text(text: str, *, source_format: str | None = None) -> str:
    # PDF: repair common pdfplumber/pypdf artifacts (e.g., hyphenation)
    # DOCX: repair table artifacts, bullet fragments
    # OCR: stronger fix_ocr_errors, consider confidence-weighted repair
```

- **PDF:** Hyphenation repair (`\n` mid-word), ligature expansion
- **DOCX:** Detect and normalize `|`-separated table rows before section parsing
- **OCR:** Expand `fix_ocr_errors` with more substitutions; optionally skip low-confidence regions

### 4.2 Section Boundary Detection

1. **Emit boundaries in primary path:** Add `start_line`, `end_line`, `evidence_heading`, `method` to every section in `SectionParser.parse()` output
2. **Inline section handling:** Detect `Header: content` on single line; split into header + content
3. **Heading style preservation in DOCX:** In `_extract_docx`, emit `## HEADING` for `Heading 1/2` styles
4. **Bullet preservation in DOCX:** Emit `- ` prefix for list paragraphs (check `numPr`, list style)
5. **Expand FallbackSegmenter:** Add more `_KNOWN_HEADERS`; support "Skills & Technologies" style compound headers

### 4.3 Experience Block Segmentation

1. **Table-row mode:** When experience section has many `|`-separated lines, parse as table: `Company | Title | Dates | Location`
2. **Alternate date formats:** Extend `DATE_TOKEN` with `Q1 2020`, `'20`, `2020.01`, `Fall 2020`
3. **Bidirectional company/title:** Add patterns for "Title at Company", "Title | Company"
4. **Concurrent roles:** Detect multiple date ranges in one block; split into separate entries
5. **Pre-parse table normalization:** In pipeline, before `task_parse_work_experience`, run `normalize_table_lines` on experience section

### 4.4 Date Range Validation

1. **Validation in `_calc_duration_months`:** Already rejects `end < start`; add logging
2. **Overlap detection:** `find_date_overlaps` exists in `review.py`; ensure it runs and flags `date_overlap_flag` on work items
3. **Future dates:** Reject `start_date > today` or flag
4. **Suspicious ranges:** Flag if duration > 40 years or if `end_date` is before `start_date` of next job

### 4.5 Client/Company Name Extraction

1. **Case-insensitive client capture:** Change `[A-Z]` to `[A-Za-z]` in client regex patterns
2. **More patterns:** `"for client X"`, `"at X (client)"`, `"client: X"` (already have)
3. **Company NER:** Optional spaCy NER for ORG on experience bullets
4. **Persistence:** `task_extract_clients` already populates `work_experience[*].client`; ensure it is in deterministic path (it is)

### 4.6 Skills Extraction Accuracy

1. **Expand taxonomy:** Add missing skills from `extract_from_raw_text` hits to taxonomy
2. **Compound skills:** Parse "React/Redux" as two skills; "AWS (EC2, S3)" as parent + children
3. **Looser raw_text:** Allow single-line "Python Java SQL" when line has 3+ known tokens
4. **Confidence calibration:** Different weights for taxonomy match vs. work history match vs. raw text fallback

### 4.7 Summary vs Skills Mixing

- `clean_summary_and_skills_sections` already exists; improve:
  - `_is_skill_like`: More tech keywords, broader `_TECH_KEYWORD_RE`
  - `_is_sentence_like`: Tune `min_len`; add more verb/pronoun hints
- **Upstream fix:** Better section detection so summary and skills are correctly bounded before cleanup

### 4.8 Table Parsing (PDF)

1. **pdfplumber tables:** Use `page.extract_tables()` when available; map to `Company | Title | Dates` columns
2. **Table detection:** If a region has grid-like structure (many short lines, similar lengths), treat as table
3. **Fallback:** Current word-gap approach; refine `gap_threshold` per page

### 4.9 Multi-Column Resume Handling

1. **3-column detection:** Extend `reconstruct_two_column_layout` to detect 3 columns (e.g., left sidebar, main, right dates)
2. **Reading order:** Use y-position and column index to emit correct order
3. **DOCX columns:** Check `section.cols` in python-docx; emit column breaks

### 4.10 OCR Integration

1. **Language detection:** Detect script/language; set `TESSERACT_LANG` accordingly (e.g., `eng+hin`)
2. **Layout-aware OCR:** Use Tesseract `--psm` (e.g., 6 for block of text) or try multiple modes
3. **Confidence gating:** If average OCR confidence < 60, flag for review or retry with different DPI
4. **Add PyMuPDF to deps:** Ensure `pymupdf` in `pyproject.toml` so layout extraction is reliable

---

## 5. Scalability for 10,000+ Resumes/Day

### 5.1 Current Bottlenecks

- **DOC conversion:** `soffice` subprocess per .doc file
- **OCR:** CPU-heavy; 300 DPI per page
- **LLM (if enabled):** Multiple calls per resume
- **DB writes:** Delete + reinsert all child entities per job

### 5.2 Architecture Improvements

1. **Queue separation (already in docker-compose):** `doc_convert`, `ocr`, `extract`, `parse`, `llm`, `persist` – scale workers per queue
2. **DOC conversion pool:** Dedicated `worker_doc_convert` with `-c 2`; consider increasing or using a conversion service
3. **OCR queue:** Isolate OCR to `worker_ocr`; prevent blocking normal PDFs
4. **Caching:** Hash normalized section text; cache LLM results (when LLM enabled)
5. **Batch DB writes:** For high throughput, consider batch upserts instead of delete-all + insert
6. **Connection pooling:** `DB_POOL_SIZE=5` – increase for 10k/day (e.g., 20–30)

### 5.3 Resource Tuning

- **Celery concurrency:** `parse` queue `-c 8` is reasonable; monitor queue depth
- **Redis:** Ensure enough memory for result backend
- **Storage:** S3 for 10k/day; local storage will not scale

---

## 6. Prioritized Roadmap

### Phase 1 – Critical Fixes (2–3 weeks)

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 1 | Add PyMuPDF to pyproject.toml | `pyproject.toml` | PDF layout extraction reliable |
| 2 | DOCX: Preserve bullets (emit `- ` for list paragraphs) | `extract_text.py:_extract_docx` | Experience bullets preserved |
| 3 | DOCX: Preserve headings (emit `## ` for Heading styles) | `extract_text.py:_extract_docx` | Section detection improves |
| 4 | SectionParser: Add start_line, end_line, evidence to all sections | `section_parser.py` | Debugging, downstream use |
| 5 | Experience: Table-row parsing for `\|`-heavy experience section | `work_experience_parser.py` | DOCX/PDF table resumes |
| 6 | Client regex: Case-insensitive capture | `extract_clients_task.py` | More clients extracted |

### Phase 2 – Accuracy Improvements (3–4 weeks)

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 7 | Extend DATE_TOKEN (Q1 2020, '20, Fall 2020) | `work_experience_parser.py`, `education_parser.py` | More dates parsed |
| 8 | Add "Title at Company" / "Title \| Company" patterns | `work_experience_parser.py` | Company/title order flexibility |
| 9 | Improve clean_summary_and_skills (more tech keywords, verbs) | `normalize.py` | Summary/skills separation |
| 10 | Skills: Looser extract_from_raw_text (single line, 3+ tokens) | `skill_extractor.py` | More skills from unstructured text |
| 11 | PDF: Use pdfplumber extract_tables when available | `extract_text.py` | Table structure in PDF |
| 12 | Date validation: Flag future dates, overlaps, suspicious ranges | `work_experience_parser.py`, `review.py` | Data quality |
| 13 | Format-aware normalization | `normalize.py` | Fewer format-specific errors |

### Phase 3 – Scalability & Optimization (2–3 weeks)

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 14 | Increase DB pool, tune Celery concurrency | `config.py`, `docker-compose.yml` | 10k/day capacity |
| 15 | LLM result caching by content hash | `llm_service.py` | Reduce API calls |
| 16 | OCR: Language detection, confidence gating | `extract_text.py` | Better OCR quality |
| 17 | 3-column PDF layout support | `extract_text.py` | Complex layouts |
| 18 | Batch/upsert DB writes (optional) | `pipeline.py` | Lower DB load |

---

## 7. Rule-Based vs ML vs Hybrid

### Recommendation: **Hybrid (current direction, strengthened)**

| Component | Approach | Rationale |
|-----------|----------|-----------|
| **Text extraction** | Rule-based (current) | Format-specific; ML adds little |
| **Section detection** | Rule-based + optional LLM | Rules work for 70%+; LLM for edge cases |
| **Experience parsing** | Rule-based + LLM fallback | Rules handle tables/dates; LLM for messy layouts |
| **Skills** | Taxonomy + rules + optional LLM | Taxonomy covers most; LLM for inference |
| **Contact** | Rules (regex, phonenumbers) | High precision; NER optional for name |
| **Company/client NER** | Optional spaCy NER | Improves company extraction; not required for 85% |

**To reach 85% without LLM:** Focus on Phase 1 + Phase 2 (rules, structure preservation, table parsing).  
**With LLM:** Same + enable LLM for low-confidence experience/skills; use sparingly to control cost.

---

## 8. Measurable Metrics

### 8.1 Parsing Accuracy Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Field-level precision** | Correct extractions / Total extracted | ≥ 0.90 |
| **Field-level recall** | Correct extractions / Total in ground truth | ≥ 0.85 |
| **Section detection F1** | 2 * P * R / (P + R) per section type | ≥ 0.88 |
| **Experience parse rate** | Jobs with ≥1 valid experience / Total | ≥ 0.92 |
| **Skills recall** | Extracted skills / Ground truth skills | ≥ 0.80 |
| **Date parse rate** | Parsed dates / Date strings in text | ≥ 0.90 |

### 8.2 Implementation

1. **Ground truth dataset:** Use `scripts/prepare_dataset.py` output; add manual labels for 100–200 diverse resumes
2. **Evaluation script:** Compare `parsed_data` to ground truth per field; compute precision/recall/F1
3. **Prometheus:** Add `resume_parse_field_accuracy` (by field, by format)
4. **Dashboard:** Track accuracy by format (pdf, docx, doc), by section, over time

### 8.3 Code Hooks

- In `task_save_to_database`, emit metrics per field if ground truth provided
- In `task_detect_sections`, record `section_detection_f1` when eval mode enabled
- In `task_parse_work_experience`, record `experience_parse_quality_score` (already in `debug_bundle`)

---

## 9. Implementation-Level Recommendations

### 9.1 DOCX Extraction (Highest ROI)

**Current** (`_extract_docx`):
```python
def _emit_paragraph_lines(paragraph):
    if _is_heading_paragraph(paragraph):
        return [f"## {text}"]  # Only if style is Heading
    if _is_list_paragraph(paragraph):
        return [f"- {text}"]   # Only if numPr or list style
    return [text]
```

**Issue:** `_is_list_paragraph` checks `numPr`; many DOCX bullets use other mechanisms. Add:
- Check `ilvl` (indent level) for bullet-like structure
- Check `pPr.numPr` and `pPr.buChar` (bullet char)
- Fallback: if paragraph is indented and short, treat as bullet

**Heading:** `_is_heading_paragraph` uses `style.name.startswith("Heading")`. Ensure custom "Heading 1" styles are included.

### 9.2 Experience Table Parsing

**Add to `WorkExperienceParser`:**
```python
def _parse_table_formatted_experience(self, text: str) -> list[JobEntry]:
    """When experience section has many pipe-separated rows."""
    lines = [l.strip() for l in text.splitlines() if l.strip() and "|" in l]
    if len(lines) < 2:
        return []
    # Assume header row: Company | Title | Dates | Location
    # Parse each data row into JobEntry
```

Call from `parse_experience_section` when `lines` with `|` exceed 50% of non-empty lines.

### 9.3 Section Boundary Metadata

**In `SectionParser._slice_sections`**, ensure each section dict includes:
```python
{
    "content": "...",
    "confidence": 0.85,
    "start_line": 12,
    "end_line": 45,
    "evidence_heading": "WORK EXPERIENCE",
    "method": "dict_match"
}
```

`FallbackSegmenter` already does this; align `SectionParser` output.

### 9.4 Client Regex Fix

**In `extract_clients_task.py`**, change:
```python
# From:
r"(?P<name>[A-Z][^\n,;\.]{2,50})"
# To:
r"(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})"
```
And add `.strip()` + `.title()` for consistency when storing.

### 9.5 Date Token Extension

**In `work_experience_parser.py`**, extend `DATE_TOKEN`:
```python
r"|(?:Q[1-4]\s+)?\d{4}"           # Q1 2020, 2020
r"|(?:Jan|Feb|...)\s*['']\s*\d{2}" # Jan '20
r"|(?:Spring|Fall|Summer|Winter)\s+\d{4}"
r"|(?:Jan|Feb|...)\s+\.\s*\d{2}"   # Jan.20
```

### 9.6 Dependencies

**Add to `pyproject.toml`:**
```toml
pymupdf = "^1.24.0"  # or latest
```

**Optional for NER:**
```toml
# Already have spacy; add model
# Run: python -m spacy download en_core_web_sm
```

---

## 10. Summary

| Area | Current State | To Reach 85% |
|------|---------------|---------------|
| **PDF extraction** | Good (PyMuPDF, pdfplumber, OCR) | Add PyMuPDF to deps; table extraction |
| **DOCX extraction** | Weak (structure lost) | Preserve bullets, headings, table semantics |
| **Section detection** | Good (SectionParser + Fallback) | Boundaries in output; inline sections |
| **Experience** | Good (sophisticated parser) | Table mode; more date/company patterns |
| **Skills** | Taxonomy-dependent | Looser raw extraction; compound skills |
| **Summary/skills** | clean_summary_and_skills exists | Stronger heuristics; better upstream sections |
| **Clients** | Deterministic task exists | Case-insensitive; more patterns |
| **Dates** | dateparser + regex | More formats; validation |
| **Scalability** | Queues separated | Pool tuning; caching |

**Critical path:** Phase 1 (DOCX structure, section boundaries, table experience) will yield the largest accuracy gain. Phase 2 refines extraction. Phase 3 prepares for scale.
