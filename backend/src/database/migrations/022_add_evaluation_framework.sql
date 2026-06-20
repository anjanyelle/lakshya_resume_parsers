-- ============================================================
-- EVALUATION FRAMEWORK DATABASE SCHEMA
-- Migration 022: Add comprehensive evaluation and debugging tables
-- ============================================================

-- ============================================================
-- 1. EVALUATION DEBUG LOGS
-- Stores all intermediate results for debugging and analysis
-- ============================================================

CREATE TABLE IF NOT EXISTS evaluation_debug_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    parsing_job_id UUID REFERENCES parsing_jobs(id) ON DELETE CASCADE,
    request_id VARCHAR(100), -- For request tracing
    stage VARCHAR(50) NOT NULL, -- 'text_extraction', 'section_splitting', 'model_input', 'model_output', 'final_output'
    log_type VARCHAR(20) NOT NULL, -- 'input', 'processing', 'output', 'error'
    data JSONB NOT NULL, -- The actual log data
    metadata JSONB, -- Additional metadata (timestamps, sizes, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_debug_logs_candidate_id ON evaluation_debug_logs(candidate_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_debug_logs_parsing_job_id ON evaluation_debug_logs(parsing_job_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_debug_logs_request_id ON evaluation_debug_logs(request_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_debug_logs_stage ON evaluation_debug_logs(stage);
CREATE INDEX IF NOT EXISTS idx_evaluation_debug_logs_created_at ON evaluation_debug_logs(created_at DESC);

-- ============================================================
-- 2. EVALUATION TEST RESULTS
-- Stores accuracy test results for systematic evaluation
-- ============================================================

CREATE TABLE IF NOT EXISTS evaluation_test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite VARCHAR(100) NOT NULL, -- 'simple_resumes', 'complex_resumes', etc.
    test_case_id VARCHAR(100) NOT NULL, -- Unique identifier for test case
    resume_file_path VARCHAR(500),
    resume_file_type VARCHAR(20),
    ground_truth_data JSONB NOT NULL, -- Expected results
    parsed_data JSONB NOT NULL, -- Actual results
    metrics JSONB NOT NULL, -- Accuracy metrics, F1 scores, etc.
    test_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    test_duration_ms INTEGER,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_evaluation_test_results_test_suite ON evaluation_test_results(test_suite);
CREATE INDEX IF NOT EXISTS idx_evaluation_test_results_test_case_id ON evaluation_test_results(test_case_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_test_results_test_date ON evaluation_test_results(test_date DESC);

-- ============================================================
-- 3. EVALUATION ERROR LOGS
-- Comprehensive error classification and tracking
-- ============================================================

CREATE TYPE error_category AS ENUM (
    'extraction_error', 'section_splitter_error', 'model_inference_error', 
    'json_formatting_error', 'validation_error', 'system_error'
);

CREATE TABLE IF NOT EXISTS evaluation_error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE SET NULL,
    parsing_job_id UUID REFERENCES parsing_jobs(id) ON DELETE SET NULL,
    request_id VARCHAR(100),
    error_type VARCHAR(50) NOT NULL, -- Specific error type
    error_category error_category NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    context_data JSONB, -- Pipeline state, input data, etc.
    recovery_attempted BOOLEAN DEFAULT false,
    recovery_successful BOOLEAN,
    recovery_method VARCHAR(100),
    severity VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_error_logs_candidate_id ON evaluation_error_logs(candidate_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_error_logs_parsing_job_id ON evaluation_error_logs(parsing_job_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_error_logs_error_type ON evaluation_error_logs(error_type);
CREATE INDEX IF NOT EXISTS idx_evaluation_error_logs_error_category ON evaluation_error_logs(error_category);
CREATE INDEX IF NOT EXISTS idx_evaluation_error_logs_severity ON evaluation_error_logs(severity);
CREATE INDEX IF NOT EXISTS idx_evaluation_error_logs_created_at ON evaluation_error_logs(created_at DESC);

-- ============================================================
-- 4. EVALUATION PERFORMANCE METRICS
-- Detailed performance tracking for each pipeline stage
-- ============================================================

CREATE TABLE IF NOT EXISTS evaluation_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parsing_job_id UUID REFERENCES parsing_jobs(id) ON DELETE CASCADE,
    request_id VARCHAR(100),
    stage_name VARCHAR(50) NOT NULL, -- 'text_extraction', 'section_splitting', etc.
    duration_ms INTEGER NOT NULL,
    memory_usage_mb INTEGER,
    cpu_usage_percent NUMERIC(5,2),
    input_size_bytes INTEGER,
    output_size_bytes INTEGER,
    custom_metrics JSONB, -- Stage-specific metrics
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_performance_metrics_parsing_job_id ON evaluation_performance_metrics(parsing_job_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_performance_metrics_stage_name ON evaluation_performance_metrics(stage_name);
CREATE INDEX IF NOT EXISTS idx_evaluation_performance_metrics_recorded_at ON evaluation_performance_metrics(recorded_at DESC);

-- ============================================================
-- 5. EVALUATION CONFIDENCE SCORES
-- Detailed confidence scoring for extracted fields
-- ============================================================

CREATE TABLE IF NOT EXISTS evaluation_confidence_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    parsing_job_id UUID REFERENCES parsing_jobs(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL, -- 'name', 'email', 'work_experience', etc.
    field_path VARCHAR(200), -- For nested fields: 'work_experience[0].company'
    confidence_score NUMERIC(5,4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    confidence_factors JSONB, -- Breakdown of confidence calculation
    validation_results JSONB, -- Validation pass/fail for each rule
    extraction_method VARCHAR(50), -- 'rule_based', 'deberta', 'llm', 'hybrid'
    requires_review BOOLEAN DEFAULT false,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_confidence_scores_candidate_id ON evaluation_confidence_scores(candidate_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_confidence_scores_parsing_job_id ON evaluation_confidence_scores(parsing_job_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_confidence_scores_field_name ON evaluation_confidence_scores(field_name);
CREATE INDEX IF NOT EXISTS idx_evaluation_confidence_scores_requires_review ON evaluation_confidence_scores(requires_review);

-- ============================================================
-- 6. EVALUATION TEST SUITES
-- Metadata for test suites and test cases
-- ============================================================

CREATE TABLE IF NOT EXISTS evaluation_test_suites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    suite_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    suite_type VARCHAR(50), -- 'accuracy', 'performance', 'stress', 'regression'
    target_accuracy NUMERIC(5,2), -- Target accuracy percentage
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_run TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS evaluation_test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    suite_id UUID REFERENCES evaluation_test_suites(id) ON DELETE CASCADE,
    test_case_id VARCHAR(100) NOT NULL,
    description TEXT,
    resume_file_path VARCHAR(500),
    difficulty_level VARCHAR(20), -- 'easy', 'medium', 'hard', 'expert'
    expected_outcome VARCHAR(50), -- 'success', 'partial_success', 'failure'
    tags JSONB, -- ['formatting', 'multilingual', 'scanned_pdf', etc.]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_evaluation_test_cases_suite_id ON evaluation_test_cases(suite_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_test_cases_test_case_id ON evaluation_test_cases(test_case_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_test_cases_difficulty_level ON evaluation_test_cases(difficulty_level);

-- ============================================================
-- 7. EVALUATION SUMMARY
-- Aggregated evaluation metrics for dashboard
-- ============================================================

CREATE TABLE IF NOT EXISTS evaluation_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    summary_date DATE NOT NULL,
    total_resumes_processed INTEGER DEFAULT 0,
    successful_parses INTEGER DEFAULT 0,
    failed_parses INTEGER DEFAULT 0,
    success_rate NUMERIC(5,2),
    avg_processing_time_ms NUMERIC(10,2),
    avg_confidence_score NUMERIC(5,2),
    error_breakdown JSONB, -- Count by error type
    accuracy_metrics JSONB, -- Overall accuracy metrics
    performance_metrics JSONB, -- Performance trends
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_summary_summary_date ON evaluation_summary(summary_date DESC);
CREATE INDEX IF NOT EXISTS idx_evaluation_summary_created_at ON evaluation_summary(created_at DESC);

-- Trigger for auto-updating updated_at
DROP TRIGGER IF EXISTS set_evaluation_summary_updated_at ON evaluation_summary;
CREATE TRIGGER set_evaluation_summary_updated_at
    BEFORE UPDATE ON evaluation_summary
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 8. VIEWS FOR COMMON QUERIES
-- ============================================================

-- View for parsing job performance summary
CREATE OR REPLACE VIEW v_parsing_job_performance AS
SELECT 
    pj.id as parsing_job_id,
    pj.candidate_id,
    pj.status,
    pj.processing_duration_ms,
    pj.confidence_score,
    COUNT(epl.id) as debug_log_count,
    COUNT(eel.id) as error_count,
    COUNT(epm.id) as performance_metric_count,
    COUNT(ecs.id) as confidence_score_count
FROM parsing_jobs pj
LEFT JOIN evaluation_debug_logs epl ON pj.id = epl.parsing_job_id
LEFT JOIN evaluation_error_logs eel ON pj.id = eel.parsing_job_id
LEFT JOIN evaluation_performance_metrics epm ON pj.id = epm.parsing_job_id
LEFT JOIN evaluation_confidence_scores ecs ON pj.id = ecs.parsing_job_id
GROUP BY pj.id;

-- View for error analysis
CREATE OR REPLACE VIEW v_error_analysis AS
SELECT 
    error_category,
    error_type,
    COUNT(*) as error_count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage,
    AVG(CASE WHEN recovery_successful THEN 100 ELSE 0 END) as recovery_rate,
    MIN(created_at) as first_occurrence,
    MAX(created_at) as last_occurrence
FROM evaluation_error_logs
GROUP BY error_category, error_type
ORDER BY error_count DESC;

-- View for accuracy trends
CREATE OR REPLACE VIEW v_accuracy_trends AS
SELECT 
    test_suite,
    DATE(test_date) as test_date,
    COUNT(*) as total_tests,
    AVG((metrics->>'text_extraction_accuracy')::NUMERIC) as avg_text_accuracy,
    AVG((metrics->>'section_detection_accuracy')::NUMERIC) as avg_section_accuracy,
    AVG((metrics->>'entity_extraction_accuracy')::NUMERIC) as avg_entity_accuracy,
    AVG((metrics->>'overall_accuracy')::NUMERIC) as avg_overall_accuracy
FROM evaluation_test_results
GROUP BY test_suite, DATE(test_date)
ORDER BY test_date DESC;

-- ============================================================
-- 9. FUNCTIONS FOR COMMON OPERATIONS
-- ============================================================

-- Function to record debug log
CREATE OR REPLACE FUNCTION record_debug_log(
    p_candidate_id UUID,
    p_parsing_job_id UUID,
    p_request_id VARCHAR(100),
    p_stage VARCHAR(50),
    p_log_type VARCHAR(20),
    p_data JSONB,
    p_metadata JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO evaluation_debug_logs (
        candidate_id, parsing_job_id, request_id, stage, log_type, data, metadata
    ) VALUES (
        p_candidate_id, p_parsing_job_id, p_request_id, p_stage, p_log_type, p_data, p_metadata
    ) RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- Function to record error
CREATE OR REPLACE FUNCTION record_error_log(
    p_candidate_id UUID,
    p_parsing_job_id UUID,
    p_request_id VARCHAR(100),
    p_error_type VARCHAR(50),
    p_error_category error_category,
    p_error_message TEXT,
    p_stack_trace TEXT DEFAULT NULL,
    p_context_data JSONB DEFAULT NULL,
    p_severity VARCHAR(20) DEFAULT 'medium'
) RETURNS UUID AS $$
DECLARE
    v_error_id UUID;
BEGIN
    INSERT INTO evaluation_error_logs (
        candidate_id, parsing_job_id, request_id, error_type, error_category,
        error_message, stack_trace, context_data, severity
    ) VALUES (
        p_candidate_id, p_parsing_job_id, p_request_id, p_error_type, p_error_category,
        p_error_message, p_stack_trace, p_context_data, p_severity
    ) RETURNING id INTO v_error_id;
    
    RETURN v_error_id;
END;
$$ LANGUAGE plpgsql;

-- Function to record performance metric
CREATE OR REPLACE FUNCTION record_performance_metric(
    p_parsing_job_id UUID,
    p_request_id VARCHAR(100),
    p_stage_name VARCHAR(50),
    p_duration_ms INTEGER,
    p_memory_usage_mb INTEGER DEFAULT NULL,
    p_cpu_usage_percent NUMERIC DEFAULT NULL,
    p_custom_metrics JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_metric_id UUID;
BEGIN
    INSERT INTO evaluation_performance_metrics (
        parsing_job_id, request_id, stage_name, duration_ms,
        memory_usage_mb, cpu_usage_percent, custom_metrics
    ) VALUES (
        p_parsing_job_id, p_request_id, p_stage_name, p_duration_ms,
        p_memory_usage_mb, p_cpu_usage_percent, p_custom_metrics
    ) RETURNING id INTO v_metric_id;
    
    RETURN v_metric_id;
END;
$$ LANGUAGE plpgsql;

-- Function to generate daily evaluation summary
CREATE OR REPLACE FUNCTION generate_daily_evaluation_summary(p_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    v_total_resumes INTEGER;
    v_successful_parses INTEGER;
    v_failed_parses INTEGER;
    v_success_rate NUMERIC;
    v_avg_processing_time NUMERIC;
    v_avg_confidence NUMERIC;
    v_error_breakdown JSONB;
BEGIN
    -- Calculate metrics
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE status = 'success'),
        COUNT(*) FILTER (WHERE status = 'failed'),
        AVG(COUNT(*) FILTER (WHERE status = 'success') * 100.0 / COUNT(*)),
        AVG(processing_duration_ms),
        AVG(confidence_score)
    INTO v_total_resumes, v_successful_parses, v_failed_parses, v_success_rate, v_avg_processing_time, v_avg_confidence
    FROM parsing_jobs
    WHERE DATE(created_at) = p_date;
    
    -- Get error breakdown
    SELECT json_object_agg(error_type, error_count)
    INTO v_error_breakdown
    FROM (
        SELECT error_type, COUNT(*) as error_count
        FROM evaluation_error_logs
        WHERE DATE(created_at) = p_date
        GROUP BY error_type
    ) subquery;
    
    -- Insert or update summary
    INSERT INTO evaluation_summary (
        summary_date, total_resumes_processed, successful_parses, failed_parses,
        success_rate, avg_processing_time_ms, avg_confidence_score, error_breakdown
    ) VALUES (
        p_date, v_total_resumes, v_successful_parses, v_failed_parses,
        v_success_rate, v_avg_processing_time, v_avg_confidence, v_error_breakdown
    )
    ON CONFLICT (summary_date) DO UPDATE SET
        total_resumes_processed = EXCLUDED.total_resumes_processed,
        successful_parses = EXCLUDED.successful_parses,
        failed_parses = EXCLUDED.failed_parses,
        success_rate = EXCLUDED.success_rate,
        avg_processing_time_ms = EXCLUDED.avg_processing_time_ms,
        avg_confidence_score = EXCLUDED.avg_confidence_score,
        error_breakdown = EXCLUDED.error_breakdown,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 10. SAMPLE DATA FOR TESTING
-- ============================================================

-- Insert sample test suite
INSERT INTO evaluation_test_suites (suite_name, description, suite_type, target_accuracy) VALUES
('accuracy_benchmark', 'Main accuracy benchmark suite with 100+ test cases', 'accuracy', 85.0),
('performance_test', 'Performance and load testing suite', 'performance', NULL),
('regression_test', 'Regression testing for known issues', 'regression', 90.0)
ON CONFLICT (suite_name) DO NOTHING;

-- ============================================================
-- End of Migration 022
-- ============================================================