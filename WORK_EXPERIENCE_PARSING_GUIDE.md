# 🔧 Work Experience Parsing Architecture Guide

## 📋 **Main Files for Work Experience Parsing**

### **🎯 Core Parser Files**

| File | Purpose | Key Methods | Your Approach |
|------|---------|--------------|--------------|
| **`work_experience_parser.py`** | **Main Rule-based Parser** | `parse_experience_section()`, `_parse_chunk()`, `_split_merged_jobs()` | **Your primary approach** - handles Client/Role/Location, Company/Role/Location, and Company:Date Range formats |
| **`work_experience_enhanced.py`** | **Enhanced Patterns** | `parse_with_enhanced_patterns()` | **Improved pattern recognition** for complex resume formats |
| **`hybrid_work_experience_parser.py`** | **Multi-Strategy Integration** | `parse_with_multiple_strategies()` | **Combines ML + Rule-based** approaches |
| **`ml_work_experience_parser.py`** | **ML-based Parser** | `parse_work_experience()` | **Machine learning approach** (currently rule-based fallback) |
| **`work_experience_sanitizer.py`** | **Data Cleaning** | `sanitize_work_experience_entries()` | **Deduplication and validation** |

---

## 🚀 **Parsing Flow in Your System**

### **Step 1: Initial Text Processing**
```python
# In work_experience_parser.py
def parse_experience_section(self, text: str, source_format: str | None = None) -> list[JobEntry]:
    all_lines = [l for l in (text or "").splitlines() if l.strip()]
    pipe_lines = [l for l in all_lines if "|" in l]
```

### **Step 2: Format Detection & Splitting**
```python
# Your enhanced _split_merged_jobs() handles 3 formats:
def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:
    # 1. Client/Role/Location Format: "Client: Company\nLocation: City, State\nRole: Title"
    # 2. Company/Role/Location Format: "Company: Name\nDate Range (Location: City, State)\nRole: Title"  
    # 3. Company: Date Range Format: "Company: Date Range (Location: City, State)\nRole: Title"
```

### **Step 3: Individual Job Parsing**
```python
def _parse_chunk(self, chunk: str) -> JobEntry:
    lines = [line.strip() for line in chunk.splitlines() if line.strip()]
    header = lines[0] if lines else ""
    company, title, location, start_date, end_date, is_current, body_start = self._parse_header_lines(lines)
```

---

## 🎯 **Your Three Resume Format Handling**

### **Format 1: Client/Role/Location (Ramu Gara)**
```python
# Pattern: "Client: Company\nLocation: City, State\nRole: Title Date Range"
CLIENT_PATTERNS = [
    re.compile(r"\b(?:end\s+client|client)\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
    re.compile(r"\bproject\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
]
```

### **Format 2: Company/Role/Location (Chandra Shyam)**
```python
# Pattern: "Company: Name\nDate Range (Location: City, State)\nRole: Title"
COMPANY_LINE_RE = re.compile(
    r"(?P<company>.+?)\s*(?:[-–—|])\s*(?P<title>.+)"
)
```

### **Format 3: Company: Date Range (Location)**
```python
# Pattern: "Company: Date Range (Location: City, State)\nRole: Title"
def _parse_header_lines(self, lines: list[str]):
    # Extracts company, title, location from complex headers
```

---

## 🤖 **ML Integration Points**

### **Hybrid Parser Integration**
```python
# In hybrid_work_experience_parser.py
def _initialize_parsers(self):
    # 1. ML Parser (Highest priority)
    from app.services.parser.ml_work_experience_parser import MLWorkExperienceParser
    self.parsers.append(("ML", MLWorkExperienceParser()))
    
    # 2. Rule-based Parser (Standard patterns)
    from app.services.parser.work_experience_parser import WorkExperienceParser
    self.parsers.append(("Rule-based", WorkExperienceParser()))
```

### **Enhanced Parser Integration**
```python
# In enhanced_parser_integration.py
if self.lightweight_manager:
    # Use lightweight models (spaCy + LayoutLM)
    lightweight_result = self.lightweight_manager.parse_resume_lightweight(resume_text)
    
    # Combine entities from spaCy
    spacy_entities = lightweight_result.spacy_result.entities
    entities = spacy_entities  # spaCy entities are our primary source
```

---

## 🔄 **Pipeline Processing**

### **Celery Task Flow**
```python
# In pipeline.py
task_parse_work_experience.s().set(queue="parse"),  # Rule-based parsing
task_extract_work_experience_details.s().set(queue="llm"),  # LLM enhancement
```

### **Data Sanitization**
```python
# In pipeline.py
from app.services.parser.work_experience_sanitizer import (
    deduplicate_work_entries,
    sanitize_work_experience_entries,
)

# Deduplicate work entries
work_exp = parsed_data.get("work_experience", [])
if isinstance(work_exp, list):
    parsed_data["work_experience"] = deduplicate_work_entries(work_exp)
```

---

## 📊 **Key Methods in Your Approach**

### **1. Main Entry Point**
```python
# work_experience_parser.py line 507
def parse_experience_section(self, text: str, source_format: str | None = None) -> list[JobEntry]
```

### **2. Job Splitting Logic**
```python
# work_experience_parser.py line 744
def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:
    # Enhanced client splitting for multiple formats
```

### **3. Header Parsing**
```python
# work_experience_parser.py line 1426
def _parse_header_lines(self, lines: list[str]) -> tuple:
    # Extracts company, title, location, dates from headers
```

### **4. Date Extraction**
```python
# work_experience_parser.py line 1698
def _parse_dates(self, text: str) -> tuple[date | None, date | None, bool]:
    # Extracts start/end dates from various formats
```

---

## 🎯 **Your Custom Format Handling**

### **Pattern Recognition**
```python
# Your enhanced patterns in work_experience_parser.py
CLIENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(?:end\s+client|client)\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
    re.compile(r"\bproject\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
    re.compile(r"\bworked\s+for\s+(?P<client>[A-Za-z0-9][A-Za-z0-9 &.,()/-]{2,})", re.IGNORECASE),
]

LOCATION_MARKER_RE = re.compile(
    r"\(?\b(?:location|loc)\b\s*[:\-–—]\s*(?P<loc>[^\n\r\t\)\|\u2022]{2,120})\)?",
    re.IGNORECASE,
)
```

### **Company Detection**
```python
# work_experience_parser.py line 83
CLIENT_PATTERNS: list[re.Pattern[str]] = [
    # Your patterns for Client/Role/Location format
]
```

---

## 🏆 **How Your System Works**

### **Step-by-Step Flow:**
1. **Text Input** → Raw resume text
2. **Format Detection** → Identifies which of your 3 formats
3. **Job Splitting** → `_split_merged_jobs()` separates individual jobs
4. **Header Parsing** → Extracts company, title, location, dates
5. **Body Extraction** → Gets descriptions and bullet points
6. **ML Enhancement** → LayoutLM + spaCy add confidence scores
7. **Sanitization** → Deduplication and validation
8. **Output** → Structured JobEntry objects

### **Key Innovation:**
- **Multi-format support** in single parser
- **Robust pattern matching** for complex headers
- **ML enhancement** with confidence scoring
- **Backward compatibility** with existing formats

---

## 🎯 **Files You Should Modify**

### **For New Formats:**
1. **`work_experience_parser.py`** - Add new patterns to `CLIENT_PATTERNS`
2. **`_split_merged_jobs()`** - Enhance format detection logic
3. **`_parse_header_lines()`** - Add new header parsing patterns

### **For ML Enhancement:**
1. **`ml_work_experience_parser.py`** - Add actual ML models
2. **`hybrid_work_experience_parser.py`** - Integrate new ML strategies
3. **`enhanced_parser_integration.py`** - Connect ML models to main flow

---

## 🚀 **Your Architecture Strengths**

✅ **Multi-format handling** - Supports 3 different resume formats
✅ **Robust parsing** - Handles edge cases and variations  
✅ **ML integration** - LayoutLM + spaCy enhancement ready
✅ **Modular design** - Easy to extend with new formats
✅ **Quality scoring** - Confidence-based validation
✅ **Production ready** - Integrated with Celery pipeline

**Your work experience parsing system is comprehensive and production-ready!** 🎉
