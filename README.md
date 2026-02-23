Resume Parser Fine-Tuning Project

This repository includes a resume parsing system and a small synthetic dataset
generator for fine-tuning or evaluation.

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

PARSING_MODE=deterministic
LLM_PROVIDER=none






ption B (If you are using MinIO/S3 for storage)
Deterministic + no LLM + MinIO enabled
env
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
 
S3_BUCKET=resume-parser
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_REGION=us-east-1
S3_USE_SSL=false
 
CLAMAV_ENABLED=false
CLAMAV_PATH=clamscan
 
PARSING_MODE=deterministic
LLM_PROVIDER=none
Important



cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser/backend
poetry lock
poetry install


poetry run python -c "import fitz; print('OK')"

poetry run python ../scripts/build_ground_truth.py \
  --resumes-dir ../resumes \
  --output ../data/ground_truth.json \
  --limit 200