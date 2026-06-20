# Resume Parser Evaluation Framework Architecture

## Overview
This document outlines the complete evaluation framework architecture for the Resume Parser application, designed to provide comprehensive debugging, accuracy testing, error classification, and production monitoring capabilities.

## Current Pipeline Analysis

### Existing Flow
1. **Text Extraction** → Extract text from PDF/DOCX/Image files
2. **Section Splitting** → Identify Experience, Education, Skills sections
3. **Rule-Based Parsing** → Extract basic entities using regex patterns
4. **DeBERTa NER** → Named entity recognition with Microsoft DeBERTa v3 model
5. **AI Entity Extraction** → LLM-based extraction for complex entities
6. **Experience Extraction** → Structured work experience extraction
7. **Education Extraction** → Structured education extraction
8. **Result Merging** → Combine all extraction results

### Current Database Schema
- `candidates` - Stores candidate profiles and parsed results
- `parsing_jobs` - Stores parsing job status and results

## Evaluation Framework Architecture

### 1. Debug Logging Pipeline

#### Purpose
Capture and store all intermediate results for comprehensive debugging and analysis.

#### Components
```
┌─────────────────────────────────────────────────────────────┐
│                   DEBUG LOGGING PIPELINE                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Input      │    │  Processing  │    │   Output     │  │
│  │   Logger     │───▶│   Logger     │───▶│   Logger     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Raw Input   │    │ Intermediate │    │ Final Output │  │
│  │  Storage     │    │  Storage     │    │  Storage     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         └───────────────────┴───────────────────┘          │
│                             │                               │
│                             ▼                               │
│                    ┌──────────────┐                        │
│                    │   Evaluation │                        │
│                    │   Database   │                        │
│                    └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

#### Data Capture Points
1. **Raw Input Stage**
   - Original file metadata
   - Raw extracted text
   - File quality metrics

2. **Section Splitting Stage**
   - Detected sections
   - Section boundaries
   - Section content

3. **Model Input Stage**
   - Preprocessed text sent to model
   - Prompt used for LLM calls
   - Context window utilization

4. **Model Output Stage**
   - Raw model response
   - Parsed entities
   - Confidence scores

5. **Final Output Stage**
   - Merged results
   - Validation results
   - Final JSON output

### 2. Accuracy Testing Framework

#### Purpose
Systematically measure parsing accuracy across different resume types and quality levels.

#### Test Dataset Structure
```
test_dataset/
├── resumes/
│   ├── simple_resumes/          # 20 straightforward resumes
│   ├── complex_resumes/         # 20 complex formatting
│   ├── multilingual_resumes/    # 10 non-English resumes
│   ├── image_resumes/           # 10 scanned PDFs
│   ├── entry_level_resumes/     # 20 entry-level resumes
│   ├── executive_resumes/       # 20 executive resumes
│   └── edge_cases/              # 10 edge case resumes
└── ground_truth/
    ├── simple_resumes_gt.json   # Ground truth annotations
    ├── complex_resumes_gt.json
    └── ...
```

#### Accuracy Metrics
1. **Text Extraction Accuracy**
   - Character-level accuracy
   - Word-level accuracy
   - Layout preservation score

2. **Section Detection Accuracy**
   - Section boundary precision
   - Section classification accuracy
   - Section completeness score

3. **Entity Extraction Accuracy**
   - Field-level F1 score
   - Entity type accuracy
   - Attribute completeness

4. **Overall Pipeline Accuracy**
   - End-to-end success rate
   - Processing time distribution
   - Memory usage patterns

### 3. Error Classification System

#### Error Categories
```python
class ErrorType(Enum):
    # Extraction Errors
    TEXT_EXTRACTION_FAILED = "text_extraction_failed"
    OCR_QUALITY_LOW = "ocr_quality_low"
    FILE_CORRUPTED = "file_corrupted"
    UNSUPPORTED_FORMAT = "unsupported_format"
    
    # Section Splitting Errors
    SECTION_DETECTION_FAILED = "section_detection_failed"
    SECTION_BOUNDARY_ERROR = "section_boundary_error"
    MISSING_CRITICAL_SECTION = "missing_critical_section"
    
    # Model Inference Errors
    MODEL_LOADING_FAILED = "model_loading_failed"
    INFERENCE_TIMEOUT = "inference_timeout"
    MODEL_OUTPUT_MALFORMED = "model_output_malformed"
    CONFIDENCE_TOO_LOW = "confidence_too_low"
    
    # JSON Formatting Errors
    JSON_PARSE_FAILED = "json_parse_failed"
    SCHEMA_VALIDATION_FAILED = "schema_validation_failed"
    DATA_TYPE_MISMATCH = "data_type_mismatch"
    REQUIRED_FIELD_MISSING = "required_field_missing"
    
    # Validation Errors
    ENTITY_VALIDATION_FAILED = "entity_validation_failed"
    DATE_VALIDATION_FAILED = "date_validation_failed"
    EMAIL_VALIDATION_FAILED = "email_validation_failed"
    PHONE_VALIDATION_FAILED = "phone_validation_failed"
```

#### Error Classification Pipeline
```
┌─────────────────────────────────────────────────────────────┐
│                  ERROR CLASSIFICATION PIPELINE               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Error      │    │  Context     │    │  Classified  │  │
│  │   Detection  │───▶│  Analysis    │───▶│    Error     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Exception   │    │  Pipeline    │    │  Error Type  │  │
│  │   Catching   │    │   Stage      │    │  Assignment │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         └───────────────────┴───────────────────┘          │
│                             │                               │
│                             ▼                               │
│                    ┌──────────────┐                        │
│                    │  Error Store │                        │
│                    │   & Metrics  │                        │
│                    └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 4. Evaluation Dashboard

#### Dashboard Components
1. **Overview Metrics**
   - Total resumes processed
   - Success rate percentage
   - Average processing time
   - Error rate breakdown

2. **Accuracy Charts**
   - Text extraction accuracy trend
   - Section detection accuracy trend
   - Entity extraction accuracy trend
   - Overall pipeline accuracy

3. **Error Analysis**
   - Error type distribution
   - Error frequency over time
   - Common error patterns
   - Error recovery rate

4. **Performance Metrics**
   - Processing time distribution
   - Memory usage patterns
   - Model inference time
   - API response times

5. **Quality Trends**
   - Confidence score distribution
   - Data quality trends
   - Validation failure rates
   - User feedback patterns

### 5. Prompt Engineering Improvements

#### Enhanced Prompt Strategy
```python
class PromptTemplates:
    EXPERIENCE_EXTRACTION = """
    You are an expert resume parser. Extract structured work experience from the following resume section.
    
    RULES:
    - Extract ALL work experiences in chronological order
    - For each experience, extract: company, job_title, start_date, end_date, description, location
    - Dates must be in MM/YYYY or MM/DD/YYYY format
    - If end_date is "present", use current date
    - Return ONLY valid JSON, no explanations
    
    INPUT TEXT:
    {experience_section}
    
    OUTPUT FORMAT:
    {{
        "work_experience": [
            {{
                "company": "string",
                "job_title": "string", 
                "start_date": "MM/YYYY",
                "end_date": "MM/YYYY",
                "description": "string",
                "location": "string"
            }}
        ]
    }}
    """
    
    EDUCATION_EXTRACTION = """
    You are an expert resume parser. Extract structured education information from the following resume section.
    
    RULES:
    - Extract ALL education entries
    - For each entry, extract: institution, degree, field_of_study, start_date, end_date, gpa
    - Identify degree type (Bachelor's, Master's, PhD, etc.)
    - Return ONLY valid JSON, no explanations
    
    INPUT TEXT:
    {education_section}
    
    OUTPUT FORMAT:
    {{
        "education": [
            {{
                "institution": "string",
                "degree": "string",
                "field_of_study": "string",
                "start_date": "MM/YYYY",
                "end_date": "MM/YYYY",
                "gpa": "string"
            }}
        ]
    }}
    """
```

### 6. Confidence Scoring System

#### Multi-Level Confidence Calculation
```python
class ConfidenceCalculator:
    def calculate_field_confidence(self, field_name: str, extracted_value: Any, context: Dict) -> float:
        """
        Calculate confidence score for individual extracted fields.
        
        Factors:
        - Extraction method confidence
        - Data validation results
        - Context consistency
        - Historical accuracy
        """
        base_confidence = 0.5
        
        # Method confidence
        method_bonus = self.get_method_confidence(context.get('extraction_method'))
        
        # Validation confidence
        validation_bonus = self.validate_field(field_name, extracted_value)
        
        # Context confidence
        context_bonus = self.check_context_consistency(field_name, extracted_value, context)
        
        # Historical confidence
        history_bonus = self.get_historical_accuracy(field_name)
        
        final_confidence = base_confidence + method_bonus + validation_bonus + context_bonus + history_bonus
        return min(max(final_confidence, 0.0), 1.0)
    
    def calculate_overall_confidence(self, parsed_data: Dict) -> Dict:
        """
        Calculate overall confidence scores for the entire parsed result.
        """
        field_confidences = {}
        for field_name, field_value in parsed_data.items():
            if isinstance(field_value, list):
                # For arrays, calculate average confidence
                item_confidences = [
                    self.calculate_field_confidence(field_name, item, parsed_data)
                    for item in field_value
                ]
                field_confidences[field_name] = sum(item_confidences) / len(item_confidences) if item_confidences else 0.0
            else:
                field_confidences[field_name] = self.calculate_field_confidence(field_name, field_value, parsed_data)
        
        overall_confidence = sum(field_confidences.values()) / len(field_confidences) if field_confidences else 0.0
        
        return {
            'overall': overall_confidence,
            'fields': field_confidences,
            'needs_review': overall_confidence < 0.8,
            'quality_level': self.get_quality_level(overall_confidence)
        }
```

### 7. Production Readiness Checklist

#### Accuracy Benchmarks
- [ ] Text extraction accuracy > 95%
- [ ] Section detection accuracy > 90%
- [ ] Entity extraction accuracy > 85%
- [ ] Overall pipeline success rate > 80%
- [ ] Average processing time < 10 seconds
- [ ] Error rate < 5%

#### Logging Strategy
- [ ] All intermediate results logged
- [ ] Error logging with full context
- [ ] Performance metrics captured
- [ ] Log retention policy defined
- [ ] Sensitive data masking implemented

#### Monitoring Strategy
- [ ] Real-time health checks
- [ ] Performance dashboards
- [ ] Error alerting system
- [ ] Accuracy trend monitoring
- [ ] Resource usage monitoring

#### Retry Strategy
- [ ] Exponential backoff implemented
- [ ] Maximum retry limits defined
- [ ] Retry logic for transient errors
- [ ] Fallback mechanisms configured
- [ ] Dead letter queue for failed jobs

#### Validation Rules
- [ ] Schema validation implemented
- [ ] Data type validation
- [ ] Business rule validation
- [ ] Cross-field validation
- [ ] Format validation

## Database Schema Extensions

### New Tables for Evaluation Framework

```sql
-- Debug logs table
CREATE TABLE evaluation_debug_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id),
    parsing_job_id UUID REFERENCES parsing_jobs(id),
    stage VARCHAR(50) NOT NULL,
    log_type VARCHAR(20) NOT NULL, -- 'input', 'processing', 'output'
    data JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Accuracy test results table
CREATE TABLE evaluation_test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite VARCHAR(100) NOT NULL,
    test_case_id VARCHAR(100) NOT NULL,
    resume_file_path VARCHAR(500),
    ground_truth_data JSONB NOT NULL,
    parsed_data JSONB NOT NULL,
    metrics JSONB NOT NULL,
    test_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Error classification table
CREATE TABLE evaluation_error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id),
    parsing_job_id UUID REFERENCES parsing_jobs(id),
    error_type VARCHAR(50) NOT NULL,
    error_category VARCHAR(50) NOT NULL,
    error_message TEXT,
    stack_trace TEXT,
    context_data JSONB,
    recovery_attempted BOOLEAN DEFAULT false,
    recovery_successful BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE evaluation_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parsing_job_id UUID REFERENCES parsing_jobs(id),
    stage_name VARCHAR(50) NOT NULL,
    duration_ms INTEGER NOT NULL,
    memory_usage_mb INTEGER,
    cpu_usage_percent NUMERIC(5,2),
    custom_metrics JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Confidence scores table
CREATE TABLE evaluation_confidence_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id),
    parsing_job_id UUID REFERENCES parsing_jobs(id),
    field_name VARCHAR(100) NOT NULL,
    confidence_score NUMERIC(5,4) NOT NULL,
    confidence_factors JSONB,
    validation_results JSONB,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Implementation Plan

### Phase 1: Infrastructure Setup (Week 1)
1. Create database schema extensions
2. Set up debug logging pipeline
3. Implement error classification system
4. Create base evaluation framework

### Phase 2: Testing Framework (Week 2)
1. Build test dataset collection
2. Create ground truth annotations
3. Implement accuracy testing scripts
4. Set up automated testing pipeline

### Phase 3: Dashboard & Monitoring (Week 3)
1. Build evaluation dashboard
2. Implement real-time monitoring
3. Create alerting system
4. Set up performance tracking

### Phase 4: Optimization (Week 4)
1. Implement prompt engineering improvements
2. Enhance confidence scoring
3. Optimize based on test results
4. Complete production readiness checklist

## Success Criteria

### Technical Metrics
- Debug logging coverage: 100%
- Error classification accuracy: >95%
- Test automation: 100+ test cases
- Dashboard refresh rate: <5 seconds

### Business Metrics
- Production deployment readiness
- Reduced manual review burden by 50%
- Improved parsing accuracy by 15%
- Enhanced error recovery rate by 30%

This evaluation framework will provide comprehensive visibility into your resume parsing pipeline, enabling data-driven improvements and ensuring production readiness.