# Roadmap to 85% Resume Parsing Accuracy

This document outlines issues, fixes, and a measurement strategy to reach **85% accuracy** for resume parsing.

---

## 1. Current State & Measurement

### How Accuracy Is Measured

| Tool | Purpose |
|------|---------|
| `tests/test_full_pipeline_regression.py` | Regression tests for key fixes (sanitizer, dates, dedup, name, clients) |
| `tests/ground_truth/test_accuracy.py` | Ground truth F1 for name, email, phone, skills |
| `tests/eval_resume_regression.py` | Full pipeline: section detection, contact, work, skills, education, certs |
| `tests/utils/accuracy_scoring.py` | Normalization: `normalize_string`, `normalize_date`, `normalize_skill` |

**Accuracy formula:** `overall = 0.4 * contact_accuracy + 0.4 * work_accuracy + 0.2 * skills_f1`

### Gaps to Fix First

1. **No ground truth dataset** – You need 50–100 resume PDFs with expected JSON to measure baseline.
2. **Accuracy report is placeholder** – `generate_accuracy_report()` does nothing.
3. **Inconsistent input quality** – PDF extraction varies by layout (columns, tables, OCR).

---

## 2. Standardization Issues

### 2.1 Input Standardization

| Issue | Impact | Fix |
|-------|--------|-----|
| Multi-column PDFs | Text order wrong → sections mis-assigned | Pre-process: column detection or layout analysis |
| OCR / scanned PDFs | Garbled text, wrong dates | `source_format="ocr"` in `normalize_resume_text`; consider OCR quality check |
| Tables in DOCX | Dates/companies in cells | `normalize_table_lines` already handles some; extend for more formats |
| Different file formats | PDF vs DOCX parsing differs | Run extraction pipeline per format; log `source_format` |

**Action:** Add `source_format` detection in `extract_text_task` and pass it through `normalize_resume_text`.

### 2.2 Schema Standardization

| Layer | Expected | Current |
|-------|----------|---------|
| `parsed_data.work_experience` | `company`, `title`, `start_date`, `end_date`, `description`, `bullets` | ✅ Consistent |
| `WorkHistory` DB | `company_name`, `job_title`, `start_date`, `end_date` | ✅ Consistent |
| API response | `company_name`, `job_title` | ✅ Consistent |
| `parsed_data.sections` | `{content, confidence}` | Some sections may be `SectionResult` objects – normalize to dict |

**Action:** Ensure `sections` always has `{content, confidence}` dicts for consistency.

---

## 3. Known Issues (from RESUME_PARSER_DEBUG_ANALYSIS.md)

### Already Fixed ✅

- [x] Sanitizer keeps entries with company+title (no dates)
- [x] Multi-key experience (`EXPERIENCE_KEYS`)
- [x] LLM merge guard (don’t overwrite good deterministic with empty)
- [x] Date parsing: Q1 2020, Jan '20, Spring 2021
- [x] Section deduplication in `_canonicalize_sections`
- [x] Summary deduplication in `clean_summary_and_skills_sections` and `_dedup_text_lines`
- [x] Name first-line heuristic
- [x] Multi-client extraction (`_extract_all_clients`)
- [x] Parsing debug endpoint (`GET /candidates/{id}/parsing-debug`)

### Remaining / Partial

| Issue | Location | Fix |
|-------|----------|-----|
| **Block segmentation** | `work_experience_parser.extract_individual_jobs` | Add more date formats (e.g. "20.01", "20/01", regional) |
| **Placeholder/skillish filtering** | `sanitizer._is_placeholder`, `_is_skillish` | Log when entries are dropped; add allowlist for common titles |
| **Section detection for non-English** | `section_parser` | Add more aliases for experience/education in other languages |
| **Work history mismatch banner** | UI | Show banner when parsed data exists but DB is empty |

---

## 4. Action Plan to Reach 85%

### Phase 1: Measure Baseline (1–2 days)

1. **Build ground truth dataset**
   ```bash
   # Create 50 resumes with expected JSON
   python scripts/build_ground_truth.py --resumes-dir ./resumes --output ./data/ground_truth.json --limit 50
   ```

2. **Run evaluation**
   ```bash
   cd backend && poetry run pytest tests/eval_resume_regression.py -v
   ```

3. **Record baseline**
   - Log `overall`, `contact_accuracy`, `work_accuracy`, `skills_f1` from `RegressionScore`.

### Phase 2: High-Impact Fixes (2–3 days)

4. **Add date parsing fallbacks**
   - In `_parse_date_str`: add "20.01", "20/01", "20-01", "20.01.2020", "Jan 20", "January 20".
   - Add `DATE_FORMATS` for edge cases.

5. **Improve section detection**
   - Lower `_length_heuristic_boost` penalty for short experience (< 220 chars).
   - Add more `EXPERIENCE_KEYS` if needed.

6. **Add fallback UI banner**
   - In `CandidateDetailPage.tsx`: show banner when `work_history` is empty but `parsed_data.work_experience` has data.

### Phase 3: Robustness (2–3 days)

7. **Improve block segmentation**
   - In `extract_individual_jobs`: add more date anchors for regional formats.
   - Log chunk count when only 1 chunk is returned.

8. **Add source format handling**
   - Pass `source_format` from extraction to normalization.
   - Use OCR-specific fixes when `source_format == "ocr"`.

9. **Implement `generate_accuracy_report`**
   - Run `eval_resume_regression` on ground truth.
   - Write `parsed_data` vs `expected` to `tests/reports/accuracy_report.json`.
   - Compute per-field accuracy.

### Phase 4: Fine-Tuning (ongoing)

10. **Use LLM for ambiguous cases**
    - When `PARSING_MODE=full`, use LLM to fill gaps when deterministic confidence is low.
    - Don’t overwrite high-confidence deterministic results.

11. **Expand ground truth**
    - Add resumes that fail current tests.
    - Cover formats: PDF, DOCX, OCR, multi-column, non-English.

12. **Monitor in production**
    - Use `/parsing-debug` for failures.
    - Track `confidence_score` and `review_confidence`.
    - Log when `mismatch` is true (parsed vs DB).

---

## 5. Quick Wins (Low Effort, High Impact)

| Fix | File | Effort |
|-----|------|--------|
| Add "20.01", "20/01" to date parsing | `pipeline._parse_date_str` | Low |
| Add UI mismatch banner | `CandidateDetailPage.tsx` | Low |
| Log sanitizer drops | `work_experience_sanitizer` | Low |
| Add more date anchors in `extract_individual_jobs` | `work_experience_parser.py` | Medium |
| Reduce experience length penalty | `section_parser._length_heuristic_boost` | Low |

---

## 6. Accuracy Targets by Field

| Field | Target | Weight |
|-------|--------|--------|
| Contact (name, email, phone, location) | 90% | 40% |
| Work experience (company, title, dates) | 85% | 40% |
| Skills | 80% | 20% |

**Overall:** 0.4 × 0.90 + 0.4 × 0.85 + 0.2 × 0.80 = **0.86** → 86% (above 85%)

---

## 7. Validation Commands

```bash
# Run regression tests
python -m pytest tests/test_full_pipeline_regression.py -v

# Run ground truth (if fixtures exist)
python -m pytest tests/ground_truth/test_accuracy.py -v -m ground_truth

# Run eval (if fixtures exist)
python -m pytest tests/eval_resume_regression.py -v

# Check parsing debug for a candidate
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/candidates/{id}/parsing-debug
```

---

## 8. Summary

**To reach 85% accuracy:**

1. **Measure** – Build ground truth and run evaluation.
2. **Standardize** – Consistent input handling (source format, normalization).
3. **Fix** – Apply remaining Phase 2 fixes (dates, sections, UI).
4. **Iterate** – Add failing cases to ground truth, fix, re-measure.

Most fixes from the analysis are already in place. The main gaps are **measurement** (ground truth dataset) and **robustness** (more date formats, edge-case section detection). Focus on Phase 1 and 2 first.
