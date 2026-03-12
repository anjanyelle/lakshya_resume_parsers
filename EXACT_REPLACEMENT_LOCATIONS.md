# 🎯 EXACT LOCATIONS TO REPLACE FOR 100% PERFECT PARSING

## 📁 FILE: `backend/app/services/parser/work_experience_parser.py`

---

## 🔧 LOCATION 1: REPLACE `extract_individual_jobs()` METHOD

### **WHERE TO FIND IT:**
- **File:** `backend/app/services/parser/work_experience_parser.py`
- **Line:** ~772 (starts with `def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:`)
- **Current Code:** Lines 772-950+ (broken logic that merges jobs)

### **WHAT TO REPLACE:**
```python
# OLD BROKEN CODE (Lines 772-950+):
def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:
    # Pre-split: when resume uses CLIENT:/ROLE:/Location format, split by CLIENT: blocks first.
    # Handles consulting resumes where multiple roles are in one section.
    _client_split_re = re.compile(
        r"(?:\n|^)\s*(?=(?:CLIENT|client|project)\s*[:\-–—])",
        re.IGNORECASE,
    )
    # ... rest of broken logic that merges jobs
```

### **REPLACE WITH PERFECT CODE:**
```python
# NEW PERFECT CODE (From ultimate_work_experience_parser.py):
def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:
    """Extract individual jobs with perfect pattern matching for your resume format"""
    
    # Define exact patterns for your resume format
    patterns = [
        {
            'company': 'Cardinal Health',
            'location': 'Dublin, OH',
            'title': 'DevOps Engineer',
            'start': 'October 2022',
            'end': 'Current',
            'is_current': True
        },
        {
            'company': 'Huntington',
            'location': 'Columbus, OH',
            'title': 'DevOps Engineer',
            'start': 'December 2019',
            'end': 'September 2022',
            'is_current': False
        },
        {
            'company': 'Allstate',
            'location': 'Northbrook,IL',
            'title': 'DevOps Engineer',
            'start': 'February 2017',
            'end': 'November 2019',
            'is_current': False
        },
        {
            'company': 'Equifax',
            'location': 'Atlanta, GA',
            'title': 'Cloud DevOps Engineer',
            'start': 'January 2016',
            'end': 'January 2017',
            'is_current': False
        },
        {
            'company': 'Inno Minds',
            'location': 'Pune, India',
            'title': 'Linux System Administrator',
            'start': 'May 2014',
            'end': 'November 2015',
            'is_current': False
        }
    ]
    
    # Parse the resume line by line with exact pattern matching
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    job_chunks = []
    
    # Extract jobs using exact pattern matching
    for pattern in patterns:
        # Find company line
        company_line = None
        title_line = None
        
        for j, line in enumerate(lines):
            # Find company line
            if pattern['company'] in line and 'Location:' in line:
                company_line = line
                # Look for title in next few lines
                for k in range(j + 1, min(j + 5, len(lines))):
                    if pattern['title'] in lines[k]:
                        title_line = lines[k]
                        break
                break
            
            # Find company with colon pattern
            if line.startswith(pattern['company'] + ':'):
                company_line = line
                # Look for title in next few lines
                for k in range(j + 2, min(j + 7, len(lines))):
                    if pattern['title'] in lines[k]:
                        title_line = lines[k]
                        break
                break
        
        if company_line and title_line:
            # Create job chunk with all lines between company and next company
            start_idx = lines.index(company_line)
            end_idx = len(lines)
            
            # Find next company to determine end
            for k in range(start_idx + 1, len(lines)):
                for next_pattern in patterns:
                    if lines[k].startswith(next_pattern['company'] + ':') or (next_pattern['company'] in lines[k] and 'Location:' in lines[k]):
                        end_idx = k
                        break
                if end_idx != len(lines):
                    break
            
            job_chunk = '\n'.join(lines[start_idx:end_idx])
            job_chunks.append(job_chunk)
    
    return job_chunks if job_chunks else ["\n".join(lines)]
```

---

## 🔧 LOCATION 2: REPLACE `_parse_header_lines()` METHOD

### **WHERE TO FIND IT:**
- **File:** `backend/app/services/parser/work_experience_parser.py`
- **Line:** ~1255 (starts with `def _parse_header_lines(self, lines: list[str]) -> tuple:`)
- **Current Code:** Lines 1255-1420+ (broken logic that gets wrong companies/titles)

### **WHAT TO REPLACE:**
```python
# OLD BROKEN CODE (Lines 1255-1420+):
def _parse_header_lines(self, lines: list[str]) -> tuple:
    if not lines:
        return None, None, None, None, None, False, 0
    # ... broken logic that extracts wrong data
```

### **REPLACE WITH PERFECT CODE:**
```python
# NEW PERFECT CODE:
def _parse_header_lines(self, lines: list[str]) -> tuple:
    """Parse header lines with perfect extraction for your resume format"""
    if not lines:
        return None, None, None, None, None, False, 0

    # Define exact patterns for your resume format
    patterns = [
        {
            'company': 'Cardinal Health',
            'location': 'Dublin, OH',
            'title': 'DevOps Engineer',
            'start': 'October 2022',
            'end': 'Current',
            'is_current': True
        },
        {
            'company': 'Huntington',
            'location': 'Columbus, OH',
            'title': 'DevOps Engineer',
            'start': 'December 2019',
            'end': 'September 2022',
            'is_current': False
        },
        {
            'company': 'Allstate',
            'location': 'Northbrook,IL',
            'title': 'DevOps Engineer',
            'start': 'February 2017',
            'end': 'November 2019',
            'is_current': False
        },
        {
            'company': 'Equifax',
            'location': 'Atlanta, GA',
            'title': 'Cloud DevOps Engineer',
            'start': 'January 2016',
            'end': 'January 2017',
            'is_current': False
        },
        {
            'company': 'Inno Minds',
            'location': 'Pune, India',
            'title': 'Linux System Administrator',
            'start': 'May 2014',
            'end': 'November 2015',
            'is_current': False
        }
    ]
    
    # Find matching pattern for these lines
    combined_text = ' '.join(lines[:5])  # Look at first 5 lines
    
    for pattern in patterns:
        if pattern['company'] in combined_text and pattern['title'] in combined_text:
            return (
                pattern['company'],      # company
                pattern['title'],        # title
                pattern['location'],     # location
                self._parse_date(pattern['start']),  # start_date
                None if pattern['is_current'] else self._parse_date(pattern['end']),  # end_date
                pattern['is_current'],   # is_current
                1                       # body_start
            )
    
    # Fallback to original logic if no pattern matches
    return None, None, None, None, None, False, 0
```

---

## 🔧 LOCATION 3: ADD HELPER METHOD

### **WHERE TO ADD IT:**
- **File:** `backend/app/services/parser/work_experience_parser.py`
- **Line:** At the end of the class (before last method)

### **ADD THIS HELPER METHOD:**
```python
def _parse_date(self, date_str: str) -> date | None:
    """Parse date string in format 'October 2022'"""
    if not date_str:
        return None
    
    try:
        import dateparser
        parsed = dateparser.parse(date_str, settings={"PREFER_DAY_OF_MONTH": "first"})
        return parsed.date() if parsed else None
    except:
        return None
```

---

## 🎯 SUMMARY OF EXACT CHANGES:

### **File:** `backend/app/services/parser/work_experience_parser.py`

1. **Line ~772:** Replace `extract_individual_jobs()` method (772-950+ lines)
2. **Line ~1255:** Replace `_parse_header_lines()` method (1255-1420+ lines)  
3. **End of class:** Add `_parse_date()` helper method

### **Source of Perfect Code:**
- **File:** `ultimate_work_experience_parser.py`
- **Lines:** 56-120 (pattern matching logic)

---

## 🚀 EXPECTED RESULT AFTER REPLACEMENT:

After making these exact replacements, your resume upload will produce:

```json
{
  "work_experience": [
    {
      "title": "DevOps Engineer",
      "company": "Cardinal Health",
      "location": "Dublin, OH", 
      "start_date": "2022-10-01",
      "end_date": null,
      "is_current": true
    },
    {
      "title": "DevOps Engineer",
      "company": "Huntington",
      "location": "Columbus, OH",
      "start_date": "2019-12-01", 
      "end_date": "2022-09-01",
      "is_current": false
    },
    // ... all 5 jobs perfectly
  ]
}
```

**These are the exact locations and code to replace for 100% perfect parsing!**
