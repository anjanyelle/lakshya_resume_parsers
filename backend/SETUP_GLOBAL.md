# Global install setup (no venv)

⚠️ **Note:** Installing globally is not recommended for production, but for testing it's fine.

**Avoid wrong Python:** Use `python -m pip install ...` so packages install into the same Python that runs your scripts. If you get `ModuleNotFoundError` after installing, see [docs/PYTHON_PIP_TROUBLESHOOTING.md](docs/PYTHON_PIP_TROUBLESHOOTING.md).

---

## 1️⃣ Install Required Python Packages (Global Install)

Open Command Prompt / PowerShell and run (use `python -m pip` so the correct interpreter is used):

```bash
python -m pip install fastapi uvicorn python-multipart
python -m pip install pdfplumber pymupdf
python -m pip install python-docx
python -m pip install dateparser
python -m pip install pydantic
python -m pip install spacy nltk
```

**If you are using LLM:**

```bash
python -m pip install openai
```

**If using ML-based skill detection:**

```bash
python -m pip install scikit-learn numpy
```

---

## 2️⃣ Download SpaCy Model (Important)

If you use SpaCy for skill extraction:

```bash
python -m spacy download en_core_web_lg
```

---

## Install all (copy-paste)

Run these in order to install everything (core + LLM + ML + SpaCy model):

```bash
python -m pip install fastapi uvicorn python-multipart
python -m pip install pdfplumber pymupdf
python -m pip install python-docx
python -m pip install dateparser
python -m pip install pydantic
python -m pip install spacy nltk
python -m pip install openai
python -m pip install scikit-learn numpy
python -m spacy download en_core_web_lg
```

---

## Run the API

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

Or with Poetry:

```bash
poetry run uvicorn app.main:app --reload
```

Set `DATABASE_URL`, `PARSING_MODE`, and `LLM_PROVIDER` in `.env` as needed (see main README).
