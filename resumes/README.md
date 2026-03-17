# Ground-Truth Resume Dataset

Place resume files here for building the ground-truth evaluation dataset.

## Target Distribution (200 samples)

| Format | Count | Description |
|--------|-------|-------------|
| PDF | 40 | Simple 1-col, 2-col, table-based, scanned image |
| DOCX | 40 | Plain, with tables, with textboxes, with headers |
| DOC | 20 | Legacy Word format |
| Image | 20 | PNG/JPG: scanned, printed, handwritten notes |
| TXT/RTF | 40 | Exported plain text, complex RTF |
| Mixed | 40 | Multilingual, gaps in employment, academic CVs, contractor profiles, executive bios |

## Directory Structure

Either:

- **Flat**: `resumes/*.pdf`, `resumes/*.docx`, etc.
- **By format**: `resumes/pdf/`, `resumes/docx/`, `resumes/images/`, etc.
- **By type**: `resumes/simple_1col/`, `resumes/2col/`, `resumes/scanned/`, etc.

The script recursively scans all subdirectories.

## Build Ground Truth

```bash
cd backend
poetry run python ../scripts/build_ground_truth.py \
  --resumes-dir ../resumes \
  --output ../data/ground_truth.json \
  --limit 200
```

Output: `data/ground_truth.json` with `file`, `format`, `parsed`, `ground_truth`, `scores` per resume.

## Evaluate Accuracy

After filling `ground_truth` manually for each record:

```bash
cd backend
poetry run python ../scripts/eval_accuracy.py \
  --dataset ../data/ground_truth.json \
  --output ../reports/accuracy_$(date +%Y%m%d).json
```

Output: summary table + JSON report with field-level precision/recall/F1, broken down by format.
