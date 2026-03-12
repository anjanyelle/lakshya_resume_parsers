# 📁 PROJECT FILES - CERTIFICATIONS & WORK EXPERIENCE SECTIONS

## 🏆 CERTIFICATIONS SECTION FILES

### **🔧 Backend Parser Files**
```
backend/app/services/parser/
├── certification_parser.py              # Main certification parsing logic
├── certification_validator.py           # Validation & cleaning of cert data
└── __pycache__/
    ├── certification_parser.cpython-313.pyc
    └── certification_validator.cpython-313.pyc
```

### **🗃️ Backend Model Files**
```
backend/app/models/
├── certification.py                     # Certification SQLAlchemy model
└── __pycache__/
    └── certification.cpython-313.pyc
```

### **📊 Backend Data Files**
```
backend/app/data/taxonomy/
├── certifications_top.py                # Certification database & aliases
└── __pycache__/
    └── certifications_top.cpython-313.pyc
```

### **🧪 Backend Test Files**
```
backend/tests/unit/
└── test_certification_parser.py        # Unit tests for cert parser
```

### **🎨 Frontend Component Files**
```
frontend/src/components/candidate-detail/
└── CertificationsSection.tsx           # React component for displaying certs
```

### **📂 External Dataset Files**
```
data/external/certifications/
├── sample_certifications.csv           # Sample certification data
├── coursera_courses.csv                # Coursera course dataset
└── awesome_certificates/
    ├── awesome-certificates.md         # Awesome certs list
    └── media/
        └── awesome-certificates.png
```

### **📝 Script Files**
```
data/scripts/
└── enhanced_work_cert_parser.py        # Enhanced work & cert parser script

# Debug/Test Files (Root)
├── debug_cert_parsing.py               # Debug certification parsing
└── enhanced_work_cert_parser.py        # Enhanced parser script
```

---

## 🏢 WORK EXPERIENCE SECTION FILES

### **🔧 Backend Parser Files**
```
backend/app/services/parser/
├── work_experience_parser.py           # Main work experience parsing logic
├── work_experience_sanitizer.py        # Sanitization & cleaning of work data
└── __pycache__/
    ├── work_experience_parser.cpython-313.pyc
    └── work_experience_sanitizer.cpython-313.pyc
```

### **🗃️ Backend Model Files**
```
backend/app/models/
├── work_history.py                      # Work history SQLAlchemy model
└── __pycache__/
    └── work_history.cpython-313.pyc
```

### **🧪 Backend Test Files**
```
backend/tests/
├── test_experience_pipeline.py          # Integration tests for experience
└── unit/
    ├── test_work_experience_parser.py   # Unit tests for work parser
    └── test_work_experience_sanitizer.py # Unit tests for sanitizer
```

### **🎨 Frontend Component Files**
```
frontend/src/components/candidate-detail/
└── WorkHistoryTimeline.tsx              # React component for work history display
```

### **📝 Script Files**
```
# Debug/Test Files (Root)
├── debug_work_parsing.py               # Debug work experience parsing
├── fix_work_parsing.py                 # Fix work parsing issues
├── EXPERIENCE_PARSING_ANALYSIS.md      # Analysis of parsing results
└── enhanced_work_cert_parser.py        # Enhanced work & cert parser script
```

---

## 🗄️ DATABASE FILES

### **📋 Database Migration Files**
```
backend/alembic/versions/
├── 003_add_years_experience_confidence.py # Migration for experience confidence
└── __pycache__/
    └── 003_add_years_experience_confidence.cpython-313.pyc
```

---

## 📊 SUMMARY BY CATEGORY

### **🏆 CERTIFICATIONS (16 files):**
- **Core Parser**: `certification_parser.py`
- **Validator**: `certification_validator.py`
- **Model**: `certification.py`
- **Data**: `certifications_top.py`
- **Frontend**: `CertificationsSection.tsx`
- **Tests**: `test_certification_parser.py`
- **Datasets**: `sample_certifications.csv`, `coursera_courses.csv`

### **🏢 WORK EXPERIENCE (28 files):**
- **Core Parser**: `work_experience_parser.py`
- **Sanitizer**: `work_experience_sanitizer.py`
- **Model**: `work_history.py`
- **Frontend**: `WorkHistoryTimeline.tsx`
- **Tests**: `test_work_experience_parser.py`, `test_experience_pipeline.py`
- **Migration**: `003_add_years_experience_confidence.py`

### **🔧 SHARED/ENHANCED FILES:**
- `enhanced_work_cert_parser.py` (handles both sections)
- Various debug scripts for both sections

---

## 🎯 KEY FILES TO MODIFY FOR FIXES:

### **For Certification Issues:**
1. `backend/app/services/parser/certification_parser.py` - Main parsing logic
2. `backend/app/data/taxonomy/certifications_top.py` - Certification database

### **For Work Experience Issues:**
1. `backend/app/services/parser/work_experience_parser.py` - Main parsing logic
2. `backend/app/services/parser/work_experience_sanitizer.py` - Data cleaning

### **For UI Updates:**
1. `frontend/src/components/candidate-detail/CertificationsSection.tsx`
2. `frontend/src/components/candidate-detail/WorkHistoryTimeline.tsx`

### **For Testing:**
1. `backend/tests/unit/test_certification_parser.py`
2. `backend/tests/unit/test_work_experience_parser.py`
