# Evaluation Framework Implementation Guide
## Step-by-Step Integration Instructions

---

## 🎯 Overview

This guide provides detailed instructions for integrating the comprehensive evaluation framework into your existing Resume Parser application. The framework includes:

1. **Debug Logging Pipeline** - Captures all intermediate results
2. **Accuracy Testing Framework** - Systematic testing against ground truth
3. **Error Classification System** - Categorizes and analyzes errors
4. **Evaluation Dashboard** - Real-time monitoring and insights
5. **Prompt Engineering Improvements** - Optimized prompts with retry logic
6. **Confidence Scoring System** - Enhanced confidence analysis
7. **Production Readiness Checklist** - Deployment validation

---

## 📁 File Structure

```
ai-service/
├── utils/
│   ├── debug_logger.py              # Debug logging pipeline
│   ├── error_classifier.py          # Error classification system
│   ├── enhanced_confidence_scorer.py # Enhanced confidence scoring
│   ├── prompt_engineering.py         # Prompt engineering improvements
│   ├── accuracy_tester.py           # Accuracy testing framework
│   └── evaluation_dashboard.py      # Evaluation dashboard
├── parsers/
│   └── master_parser.py             # Update with evaluation integration
backend/src/database/migrations/
└── 022_add_evaluation_framework.sql # Database schema extensions
```

---

## 🗄️ Step 1: Database Schema Setup

### Run the Migration

```bash
# Navigate to your backend directory
cd /path/to/Lakshya-LLM-Resume-Parser/backend

# Run the migration script
psql -U postgres -d resume_parser -f src/database/migrations/022_add_evaluation_framework.sql
```

### Verify Tables Created

```sql
-- Check that all tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'evaluation_%';

-- Expected output:
-- evaluation_debug_logs
-- evaluation_test_results
-- evaluation_error_logs
-- evaluation_performance_metrics
-- evaluation_confidence_scores
-- evaluation_test_suites
-- evaluation_test_cases
-- evaluation_summary
```

---

## 🔧 Step 2: Integrate Debug Logging into Master Parser

### Update Master Parser

Edit `ai-service/parsers/master_parser.py`:

```python
# Add imports at the top
from utils.debug_logger import DebugLogger, DebugLoggerFactory
from utils.error_classifier import ErrorClassifier, ErrorType, ErrorCategory
from utils.enhanced_confidence_scorer import EnhancedConfidenceScorer, ExtractionMethod

class MasterParser:
    def __init__(self):
        # ... existing initialization code ...
        
        # Initialize evaluation components
        self.debug_logger_factory = DebugLoggerFactory()
        self.error_classifier = ErrorClassifier()
        self.confidence_scorer = EnhancedConfidenceScorer()
        
    def parse_file(self, file_path: str, candidate_id: str, llm_provider: Optional[str] = None, force_ocr: bool = False) -> Dict[str, Any]:
        """
        Parse resume file with comprehensive debug logging.
        """
        # Initialize debug logger for this request
        debug_logger = self.debug_logger_factory.get_logger(candidate_id, enabled=True)
        
        try:
            # Log input
            debug_logger.log_input('file_input', {
                'file_path': file_path,
                'candidate_id': candidate_id,
                'force_ocr': force_ocr
            })
            
            # Step 1: Extract text with logging
            step_start = time.time()
            text_result = self._extract_text_from_file(file_path, force_ocr=force_ocr)
            metrics['text_extraction_ms'] = (time.time() - step_start) * 1000
            
            debug_logger.log_output('text_extraction', {
                'method': text_result.get('method'),
                'text_length': len(text_result.get('text', '')),
                'quality_score': text_result.get('quality_score')
            })
            
            # Step 2: Section splitting with logging
            step_start = time.time()
            sections = self._split_sections(text_result['text'])
            metrics['section_splitting_ms'] = (time.time() - step_start) * 1000
            
            debug_logger.log_section_extraction(sections)
            
            # Step 3: DeBERTa parsing with logging
            step_start = time.time()
            deberta_results = self._run_deberta_parsing(text_result['text'])
            metrics['deberta_parsing_ms'] = (time.time() - step_start) * 1000
            
            debug_logger.log_model_input('deberta-v3', text_result['text'])
            debug_logger.log_model_output('deberta-v3', None, deberta_results)
            
            # Continue with rest of pipeline...
            
            # Log final result
            debug_logger.log_final_result(result)
            
            # Export debug logs
            log_path = debug_logger.export_logs()
            
            # Add debug log path to result
            result['debug_log_path'] = log_path
            
            return result
            
        except Exception as e:
            # Classify and log error
            error_info = self.error_classifier.classify_error(e, {
                'stage': 'parse_file',
                'file_path': file_path,
                'candidate_id': candidate_id
            })
            debug_logger.log_error('parse_file', e, error_info)
            
            # Create error result
            return self._create_error_result(candidate_id, str(e), metrics, error_info)
```

---

## 🧪 Step 3: Set Up Accuracy Testing Framework

### Create Test Dataset Structure

```bash
mkdir -p test_dataset/resumes
mkdir -p test_dataset/ground_truth
```

### Create Ground Truth Data

Create `test_dataset/ground_truth/simple_resumes_gt.json`:

```json
{
  "resume_001": {
    "raw_text": "Extracted text from resume...",
    "sections": {
      "Experience": "Experience section content...",
      "Education": "Education section content..."
    },
    "name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "+1-555-123-4567",
    "work_experience": [
      {
        "company": "Tech Company",
        "job_title": "Software Engineer",
        "start_date": "01/2020",
        "end_date": "12/2023",
        "description": "Developed software applications..."
      }
    ],
    "education": [
      {
        "institution": "University",
        "degree": "Bachelor's",
        "field_of_study": "Computer Science",
        "start_date": "09/2016",
        "end_date": "05/2020"
      }
    ]
  }
}
```

### Run Accuracy Tests

Create `scripts/run_accuracy_tests.py`:

```python
#!/usr/bin/env python3
"""
Script to run accuracy tests against ground truth data
"""

import sys
sys.path.insert(0, '/path/to/ai-service')

from parsers.master_parser import MasterParser
from utils.accuracy_tester import AccuracyTester
import json

def main():
    # Initialize parser and tester
    parser = MasterParser()
    tester = AccuracyTester(parser)
    
    # Run test suite
    results = tester.run_test_suite(
        'test_dataset/resumes',
        'test_dataset/ground_truth/simple_resumes_gt.json'
    )
    
    # Generate report
    report_path = tester.generate_report()
    
    print(f"✅ Accuracy tests completed")
    print(f"📄 Report saved to: {report_path}")
    print(f"📊 Success rate: {results['aggregate_metrics']['success_rate']:.2%}")
    print(f"🎯 Average accuracy: {results['aggregate_metrics']['average_overall_accuracy']:.2%}")

if __name__ == '__main__':
    main()
```

---

## 🔍 Step 4: Integrate Error Classification

### Update Error Handling in Pipeline

```python
# In your parsing pipeline, wrap critical sections with error classification

try:
    # Text extraction
    text_result = self._extract_text_from_file(file_path)
except Exception as e:
    error_info = self.error_classifier.classify_error(e, {
        'stage': 'text_extraction',
        'file_path': file_path
    })
    
    # Log to database if you have database connection
    if self.db_connection:
        self.db_connection.execute(
            "SELECT record_error_log($1, $2, $3, $4, $5, $6, $7, $8)",
            [
                candidate_id,
                parsing_job_id,
                request_id,
                error_info['error_type'],
                error_info['error_category'],
                error_info['exception_message'],
                error_info['stack_trace'],
                json.dumps(error_info['context'])
            ]
        )
    
    # Try recovery strategy
    if error_info['recovery_strategies']:
        for strategy in error_info['recovery_strategies']:
            try:
                # Attempt recovery
                if "OCR" in strategy:
                    text_result = self._extract_text_from_file(file_path, force_ocr=True)
                    break
            except Exception as recovery_error:
                logger.warning(f"Recovery strategy failed: {strategy}")
                continue
```

---

## 📊 Step 5: Set Up Evaluation Dashboard

### Create Dashboard API Endpoint

Create `ai-service/api/dashboard.py`:

```python
from fastapi import APIRouter
from utils.evaluation_dashboard import EvaluationDashboard, AlertManager

router = APIRouter()
dashboard = EvaluationDashboard()
alert_manager = AlertManager()

@router.get("/dashboard/overview")
async def get_overview_metrics(time_period: str = "7d"):
    """Get overview metrics for dashboard."""
    return dashboard.get_overview_metrics(time_period)

@router.get("/dashboard/accuracy-trends")
async def get_accuracy_trends(time_period: str = "30d"):
    """Get accuracy trends over time."""
    return dashboard.get_accuracy_trends(time_period)

@router.get("/dashboard/errors")
async def get_error_analysis(time_period: str = "7d"):
    """Get error analysis."""
    return dashboard.get_error_analysis(time_period)

@router.get("/dashboard/performance")
async def get_performance_metrics(time_period: str = "7d"):
    """Get performance metrics."""
    return dashboard.get_performance_metrics(time_period)

@router.get("/dashboard/confidence")
async def get_confidence_analysis(time_period: str = "7d"):
    """Get confidence analysis."""
    return dashboard.get_confidence_analysis(time_period)

@router.get("/dashboard/alerts")
async def check_alerts():
    """Check for alerts based on current metrics."""
    metrics = dashboard.get_overview_metrics()
    alerts = alert_manager.check_alerts(metrics)
    return {"alerts": alerts}
```

---

## 🔧 Step 6: Integrate Enhanced Confidence Scoring

### Update Confidence Calculation in Master Parser

```python
# In your master parser, replace existing confidence calculation with enhanced version

def _calculate_confidence_scores(self, parsed_data: Dict[str, Any], extraction_methods: Dict[str, str] = None):
    """
    Calculate enhanced confidence scores using the new system.
    """
    # Convert string method names to ExtractionMethod enum
    method_mapping = {
        'rule_based': ExtractionMethod.RULE_BASED,
        'deberta_ner': ExtractionMethod.DEBERTA_NER,
        'llm_extraction': ExtractionMethod.LLM_EXTRACTION,
        'hybrid': ExtractionMethod.HYBRID
    }
    
    enum_methods = {}
    if extraction_methods:
        for field, method in extraction_methods.items():
            enum_methods[field] = method_mapping.get(method, ExtractionMethod.HYBRID)
    
    # Calculate enhanced confidence
    confidence_result = self.confidence_scorer.calculate_overall_confidence(
        parsed_data, enum_methods
    )
    
    return confidence_result
```

---

## 🤖 Step 7: Integrate Prompt Engineering Improvements

### Update LLM Extraction Calls

```python
from utils.prompt_engineering import PromptEngineer, JSONPostProcessor

class ExperienceExtractor:
    def __init__(self):
        self.prompt_engineer = PromptEngineer()
        self.post_processor = JSONPostProcessor()
        
    def extract_with_llm(self, experience_section: str, llm_function):
        """
        Extract experience using optimized prompts with retry logic.
        """
        expected_structure = {'work_experience': 'array'}
        
        # Try extraction with fallback
        success, result, version = self.prompt_engineer.retry_with_fallback(
            'experience',
            experience_section,
            llm_function,
            max_retries=3,
            expected_structure=expected_structure
        )
        
        if success:
            # Post-process the JSON result
            processed_result = self.post_processor.post_process_json(
                result, 'experience'
            )
            return processed_result
        else:
            logger.error("All prompt versions failed for experience extraction")
            return {'work_experience': []}
```

---

## 📈 Step 8: Set Up Automated Monitoring

### Create Monitoring Script

Create `scripts/monitoring.py`:

```python
#!/usr/bin/env python3
"""
Automated monitoring script for resume parser
"""

import sys
sys.path.insert(0, '/path/to/ai-service')

from utils.evaluation_dashboard import EvaluationDashboard, AlertManager
import requests
import smtplib
from email.mime.text import MIMEText

def send_alert(alert):
    """Send alert email."""
    msg = MIMEText(f"Alert: {alert['message']}")
    msg['Subject'] = f"Resume Parser Alert: {alert['severity']}"
    msg['From'] = 'monitoring@yourdomain.com'
    msg['To'] = 'ops-team@yourdomain.com'
    
    # Send email (configure your SMTP server)
    # with smtplib.SMTP('smtp.gmail.com', 587) as server:
    #     server.starttls()
    #     server.login('your-email', 'your-password')
    #     server.send_message(msg)
    #     server.quit()

def main():
    dashboard = EvaluationDashboard()
    alert_manager = AlertManager()
    
    # Get current metrics
    metrics = dashboard.get_overview_metrics()
    
    # Check for alerts
    alerts = alert_manager.check_alerts(metrics)
    
    # Send alerts for critical issues
    for alert in alerts:
        if alert['severity'] == 'critical':
            send_alert(alert)
            print(f"🚨 CRITICAL ALERT: {alert['message']}")
        elif alert['severity'] == 'warning':
            print(f"⚠️  WARNING: {alert['message']}")
    
    # Generate daily report
    report_path = dashboard.generate_dashboard_report()
    print(f"📊 Dashboard report: {report_path}")

if __name__ == '__main__':
    main()
```

### Set Up Cron Job

```bash
# Add to crontab for every hour monitoring
0 * * * * /usr/bin/python3 /path/to/scripts/monitoring.py
```

---

## 🧪 Step 9: Run Comprehensive Tests

### Test Integration

```bash
# Test debug logging
python -c "from utils.debug_logger import DebugLogger; logger = DebugLogger('test'); logger.log_input('test', {'test': 'data'}); print('Debug logging works')"

# Test error classification
python -c "from utils.error_classifier import ErrorClassifier; ec = ErrorClassifier(); result = ec.classify_error(ValueError('test error'), {'stage': 'test'}); print('Error classification works')"

# Test confidence scoring
python -c "from utils.enhanced_confidence_scorer import EnhancedConfidenceScorer, ExtractionMethod; cs = EnhancedConfidenceScorer(); result = cs.calculate_field_confidence('email', 'test@email.com', ExtractionMethod.RULE_BASED); print('Confidence scoring works')"

# Test prompt engineering
python -c "from utils.prompt_engineering import PromptEngineer; pe = PromptEngineer(); prompt = pe.get_prompt('experience', 'test experience section'); print('Prompt engineering works')"
```

---

## 🚀 Step 10: Production Deployment

### Pre-Deployment Checklist

1. **Database Migration**
   - [ ] Migration script run successfully
   - [ ] All tables created
   - [ ] Indexes verified
   - [ ] Functions tested

2. **Code Integration**
   - [ ] Debug logging integrated
   - [ ] Error classification integrated
   - [ ] Confidence scoring integrated
   - [ ] Prompt engineering integrated

3. **Testing**
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Accuracy tests run successfully
   - [ ] Performance tests acceptable

4. **Monitoring**
   - [ ] Dashboard accessible
   - [ ] Alerts configured
   - [ ] Logging operational
   - [ ] Backup systems tested

### Deploy to Production

```bash
# 1. Backup current deployment
./backup.sh all

# 2. Deploy new code
git pull origin main
docker-compose build
docker-compose up -d

# 3. Run database migration
docker exec -it resume-parser-postgres psql -U resume_parser -d resume_parser -f /migrations/022_add_evaluation_framework.sql

# 4. Verify deployment
./healthcheck.sh

# 5. Monitor logs
docker-compose logs -f
```

---

## 📊 Step 11: Monitor and Optimize

### First Week Monitoring

1. **Daily Checks**
   - Review dashboard metrics
   - Check error logs
   - Monitor confidence scores
   - Validate accuracy trends

2. **Performance Optimization**
   - Analyze slow stages
   - Optimize database queries
   - Tune model parameters
   - Adjust retry logic

3. **Accuracy Improvement**
   - Review common errors
   - Update prompts based on failures
   - Add validation rules
   - Improve training data

---

## 🎯 Expected Outcomes

### Immediate Benefits

1. **Visibility**
   - Complete pipeline visibility
   - Intermediate result tracking
   - Error categorization
   - Performance insights

2. **Quality Improvement**
   - Systematic accuracy measurement
   - Error pattern identification
   - Data quality tracking
   - Confidence-based review

3. **Operational Excellence**
   - Proactive alerting
   - Automated monitoring
   - Simplified debugging
   - Faster issue resolution

### Long-term Benefits

1. **Continuous Improvement**
   - Data-driven optimization
   - Performance trend analysis
   - Accuracy benchmarking
   - Quality assurance

2. **Production Readiness**
   - Comprehensive monitoring
   - Error recovery mechanisms
   - Scalability validation
   - Security compliance

3. **Business Value**
   - Reduced manual review
   - Improved parsing accuracy
   - Better user experience
   - Lower operational costs

---

## 📞 Support and Maintenance

### Regular Maintenance Tasks

- **Daily**: Monitor dashboard, review alerts
- **Weekly**: Review accuracy trends, analyze errors
- **Monthly**: Generate comprehensive reports, update benchmarks
- **Quarterly**: Review architecture, optimize performance

### Troubleshooting

1. **Debug logging not working**
   - Check if enabled in configuration
   - Verify file permissions
   - Review integration code

2. **Accuracy tests failing**
   - Verify ground truth data
   - Check test file paths
   - Review parser initialization

3. **Dashboard not updating**
   - Check database connection
   - Verify time filters
   - Review cache settings

---

This implementation guide provides a complete roadmap for integrating the evaluation framework into your Resume Parser application. Follow these steps systematically to ensure a smooth transition to production-ready parsing with comprehensive monitoring and quality assurance.