# Skill Extraction — Industry Approach

This project follows the recommended industry pattern: **spaCy NLP + predefined skills dataset + custom normalization**.

---

## 1. Required libraries (no venv needed)

```bash
pip install spacy
pip install pandas
pip install scikit-learn
```

Download the English NLP model:

```bash
python -m spacy download en_core_web_sm
```

---

## 2. Predefined skills dataset

We use a **master taxonomy** instead of a manual list:

- **Location:** `app/data/taxonomy/skills_seed.json`
- **Contents:** Normalized skill names, categories, synonyms (e.g. "React", "ReactJS" → react).
- **Role:** Only skills in this taxonomy are stored; no hallucinated or free-form skills.

**Optional — ESCO (European Skills Database):**

- Download: https://esco.ec.europa.eu/en/use-esco/download  
- Gives 13,000+ standardized skills and an official taxonomy.  
- You can load ESCO CSV and map `preferredLabel` into our seed format or use it as an extended validation list.

---

## 3. How this codebase does it

- **spaCy:** Used for tokenization and **phrase matching** (multi-word skills: "Power BI", "Machine Learning", "SQL Server").
- **PhraseMatcher:** Patterns are built from the taxonomy + synonyms; matching is case-insensitive (`attr="LOWER"`).
- **Normalization:** Lowercase, strip, synonym mapping, canonical form (e.g. "Amazon Redshift" → redshift), category from a fixed master list.
- **Validation:** Every skill is checked against the master taxonomy; categories are restricted to a fixed list (no free-form categories).

Relevant code:

- `app/services/parser/skill_extractor.py` — `SkillExtractor` (taxonomy load, PhraseMatcher, extract from section/experience/raw).
- `app/workers/pipeline.py` — `task_extract_skills` (section vs full extraction, 4-layer filter, strict dictionary, no guessed years).

---

## 4. Phrase matching (multi-word skills)

We use spaCy’s `PhraseMatcher`, not a simple token loop, so multi-word skills are matched correctly:

- Big Data, Machine Learning, Power BI, SQL Server, Spring Boot, etc.

Patterns come from `skills_seed.json` (name + synonyms). No manual `MASTER_SKILLS` list in code; the taxonomy is the single source of truth.

---

## 5. Optional AI-based extraction

If you use an LLM to extract skills from text:

- Prompt: *Extract ALL technical skills from this resume. Return only a JSON array. Do not summarize or infer; only explicitly mentioned skills.*
- **Always validate** the LLM output against the master taxonomy (and normalization) before storing.

This project keeps LLM skill extraction disabled by default and relies on taxonomy + phrase matching + normalization for stable, consistent results.

---

## 6. Optional ready-made library

Libraries like **skillNer** can be used for prototyping, but production systems usually combine:

- A **controlled taxonomy** (our `skills_seed.json` or ESCO),
- **Phrase matching** (spaCy),
- **Normalization and validation** (no free-form categories or guessed years).

See `SETUP_GLOBAL.md` for install steps and `app/data/taxonomy/skills_seed.json` for the current skill list.
