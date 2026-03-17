# Dataset Download Links for Enhanced Resume Parser

## 🎯 **Work Experience & Certification Datasets**

### **1. Resume Datasets (Primary Source)**

#### **A. Resume Classification Dataset**
- **Link**: https://github.com/noran-mohamed/Resume-Classification-Dataset
- **Format**: CSV with Category and Text columns
- **Records**: 13,389 resumes
- **Content**: Real resumes with job titles and extracted text
- **Download**: Clone the repository or download CSV files
```bash
git clone https://github.com/noran-mohamed/Resume-Classification-Dataset.git
```

#### **B. Resume Dataset (Structured)**
- **Link**: https://www.kaggle.com/datasets/suriyaganesh/resume-dataset-structured
- **Format**: Structured CSV
- **Content**: Pre-processed resume data with work experience
- **Requires**: Kaggle account for download

#### **C. AI-Powered Resume Screening Dataset (2025)**
- **Link**: https://www.kaggle.com/datasets/mdtalhask/ai-powered-resume-screening-dataset-2025
- **Format**: CSV
- **Content**: Latest resume screening data with annotations
- **Requires**: Kaggle account

### **2. Company Databases**

#### **A. Fortune 500 Companies (1955-2019)**
- **Link**: https://github.com/cmusam/fortune500
- **Format**: CSV files by year
- **Content**: Company names, rankings, revenue, industry
- **Download**:
```bash
git clone https://github.com/cmusam/fortune500.git
# CSV files are in the csv/ directory
```

#### **B. Kaggle Company Dataset**
- **Link**: https://www.kaggle.com/datasets/rm1000/fortune-500-companies
- **Format**: CSV
- **Content**: Company information with industry classification
- **Requires**: Kaggle account

#### **C. Company Information Database**
- **Link**: https://www.gigasheet.com/sample-data/fortune-500-companies
- **Format**: CSV/Excel
- **Content**: Comprehensive company data with industry tags
- **Download**: Direct download available

### **3. Professional Certifications Datasets**

#### **A. Coursera Course & Certification Data**
- **Link**: https://www.kaggle.com/datasets/kashnitsky/coursera-courses-dataset
- **Format**: CSV
- **Content**: Course titles, providers, skills, duration
- **Requires**: Kaggle account

#### **B. Professional Certifications Database**
- **Link**: https://github.com/florex/resume_corpus
- **Format**: CSV/JSON
- **Content**: Multi-labeled resume dataset with certifications
- **Download**:
```bash
git clone https://github.com/florex/resume_corpus.git
```

#### **C. Job Postings Dataset (for skill mapping)**
- **Link**: https://github.com/binoydutt/Resume-Job-Description-Matching
- **Format**: CSV
- **Content**: Job descriptions with required skills and certifications
- **Download**:
```bash
git clone https://github.com/binoydutt/Resume-Job-Description-Matching.git
# Look for data.csv file
```

### **4. Job Titles & Skills Datasets**

#### **A. Job Title Classification Dataset**
- **Link**: https://www.kaggle.com/datasets/shashichander003/job-titles-dataset
- **Format**: CSV
- **Content**: Job titles with categories and seniority levels
- **Requires**: Kaggle account

#### **B. Skills Taxonomy (ESCO)**
- **Link**: https://ec.europa.eu/esco/portal/skill-browser
- **Format**: JSON/CSV export
- **Content**: European skills classification system
- **Download**: Free export from the portal

#### **C. Technical Skills Dataset**
- **Link**: https://github.com/owid/technical-skills-dataset
- **Format**: CSV
- **Content**: Technical skills with categories and difficulty levels
- **Download**:
```bash
git clone https://github.com/owid/technical-skills-dataset.git
```

### **5. Training & Course Datasets**

#### **A. EdX Course Dataset**
- **Link**: https://www.kaggle.com/datasets/edx/edx-courses-dataset
- **Format**: CSV
- **Content**: Course information with skills and outcomes
- **Requires**: Kaggle account

#### **B. Udemy Course Dataset**
- **Link**: https://www.kaggle.com/datasets/hugoromanish/udemy-courses-dataset
- **Format**: CSV
- **Content**: Course titles, descriptions, skills taught
- **Requires**: Kaggle account

## 📁 **Directory Structure After Download**

```
data/
├── external/
│   ├── work_experience/
│   │   ├── resume_classification_dataset.csv      # From GitHub
│   │   ├── resume_dataset_structured.csv        # From Kaggle
│   │   ├── ai_resume_screening_2025.csv          # From Kaggle
│   │   └── job_titles_dataset.csv                # From Kaggle
│   ├── companies/
│   │   ├── fortune500_2019.csv                   # From GitHub
│   │   ├── fortune500_historical/                 # From GitHub (multiple years)
│   │   └── company_information.csv                # From Gigasheet
│   ├── certifications/
│   │   ├── coursera_courses.csv                   # From Kaggle
│   │   ├── resume_corpus_certifications.csv      # From GitHub
│   │   ├── edx_courses.csv                        # From Kaggle
│   │   └── udemy_courses.csv                      # From Kaggle
│   ├── skills/
│   │   ├── esco_skills_taxonomy.json              # From ESCO portal
│   │   ├── technical_skills_dataset.csv            # From GitHub
│   │   └── job_matching_skills.csv                # From GitHub
│   └── mappings/
│       ├── job_title_mappings.json                # Generated
│       ├── company_normalization.json             # Generated
│       └── certification_standardization.json    # Generated
```

## 🚀 **Quick Download Commands**

### **GitHub Datasets (Free)**
```bash
# Resume Classification Dataset
git clone https://github.com/noran-mohamed/Resume-Classification-Dataset.git

# Fortune 500 Companies
git clone https://github.com/cmusam/fortune500.git

# Resume Corpus (with certifications)
git clone https://github.com/florex/resume_corpus.git

# Job-Description Matching
git clone https://github.com/binoydutt/Resume-Job-Description-Matching.git

# Technical Skills Dataset
git clone https://github.com/owid/technical-skills-dataset.git
```

### **Kaggle Datasets (Requires Account)**
```python
# Use Kaggle API to download datasets
import kaggle

# Resume datasets
kaggle.api.dataset_download_files('suriyaganesh/resume-dataset-structured')
kaggle.api.dataset_download_files('mdtalhask/ai-powered-resume-screening-dataset-2025')
kaggle.api.dataset_download_files('shashichander003/job-titles-dataset')

# Course & Certification datasets
kaggle.api.dataset_download_files('kashnitsky/coursera-courses-dataset')
kaggle.api.dataset_download_files('edx/edx-courses-dataset')
kaggle.api.dataset_download_files('hugoromanish/udemy-courses-dataset')

# Company dataset
kaggle.api.dataset_download_files('rm1000/fortune-500-companies')
```

## 📊 **Dataset Quality Assessment**

### **High Priority (Download First)**
1. **Resume Classification Dataset** - 13K+ real resumes
2. **Fortune 500 Companies** - Company normalization data
3. **Coursera Courses Dataset** - Certification and course data
4. **Job-Description Matching** - Skills mapping data

### **Medium Priority**
1. **Resume Dataset Structured** - Additional resume data
2. **Job Titles Dataset** - Title normalization
3. **ESCO Skills Taxonomy** - Skills classification

### **Optional (If Needed)**
1. **AI Resume Screening 2025** - Latest data
2. **EdX/Udemy Courses** - More course data
3. **Technical Skills Dataset** - Additional skills

## 🔧 **Next Steps**

1. **Download high-priority datasets** using the links above
2. **Place files** in the specified directory structure
3. **Run the processing scripts** to normalize and integrate data
4. **Test the enhanced parser** with your new datasets
5. **Fine-tune patterns** based on your specific resume formats

These datasets will provide comprehensive coverage for work experience and certification parsing using the Kickresume-style approach!
