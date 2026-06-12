# Resume Parser Deep Audit Report

## Executive Summary

The parser extracts email and phone correctly but fails on skills, experience, education, and confidence scoring. **Root cause: a duplicate method definition in `hybrid_merger.py` crashes the entire merge silently, falling back to an incomplete result.** Several secondary bugs compound the problem.

---

## 1. Root Cause Analysis

### CRITICAL BUG #1 — Duplicate `_merge_union_fields` causes silent merge crash

**File:** `ai-service/parsers/hybrid_merger.py`

`_merge_union_fields` is defined **twice** (lines 222 and 373). Python silently overwrites the first with the second. The second definition calls `stats['union_merge_used'] += 1`, but the `merge_stats` dict (created in `merge()`) only has the key `union_fields_used`. This raises a `KeyError`.

The `merge()` method wraps everything in `try/except Exception` and returns `rule_result` as fallback. **All structured data (skills, experience, education) from AI and experience extractor is thrown away.** This is why:

- Skills tab is empty
- Experience shows garbage
- Confidence is 0%

**Fix:** Delete the duplicate definition at lines 373–411 and rename the stats key to be consistent.

### CRITICAL BUG #2 — NER model loads with wrong architecture

**File:** `ai-service/parsers/ai_ner_parser.py`

The startup log shows:

```
classifier.bias   | MISSING
classifier.weight | MISSING
```

`jjzha/jobbert-base-cased` is a **masked language model** checkpoint. Loading it as `token-classification` (NER) gives randomly initialized classifier weights. The model produces random entity labels — it cannot reliably identify names, companies, or locations.

### CRITICAL BUG #3 — Experience date defaults to Unix epoch Jan 1, 1970

**File:** `ai-service/parsers/experience_extractor.py`

When `dateparser.parse()` cannot parse a date string, it returns `datetime(1970, 1, 1, 0, 0)` (Unix epoch). The extractor does not guard against this. Screenshot shows "Jan 1, 1970 - Present" — confirming the date string from the PDF was not parseable.

### CRITICAL BUG #4 — Section splitter misses PDF section headers

**File:** `ai-service/parsers/section_splitter.py`

The section header regex:

```python
r'^\s*([A-Z][A-Z\s]{2,}|[A-Za-z][A-Za-z\s&/-]{3,})\s*[:\-=_]*\s*$'
```

Fails on PDF-extracted headers that contain inline artifacts, trailing spaces, or `(cid:xxx)` sequences from font encoding. When no section is detected, `_extract_experience()` and `_extract_education()` fall back to the **full resume text** — including all bullet points — which is why "tracking." (last word of a bullet) becomes the job title.

### CRITICAL BUG #5 — `_merge_results` silently drops experience/education skills

**File:** `ai-service/parsers/master_parser.py` lines 468–481

```python
for key, value in experience_results.items():
    if key not in combined_rule:   # <-- only adds if not present
        combined_rule[key] = value
```

Since `rule_results` always has a `skills` key (from `extract_skills`), experience-derived skills are never added to `combined_rule`.

---

## 2. Detailed Issue List

### Architecture Issues

| #   | Severity | Issue                                                                                           |
| --- | -------- | ----------------------------------------------------------------------------------------------- |
| 1   | CRITICAL | Duplicate `_merge_union_fields` — second definition silently overwrites first                   |
| 2   | CRITICAL | `stats['union_merge_used']` KeyError crashes entire merge, returns bare rule_result             |
| 3   | CRITICAL | NER model classifier weights are randomly initialized (MISSING from checkpoint)                 |
| 4   | HIGH     | Section splitter falls back to full text when sections not found — corrupts all extractors      |
| 5   | HIGH     | dateparser returns epoch 1970-01-01 for unparseable dates, not guarded                          |
| 6   | HIGH     | `_merge_results` uses `if key not in combined_rule` — drops experience/education fields         |
| 7   | MEDIUM   | Summary extractor falls back to first long paragraph — picks up bullet points instead           |
| 8   | MEDIUM   | `experience_pattern.findall` returns list of tuples but code indexes `match[0]` after iterating |
| 9   | LOW      | Confidence scorer receives incomplete merged result → always scores 0%                          |

### Skills Extraction Issues

| #   | Severity | Issue                                                                              |
| --- | -------- | ---------------------------------------------------------------------------------- |
| 10  | HIGH     | AI NER skill model `Nucha/Nucha_ITSkillNER_BERT` may not load — falls back to None |
| 11  | HIGH     | Even if both rule+AI skills are found, merge crash discards AI skills              |
| 12  | MEDIUM   | Rule-based skill taxonomy hardcoded at ~90 entries — misses domain-specific tools  |

### Experience Extraction Issues

| #   | Severity | Issue                                                             |
| --- | -------- | ----------------------------------------------------------------- |
| 13  | CRITICAL | Job block splitter regex too simple for multi-line resume formats |
| 14  | HIGH     | Company name extraction picks up city name when format deviates   |
| 15  | HIGH     | Date epoch fallback not filtered — "Jan 1, 1970" stored in DB     |

---

## 3. Pipeline Breakdown with Failure Points

```
PDF Upload
    │
    ▼
Text Extraction          ← ✅ Works (pdfminer/pdfplumber)
    │
    ▼
Section Splitting        ← ⚠️  OFTEN FAILS on real PDFs (cid: artifacts, inline headers)
    │
    ├── Falls back to full text ← ❌ Corrupts all downstream extractors
    ▼
Rule Parsing             ← ✅ email, phone extracted correctly
    │                        ⚠️  skills extracted but may be incomplete
    ▼
AI NER Parsing           ← ❌ Model has random classifier — outputs garbage NER labels
    │                        ⚠️  Skill model may work if Nucha model loaded
    ▼
Experience Extraction    ← ❌ Runs on full text if section not found
    │                        ❌ Date epoch bug; job title picks up bullet words
    ▼
Education Extraction     ← ⚠️  Partially works if section detected
    ▼
merge() in HybridMerger  ← ❌ CRASHES with KeyError on stats['union_merge_used']
    │                        ❌ Returns bare rule_result (only email/phone/dates)
    ▼
Confidence Scoring       ← ❌ Scores 0% because merged_result is missing all fields
    ▼
Final Result             ← ❌ skills=[], work_experience=[], education=[], confidence=0%
```

---

## 4. Accuracy Metrics (Actual vs Expected)

Based on screenshot analysis of Anjan Yelle's resume:

| Field      | Expected             | Actual                        | Precision | Recall | F1   |
| ---------- | -------------------- | ----------------------------- | --------- | ------ | ---- |
| Name       | Anjan Yelle          | Anjan Yelle                   | 1.0       | 1.0    | 1.0  |
| Email      | ✅ Correct           | ✅ Correct                    | 1.0       | 1.0    | 1.0  |
| Phone      | ✅ Correct           | ✅ Correct                    | 1.0       | 1.0    | 1.0  |
| Skills     | ~20 skills           | 0 (empty tab)                 | 0.0       | 0.0    | 0.0  |
| Experience | 2 positions          | 1 corrupted entry "tracking." | 0.0       | 0.0    | 0.0  |
| Education  | B.E. CSE, MVSR       | Not shown                     | ~0.0      | ~0.0   | ~0.0 |
| Summary    | Professional summary | Raw bullet text dump          | 0.0       | 0.0    | 0.0  |
| Confidence | ~75–85%              | 0%                            | —         | —      | —    |

**Overall system accuracy: ~15%** (only contact info working)

---

## 5. Missing Components

| Component                    | Status                         | Impact                               |
| ---------------------------- | ------------------------------ | ------------------------------------ |
| Trained NER classifier       | Missing — base checkpoint used | Name/company extraction broken       |
| `skills_taxonomy.json`       | Missing (warning on startup)   | Falls back to 90-item hardcoded list |
| `sentence_transformers`      | Not installed                  | Semantic skill matching disabled     |
| `tesseract` OCR              | Not installed                  | Scanned PDFs cannot be processed     |
| Epoch date guard             | Missing                        | Corrupt dates stored in DB           |
| Section splitter PDF cleanup | Missing                        | Headers not reliably found           |

---

## 6. Why Rule-Based Performed Better

The previous rule-based system worked better because:

1. It directly matched regex patterns without a broken merge layer
2. Skills were matched against a taxonomy and returned directly — no hybrid crash
3. No dependency on a misconfigured NER model
4. Section detection failure did not cascade — rules ran on full text intentionally

The hybrid approach added the merge layer which introduced the silent KeyError crash, making the final output **worse** than pure rule-based.

---

## 7. Step-by-Step Fix Plan (Priority Order)

### Priority 1 — Fix the merge crash (30 minutes)

**`hybrid_merger.py`**: Delete the duplicate `_merge_union_fields` at lines 373–411. Fix the `merge_stats` key:

```python
# In merge(), change:
merge_stats = {
    'rule_priority_used': 0,
    'ai_priority_used': 0,
    'union_fields_used': 0,    # must match what _merge_union_fields uses
    'conflicts_resolved': 0,
    'union_merge_used': 0      # ADD this key
}
```

### Priority 2 — Fix epoch date guard (15 minutes)

**`experience_extractor.py`**, in `_parse_dates` / date parsing logic:

```python
parsed = dateparse(date_str)
if parsed and parsed.year < 2000:  # guard against epoch default
    parsed = None
```

### Priority 3 — Fix `_merge_results` to merge skills (15 minutes)

**`master_parser.py`** lines 468–481: Instead of `if key not in combined_rule`, merge list fields additively:

```python
for key, value in experience_results.items():
    if key in combined_rule and isinstance(combined_rule[key], list):
        combined_rule[key] = combined_rule[key] + (value if isinstance(value, list) else [])
    elif key not in combined_rule:
        combined_rule[key] = value
```

### Priority 4 — Fix section splitter for PDF text (1 hour)

**`section_splitter.py`**: Add PDF artifact cleanup before section detection:

```python
text = re.sub(r'\(cid:\d+\)', '', text)  # remove cid: artifacts
text = re.sub(r'\s{3,}', '\n', text)     # normalize whitespace columns
```

Also add uppercase-only header detection:

```python
if re.match(r'^[A-Z][A-Z\s]{3,}$', line.strip()):  # "PROFESSIONAL EXPERIENCE"
    # detected as section header
```

### Priority 5 — Replace NER model (2–4 hours)

Replace `jjzha/jobbert-base-cased` (MLM checkpoint) with a properly fine-tuned NER model. Options:

- `dslim/bert-base-NER` — standard CoNLL NER, works for PER/ORG/LOC
- `Jean-Baptiste/roberta-large-ner-english` — higher accuracy

```python
self.ner_pipeline = pipeline(
    task='ner',
    model='dslim/bert-base-NER',   # replace jjzha/jobbert-base-cased
    aggregation_strategy='simple',
    device=device
)
```

### Priority 6 — Fix summary section detection (30 minutes)

**`master_parser.py`** `_extract_summary`: Add explicit fallback skip for lines containing bullet points, dates, or cid: artifacts before selecting fallback paragraph.

---

## 8. Recommended Architecture

```
PDF/DOCX
    │
    ▼
Text Extraction (pdfminer + fallback pdfplumber)
    │
    ▼
PDF Artifact Cleanup (remove cid:, normalize whitespace)
    │
    ▼
Section Splitter (regex + keyword matching, ALL-CAPS header support)
    │
    ├── experience_text
    ├── education_text
    ├── skills_text
    └── summary_text
    │
    ▼
Rule Parser (runs on full text + per-section)
    ├── email, phone, linkedin, github  → high confidence
    ├── skills (taxonomy match)         → medium confidence
    └── name (first-line heuristic)     → medium confidence
    │
    ▼
Structured Extractor (runs per-section text)
    ├── ExperienceExtractor → work_experience[]
    └── EducationExtractor  → education[]
    │
    ▼
NER Parser (dslim/bert-base-NER) — OPTIONAL enrichment only
    ├── PER → candidate name candidate
    └── ORG → company name validation
    │
    ▼
HybridMerger (fixed, no crash)
    ├── RULE_PRIORITY: email, phone, dates
    ├── UNION: skills (rule + AI union)
    └── STRUCTURED: work_experience, education (from structured extractor)
    │
    ▼
Confidence Scorer
    │
    ▼
Final JSON Output
```

---

## 9. Code-Level Fixes Summary

| File                      | Line(s)            | Fix                                                           |
| ------------------------- | ------------------ | ------------------------------------------------------------- |
| `hybrid_merger.py`        | 373–411            | Delete duplicate `_merge_union_fields`                        |
| `hybrid_merger.py`        | 102–107            | Add `union_merge_used: 0` to `merge_stats` dict               |
| `experience_extractor.py` | date parse         | Guard against `year < 1990` epoch dates                       |
| `master_parser.py`        | 468–481            | Use additive list merge instead of `if key not in`            |
| `section_splitter.py`     | compile_patterns   | Add cid: artifact cleanup and ALL-CAPS header regex           |
| `ai_ner_parser.py`        | 14                 | Replace `jjzha/jobbert-base-cased` with `dslim/bert-base-NER` |
| `master_parser.py`        | `_extract_summary` | Skip bullet/date paragraphs in fallback                       |

---

## 10. Training Strategy

The current models do **not** need to be trained — the fix is to use an already fine-tuned NER model (`dslim/bert-base-NER`). Training is only needed if you want resume-domain-specific accuracy.

If training is desired:

1. **Dataset**: Label 500–1000 Indian resumes with PERSON, ORG, LOC, SKILL entities using Label Studio or Prodigy
2. **Format**: CoNLL-2003 BIO tagging format
3. **Base model**: `dslim/bert-base-NER` → fine-tune with your labeled data
4. **Training**: Hugging Face `Trainer` API, ~3–5 epochs, ~2 hours on GPU

For skills specifically, the rule-based taxonomy approach is more reliable than NER for structured skills sections — expand the taxonomy JSON rather than training a model.
