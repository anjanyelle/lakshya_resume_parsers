# DeBERTa NER Resume Training Project

This project contains the folder structure and resources for training a DeBERTa-based Named Entity Recognition (NER) model specifically for resume parsing.

## Project Structure

```
Lakshya-LLM-Resume-Parser/
├── data/
│   ├── raw/          # For JSON-MIN files (raw annotated resume data)
│   ├── converted/    # For CoNLL format output (processed training data)
│   └── splits/       # For train and test dataset splits
├── models/           # For saved trained model checkpoints and artifacts
├── scripts/          # For all Python training and preprocessing scripts
├── requirements.txt  # Required Python libraries
└── README.md         # This file
```

## Folder Descriptions

### `data/raw/`
- **Purpose**: Store raw JSON-MIN format resume annotation files
- **Contents**: Original annotated resume data in JSON-MIN format
- **Note**: This is the input data that will be processed and converted

### `data/converted/`
- **Purpose**: Store processed CoNLL format files ready for training
- **Contents**: Resume data converted to CoNLL format (token-label pairs)
- **Note**: This format is required for training the DeBERTa NER model

### `data/splits/`
- **Purpose**: Store train/validation/test dataset splits
- **Contents**: 
  - `train.txt` - Training dataset
  - `test.txt` - Test dataset
  - (optional) `dev.txt` or `val.txt` - Validation dataset
- **Note**: Files should be in CoNLL format

### `models/`
- **Purpose**: Store trained model checkpoints and artifacts
- **Contents**: 
  - Trained DeBERTa model files
  - Configuration files
  - Tokenizer files
  - Training logs and metrics
- **Note**: This directory will contain the final trained model

### `scripts/`
- **Purpose**: Contains all Python scripts for data processing and training
- **Potential scripts**:
  - `convert_json_to_conll.py` - Convert JSON-MIN to CoNLL format
  - `split_dataset.py` - Split data into train/test sets
  - `train_ner_model.py` - Main training script
  - `evaluate_model.py` - Model evaluation script
  - `inference.py` - Run inference on new resumes

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Then start the API: `poetry run uvicorn app.main:app --reload`

### Deployed on Render – 503 or "Database schema not ready"

**Root cause:** The APIs return 503 or 400 when the database is **missing tables** (`candidates`, `parsing_jobs`, `audit_logs`, etc.). This often happens if:

- The database was created empty and Alembic reports "Migrations completed" but the schema was never applied (e.g. DB already marked at `head` from another app), or
- Migrations failed silently or ran against a different `DATABASE_URL`.

**What we do automatically:**

- Startup runs `alembic upgrade head` then `Base.metadata.create_all(..., checkfirst=True)` so missing tables are created if possible.
- Register/login/upload catch missing-table errors and either return a clear 503 or, for register, still return success and only skip audit logging.

**Permanent fix (recommended):**

1. In Render Dashboard, create a **new PostgreSQL** instance (or use one that has never had this app’s migrations run).
2. Set the backend service’s **DATABASE_URL** to that new database.
3. Redeploy. On first start, `alembic upgrade head` will run from scratch and create all tables.

After that, register, login, and upload should work without 503.

### Parsing speed on production (Render / no Redis, no LLM)

Uploads can feel slow because parsing runs in the same process (no Celery workers on Render) and the default pipeline has many steps.

**What we do automatically:**

- If `LLM_PROVIDER` is `none`, the app uses the **deterministic** pipeline (no LLM steps), so parsing finishes in seconds instead of minutes.
- Defaults: `PDF_MAX_PAGES=20`, `OCR_MAX_PAGES=10` (lower than before for faster extraction).
- When `ENVIRONMENT` is not `development` or `local`, PDF extraction is capped at **15 pages** and OCR at **5 pages** so resumes finish quickly.

**Recommended env for Render (fast parsing):**

```env
ENVIRONMENT=production
PARSING_MODE=deterministic
LLM_PROVIDER=none
```

Optional: `PDF_MAX_PAGES=15` and `OCR_MAX_PAGES=5` for even faster runs (defaults already apply production caps above).

---

Quick Start
- Generate dataset files:
  - python scripts/prepare_dataset.py

Outputs
- data/train.jsonl
- data/val.jsonl

Each JSONL line has:
{
  "input": "<raw resume text>",
  "output": "<stringified JSON with structured fields>"
}

Notes
- The dataset generator includes 5 diverse examples.
- Intended for local experimentation and prompt/finetune iteration.






anjanyelle@Hello backend % poetry run uvicorn app.main:app --reload



poetry run uvicorn app.main:app --reload


poetry --version


poetry install
poetry run uvicorn app.main:app --reload


Fast mode added: PARSING_MODE=deterministic
Now you have 3 modes:

text_only = extract text only
deterministic = fast parse without any LLM but still saves to DB
full = everything including LLM
In deterministic, the workflow is:

extract_text → clean_text → detect_sections → extract_contact_info → parse_work_experience → parse_education → parse_certifications → extract_skills → taxonomy_mapping → calculate_confidence → save_to_database

So you should get:





APP_NAME="Resume Parser API"
ENVIRONMENT=development
API_V1_STR=/api/v1
LOG_LEVEL=INFO

DATABASE_URL="postgresql+psycopg2://postgres:Anjan%24123@localhost:5432/resume_parser"
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

STORAGE_DIR=./storage
UPLOAD_MAX_SIZE_MB=20
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
ALLOWED_UPLOAD_EXTENSIONS=["pdf","doc","docx","txt","rtf","png","jpg","jpeg"]

CLAMAV_ENABLED=false
CLAMAV_PATH=clamscan

1. Place your JSON-MIN annotated resume files in `data/raw/`
2. Run the conversion script to create CoNLL format files in `data/converted/`
3. Split the dataset using the split script to create files in `data/splits/`
4. Train the model using the training script
5. The trained model will be saved in `models/`

## Dependencies

- `transformers` - Hugging Face transformers library for DeBERTa model
- `datasets` - Dataset handling and processing
- `seqeval` - Evaluation metrics for sequence labeling
- `torch` - PyTorch deep learning framework
- `accelerate` - Distributed training and mixed precision
- `evaluate` - Evaluation metrics library   python training/data/colab_train.py
- `scikit-learn` - Machine learning utilities  


cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service"
source venv/bin/activate
python main.py



cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src"
npm install
npm run dev


cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/frontend"
npm install
npm run dev



cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser
source venv/bin/activate
python3 test_deberta_model.py --file resume1.txt