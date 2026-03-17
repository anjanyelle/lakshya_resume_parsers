# Data Loss Verification — Logging Strategy

Use these log points to verify that no content is lost during resume upload, extraction, cleaning, parsing, or API response.

## Log prefix

All verification logs use the prefix **`[DATA-LOSS CHECK]`** so you can filter them easily.

---

## 1. File upload stage (frontend)

**Where:** `frontend/src/store/uploadStore.ts`

- **When files are selected:** Logs file count, name, size, and type for each file.
- **When upload completes:** Logs file name, size, and `jobId` returned by the API.
- **When polling sees success:** Logs `jobId` and file name.

**How to see:** Open DevTools → Console. Only in `import.meta.env.DEV` (e.g. `npm run dev`).

---

## 2. Text extraction stage (backend)

**Where:** `backend/app/services/parser/extract_text.py` and `backend/app/workers/extract_text_task.py`

- **Start:** `Starting text extraction` with path and extension.
- **PDF:** After extraction, logs method (pymupdf/pdfplumber/ocr), output length, approximate line count, and a short sample.
- **DOCX:** Logs output length, paragraph count, table count, and sample.
- **Image/OCR:** Logs output length, confidence, and sample.
- **Plain text (txt/rtf):** Logs output length and sample.
- **OCR fallback:** When text is below threshold, logs `Low text detected, triggering OCR` and after OCR logs output length and confidence.
- **extract_text_task:** After `extract_text()`, logs total chars, method, and OCR flag; logs first 250 chars of raw extracted text; after table normalization (docx/doc), logs before/after length and whether normalization was applied.

**How to see:** Backend stdout or log file (e.g. `backend/logs/app.log`). Search for `[DATA-LOSS CHECK]` or `extract_text`.

---

## 3. Clean text stage (backend)

**Where:** `backend/app/workers/pipeline.py` → `task_clean_text`

- Logs **raw length** (before normalize), **cleaned length** (after), **source format**, and a short sample of cleaned text.

**How to see:** Same backend logs. Search for `Clean text stage`.

---

## 4. Final extracted data vs raw (backend)

**Where:** `backend/app/workers/pipeline.py` → `task_save_to_database`

- Logs **raw_text_chars**, **work_entries** count, **work_desc_total_chars**, **education** count, **certifications** count, **summary_chars**.
- Use this to compare raw input size to structured output size and spot drops (e.g. many raw chars but few work entries or short summary).

**How to see:** Backend logs. Search for `Final extracted vs raw`.

---

## 5. Extraction debug API (backend + frontend)

**Endpoint:** `GET /api/v1/jobs/{job_id}/extraction-debug`  
**Where:** `backend/app/api/v1/endpoints/jobs.py`

Returns:

- `raw_text_length`
- `raw_text_sample_first_200` / `raw_text_sample_last_100`
- `parsed_work_experience_count`, `parsed_work_description_total_chars`
- `parsed_education_count`, `parsed_certifications_count`
- `parsed_summary_length`
- `text_extraction_method`, `used_ocr`

**Frontend:** On candidate detail load (dev only), the app calls this for the latest job and logs the result in the console under `[DATA-LOSS CHECK] Backend extraction debug`.

**Manual check:**  
`curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/jobs/<job_id>/extraction-debug`

---

## 6. Final frontend rendering (frontend)

**Where:** `frontend/src/pages/CandidateDetailPage.tsx`

After loading candidate and review data:

- Logs **DB counts** (work_history, education, certifications) and **parsed_data counts** (work_experience, education, certifications, summary length and sample).
- Then fetches `extraction-debug` for the latest job and logs it for comparison.

**How to see:** DevTools → Console. Only when `import.meta.env.DEV` is true.

---

## Quick checklist

| Stage             | Backend log / Frontend log  | What to compare                          |
| ----------------- | --------------------------- | ---------------------------------------- |
| Upload            | Frontend console            | File size vs later raw_text_length       |
| Extraction        | Backend `[DATA-LOSS CHECK]` | Output length and sample per method/OCR  |
| Table norm (docx) | Backend                     | before/after chars                       |
| Clean text        | Backend                     | raw_len vs cleaned_len                   |
| Save to DB        | Backend                     | raw_text_chars vs work/edu/certs/summary |
| API response      | Frontend + extraction-debug | DB vs parsed counts and summary length   |

---

## Interpreting results

- **Large drop from raw_text_length to parsed_summary_length or work_desc_total_chars:** Possible over-trimming, section not detected, or parser dropping content.
- **OCR path with low confidence:** Possible character/word loss; check `raw_text_sample_*` for gibberish or missing words.
- **Table norm before/after very different:** Table handling may be dropping or merging lines (docx).
- **Frontend DB counts zero but parsed_data counts > 0:** Data not yet saved to DB (e.g. text-only or failed save); use “Reprocess” or fix pipeline.
