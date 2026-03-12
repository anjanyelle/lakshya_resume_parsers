# Work Experience & Certification Dataset Requirements

## Datasets Needed for Kickresume-Style Parser

### 1. Work Experience Datasets

#### A. Job History Dataset
**Required Fields:**
- `job_title` (normalized)
- `company_name` 
- `start_date`, `end_date`
- `job_description`/responsibilities
- `industry`/sector
- `employment_type` (full-time, contract, etc.)
- `location` (city, country)
- `skills_used` (technical skills mentioned)

**Sources:**
- LinkedIn job postings dataset
- Indeed resume dataset
- Kaggle: "Job Postings Dataset" 
- Kaggle: "Resume Dataset" with work experience

#### B. Company Dataset
**Required Fields:**
- `company_name`
- `industry classification`
- `company_size`
- `location` (headquarters)
- `company_type` (startup, enterprise, etc.)

### 2. Certification Datasets

#### A. Professional Certifications
**Required Fields:**
- `certification_name`
- `issuing_organization` (CompTIA, Google, IBM, etc.)
- `certification_level` (Foundation, Professional, Expert)
- `validity_period`/expiration
- `skills_covered`
- `industry_relevance`

**Sources:**
- Coursera/edX certification data
- CompTIA certification database
- Google Career Certifications
- IBM Professional Certifications
- Microsoft Certifications

#### B. Course & Training Dataset
**Required Fields:**
- `course_title`
- `provider` (Coursera, Udemy, etc.)
- `duration`
- `skills_taught`
- `completion_date`
- `credential_type`

### 3. Integration Structure

#### Directory Layout:
```
data/
├── external/
│   ├── work_experience/
│   │   ├── job_history_dataset.csv
│   │   ├── company_database.csv
│   │   └── job_titles_normalized.csv
│   ├── certifications/
│   │   ├── professional_certifications.csv
│   │   ├── training_courses.csv
│   │   └── certification_authorities.csv
│   └── mappings/
│       ├── job_title_mappings.json
│       ├── company_normalization.json
│       └── certification_standardization.json
├── processed/
│   ├── work_experience_annotations.json
│   └── certification_annotations.json
└── models/
    ├── work_experience_parser/
    └── certification_parser/
```

### 4. Data Processing Scripts Needed

#### A. Work Experience Processor
- Normalize job titles
- Extract dates and duration
- Identify companies and standardize names
- Extract skills from job descriptions
- Classify industries

#### B. Certification Processor  
- Standardize certification names
- Identify issuing authorities
- Extract validity periods
- Map certifications to skills
- Classify by industry/domain

### 5. Training Data Format

#### Work Experience JSON:
```json
{
  "work_experience": [
    {
      "job_title": "Senior Software Engineer",
      "company": "Google",
      "start_date": "2022-01-01",
      "end_date": "2024-01-01",
      "duration_months": 24,
      "responsibilities": [
        "Developed scalable web applications",
        "Led team of 5 engineers"
      ],
      "skills_used": ["Python", "React", "AWS"],
      "industry": "Technology",
      "location": "Mountain View, CA"
    }
  ]
}
```

#### Certification JSON:
```json
{
  "certifications": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon Web Services",
      "level": "Professional",
      "issue_date": "2023-06-01",
      "expiration_date": "2026-06-01",
      "credential_id": "AWS-123456",
      "skills_covered": ["Cloud Architecture", "AWS", "DevOps"],
      "industry": "Technology"
    }
  ]
}
```

### 6. Recommended Datasets to Download

#### From Kaggle:
1. "Resume Dataset" - Contains real resumes with work experience
2. "Job Postings Dataset" - For job title normalization
3. "LinkedIn Job Data" - Company and industry information
4. "Coursera Course Dataset" - Certification and course data

#### From GitHub/Open Sources:
1. "Professional Certifications Database"
2. "Company Information Database"
3. "Skills Taxonomy" (ESCO or similar)

### 7. Next Steps

1. **Download datasets** from recommended sources
2. **Create processing scripts** for each data type
3. **Build normalization mappings** for companies and job titles
4. **Train separate models** for work experience and certification parsing
5. **Integrate with existing LLM service** for enhanced parsing
