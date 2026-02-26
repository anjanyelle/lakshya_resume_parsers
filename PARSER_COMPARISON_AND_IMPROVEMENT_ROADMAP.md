# Lakshya Resume Parser vs. Top Commercial AI Parsers

**Document Version:** 1.0  
**Date:** February 2025  
**Purpose:** Compare Lakshya-LLM-Resume-Parser with top commercial parsers (Skima AI, Affinda, RChilli, Textkernel, Sovren, Zappyhire, Docparser), identify major drawbacks, and propose improvements for higher accuracy.

---

## Executive Summary

Commercial parsers achieve higher accuracy through:
- **Specialized ML/NLP models** trained on CV subsections (not just regex + LLM)
- **Large taxonomies** (3M+ skills, 2.4M job profiles)
- **Deep learning + NER** for entity extraction
- **50+ language support** with multilingual parsing
- **Semantic matching** beyond keyword matching
- **ATS integration** and enterprise workflows

Lakshya uses a **hybrid deterministic + optional LLM** approach with regex, keyword aliases, and taxonomy-based skills. It lacks a dedicated NER model, multilingual parsing, and enterprise-grade taxonomies.

---

## Part 1: How Commercial Parsers Work

### 1.1 Skima AI
- **Approach:** AI-powered parsing with NLP, high accuracy for candidate screening
- **Features:** 56+ language support, strong ATS integration, faster candidate screening
- **Architecture:** Advanced text extraction (layout-aware), semantic understanding

### 1.2 Affinda
- **Approach:** NLP + machine learning trained on CV subsections (Education, Skills, Work Experience)
- **Features:** 50+ languages, NLP semantic understanding (e.g., "Work History" = "Job History" = "Previous Employment"), 100+ custom fields, resume redaction
- **Architecture:** ML models trained specifically for CV parsing

### 1.3 RChilli
- **Approach:** Deep learning / AI framework
- **Features:** 200+ data fields, REST API, multi-format (DOC, DOCX, PDF, RTF, TXT, ODT, HTML)
- **Taxonomy:** 3M+ skills, 2.4M job profiles, multi-language
- **Architecture:** Real-time duplicate detection, bulk parsing, taxonomy ontologies

### 1.4 Textkernel
- **Approach:** Multilingual parsing, OCR
- **Features:** Advanced semantic search/match

### 1.5 Sovren
- **Approach:** API-first parsing
- **Features:** Semantic matching for deeper candidate analysis

### 1.6 Zappyhire
- **Approach:** Deep Learning + Named Entity Recognition (NER)
- **Features:** 93% precision in information extraction, semantic search (contextual understanding vs. keyword matching)
- **Architecture:** Deep NLP for text extraction, NER for entity identification

### 1.7 Docparser
- **Approach:** Customizable parsing rules
- **Features:** User-defined rules, refine data extraction without cleanup

---

## Part 2: How Lakshya Parser Works

### 2.1 Architecture Overview

```
Upload → extract_text → clean_text → detect_sections → extract_contact →
  parse_work_experience → extract_clients → parse_education →
  parse_certifications → extract_achievements → extract_skills →
  taxonomy_mapping → calculate_confidence → save_to_database
```

**Optional LLM path** (when `PARSING_MODE=full` and `LLM_PROVIDER` set):
- `task_extract_structured_resume`, `task_extract_work_experience_details`, `task_extract_experience_skills`
- LLM merge with guards (don't overwrite good deterministic with empty)

### 2.2 Key Components

| Component | Location | Approach |
|-----------|----------|----------|
| **Text extraction** | `extract_text.py` | PyMuPDF → pdfplumber → pypdf → OCR (Tesseract); python-docx for DOCX |
| **Section detection** | `section_parser.py`, `fallback_segmenter.py` | Regex + 300+ section aliases; spaCy PhraseMatcher with `spacy.blank("xx")` (tokenization only, no NER) |
| **Contact extraction** | `contact_extractor.py` | Regex, NAME_LABEL_REGEX, lines 1–4, ALL CAPS fallback |
| **Work experience** | `work_experience_parser.py` | Date anchors (`DATE_RANGE_RE`), `COMPANY_LINE_RE`, `dateparser` fallback |
| **Skills** | `skill_extractor.py` | Taxonomy-based (`skills_master`), PhraseMatcher, SKILL_ALIASES |
| **Education** | `education_parser.py` | Year/institution regex, DEGREE_ALIASES |
| **Certifications** | `certification_parser.py`, `section_boundary_extractor.py` | Regex, inline patterns, CERTIFICATION_HEADINGS |

### 2.3 Technology Stack

- **Languages:** Python (FastAPI, Celery)
- **NLP:** spaCy (blank model only, no pretrained NER)
- **LLM:** Optional (OpenAI, Anthropic, local Ollama)
- **OCR:** Tesseract (English by default: `TESSERACT_LANG=eng`)
- **Formats:** PDF, DOC, DOCX, TXT, RTF, PNG, JPG

### 2.4 Language Support

- **OCR:** English only (configurable)
- **Section parsing:** Multilingual aliases (~300+ keys) but no language-specific models
- **Parsing logic:** English-centric; no dedicated multilingual parsing

---

## Part 3: Major Drawbacks & Issues with Lakshya Parser

### 3.1 Critical Drawbacks

| # | Drawback | Impact | Commercial Parser Gap |
|---|----------|--------|------------------------|
| 1 | **No dedicated NER model** | spaCy uses `spacy.blank("xx")` – tokenization only, no entity recognition | Zappyhire, Affinda use NER for entity extraction |
| 2 | **Regex-heavy, rule-based** | Brittle for format variations; misses non-standard layouts | Commercial parsers use ML trained on CV subsections |
| 3 | **Limited taxonomy** | Skills in `skills_master` – smaller than enterprise taxonomies (3M+ skills) | RChilli: 3M+ skills, 2.4M job profiles |
| 4 | **Single language focus** | OCR English only; parsing English-centric | Skima: 56+, Affinda: 50+ languages |
| 5 | **No semantic matching** | Keyword/taxonomy matching only | Sovren, Textkernel, Zappyhire: semantic search |
| 6 | **Section detection weak** | Non-English headers, inline sections ("Skills: Python, Java") missed | Affinda: NLP understands semantic equivalence |
| 7 | **No resume redaction** | PII not redacted | Affinda: resume redaction |

### 3.2 Known Technical Issues (from Audit)

| Issue | Location | Root Cause |
|-------|----------|------------|
| **Name missing** | `contact_extractor.py` | Name beyond line 30 not considered; ALL CAPS fallback helps but not all cases |
| **Summary missing/duplicate** | `section_parser`, `fallback_segmenter` | Section merge, canonicalization duplicates |
| **Work history incomplete** | `work_experience_parser` | Single chunk when no date boundaries; table layout misread |
| **Skills missing** | `skill_extractor` | Taxonomy dependency; skills not in taxonomy dropped |
| **Certifications missing** | `section_parser`, `certification_validator` | Section header not detected; over-filtering |
| **Education missing** | `section_parser` | Non-English headers; table layout |
| **PDF slow** | `extract_text.py` | OCR sequential (now parallel); large PDFs |
| **DOCX inconsistent** | `extract_text.py` | Bullets lost; headings lost; table order |
| **Multi-column PDF** | `extract_text.py` | Text order wrong → sections mis-assigned |

### 3.3 Accuracy Gaps

From `accuracy_report.json` (sample):
- **Overall:** ~26%
- **Section found rate:** 0.17
- **Work accuracy:** 0
- **Education F1:** 0
- **Certifications F1:** 0
- **Skills F1:** 0.86 (relatively better)

Target: 85%+ overall (0.4 × contact + 0.4 × work + 0.2 × skills)

---

## Part 4: What We Need for Higher Accuracy

### 4.1 Short-Term (Phase 1–2)

| Priority | Action | Effort |
|----------|--------|--------|
| 1 | **Build ground truth dataset** (50–100 resumes) | Medium |
| 2 | **Add date parsing fallbacks** (20.01, 20/01, Q1 2020, Jan '20) | Low |
| 3 | **Expand section aliases** (non-English, inline) | Low |
| 4 | **Improve block segmentation** (1-chunk fallback, company/title) | Medium |
| 5 | **Relax sanitizer** (placeholders, skillish filtering) | Low |
| 6 | **Implement `generate_accuracy_report`** | Low |

### 4.2 Medium-Term (Phase 3–4)

| Priority | Action | Effort |
|----------|--------|--------|
| 1 | **Add pretrained NER** (e.g., spaCy `en_core_web_sm` for PERSON, ORG, DATE) | Medium |
| 2 | **Multi-column PDF** layout analysis | High |
| 3 | **Source format handling** (OCR vs. native PDF) | Medium |
| 4 | **LLM for ambiguous cases** (low-confidence deterministic → LLM) | Medium |
| 5 | **Expand skills taxonomy** | Medium |

### 4.3 Long-Term (Enterprise)

| Priority | Action | Effort |
|----------|--------|--------|
| 1 | **Fine-tune NER on resume data** | High |
| 2 | **Multilingual support** (OCR + parsing) | High |
| 3 | **Semantic matching** (embeddings) | High |
| 4 | **Resume redaction** | Medium |
| 5 | **ATS integration** | High |

---

## Part 5: Comparison Matrix

| Feature | Lakshya | Skima | Affinda | RChilli | Zappyhire |
|---------|---------|-------|---------|---------|-----------|
| **Core approach** | Regex + LLM (optional) | AI/NLP | NLP + ML | Deep learning | Deep Learning + NER |
| **Languages** | 1 (English) | 56+ | 50+ | Multi | Multi |
| **Data fields** | ~20–30 | High | 100+ | 200+ | High |
| **Skills taxonomy** | Limited | Yes | Yes | 3M+ | Yes |
| **NER** | No (blank spaCy) | Yes | Yes | Yes | Yes |
| **Semantic matching** | No | Yes | Yes | Yes | Yes |
| **OCR** | Tesseract (eng) | Yes | Yes | Yes | Yes |
| **Resume redaction** | No | No | Yes | No | No |
| **Custom rules** | No | No | Yes | Yes | No |
| **ATS integration** | No | Yes | Yes | Salesforce, Oracle, Zoho | Yes |

---

## Part 6: Recommended Architecture Evolution

### Current Flow
```
[Upload] → extract_text → clean_text → detect_sections → 
  [regex parsers] → [optional LLM] → save
```

### Target Flow (for 85%+ accuracy)
```
[Upload] → extract_text → clean_text → detect_sections →
  [regex parsers] → [NER fallback for entities] → [LLM for low-confidence] →
  [validation] → save
```

### Key Additions
1. **NER:** Use `en_core_web_sm` or similar for PERSON, ORG, DATE in contact and work experience.
2. **Confidence gating:** When deterministic confidence < threshold, call LLM.
3. **Ground truth:** Automated accuracy tracking against fixtures.
4. **Multi-column:** Layout-aware PDF extraction.

---

## Part 7: Summary

| Aspect | Commercial Parsers | Lakshya | Gap |
|--------|--------------------|---------|-----|
| **Technology** | Deep learning, NER, ML on CV subsections | Regex, keyword aliases, optional LLM | Major |
| **Languages** | 50–56+ | 1 | Major |
| **Taxonomy** | 3M+ skills, 2.4M job profiles | Limited | Major |
| **Accuracy** | 90%+ (claimed) | ~26–85% (varies) | Major |
| **Semantic** | Yes | No | Major |
| **Custom rules** | Some (Docparser) | No | Minor |

**To reach commercial parity:** Focus on NER, expanded taxonomy, multilingual support, and semantic matching. Short-term: ground truth, date fallbacks, section aliases, and NER integration.

---

## References

- `ACCURACY_IMPROVEMENT_ROADMAP.md`
- `PRODUCTION_RESUME_PARSER_AUDIT.md`
- `RESUME_PARSER_DEBUG_ANALYSIS.md`
- `RESUME_PARSER_TECHNICAL_AUDIT_85_PERCENT_ACCURACY.md`
- `backend/tests/reports/accuracy_report.json`