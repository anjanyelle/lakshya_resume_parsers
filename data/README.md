# Data directory

This folder holds evaluation and ground-truth data used by the parser and accuracy reports.

## Work history shape (model-aligned)

Work history entries in `ground_truth.json`, `eval_test.json`, and in persisted `resume.json` (after parsing) use the **same field names as the DB/API model** for consistency:

- **company_name** – employer organization (alias: `company` in legacy parsed payloads)
- **client_name** – end client when applicable (alias: `client`)
- **job_title** – role/title (alias: `title`); never use literal `"Role"` as placeholder
- **start_date**, **end_date** – ISO date or YYYY-MM
- **is_current** – boolean
- **location** – e.g. "City, ST" (no extra trailing parenthesis)
- **description** – responsibilities/achievements; populated from bullets when missing

The pipeline writes both the canonical keys (`company`, `title`, `client`) and the model keys (`company_name`, `job_title`, `client_name`) into `resume.json` so frontend and eval can rely on the model-wise shape.

## Files

- **ground_truth.json** – Full resume samples with expected `parsed` output (sections, contact, work_history, education, etc.).
- **eval_test.json** – Eval fixtures with `parsed` and `ground_truth` per file.
- **ResumeNER/** – NER training data for resume entity recognition.
- **Skills-Extraction-Dataset/** – Skills extraction dataset.
