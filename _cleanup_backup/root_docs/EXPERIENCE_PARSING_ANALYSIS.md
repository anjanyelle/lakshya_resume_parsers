# Experience Parsing: End-to-End Technical Analysis

## 1. Flow Map (Data Path)

```
PDF/DOC/DOCX
    → extract_text_task (extract_text.py)
    → job.raw_text
    → task_detect_sections (SectionParser.parse)
    → parsed_data["sections"]["experience"] = { content, confidence }
    → task_parse_work_experience
    → parsed_data["work_experience"] = [{ company, title, start_date, end_date, ... }]
    → _apply_llm_resume (in task_save_to_database)
    → sanitize_work_experience_entries
    → WorkHistory rows (company_name, job_title, start_date, end_date, ...)
    → Candidate.work_history (SQLAlchemy relationship)
    → CandidatePublicRead.model_validate(candidate)
    → API GET /candidates/{id} → work_history: WorkHistoryRead[]
    → Frontend WorkHistoryTimeline(items=candidate.work_history)
```

**Key files:**

- `backend/app/services/parser/extract_text.py` – raw text
- `backend/app/services/parser/section_parser.py` – section detection
- `backend/app/workers/pipeline.py` – `task_detect_sections`, `task_parse_work_experience`, `task_save_to_database`
- `backend/app/services/parser/work_experience_parser.py` – experience parsing
- `backend/app/services/parser/work_experience_sanitizer.py` – filtering
- `backend/app/models/work_history.py` – DB schema
- `backend/app/schemas/candidate.py` – API schema
- `frontend/src/components/candidate-detail/WorkHistoryTimeline.tsx` – UI

---

## 2. Root Cause Analysis

### 2.1 Section boundary detection failure

**Location:** `section_parser.py`, `fallback_segmenter.py`

**Issue:** `sections.get("experience", {})` can be empty if:

- No header like "Work Experience" / "Professional Experience" is detected
- Multi-column PDFs: text order breaks header→content mapping
- `_slice_sections` / `_infer_sections_no_headers` mis-assigns lines
- `_length_heuristic_boost` penalizes short experience (<220 chars) with -0.12 confidence

**Checkpoint:** Log `parsed_data["sections"]` after `task_detect_sections`. Inspect `sections["experience"]["content"]` length and `confidence`.

---

### 2.2 Experience section key / content mismatch

**Location:** `pipeline.py:2099`

```python
experience_block = sections.get("experience", {})
experience_text = experience_block.get("content", "")
```

Section keys are canonicalized (`work_experience` → `experience`). If section detection produces `professional_experience` or `work_history`, they map to `experience`. If detection fails entirely, `experience` is missing and `experience_text` is empty.

**Checkpoint:** Verify `sections` keys. If `experience` is absent, `task_parse_work_experience` falls back to `raw_text` (line 2131).

---

### 2.3 Work experience parser block segmentation

**Location:** `work_experience_parser.py:418-477` – `extract_individual_jobs`

**Issue:** Boundaries depend on:

- `DATE_ANCHOR_RE` / `DATE_RANGE_RE` / `PRESENT_RE`
- `_has_date_anchor(line)` – lines with date patterns

If dates use non-standard formats (e.g. "Q1 2020", "20.01", regional formats), no boundaries are found → `return ["\n".join(lines)]` → single chunk → poor parsing.

**Checkpoint:** Log `chunks` from `extract_individual_jobs`. If you see one large chunk, date detection failed.

---

### 2.4 Date normalization / parsing

**Location:** `work_experience_parser.py` – `_parse_dates`, `DATE_RANGE_RE`; `pipeline.py:567` – `_parse_date_str`

**Issue:**

- `_parse_date_str` uses `dateparser.parse(value, settings={"PREFER_DAY_OF_MONTH": "first"})`. `None` input → `None` output.
- `sanitizer._normalize_date_token` only does `_collapse_spaces`; it does not parse. Dates stay as strings.
- If `start_date` / `end_date` are `None` or unparseable, `_has_any_date` is false.

**Checkpoint:** Log `entry.get("start_date")`, `entry.get("end_date")` before sanitizer. Log `_has_any_date(normalized)` result.

---

### 2.5 Sanitizer drops valid entries (critical)

**Location:** `work_experience_sanitizer.py:176-178`

```python
if not _has_any_date(normalized) and not _has_any_body(normalized):
    continue  # DROPS ENTRY
```

**Issue:** Entries are dropped if:

- No `start_date` or `end_date` (or both empty after normalization)
- No `description` and no `bullets`

Many resumes have "Company | Title" and "2020 – Present" on separate lines. If date parsing fails or dates are missing, valid entries are removed.

**Checkpoint:** Log `cleaned` before and after this filter. Count dropped entries.

---

### 2.6 Placeholder / skillish header filtering

**Location:** `work_experience_sanitizer.py:145-149`, `work_experience_parser.py:336-365`

**Issue:**

- `_is_placeholder(company)` or `_is_placeholder(title)` → entry dropped
- `_is_skillish(company)` or `_is_skillish(title)` → entry dropped (e.g. "Python, Java, AWS" mis-parsed as company)
- `_is_plausible_job` requires `has_dates or (has_body and company and title and 2+ bullets)` for date-less jobs

**Checkpoint:** Log which entries fail `_is_placeholder` / `_is_skillish` / `_is_plausible_job`.

---

### 2.7 work_experience overwritten by LLM merge

**Location:** `pipeline.py:493-521` – `_apply_llm_resume`; `pipeline.py:3454-3466` – `llm_structured_verified` merge

**Issue:**

- `_apply_llm_resume`: if `work_experience` is missing or empty, it is filled from `llm_resume.project_client_experience` / `client_experience` / `projects`.
- `llm_structured` merge: if `_work_experience_is_low_quality(existing)` and `incoming_ok`, `parsed["work_experience"]` is replaced by LLM data. LLM can overwrite good deterministic results with empty or low-quality data.

**Checkpoint:** Log `parsed.get("work_experience")` before and after `_apply_llm_resume` and after the `llm_structured` merge.

---

### 2.8 DB schema mapping

**Location:** `pipeline.py:3782-3795`

```python
WorkHistory(
    company_name=entry.get("company"),   # parsed uses "company"
    job_title=entry.get("title"),       # parsed uses "title"
    ...
)
```

**Issue:** Mapping is correct. `WorkHistoryRead` uses `company_name`, `job_title`; frontend expects `company_name`, `job_title`. No mismatch here.

---

### 2.9 Frontend / API contract

**Location:** `WorkHistoryTimeline.tsx`, `types/candidate.ts`

**Issue:** Frontend expects `item.job_title`, `item.company_name`, `item.id`. API returns `WorkHistoryRead` with those fields. No mismatch.

---

### 2.10 String vs array

**Issue:** `work_experience` is always a list in `parsed_data`. `sanitize_work_experience_entries` returns `list[dict]`. DB stores one row per entry. No string/array confusion.

---

## 3. Debugging Checkpoints

| #   | Location                                          | Log                                                                          | Purpose           |
| --- | ------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------- |
| 1   | `task_detect_sections` end                        | `sections.keys()`, `sections.get("experience", {}).get("content", "")[:200]` | Section detection |
| 2   | `task_parse_work_experience` start                | `has_experience_section`, `len(experience_text)`, `exp_conf`                 | Section input     |
| 3   | `task_parse_work_experience` before payload       | `len(primary_jobs)`, `primary_score`, `llm_triggered`                        | Parser output     |
| 4   | `task_parse_work_experience` end                  | `len(payload)`, `payload[0]` if any                                          | Final payload     |
| 5   | `task_save_to_database` after `_apply_llm_resume` | `len(parsed.get("work_experience", []))`                                     | Post-merge        |
| 6   | `sanitize_work_experience_entries`                | Input count, output count, sample dropped entry                              | Sanitizer filter  |
| 7   | `task_save_to_database` before session.add        | `len(work_entries)`, `work_entries[0]` if any                                | Pre-DB            |

---

## 4. Logging Strategy

Add structured logging in `pipeline.py`:

```python
# In task_parse_work_experience, after line 2105:
logger.info(
    "Experience section input",
    extra={
        "job_id": job_id,
        "has_experience_section": has_experience_section,
        "experience_text_len": len(experience_text or ""),
        "exp_conf": exp_conf,
        "raw_text_len": len(raw_text or ""),
    },
)

# After payload construction (before _update_job):
logger.info(
    "Experience parse result",
    extra={
        "job_id": job_id,
        "payload_count": len(payload),
        "first_entry_keys": list(payload[0].keys()) if payload else [],
        "has_dates_in_first": bool(payload and (payload[0].get("start_date") or payload[0].get("end_date"))),
    },
)

# In task_save_to_database, before sanitize:
raw_we = parsed.get("work_experience", [])
logger.info(
    "Pre-sanitize work_experience",
    extra={
        "job_id": job_id,
        "raw_count": len(raw_we) if isinstance(raw_we, list) else 0,
        "raw_type": type(raw_we).__name__,
    },
)

# After sanitize:
logger.info(
    "Post-sanitize work_entries",
    extra={
        "job_id": job_id,
        "sanitized_count": len(work_entries),
        "dropped_count": len(raw_we) - len(work_entries) if isinstance(raw_we, list) else 0,
    },
)
```

---

## 5. Recommended Fixes

### 5.1 Relax sanitizer date/body requirement (high impact)

**File:** `work_experience_sanitizer.py`

**Change:** Allow entries with company + title even without date/body, or add a confidence-based bypass:

```python
# Option A: Allow company+title only when both present
if not company and not title:
    continue
if not _has_any_date(normalized) and not _has_any_body(normalized):
    # Only drop if we also lack company/title
    if not company or not title:
        continue
    # Or: allow through with a flag for review
    normalized["_needs_review"] = True
cleaned.append(normalized)
```

### 5.2 Improve date parsing robustness

**File:** `pipeline.py` – `_parse_date_str`

**Change:** Handle more formats and avoid `None` for obvious date strings:

```python
def _parse_date_str(value: str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    # dateparser handles many formats; add DATE_FORMATS if needed
    parsed = dateparser.parse(raw, settings={"PREFER_DAY_OF_MONTH": "first"})
    return parsed.date() if parsed else None
```

### 5.3 Merge experience sections (work_experience + professional_experience)

**File:** `pipeline.py` – `task_parse_work_experience`

**Change:** Aggregate content from all experience-like sections before parsing:

```python
experience_candidates = ["experience", "work_experience", "professional_experience", "employment"]
experience_text = ""
for key in experience_candidates:
    block = sections.get(key, {}) if isinstance(sections, dict) else {}
    if isinstance(block, dict):
        content = str(block.get("content", "") or "").strip()
        if content and len(content) > len(experience_text):
            experience_text = content
            experience_block = block
```

### 5.4 Preserve deterministic work_experience over low-quality LLM

**File:** `pipeline.py` – `llm_structured` merge block (~3455)

**Change:** Do not overwrite non-empty deterministic `work_experience` with empty LLM data:

```python
if key == "work_experience":
    incoming_ok = not _work_experience_is_low_quality(value)
    existing_ok = not _work_experience_is_low_quality(existing) if existing else False
    # Prefer deterministic if LLM is empty or low quality
    if existing and not value:
        continue  # Keep existing
    if _work_experience_is_low_quality(existing) and value and incoming_ok:
        parsed[key] = value
    elif existing is None and incoming_ok:
        parsed[key] = value
    continue
```

### 5.5 Add debug endpoint for experience pipeline

**File:** `backend/app/api/v1/endpoints/candidates.py` or `admin.py`

**Change:** Add an endpoint that returns `parsed_data.work_experience`, `parsed_data.sections.experience`, and `candidate.work_history` for a given job/candidate to compare pipeline stages.

---

## 6. Production Fix Strategy

1. **Immediate:** Add logging at checkpoints 1–7. Reproduce with a failing resume and inspect where experience is lost.
2. **Short-term:** Relax sanitizer (5.1) so entries with company+title are kept even without dates.
3. **Short-term:** Harden `_parse_date_str` and ensure `start_date`/`end_date` are preserved through sanitizer.
4. **Medium-term:** Merge multiple experience section keys (5.3).
5. **Medium-term:** Adjust LLM merge so deterministic results are not overwritten by empty LLM output (5.4).
6. **Ongoing:** Add a debug endpoint (5.5) for support and regression checks.

---

## 7. Quick Validation Commands

```bash
# Run a single resume through the pipeline and inspect logs
cd backend && python -c "
from app.workers.pipeline import task_detect_sections, task_parse_work_experience
from app.core.database import SessionLocal
from app.models.parsing_job import ParsingJob
# Load a job_id from a failed case, then:
# task_detect_sections(job_id)
# task_parse_work_experience(job_id)
# Inspect parsed_data in DB
"
```

```bash
# Unit test sanitizer with a minimal entry (no dates)
cd backend && python -c "
from app.services.parser.work_experience_sanitizer import sanitize_work_experience_entries
entries = [{'company': 'Acme', 'title': 'Engineer', 'start_date': None, 'end_date': None, 'description': ''}]
out = sanitize_work_experience_entries(entries)
print('Input:', len(entries), 'Output:', len(out))  # Expect 0 due to current filter
"
```
