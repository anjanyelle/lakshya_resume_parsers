# Resume Parser: End-to-End Debugging Analysis

## Executive Summary

This document analyzes five recurring issues in the Resume Parser system and provides ranked root causes, exact failure points, debug checkpoints, and fix strategies.

---

## Issue 1: Work History Missing for Some Resumes

### Root Cause Analysis (Ranked by Probability)

| Rank | Cause | Location | Probability |
|------|-------|----------|-------------|
| 1 | Sanitizer drops entries without date/body | `work_experience_sanitizer.py:176-178` | **HIGH** – Fixed in Prompt 1 |
| 2 | Section detection fails → experience section empty | `section_parser.py`, `task_parse_work_experience` | **HIGH** – Fixed with EXPERIENCE_KEYS |
| 3 | LLM overwrites good deterministic data with empty list | `pipeline.py` llm_structured merge | **MEDIUM** – Fixed in Prompt 2 |
| 4 | Date parsing fails → entries lack dates → sanitizer drops | `_parse_date_str`, `work_experience_parser` | **MEDIUM** – Fixed with date fallbacks |
| 5 | Block segmentation fails (single chunk) | `work_experience_parser.extract_individual_jobs` | **MEDIUM** |
| 6 | Placeholder/skillish header filtering | `work_experience_sanitizer`, `_is_plausible_job` | **LOW** |

### Exact Failure Points

1. **`work_experience_sanitizer.py`** – Filter `if not _has_any_date and not _has_any_body: continue` (relaxed in Prompt 1).
2. **`pipeline.py:2098-2125`** – Single-key `sections.get("experience")` missed `professional_experience`, etc. (fixed with EXPERIENCE_KEYS).
3. **`pipeline.py:3472-3484`** – LLM merge overwrote deterministic `work_experience` with empty list (fixed in Prompt 2).
4. **`pipeline.py:3803`** – `sanitize_work_experience_entries(parsed.get("work_experience", []))` – if `parsed` has empty list after merge, nothing saved.

### Debug Checkpoints

- **DIAG 1** (after `task_detect_sections`): `sections keys`, `exp_len`, `exp_conf`
- **DIAG 2** (after `primary_jobs`): `primary_jobs count`, first entry
- **DIAG 3** (pre-sanitize): `raw_we count`, first 3 entries
- **DIAG 4** (post-sanitize): `work_entries count`, `dropped` count

### Schema Validation

- `parsed_data["work_experience"]` must be `list[dict]` with keys: `company`, `title`, `start_date`, `end_date`, `description`, `bullets`
- `WorkHistory` model: `company_name`, `job_title`, `start_date`, `end_date`, `description`
- API `WorkHistoryRead`: `company_name`, `job_title` – **no mismatch**
- Frontend `WorkHistory`: `company_name`, `job_title` – **no mismatch**

---

## Issue 2: Summary Contains Duplicate Text

### Root Cause Analysis (Ranked by Probability)

| Rank | Cause | Location | Probability |
|------|-------|----------|-------------|
| 1 | Section canonicalization merges duplicate content | `section_parser._canonicalize_sections` | **HIGH** |
| 2 | `clean_summary_and_skills_sections` moves lines back and forth | `normalize.clean_summary_and_skills_sections` | **MEDIUM** |
| 3 | Multiple summary-like headers (Profile, Summary, Objective) map to same key | `section_parser._canonical_section_key` | **HIGH** |
| 4 | `_guess_summary_from_raw_text` overlaps with `summary_section` | `pipeline._guess_summary_from_raw_text` | **LOW** |

### Exact Failure Points

1. **`section_parser.py:2923-2941`** – `_canonicalize_sections`:
   ```python
   canonical.setdefault(canonical_key, []).extend(lines or [])
   ```
   If "profile" and "summary" both map to "summary", their lines are concatenated. If both sections contain similar content (e.g. "Experienced engineer..."), duplicates result.

2. **`normalize.py:397-398`** – `out_summary["content"] = "\n".join([*kept_summary, *moved_to_summary])` – No deduplication of lines before join.

3. **`section_parser.py:2982-2999`** – `_canonical_section_key` maps `profile`, `professional_profile`, `summary`, `objective`, etc. all to `"summary"`. Multiple headers → one section with merged lines → potential duplicates.

### Debug Checkpoints

- Log `sections["summary"]["content"]` line count and line hashes before/after `clean_summary_and_skills_sections`.
- Log `cleaned_counts` – `moved_summary_to_skills`, `moved_skills_to_summary`.
- Log `_canonicalize_sections` input keys vs output keys.

### Fix Strategy

1. **Deduplicate in `_canonicalize_sections`**: Before `extend`, dedupe lines by normalized content (e.g. `seen.add(line.strip().lower())`).
2. **Deduplicate in `clean_summary_and_skills_sections`**: Before building `out_summary["content"]`, remove duplicate lines (e.g. by `dict.fromkeys` order-preserving dedup).
3. **Deduplicate in `task_save_to_database`**: Before setting `candidate.summary`, run `"\n".join(dict.fromkeys(summary.splitlines()))` or similar.

---

## Issue 3: Candidate Name Missing or Incorrect

### Root Cause Analysis (Ranked by Probability)

| Rank | Cause | Location | Probability |
|------|-------|----------|-------------|
| 1 | Name not in top 30 lines (ContactExtractor limit) | `contact_extractor.extract_name` | **HIGH** |
| 2 | `_is_plausible_person_name` rejects valid names | `pipeline._is_plausible_person_name` | **MEDIUM** |
| 3 | `NAME_LABEL_REGEX` / spaCy NER miss non-standard formats | `contact_extractor.extract_name` | **MEDIUM** |
| 4 | Merge logic prefers existing (wrong) over incoming | `pipeline.py:3815-3822` | **LOW** |
| 5 | `_guess_name_from_raw_text` returns tool list | `pipeline._guess_name_from_raw_text` | **LOW** |

### Exact Failure Points

1. **`contact_extractor.py:886`** – `top_lines = lines[:30]` – Name beyond line 30 is never considered.
2. **`contact_extractor.py:889`** – `NAME_LABEL_REGEX` – Requires explicit "Name:" label; many resumes put name as first line without label.
3. **`pipeline.py:3815-3822`** – Merge logic:
   ```python
   if _is_plausible_person_name(incoming_name) and (
       not existing_name or not _is_plausible_person_name(existing_name) or _looks_like_tool_list(existing_name)
   ):
       candidate.full_name = incoming_name
   ```
   If `existing_name` is "Python, Java" (tool list), we replace. But if `incoming_name` is empty and `existing_name` is wrong, we keep wrong.
4. **`pipeline.py:3816`** – `incoming_name = name or _guess_name_from_raw_text(job.raw_text)` – `name` comes from `contact["name"]["name"]`. If contact extractor failed, we fall back to guess.

### Debug Checkpoints

- Log `contact["name"]`, `personal_info.full_name`, `incoming_name`, `existing_name` before merge.
- Log `_is_plausible_person_name(incoming_name)` and `_looks_like_tool_list(existing_name)`.
- Log first 5 lines of `raw_text` (name often on line 1).

### Fix Strategy

1. **Expand name extraction window**: Use first 50 lines or first 500 chars for name detection.
2. **First-line heuristic**: If line 1 is 2–4 title-cased words, no digits, no @, treat as name.
3. **Relax `_is_plausible_person_name`**: Allow single-word names (e.g. "Madonna") or 6+ word names (e.g. "Dr. John Robert Smith Jr.") when confidence is high.
4. **Prefer incoming when existing is low-confidence**: If `existing_name` came from a low-confidence source, prefer `incoming_name` when plausible.

---

## Issue 4: Only 1–2 Clients Extracted When Multiple Exist

### Root Cause Analysis (Ranked by Probability)

| Rank | Cause | Location | Probability |
|------|-------|----------|-------------|
| 1 | `_extract_first_client` returns on first match | `extract_clients_task._extract_first_client` | **HIGH** |
| 2 | Client patterns use `search` not `finditer` | `_STRONG_CLIENT_RE`, `_MEDIUM_CLIENT_RES` | **HIGH** |
| 3 | `task_extract_clients` runs before `work_experience` is populated | Pipeline order | **LOW** |
| 4 | Clients in bullets not in `_iter_text_sources` | `_iter_text_sources` includes description + bullets | **LOW** |

### Exact Failure Points

1. **`extract_clients_task.py:88-107`** – `_extract_first_client`:
   ```python
   m = _STRONG_CLIENT_RE.search(line2)
   if m:
       return cleaned, "high"  # RETURNS IMMEDIATELY – only first match
   ```
   A line like "Client: Acme Corp, Client: Beta Inc" – only "Acme Corp" is extracted.

2. **`_STRONG_CLIENT_RE`** – `r"client[s]?\s*[:–\-]\s*(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})"` – Matches one client per line. To get multiple, need `finditer` and collect all.

3. **`extract_clients_task.py:154-165`** – Per work item, `best` is single client. Each work entry gets at most one client. Clients list is built from unique across entries – so N work entries → up to N clients. But if one entry has "Client A, Client B, Client C" in description, we only get A.

### Debug Checkpoints

- Log `_extract_first_client` result per work item.
- Log `all_clients` before/after loop.
- Log raw description text for entries with multiple "Client:" mentions.

### Fix Strategy

1. **`_extract_all_clients`**: Replace `_extract_first_client` with `_extract_all_clients(text) -> list[tuple[str, str]]` that uses `finditer` for each pattern and collects all matches.
2. **Update work item loop**: For each item, call `_extract_all_clients` and merge into `item2["client"]` (or add `clients: list[str]` if schema supports multiple).
3. **Deduplicate**: Use `all_clients_set` to avoid duplicates when merging.

---

## Issue 5: Parsed Data Exists Internally but UI Shows Incomplete Data

### Root Cause Analysis (Ranked by Probability)

| Rank | Cause | Location | Probability |
|------|-------|----------|-------------|
| 1 | `work_history` comes from DB, not `parsed_data` | API returns `Candidate.work_history` | **HIGH** |
| 2 | Sanitizer dropped all entries before DB write | `task_save_to_database` | **HIGH** |
| 3 | Lazy loading / relationship not populated | SQLAlchemy `work_history` relationship | **LOW** |
| 4 | Frontend uses `candidate.work_history` not `parsed_data.work_experience` | `CandidateDetailPage`, `WorkHistoryTimeline` | **CONFIRMED** |
| 5 | API response transformation filters fields | `CandidatePublicRead` | **LOW** |

### Exact Failure Points

1. **Data flow**: `parsed_data.work_experience` → `sanitize_work_experience_entries` → `WorkHistory` rows → `Candidate.work_history`. If sanitizer returns `[]`, DB gets 0 rows. UI shows `candidate.work_history` = `[]`.

2. **`CandidateDetailPage.tsx:479`** – `WorkHistoryTimeline items={candidate.work_history}` – UI reads from `candidate`, not from `parsedData` or `latestJob.parsed_data`.

3. **`CorrectionSplitView`** – Uses `workHistory={candidate.work_history}` for display. Corrections view may show `parsedData` for comparison, but main display is `candidate`.

### Debug Checkpoints

- Compare `job.parsed_data.work_experience` (from latest job) vs `candidate.work_history` (from DB) for same candidate.
- Log `len(work_entries)` after sanitize – if 0, nothing written to DB.
- Verify API response includes `work_history` array (check network tab).

### Fix Strategy

1. **Ensure sanitizer keeps valid entries**: Already addressed in Prompt 1.
2. **Fallback UI**: If `candidate.work_history` is empty but `latestJob?.parsed_data?.work_experience` has data, show a banner: "Work history parsed but not yet saved. Retry processing or save corrections."
3. **Debug endpoint**: Expose `parsed_data.work_experience` vs `candidate.work_history` for a given job to diagnose mismatch.

---

## Schema Validation Checklist

| Layer | Field | Expected Type | Notes |
|-------|-------|---------------|-------|
| `parsed_data` | `work_experience` | `list[dict]` | Keys: company, title, start_date, end_date, description, bullets |
| `parsed_data` | `sections.summary.content` | `str` | May have duplicates |
| `parsed_data` | `contact.name.name` | `str` | Candidate name |
| `WorkHistory` | `company_name`, `job_title` | `str` | DB columns |
| `Candidate` | `full_name`, `summary` | `str` | DB columns |
| API `WorkHistoryRead` | `company_name`, `job_title` | `str` | Matches DB |
| Frontend `WorkHistory` | `company_name`, `job_title` | `str` | Matches API |

---

## Consolidated Fix Strategy

### Phase 1: Stabilize Experience (Already Applied)

- [x] Relax sanitizer (Prompt 1)
- [x] Multi-key experience section (EXPERIENCE_KEYS)
- [x] LLM merge guard (Prompt 2)
- [x] Date parsing fallbacks (Q1, Jan '20, Spring)
- [x] DIAG logging

### Phase 2: Summary Deduplication

1. In `section_parser._canonicalize_sections`: Dedupe lines when merging (e.g. `seen = set()`; only extend if `line.strip().lower() not in seen`).
2. In `clean_summary_and_skills_sections`: Dedupe `kept_summary` and `moved_to_summary` before join.
3. In `task_save_to_database`: Before `candidate.summary = inferred_summary`, dedupe lines.

### Phase 3: Name Extraction

1. Extend `extract_name` to use first 50 lines or 600 chars.
2. Add first-line heuristic: if line 1 matches `^[A-Z][a-z]+ [A-Z][a-z]+(\s+[A-Z][a-z]+){0,2}$`, use as name.
3. Log name extraction sources for debugging.

### Phase 4: Multi-Client Extraction

1. Implement `_extract_all_clients(text)` using `finditer`.
2. Update `task_extract_clients` to collect all clients per work item.
3. Consider `clients: list[str]` per work entry if schema allows.

### Phase 5: UI/API Alignment

1. Add debug endpoint: `GET /api/v1/candidates/{id}/parsing-debug` returning `parsed_data.work_experience` vs `work_history`.
2. Optional: Show "Parsed but unsaved" banner when `parsed_data` has data but DB is empty.

---

## Quick Reference: Key Files

| Issue | Primary File | Secondary |
|-------|--------------|------------|
| Work history | `pipeline.py`, `work_experience_sanitizer.py` | `work_experience_parser.py` |
| Summary duplicates | `section_parser.py`, `normalize.py` | `pipeline.py` |
| Name | `contact_extractor.py`, `pipeline.py` | `llm_service.py` |
| Clients | `extract_clients_task.py` | `work_experience_parser.py` (CLIENT_PATTERNS) |
| UI incomplete | `pipeline.py` (task_save_to_database) | `candidates.py` (API), `CandidateDetailPage.tsx` |
